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
# from openai import AzureOpenAI

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

    return "skill level", {"sample_error_probability": 0.24}, [{"major_error_name": "Sample", "confidence": 0.85}]

def create_answers():
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
    
    return "sample analysis text", "sample recommend text"

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
        
        analysis_text, recommend_text = create_answers()

        # # 절대 URL 생성
        # base_url = str(request.base_url).rstrip("/")
        # input_url = f"{base_url}/uploads/{os.path.basename(cropped_input_filename)}"
        # cropped_output_url = f"{base_url}/results/{os.path.basename(cropped_filename)}"
        # output_url = f"{base_url}/results/{os.path.basename(output_filename)}"

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
        raise HTTPException(status_code=400, detail=f"이미지 처리 중 오류가 발생했습니다: {str(e)}")