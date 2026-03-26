import os
import sys
import time
import math
import io
from typing import List, Tuple, Dict, Optional

import numpy as np
import pandas as pd
from PIL import Image
from pathlib import Path
from fastapi import Request, APIRouter, UploadFile, File, HTTPException, Form
from openai import AzureOpenAI
from sklearn.cluster import DBSCAN
from sqlalchemy import text

from datetime import datetime
from app.models.schemas import (
    ShootingResult, MajorError, ShootingAnalysisRequest, ShootingAnalysisResponse, ErrorResponse,
    ShootingDataRecord, SyncDataRequest, SyncDataResponse, SessionDataResponse,
)
from app.models.shootinginfer import ShootingInference
from app.utils.model_utils import get_save_path
from app.utils.db import get_engine

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "data" / "laser"

engine = get_engine()


def load_game_record(game_id: str) -> pd.DataFrame:
    """
    Load shooting records for a specific game session from DB.

    Args:
        game_id (str): Unique identifier of the shooting session (hd_id).

    Returns:
        pd.DataFrame: Shooting records for the session.

    Raises:
        ValueError: If no records are found for the given game_id.
    """
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
    """
    Detect a dense cluster using DBSCAN.

    NOTE:
    - This is NOT a strict 'circle of diameter D' check.
    - This detects density-connected clusters with max neighbor distance R.

    Args:
        points: list of (x, y) normalized coordinates
        min_shots: DBSCAN min_samples
        diameter: group diameter (15 MOA @ 10m normalized)

    Returns:
        dict with:
            - found (bool)
            - center (x, y) or None
            - indices (list of shot indices)
    """
    if len(points) < min_shots:
        return {"found": False, "center": None, "indices": []}

    pts = np.array(points)
    R = diameter / 2

    dbscan = DBSCAN(
        eps=R,
        min_samples=min_shots,
        metric="euclidean",
    ).fit(pts)

    labels = dbscan.labels_
    print(f"DBSCAN labels: {labels}")
    # labels: -1 = noise, 0,1,2,... = cluster id

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
        return {
            "found": True,
            "center": center.tolist(),
            "indices": best_indices,
        }

    return {"found": False, "center": None, "indices": []}

def calculate_result(shooting_result: list) -> Tuple[List[float], float, List[float], str]:
    """
    Calculate COI (Center of Impact), Mean Radius, standard deviations and skill level.

    This function computes statistical shooting accuracy metrics based on
    a list of `ShootingResult` objects.

    Metrics:
        - COI (Center of Impact):
            Mean of X and Y coordinates.
        - Mean Radius (MR):
            Mean Euclidean distance of each shot from the COI.
        - Standard deviation:
            Standard deviation of X and Y coordinates.

    Args:
        shooting_result (list[ShootingResult]):
            List of shooting results containing impact coordinates.

    Returns:
        Tuple[List[float], float, List[float], str]:
            - coi: [mean_x, mean_y]
            - mean_radius: Mean radial distance from COI
            - std: [sigma_x, sigma_y]
            - skill_level: str ("초급", "중급", "고급")
    """
    x_vals = np.array([shot.pointX for shot in shooting_result], dtype=np.float64)
    y_vals = np.array([shot.pointY for shot in shooting_result], dtype=np.float64)
    points = np.column_stack((x_vals, y_vals))

    # COI
    coi_x = float(np.mean(x_vals))
    coi_y = float(np.mean(y_vals))
    # coi_x = float(np.median(x_vals))
    # coi_y = float(np.median(y_vals))
    old_coi = np.array([coi_x, coi_y])

    distances = np.linalg.norm(points - old_coi, axis=1)
    mean_radius = float(np.mean(distances))
    std = [float(np.std(x_vals, ddof=0)), float(np.std(y_vals, ddof=0))]
    print(f"mean_radius: {mean_radius}")

    # mean_d = np.median(distances)
    mean_d = np.mean(distances)
    std_d = np.std(distances, ddof=0)
    threshold = mean_d + std_d * 1
    valid_mask = distances <= threshold
    valid_points = points[valid_mask]
    print(f"valid points len: {len(valid_points)}")
    
    diameter = 0.1706
    grouping_result = detect_group_dbscan(points.tolist(), min_shots=4, diameter=diameter)
    print("grouping_result:", grouping_result["found"])

    if grouping_result["found"] == False:
        skill_level = "입문"
        print(f"skill_level: {skill_level}")

        return old_coi.tolist(), mean_radius, std, skill_level, threshold
    
    else:
        coi = grouping_result["center"]

        total_score = sum([shot.score for shot in shooting_result])
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
    """
    Analysis using ML model.

    This function processes the shooting analysis data using
    a machine learning model to extract relevant metrics and
    insights.
    
    Args:
        Not yet

    Returns:
        Tuple[Dict[str, float], List[MajorError]]: A tuple containing:
            - error_probabilities: A dictionary with error types as keys and their probabilities as values.
            - major_error_list: A list of MajorError instances representing significant errors detected.
    """
    
    if len(shooting_result) != 10:
        return {}, []

    model_path = str(MODEL_DIR / "shooting_model_pure_coords.pkl")
    feature_path = str(MODEL_DIR / "feature_columns.pkl")
    model = ShootingInference(
        model_path=model_path,
        feature_path=feature_path,
    )
    error_probabilities, major_error_list = model.predict(shooting_result, coi)

    if mean_radius >= 0.02:
        std_ratio = std[0] / std[1]
        lo, hi = 0.7, 1.3

        if std_ratio <= lo:
            # 수직 분산: 경계(0.7)에서 0.6, r→0으로 갈수록 1.0 수렴
            dist = math.log(lo / std_ratio)
            confidence = 0.6 + 0.4 * math.tanh(3.0 * dist)
            major_error_list.append(MajorError(major_error_name="수직 분산", confidence=round(confidence, 4)))
        elif std_ratio >= hi:
            # 수평 분산: 경계(1.3)에서 0.6, r→∞으로 갈수록 1.0 수렴
            dist = math.log(std_ratio / hi)
            confidence = 0.6 + 0.4 * math.tanh(3.0 * dist)
            major_error_list.append(MajorError(major_error_name="수평 분산", confidence=round(confidence, 4)))
        else:
            # 산란: 중심(r=1)에서 1.0, 경계(0.7/1.3)에서 0.6 (로그 선형)
            if std_ratio <= 1.0:
                t = math.log(1.0 / std_ratio) / math.log(1.0 / lo)
            else:
                t = math.log(std_ratio) / math.log(hi)
            confidence = 1.0 - 0.4 * t
            major_error_list.append(MajorError(major_error_name="산란", confidence=round(confidence, 4)))
    print("major_error_list:", major_error_list)
    
    return error_probabilities, major_error_list

def create_answers(
    skill_level: str,
    major_error: list,
) -> Tuple[str, str]:
    """Generate analysis and recommendation texts using an LLM.

    This function invokes a Large Language Model (LLM) to generate
    a natural language analysis summary and a corresponding
    recommendation based on processed shooting analysis data.

    Args:
        Not yet
        
    Returns:
        Tuple[str, str]: A tuple containing:
            - analysis_text: Generated analysis explanation.
            - recommendation_text: Generated recommendation or drill text.
    """
    print("len major_error:", len(major_error))
    if len(major_error) == 0:
        analysis_text = "세션 분석에는 10발 사격 결과가 필요합니다."
        recommendation_text = "세션 분석에는 10발 사격 결과가 필요합니다."

    else:
        major_error_text = "\n".join(
            f"- {e.major_error_name}"
            for e in major_error
        )
        print("major error text:", major_error_text)

        client = AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            api_version="2025-03-01-preview",
        )

        system_prompt = (
            "당신은 권총 사격을 지도하는 전문 코치이다. "
            "이미 분석된 사격 오류를 바탕으로 원인 설명과 교정 조언만 제공한다.\n\n"

            "숙련도별 코칭 전략:\n"
            "- 입문: 탄착군 그룹핑에 실패한 것과 해결하기 위한 가장 기초적인 방법을 설명합니다. \n"
            "- 초급: 안전과 가장 기초적인 그립, 트리거 조작의 원리를 친절하고 상세하게 설명합니다. \n"
            "- 중급: 동작의 일관성과 정밀도를 높이는 데 집중하며, 잘못된 습관을 교정하는 기술적 조언을 제공합니다. \n"
            "- 고급: 미세한 근육 조절, 호흡의 완성도, 심리적 안정을 강조하며 전문적인 용어를 곁들여 핵심만 전달합니다. \n\n"

            "절대 규칙:\n"
            "- 사격 오류를 새로 추론하거나 재분류하지 마라\n"
            "- 입력으로 주어진 '주요 오류'만을 근거로 설명하라\n"
            "- 수치, 좌표, 방향, 확률, 신뢰도라는 표현을 절대 사용하지 마라\n"
            "- 오류명은 영문 그대로 사용하고, 그 외 설명은 한국어로 작성하라\n"
            "- 이모지를 사용하지 마라\n"
            "- 모든 문장은 '-합니다'체나 '-됩니다'체를 사용하라\n\n"

            "출력 형식:\n"
            "- 두 개의 단락으로 구성하고 각 단락명과 내용은 줄바꿈으로 구분 (분석 / 피드백)\n"
            "- 전체 200자 이내\n"
        )

        user_prompt = f"""
        [유저 정보]
        숙련도: {skill_level}

        [사격 분석 결과 - 주요 오류]
        {major_error_text}

        [지시 사항]
        1. 위 주요 오류가 사격 동작에서 어떻게 발생했는지 설명하라.
        2. 오류들이 서로 어떤 연관성을 가지는지 간략히 서술하라.
        3. 각 오류를 교정하기 위한 실질적인 훈련 포인트를 제시하라.
        4. 분석 단락과 피드백 단락으로 나누어 작성하라.
        5. 수치, 방향, 좌표, 확률은 절대 언급하지 마라.
        """

        response = client.responses.create(
            model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            max_output_tokens=400,
        )

        full_text = response.output_text.strip()
        print("LLM full_text\n", full_text)

        if "\n\n" in full_text:
            analysis_text, recommendation_text = full_text.split("\n\n", 1)
            analysis_text = analysis_text.split("분석", 1)[-1].strip()
            recommendation_text = recommendation_text.split("피드백", 1)[-1].strip()
        else:
            analysis_text = full_text
            recommendation_text = ""

    return analysis_text, recommendation_text


# CSV 파일은 모듈 로드 시 1회만 읽어 메모리에 유지
_COACHING_TABLE_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "coaching_lookup.csv"
_COACHING_TABLE: pd.DataFrame = pd.read_csv(_COACHING_TABLE_PATH)

# major_error_name → CSV error_en 매핑
# ML 모델 label_map 출력값 + 분산 오류 한글명 모두 포함
_ERROR_NAME_MAP = {
    # ML 모델 출력 (shootinginfer.py label_map)
    "급격한 방아쇠 당김(Jerking)":    "Jerking",
    "손바닥 밀어올림(Heeling)":       "Heeling",
    "엄지 압력/방아쇠 손가락 불량":   "Thumbing",
    "검지 끝 사용 불량":              "Too Little Finger",
    "그립 과도 압력(Lobstering)":     "Lobstering",
    # 분산 오류 (create_analysis에서 직접 추가)
    "수직 분산": "Vertical Variance",
    "수평 분산": "Horizontal Variance",
    "산란":     "Scattering",
}

# skill_level → CSV level 매핑 (입문/완벽은 테이블에 없으므로 근사값 사용)
_LEVEL_MAP = {
    "입문": "초급",
    "초급": "초급",
    "중급": "중급",
    "고급": "고급",
    "완벽": "고급",
}


def create_answers_table(
    skill_level: str,
    major_error: list,
) -> Tuple[str, str]:
    """Generate analysis and recommendation texts from coaching_lookup.csv.

    Args:
        skill_level (str): Shooter skill level ("입문"/"초급"/"중급"/"고급"/"완벽").
        major_error (list[MajorError]): List of detected major errors.

    Returns:
        Tuple[str, str]:
            - analysis_text: Coaching description per error.
            - recommend_text: Drills and key points per error.
    """
    if not major_error:
        msg = "세션 분석에는 10발 사격 결과가 필요합니다."
        return msg, msg

    level = _LEVEL_MAP.get(skill_level, "초급")
    df = _COACHING_TABLE

    analysis_lines = []
    recommend_lines = []

    for err in major_error:
        # error_en 또는 error(한글) 컬럼으로 매핑
        en_name = _ERROR_NAME_MAP.get(err.major_error_name, err.major_error_name)
        row = df[(df["error_en"] == en_name) & (df["level"] == level)]

        # 정확히 일치하는 행이 없으면 초급으로 fallback
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


@router.get("/users", response_model=List[str])
async def get_users() -> List[str]:
    """
    Retrieve all unique user IDs from game_record_hd.
    """
    try:
        query = text("SELECT DISTINCT user_id FROM game_record_hd WHERE user_id IS NOT NULL AND user_id != '' ORDER BY user_id")
        with engine.connect() as conn:
            rows = conn.execute(query).fetchall()

        user_ids = [row[0] for row in rows if row[0] is not None]
        print("len users:", len(user_ids))
        return user_ids

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"유저 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")


@router.get("/sessions", response_model=List[str])
async def get_sessions(user_id: Optional[str] = None) -> List[str]:
    """
    Retrieve shooting session IDs from game_record_hd, optionally filtered by user_id.

    Args:
        user_id (str, optional): Filter sessions by this user ID.

    Returns:
        List[str]: A list of unique shooting session IDs.
    """
    try:
        if user_id:
            query = text("""
                SELECT hd.id
                FROM game_record_hd hd
                WHERE hd.user_id = :user_id
                  AND EXISTS (SELECT 1 FROM game_record_dt dt WHERE dt.hd_id = hd.id)
                ORDER BY hd.created_at DESC
            """)
            params = {"user_id": user_id}
        else:
            query = text("""
                SELECT hd.id
                FROM game_record_hd hd
                WHERE EXISTS (SELECT 1 FROM game_record_dt dt WHERE dt.hd_id = hd.id)
                ORDER BY hd.created_at DESC
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
    """
    Process shooting analysis for a specific session.

    This endpoint loads shooting data for the given session ID,
    constructs structured shooting results, computes accuracy metrics,
    performs error analysis, and returns a complete analysis response.

    Args:
        request (Request):
            FastAPI request object.
        game_id (str):
            Unique identifier of the shooting session.

    Returns:
        ShootingAnalysisResponse:
            Full shooting analysis including metrics, errors,
            and recommendation texts.

    Raises:
        HTTPException:
            If data loading, processing, or validation fails.
    """    
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
    """
    shooting_analysis_data 테이블에서 user_id (및 session_id)로 데이터 조회.

    Args:
        user_id (str): 조회할 사용자 ID.
        session_id (str, optional): 특정 세션 ID (hd_id). 없으면 해당 유저의 전체 데이터 반환.

    Returns:
        SessionDataResponse: 조회된 사격 데이터 레코드 목록.
    """
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


@router.post("/sync", response_model=SyncDataResponse)
async def sync_data(request_body: SyncDataRequest) -> SyncDataResponse:
    """
    원천 데이터를 shooting_analysis_data 테이블에 동기화.
    이미 존재하는 (hd_id, nth) 조합은 스킵(upsert).

    Args:
        request_body (SyncDataRequest): 동기화할 사격 데이터 레코드 목록.

    Returns:
        SyncDataResponse: 삽입 수, 스킵 수, 결과 메시지.
    """
    try:
        inserted = 0
        skipped = 0

        with engine.begin() as conn:
            for record in request_body.records:
                create_at_val = record.create_at if record.create_at else datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

                result = conn.execute(text("""
                    INSERT IGNORE INTO shooting_analysis_data
                        (hd_id, nth, score, point_x, point_y, shot_time, user_id, distance, create_at)
                    VALUES
                        (:hd_id, :nth, :score, :point_x, :point_y, :shot_time, :user_id, :distance, :create_at)
                """), {
                    "hd_id": record.hd_id,
                    "nth": record.nth,
                    "score": record.score,
                    "point_x": record.point_x,
                    "point_y": record.point_y,
                    "shot_time": record.shot_time,
                    "user_id": record.user_id,
                    "distance": record.distance,
                    "create_at": create_at_val,
                })

                # INSERT IGNORE: rowcount 1 = 삽입, 0 = 중복 스킵
                if result.rowcount == 1:
                    inserted += 1
                else:
                    skipped += 1

        return SyncDataResponse(
            inserted=inserted,
            skipped=skipped,
            message=f"동기화 완료: {inserted}개 삽입, {skipped}개 스킵",
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"데이터 동기화 중 오류가 발생했습니다: {str(e)}")