from pydantic import BaseModel
from typing import Dict, List, Tuple, Optional
from datetime import datetime


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


class ShootingDataRecord(BaseModel):
    """분석용 사격 데이터 레코드 (shooting_analysis_data 테이블)"""
    hd_id: str
    user_id: str
    nth: int
    score: float
    point_x: float
    point_y: float
    shot_time: float
    distance: int
    create_at: Optional[str] = None


class SyncDataRequest(BaseModel):
    """원천 데이터 동기화 요청"""
    records: List[ShootingDataRecord]


class SyncDataResponse(BaseModel):
    """동기화 응답"""
    inserted: int
    skipped: int
    message: str


class SessionDataResponse(BaseModel):
    """세션 데이터 조회 응답"""
    user_id: str
    session_id: Optional[str]
    total_records: int
    records: List[ShootingDataRecord]


class ShotResultItem(BaseModel):
    """shooting_result 리스트의 개별 발 데이터"""
    hd_id: str
    nth: int
    score: Optional[float] = None
    point_x: float                   # save_record_dt NOT NULL
    point_y: float                   # save_record_dt NOT NULL
    distance: Optional[float] = None
    shot_time: Optional[float] = None
    direction: Optional[str] = None
    color: Optional[str] = None
    user_id: Optional[str] = None
    image_path: Optional[str] = None


class SessionSyncRequest(BaseModel):
    """세션 단위 동기화 요청 (헤더 + 발별 데이터)"""
    id: str
    game_id: Optional[str] = None
    mst_idx: Optional[int] = 0
    user_id: Optional[str] = None
    shooting_point_tot: Optional[float] = 0
    shooting_point_best: Optional[float] = 0
    shooting_point_worst: Optional[float] = 0
    shooting_point_avg: Optional[float] = 0
    shooting_point_tot_by_perfect: Optional[float] = 0
    shooting_count: Optional[int] = 0
    total_shooting_time: Optional[float] = 0
    disqualified: Optional[int] = 0
    grade: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    video_path: Optional[str] = None
    shooting_result: List[ShotResultItem]


class SessionSyncResponse(BaseModel):
    """세션 동기화 응답"""
    hd_inserted: int
    hd_skipped: int
    dt_inserted: int
    message: str