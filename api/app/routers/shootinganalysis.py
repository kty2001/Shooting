import os
import time
import math
import io
from typing import List, Tuple, Dict

import numpy as np
import pandas as pd
from PIL import Image
from pathlib import Path
from fastapi import Request, APIRouter, UploadFile, File, HTTPException, Form
from openai import AzureOpenAI

from app.models.schemas import ShootingResult, MajorError, ShootingAnalysisRequest, ShootingAnalysisResponse, ErrorResponse
from app.utils.model_utils import get_save_path

router = APIRouter()

DATA_DIR = Path("../data/game_record")
GAME_RECORD_SP = None


def load_all_game_records() -> pd.DataFrame:
    """
    Load and concatenate all shooting game record CSV files into a single DataFrame.

    This function searches for CSV files matching the pattern
    `game_record_sp_sample_*.csv` under `DATA_DIR`, reads them into pandas
    DataFrames, and concatenates them into one unified DataFrame.

    Returns:
        pd.DataFrame:
            A DataFrame containing all loaded game record data.

    Raises:
        RuntimeError:
            If no valid CSV files could be loaded.
    """
    dfs = []
    csv_files = sorted(DATA_DIR.glob("game_record_sp_sample_*.csv"))
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            dfs.append(df)

        except Exception as e:
            print(f"[WARN] failed to load {csv_file}: {e}")
        break

    if not dfs:
        raise RuntimeError("No valid CSV files loaded")

    return pd.concat(dfs, ignore_index=True)

def load_game_record(game_id: str) -> pd.DataFrame:
    """
    Load shooting records for a specific game session.

    This function filters the preloaded global DataFrame `GAME_RECORD_SP`
    using the given `game_id` (matched against the `hd_id` column)
    and returns only the rows belonging to that session.

    Args:
        game_id (str):
            Unique identifier of the shooting session.

    Returns:
        pd.DataFrame:
            A DataFrame containing shooting records for the specified session.

    Raises:
        ValueError:
            If no records are found for the given `game_id`.
    """
    df = GAME_RECORD_SP

    session_df = df[df["hd_id"] == game_id]

    if session_df.empty:
        raise ValueError(f"Session not found: {game_id}")

    return session_df.reset_index(drop=True)

def calculate_coi_mr_std(shooting_result: list):
    """
    Calculate COI (Center of Impact), Mean Radius, and standard deviations.

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
        Tuple[List[float], float, List[float]]:
            - coi: [mean_x, mean_y]
            - mean_radius: Mean radial distance from COI
            - std: [sigma_x, sigma_y]
    """
    x_vals = np.array([shot.pointX for shot in shooting_result])
    y_vals = np.array([shot.pointY for shot in shooting_result])

    # COI
    coi_x = float(np.mean(x_vals))
    coi_y = float(np.mean(y_vals))
    coi = [float(np.mean(x_vals)), float(np.mean(y_vals))]

    r = np.sqrt((x_vals - coi_x)**2 + (y_vals - coi_y)**2)
    mean_radius = float(np.mean(r))

    std_x = float(np.std(x_vals, ddof=0))
    std_y = float(np.std(y_vals, ddof=0))
    std = [std_x, std_y]

    return coi, mean_radius, std

def create_analysis():
    """Analysis using ML model.

    This function processes the shooting analysis data using
    a machine learning model to extract relevant metrics and
    insights.
    
    Args:
        Not yet

    Returns:
        Tuple[str, Dict[str, float], List[MajorError]]: A tuple containing:
            - skill_level: A string representing the assessed skill level.
            - error_probabilities: A dictionary with error types as keys and their probabilities as values.
            - major_error_list: A list of MajorError instances representing significant errors detected.
    """
    skill_level = "Beginner"
    error_probabilities = {
        "sample_error_probability1": 0.24,
        "sample_error_probability2": 0.34,
        "sample_error_probability3": 0.44,
    }
    major_error_list = [
        MajorError(major_error_name="Sample", confidence=0.85),
        MajorError(major_error_name="Example", confidence=0.75)
    ]

    return skill_level, error_probabilities, major_error_list

def create_answers(
    skill_level: str,
    error_probabilities: dict,
    major_error: list,
    coi: list,
    mean_radius: float,
    std: list,
):
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
    dx = coi[0] - 0.5
    dy = coi[1] - 0.5

    if abs(dx) < 0.03 and abs(dy) < 0.03:
        direction = "중앙"
    elif dx < 0 and dy < 0:
        direction = "좌상(10~11시)"
    elif dx < 0 and dy > 0:
        direction = "좌하(7~8시)"
    elif dx > 0 and dy < 0:
        direction = "우상(1~2시)"
    else:
        direction = "우하(4~5시)"

    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        api_version="2025-03-01-preview",
    )

    # ---- prompt 구성 ----
    system_prompt = ("당신은 권총 사격을 지도하는 전문 코치이자 탄착군 분석 전문가이다. "
        "다음 사격 진단 기준을 바탕으로 분석하며, 오류명을 제외한 나머지 답변은 한국어로만 작성한다.\n\n"
                
        "[편향(COI) 진단 기준]\n"
        "- 7시 방향: Jerking(급격한 방아쇠 당김) / 트리거 속도 유지 필요\n"
        "- 3시/9시 방향: 방아쇠 손가락 위치 불량 / 손가락 배치 점검 필요\n"
        "- 1시 방향: Heeling(손바닥 밀어올림) / 그립 압력 및 손목 고정 필요\n"
        "- 3시 방향(측면): Thumbing(엄지로 프레임 밀어냄) / 엄지 위치 고정 필요\n"
        "- 5시 방향: Lobstering(그립 과도한 압력) / 일정 그립 압력 유지 필요\n\n"
        
        "[분산(MR/Std) 진단 기준]\n"
        "- 상하 분산이 큰 경우(Vertical Variance): 호흡 불안정 및 어깨 긴장 / 어깨 이완 및 발사 순간 호흡 정지 필요\n"
        "- 좌우 분산이 큰 경우(Horizontal Variance): 자세 및 그립 비대칭 / 스탠스 안정화 및 대칭적 그립 압력 필요\n"
        "- 전반적 분산이 큰 경우(Scattering): 다수 문제 복합 / 조준 및 트리거 컨트롤 기본기 재정렬 필요\n\n"
        
        "설명은 간결해야 하며, 수치 값(좌표, 표준편차 등)은 절대 직접 언급하지 말고 그 의미와 경향만 설명한다. "
        "공백 포함 300자 이내로 제한하며, 두 개의 단락(분석/권고)으로 구성한다."
    )

    user_prompt = f"""
    사격 통계 데이터:
    - 탄착 중심 편향 방향: {direction}
    - 평균 반경 (MR): {mean_radius:.4f}
    - 탄착 분산: σx={std[0]:.4f}, σy={std[1]:.4f}

    지시 사항:
    1. 위 데이터를 시스템 지침의 '진단 기준'에 대입하여 핵심 문제를 1~2개 도출하라.
    2. COI 편향 방향은 위에 주어진 값을 그대로 사용하고 재판단하지 마라.
    3. COI의 편향 방향(시계 방향 기준)과 분산 비율(σx/σy)에 따른 문제점을 각각 설명하라.
    4. 수치와 좌표는 절대 언급하지 말고 '경향성'으로만 표현하라.
    5. 분석 문단과 교정 권고 문단으로 나누어 작성하라.
    """
    # Shooter skill level: {skill_level}

    # ML 예측 오류 유형 및 확률:
    # {error_probabilities}

    # 주요 오류:
    # {major_error}

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
        # temperature=0.4,
        max_output_tokens=300,
    )

    full_text = response.output_text.strip()
    print("LLM full_text\n", full_text)

    # ---- 간단 분리 (또는 JSON 출력으로 바꿔도 됨) ----
    if "\n\n" in full_text:
        analysis_text, recommendation_text = full_text.split("\n\n", 1)
    else:
        analysis_text = full_text
        recommendation_text = ""

    return analysis_text, recommendation_text


GAME_RECORD_SP = load_all_game_records()


@router.get("/sessions", response_model=List[str])
async def get_sessions():
    """
    Retrieve all available shooting session IDs.

    This endpoint extracts unique session identifiers (`hd_id`)
    from the preloaded game record DataFrame.

    Returns:
        List[str]:
            A list of unique shooting session IDs.

    Raises:
        HTTPException:
            If the required `hd_id` column is missing or data access fails.
    """
    try:
        print(GAME_RECORD_SP.columns)
        if "hd_id" not in GAME_RECORD_SP.columns:
            raise HTTPException(status_code=400, detail="GAME_RECORD_SP에 'hd_id' 컬럼이 없습니다.")

        session_ids = GAME_RECORD_SP["hd_id"].dropna().unique()
        session_ids = list(map(str, session_ids))
        print("len sessions:", len(session_ids))

        return session_ids
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"세션 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")


@router.get("/process", response_model=ShootingAnalysisResponse, responses={400: {"model": ErrorResponse}})
async def process_analysis(request: Request, game_id: str):
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
        print(data)
        
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
        print("shooting_result[0]:", shooting_result[0])

        coi, mean_radius, std = calculate_coi_mr_std(shooting_result)

        skill_level, error_probabilities, major_error = create_analysis()
        
        analysis_text, recommend_text = create_answers(
            skill_level=skill_level,
            error_probabilities=error_probabilities,
            major_error=major_error,
            coi=coi,
            mean_radius=mean_radius,
            std=std,
        )

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
            error_probabilities=error_probabilities,
            major_error=major_error,
            analysis_text=analysis_text,
            recommend_text=recommend_text,
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"탄착 분석 중 오류가 발생했습니다: {str(e)}")