from pydantic import BaseModel
from typing import Dict, List, Tuple, Optional


# class ImageResponse(BaseModel):
#     """이미지 처리 응답 스키마"""
#     input_width: int
#     input_height: int
#     output_width: int
#     output_height: int
#     input_metric: float  # 선명도 또는 노이즈 레벨
#     output_metric: float  # 선명도 또는 노이즈 레벨
#     input_image_url: str
#     output_image_url: str
#     processing_time: float  # 처리 시간 (초)


# class AnalysisResponse(BaseModel):
#     """두유 분석 응답 스키마"""
#     input_width: int
#     input_height: int
#     output_width: int
#     output_height: int
#     input_metric: float
#     output_metric: float
#     average_angle: float
#     min_index: int
#     width: int
#     marks: List[int]
#     sorted_marks: List[Tuple[int, int]]
#     predict_value: Optional[float]
#     input_image_url: str
#     cropped_image_url: str
#     output_image_url: str


class ShootingResult(BaseModel):
    nth: int
    score: float
    time: float
    pointX: float
    pointY: float
    distance: int
    color: str


class MajorError(BaseModel):
    major_error_name: str
    confidence: float


class ShootingAnalysisRequest(BaseModel):
    """탄착 분석 요청 스키마"""
    game_record_hd_id: str


class ShootingAnalysisResponse(BaseModel):
    """탄착 분석 응답 스키마"""
    game_id: str
    user_id: str
    dominant_hand: str
    shooting_result: List[ShootingResult]
    coi: List[float]
    mean_radius: float
    std: List[float]
    ttf: float
    skill_level: str
    threshold: float
    error_probabilities: Dict[str, float]
    major_error: List[MajorError]
    analysis_text: str
    recommend_text: str


class ErrorResponse(BaseModel):
    """에러 응답 스키마"""
    detail: str 