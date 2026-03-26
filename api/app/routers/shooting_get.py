import os
import sys
import math
from typing import List, Tuple, Dict, Optional

import numpy as np
import pandas as pd
from pathlib import Path
from fastapi import Request, APIRouter, HTTPException
from openai import AzureOpenAI
from sklearn.cluster import DBSCAN
from sqlalchemy import text

from app.models.schemas import (
    ShootingResult, MajorError, ShootingAnalysisResponse, ErrorResponse,
    ShootingDataRecord, SessionDataResponse,
)
from app.models.shootinginfer import ShootingInference
from app.utils.db import get_engine

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "data" / "laser"

engine = get_engine()

# CSV 파일은 모듈 로드 시 1회만 읽어 메모리에 유지
_COACHING_TABLE_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "coaching_lookup.csv"
_COACHING_TABLE: pd.DataFrame = pd.read_csv(_COACHING_TABLE_PATH)

_ERROR_NAME_MAP = {
    "급격한 방아쇠 당김(Jerking)":    "Jerking",
    "손바닥 밀어올림(Heeling)":       "Heeling",
    "엄지 압력/방아쇠 손가락 불량":   "Thumbing",
    "검지 끝 사용 불량":              "Too Little Finger",
    "그립 과도 압력(Lobstering)":     "Lobstering",
    "수직 분산": "Vertical Variance",
    "수평 분산": "Horizontal Variance",
    "산란":     "Scattering",
}

_LEVEL_MAP = {
    "입문": "초급",
    "초급": "초급",
    "중급": "중급",
    "고급": "고급",
    "완벽": "고급",
}


# ── 헬퍼 함수 ──────────────────────────────────────────────────────────────────

def load_game_record(game_id: str) -> pd.DataFrame:
    query = text("""
        SELECT nth, score, shot_time, point_x, point_y, distance, color
        FROM game_record_dt
        WHERE hd_id = :hd_id
        ORDER BY nth
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"hd_id": game_id})

    if df.empty:
        raise ValueError(f"Session not found: {game_id}")

    return df.reset_index(drop=True)


def detect_group_dbscan(
    points: List[Tuple[float, float]],
    min_shots: int = 4,
    diameter: float = 0.1706,
):
    if len(points) < min_shots:
        return {"found": False, "center": None, "indices": []}

    pts = np.array(points)
    R = diameter / 2

    dbscan = DBSCAN(eps=R, min_samples=min_shots, metric="euclidean").fit(pts)

    labels = dbscan.labels_
    print(f"DBSCAN labels: {labels}")

    best_cluster = None
    best_indices = []

    for label in set(labels):
        if label == -1:
            continue
        indices = np.where(labels == label)[0]
        if len(indices) >= min_shots and len(indices) > len(best_indices):
            best_indices = indices.tolist()
            best_cluster = label

    if best_cluster is not None:
        center = pts[best_indices].mean(axis=0)
        return {"found": True, "center": center.tolist(), "indices": best_indices}

    return {"found": False, "center": None, "indices": []}


def calculate_result(shooting_result: list) -> Tuple[List[float], float, List[float], str, float]:
    x_vals = np.array([shot.pointX for shot in shooting_result], dtype=np.float64)
    y_vals = np.array([shot.pointY for shot in shooting_result], dtype=np.float64)
    points = np.column_stack((x_vals, y_vals))

    coi_x = float(np.mean(x_vals))
    coi_y = float(np.mean(y_vals))
    old_coi = np.array([coi_x, coi_y])

    distances = np.linalg.norm(points - old_coi, axis=1)
    mean_radius = float(np.mean(distances))
    std = [float(np.std(x_vals, ddof=0)), float(np.std(y_vals, ddof=0))]
    print(f"mean_radius: {mean_radius}")

    mean_d = np.mean(distances)
    std_d = np.std(distances, ddof=0)
    threshold = mean_d + std_d * 1
    valid_points = points[distances <= threshold]
    print(f"valid points len: {len(valid_points)}")

    diameter = 0.1706
    grouping_result = detect_group_dbscan(points.tolist(), min_shots=4, diameter=diameter)
    print("grouping_result:", grouping_result["found"])

    if not grouping_result["found"]:
        skill_level = "입문"
        print(f"skill_level: {skill_level}")
        return old_coi.tolist(), mean_radius, std, skill_level, threshold

    coi = grouping_result["center"]
    total_score = sum(shot.score for shot in shooting_result)
    if total_score >= 100:
        skill_level = "완벽"
    elif total_score >= 95:
        skill_level = "고급"
    elif total_score >= 80:
        skill_level = "중급"
    else:
        skill_level = "초급"
    print(f"skill_level: {skill_level}")

    return coi, mean_radius, std, skill_level, diameter


def create_analysis(
    shooting_result: list,
    coi: list,
    mean_radius: float,
    std: list,
) -> Tuple[Dict[str, float], List[MajorError]]:
    if len(shooting_result) != 10:
        return {}, []

    model_path = str(MODEL_DIR / "shooting_model_pure_coords.pkl")
    feature_path = str(MODEL_DIR / "feature_columns.pkl")
    model = ShootingInference(model_path=model_path, feature_path=feature_path)
    error_probabilities, major_error_list = model.predict(shooting_result, coi)

    if mean_radius >= 0.02:
        std_ratio = std[0] / std[1]
        lo, hi = 0.7, 1.3

        if std_ratio <= lo:
            dist = math.log(lo / std_ratio)
            confidence = 0.6 + 0.4 * math.tanh(3.0 * dist)
            major_error_list.append(MajorError(major_error_name="수직 분산", confidence=round(confidence, 4)))
        elif std_ratio >= hi:
            dist = math.log(std_ratio / hi)
            confidence = 0.6 + 0.4 * math.tanh(3.0 * dist)
            major_error_list.append(MajorError(major_error_name="수평 분산", confidence=round(confidence, 4)))
        else:
            if std_ratio <= 1.0:
                t = math.log(1.0 / std_ratio) / math.log(1.0 / lo)
            else:
                t = math.log(std_ratio) / math.log(hi)
            confidence = 1.0 - 0.4 * t
            major_error_list.append(MajorError(major_error_name="산란", confidence=round(confidence, 4)))

    print("major_error_list:", major_error_list)
    return error_probabilities, major_error_list


def create_answers_table(skill_level: str, major_error: list) -> Tuple[str, str]:
    if not major_error:
        msg = "세션 분석에는 10발 사격 결과가 필요합니다."
        return msg, msg

    level = _LEVEL_MAP.get(skill_level, "초급")
    df = _COACHING_TABLE
    analysis_lines = []
    recommend_lines = []

    for err in major_error:
        en_name = _ERROR_NAME_MAP.get(err.major_error_name, err.major_error_name)
        row = df[(df["error_en"] == en_name) & (df["level"] == level)]

        if row.empty:
            row = df[(df["error_en"] == en_name) & (df["level"] == "초급")]

        if row.empty:
            print(f"[WARN] coaching_lookup에 '{en_name}' / '{level}' 항목 없음")
            continue

        r = row.iloc[0]
        analysis_lines.append(f"[{err.major_error_name}] {r['coaching']}")
        recommend_lines.append(f"[{err.major_error_name}] 드릴: {r['drill']} / 핵심: {r['key_point']}")

    analysis_text  = "\n".join(analysis_lines)  if analysis_lines  else "해당 오류에 대한 코칭 정보가 없습니다."
    recommend_text = "\n".join(recommend_lines) if recommend_lines else "해당 오류에 대한 드릴 정보가 없습니다."

    return analysis_text, recommend_text


# ── GET 엔드포인트 ─────────────────────────────────────────────────────────────

@router.get("/users", response_model=List[str])
async def get_users() -> List[str]:
    """shooting_analysis_data에서 고유 user_id 목록 반환."""
    try:
        query = text("""
            SELECT DISTINCT user_id
            FROM shooting_analysis_data
            WHERE user_id IS NOT NULL AND user_id != ''
            ORDER BY user_id
        """)
        with engine.connect() as conn:
            rows = conn.execute(query).fetchall()

        user_ids = [row[0] for row in rows if row[0] is not None]
        print("len users:", len(user_ids))
        return user_ids

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"유저 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")


@router.get("/sessions", response_model=List[str])
async def get_sessions(user_id: Optional[str] = None) -> List[str]:
    """shooting_analysis_data에서 세션 ID(hd_id) 목록 반환. user_id로 필터 가능."""
    try:
        if user_id:
            query = text("""
                SELECT DISTINCT hd_id
                FROM shooting_analysis_data
                WHERE user_id = :user_id
                ORDER BY hd_id DESC
            """)
            params = {"user_id": user_id}
        else:
            query = text("""
                SELECT DISTINCT hd_id
                FROM shooting_analysis_data
                ORDER BY hd_id DESC
            """)
            params = {}

        with engine.connect() as conn:
            rows = conn.execute(query, params).fetchall()

        session_ids = [row[0] for row in rows if row[0] is not None]
        print(f"len sessions (user_id={user_id}):", len(session_ids))
        return session_ids

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"세션 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")


@router.get("/process", response_model=ShootingAnalysisResponse, responses={400: {"model": ErrorResponse}})
async def process_analysis(request: Request, game_id: str) -> ShootingAnalysisResponse:
    """game_id에 해당하는 세션의 사격 분석을 수행하고 결과 반환."""
    try:
        data = load_game_record(game_id)

        shooting_result = [
            ShootingResult(
                nth=int(row["nth"]),
                score=float(row["score"]),
                time=float(row["shot_time"]),
                pointX=float(row["point_x"]),
                pointY=float(row["point_y"]),
                distance=int(row["distance"]),
                color=str(row["color"]),
            )
            for i, row in data.iterrows()
        ]

        coi, mean_radius, std, skill_level, threshold = calculate_result(shooting_result)

        if skill_level == "완벽":
            return ShootingAnalysisResponse(
                game_id=game_id,
                user_id="user_001",
                dominant_hand="right",
                shooting_result=shooting_result,
                coi=coi,
                mean_radius=mean_radius,
                std=std,
                ttf=6.42,
                skill_level=skill_level,
                threshold=threshold,
                error_probabilities={},
                major_error=[],
                analysis_text="완벽한 사격입니다! 모든 샷이 중심에 가깝고 일관된 결과를 보여줍니다. 현재의 그립과 자세를 유지하면서, 정기적으로 연습하여 이 수준을 지속적으로 유지하는 것을 권장드립니다.",
                recommend_text="현재의 훈련 루틴을 유지하되, 가끔씩 다른 거리나 조건에서 연습하여 다양한 상황에서도 완벽한 사격이 가능하도록 준비하는 것을 추천드립니다.",
            )
        else:
            error_probabilities, major_error = create_analysis(shooting_result, coi, mean_radius, std)
            analysis_text, recommend_text = create_answers_table(skill_level, major_error)

            return ShootingAnalysisResponse(
                game_id=game_id,
                user_id="user_001",
                dominant_hand="right",
                shooting_result=shooting_result,
                coi=coi,
                mean_radius=mean_radius,
                std=std,
                ttf=6.42,
                skill_level=skill_level,
                threshold=threshold,
                error_probabilities=error_probabilities,
                major_error=major_error,
                analysis_text=analysis_text,
                recommend_text=recommend_text,
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"탄착 분석 중 오류가 발생했습니다: {str(e)}")


@router.get("/data", response_model=SessionDataResponse)
async def get_session_data(user_id: str, session_id: Optional[str] = None) -> SessionDataResponse:
    """shooting_analysis_data에서 user_id (및 session_id)로 데이터 조회."""
    try:
        if session_id:
            query = text("""
                SELECT hd_id, nth, score, point_x, point_y, shot_time, user_id, distance, create_at
                FROM shooting_analysis_data
                WHERE user_id = :user_id AND hd_id = :hd_id
                ORDER BY hd_id, nth
            """)
            params = {"user_id": user_id, "hd_id": session_id}
        else:
            query = text("""
                SELECT hd_id, nth, score, point_x, point_y, shot_time, user_id, distance, create_at
                FROM shooting_analysis_data
                WHERE user_id = :user_id
                ORDER BY hd_id, nth
            """)
            params = {"user_id": user_id}

        with engine.connect() as conn:
            rows = conn.execute(query, params).fetchall()

        records = [
            ShootingDataRecord(
                hd_id=str(row[0]),
                nth=int(row[1]),
                score=float(row[2]),
                point_x=float(row[3]),
                point_y=float(row[4]),
                shot_time=float(row[5]),
                user_id=str(row[6]),
                distance=int(row[7]),
                create_at=str(row[8]) if row[8] else None,
            )
            for row in rows
        ]

        return SessionDataResponse(
            user_id=user_id,
            session_id=session_id,
            total_records=len(records),
            records=records,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"데이터 조회 중 오류가 발생했습니다: {str(e)}")
