import os
import sys
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
from app.models.shootinginfer import ShootingInference
from app.utils.model_utils import get_save_path

sys.stdout.reconfigure(encoding='utf-8')

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "game_record"
MODEL_DIR = BASE_DIR / "data" / "laser"
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
    old_coi = np.array([coi_x, coi_y])

    distances = np.linalg.norm(points - old_coi, axis=1)
    sigma = np.std(distances, ddof=0)
    threshold = sigma * 2

    valid_mask = distances <= threshold
    valid_points = points[valid_mask]
    print(f"valid points len: {len(valid_points)}")

    if len(valid_points) < 5:

        mean_radius = float(np.mean(distances))
        std = [float(np.std(x_vals, ddof=0)), float(np.std(y_vals, ddof=0))]
        skill_level = "입문"
        print(f"skill_level: {skill_level}")

        return old_coi.tolist(), mean_radius, std, skill_level, threshold
    
    else:
        filtered_points = valid_points

        refined_coi_x = float(np.mean(filtered_points[:, 0]))
        refined_coi_y = float(np.mean(filtered_points[:, 1]))
        coi = [refined_coi_x, refined_coi_y]

        r = np.sqrt(
            (filtered_points[:, 0] - refined_coi_x) ** 2 +
            (filtered_points[:, 1] - refined_coi_y) ** 2
        )
        mean_radius = float(np.mean(r))

        std_x = float(np.std(filtered_points[:, 0], ddof=0))
        std_y = float(np.std(filtered_points[:, 1], ddof=0))
        std = [std_x, std_y]

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

        return coi, mean_radius, std, skill_level, threshold

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

    model_path = str(MODEL_DIR / "shooting_model_v7.pkl")
    feature_path = str(MODEL_DIR / "feature_columns_v7.pkl")
    model = ShootingInference(
        model_path=model_path,
        feature_path=feature_path,
    )
    error_probabilities, major_error_list = model.predict(shooting_result, coi, mean_radius, std)
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
            max_output_tokens=200,
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


GAME_RECORD_SP = load_all_game_records()


@router.get("/sessions", response_model=List[str])
async def get_sessions() -> List[str]:
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
        elif skill_level == "입문":
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
                analysis_text="입문 단계입니다. 샷들이 중심에서 멀리 떨어져 있고, 일관성이 부족한 모습입니다. 그립과 자세를 점검하고, 기본적인 트리거 조작 연습에 집중하는 것을 권장드립니다.",
                recommend_text="기본적인 사격 자세와 그립을 교정하는 드릴을 추천드립니다. 예를 들어, 벽에 총을 대고 그립을 연습하거나, 트리거 조작을 손가락만으로 연습하는 드릴이 도움이 될 수 있습니다.",
            )
        else:
            print(5)
            error_probabilities, major_error = create_analysis(shooting_result, coi, mean_radius, std)
            analysis_text, recommend_text = create_answers(skill_level, major_error)

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