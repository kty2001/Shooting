-- 분석용 사격 데이터 테이블
-- 원천 테이블(game_record_hd, game_record_dt)에서 필요한 컬럼만 추출하여 저장

CREATE TABLE IF NOT EXISTS game_record_ff (
    id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    hd_id      VARCHAR(100)   NOT NULL COMMENT '세션 ID (game_record_hd.id)',
    nth        INT            NOT NULL COMMENT '발사 순서',
    score      FLOAT          NOT NULL COMMENT '점수',
    point_x    FLOAT          NOT NULL COMMENT '탄착 X 좌표 (정규화)',
    point_y    FLOAT          NOT NULL COMMENT '탄착 Y 좌표 (정규화)',
    shot_time  FLOAT          NOT NULL COMMENT '발사 시간 (초)',
    user_id    VARCHAR(100)   NOT NULL COMMENT '사용자 ID',
    distance   INT            NOT NULL COMMENT '사격 거리 (m)',
    create_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성 시각',

    UNIQUE KEY uq_hd_nth (hd_id, nth),
    INDEX idx_user_id (user_id),
    INDEX idx_hd_id   (hd_id)
) CHARACTER SET utf8mb4 COMMENT='분석 전용 사격 데이터 테이블 (game_record_ff)';
