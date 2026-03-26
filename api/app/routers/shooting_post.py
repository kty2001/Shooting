import sys
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.models.schemas import (
    SyncDataRequest, SyncDataResponse,
    SessionSyncRequest, SessionSyncResponse,
)
from app.utils.db import get_engine

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

router = APIRouter()

engine = get_engine()


# ── POST 엔드포인트 ────────────────────────────────────────────────────────────

@router.post("/sync", response_model=SyncDataResponse)
async def sync_data(request_body: SyncDataRequest) -> SyncDataResponse:
    """
    발 단위 데이터를 shooting_analysis_data 테이블에 동기화 (기존 방식 유지).
    이미 존재하는 (hd_id, nth) 조합은 스킵.
    """
    try:
        inserted = 0
        skipped = 0

        with engine.begin() as conn:
            for record in request_body.records:
                create_at_val = (
                    record.create_at
                    if record.create_at
                    else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )

                result = conn.execute(text("""
                    INSERT IGNORE INTO shooting_analysis_data
                        (hd_id, nth, score, point_x, point_y, shot_time, user_id, distance, create_at)
                    VALUES
                        (:hd_id, :nth, :score, :point_x, :point_y, :shot_time, :user_id, :distance, :create_at)
                """), {
                    "hd_id":      record.hd_id,
                    "nth":        record.nth,
                    "score":      record.score,
                    "point_x":    record.point_x,
                    "point_y":    record.point_y,
                    "shot_time":  record.shot_time,
                    "user_id":    record.user_id,
                    "distance":   record.distance,
                    "create_at":  create_at_val,
                })

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


@router.post("/session-sync", response_model=SessionSyncResponse)
async def session_sync(request_body: SessionSyncRequest) -> SessionSyncResponse:
    """
    세션 단위 데이터를 save_record_hd / save_record_dt 테이블에 저장.

    - 헤더(save_record_hd): 세션 요약 정보 1행 저장
    - 상세(save_record_dt): shooting_result 리스트의 각 발 저장
    - 이미 존재하는 세션 id는 헤더/상세 모두 스킵
    """
    try:
        hd_inserted = 0
        hd_skipped = 0
        dt_inserted = 0

        with engine.begin() as conn:
            # ── 1. save_record_hd 저장 ──────────────────────────────────────
            hd_result = conn.execute(text("""
                INSERT IGNORE INTO save_record_hd
                    (id, game_id, mst_idx, user_id,
                     shooting_point_tot, shooting_point_best, shooting_point_worst,
                     shooting_point_avg, shooting_point_tot_by_perfect,
                     shooting_count, total_shooting_time, disqualified, grade, created_at)
                VALUES
                    (:id, :game_id, :mst_idx, :user_id,
                     :shooting_point_tot, :shooting_point_best, :shooting_point_worst,
                     :shooting_point_avg, :shooting_point_tot_by_perfect,
                     :shooting_count, :total_shooting_time, :disqualified, :grade, :created_at)
            """), {
                "id":                          request_body.id,
                "game_id":                     request_body.game_id,
                "mst_idx":                     request_body.mst_idx,
                "user_id":                     request_body.user_id,
                "shooting_point_tot":          request_body.shooting_point_tot,
                "shooting_point_best":         request_body.shooting_point_best,
                "shooting_point_worst":        request_body.shooting_point_worst,
                "shooting_point_avg":          request_body.shooting_point_avg,
                "shooting_point_tot_by_perfect": request_body.shooting_point_tot_by_perfect,
                "shooting_count":              request_body.shooting_count,
                "total_shooting_time":         request_body.total_shooting_time,
                "disqualified":                request_body.disqualified,
                "grade":                       request_body.grade,
                "created_at":                  request_body.created_at if request_body.created_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

            if hd_result.rowcount == 1:
                hd_inserted = 1

                # ── 2. save_record_dt 저장 (헤더가 새로 삽입된 경우만) ──────
                for shot in request_body.shooting_result:
                    conn.execute(text("""
                        INSERT INTO save_record_dt
                            (hd_id, nth, score, point_x, point_y,
                             distance, shot_time)
                        VALUES
                            (:hd_id, :nth, :score, :point_x, :point_y,
                             :distance, :shot_time)
                    """), {
                        "hd_id":    request_body.id,
                        "nth":      shot.nth,
                        "score":    shot.score,
                        "point_x":  shot.point_x,
                        "point_y":  shot.point_y,
                        "distance": shot.distance,
                        "shot_time":shot.shot_time,
                    })
                    dt_inserted += 1

            else:
                hd_skipped = 1

        return SessionSyncResponse(
            hd_inserted=hd_inserted,
            hd_skipped=hd_skipped,
            dt_inserted=dt_inserted,
            message=f"세션 {'저장 완료' if hd_inserted else '이미 존재 (스킵)'}: hd {hd_inserted}건, dt {dt_inserted}건",
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"세션 동기화 중 오류가 발생했습니다: {str(e)}")
