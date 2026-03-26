"""
더미 데이터로 /sync (POST) 및 /data (GET) 엔드포인트를 테스트하는 스크립트.

사용법:
    python test_dummy.py

서버가 localhost:8000에서 실행 중이어야 합니다.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/shootinganalysis"


# ── 더미 데이터 생성 ──────────────────────────────────────────────────────────
DUMMY_SESSIONS = [
    {
        "hd_id": "test_session_001",
        "user_id": "test_user_001",
        "shots": [
            {"nth": 1,  "score": 10.0, "point_x":  0.02, "point_y":  0.01, "shot_time": 2.3, "distance": 10},
            {"nth": 2,  "score":  9.5, "point_x": -0.03, "point_y":  0.02, "shot_time": 2.8, "distance": 10},
            {"nth": 3,  "score": 10.0, "point_x":  0.01, "point_y": -0.01, "shot_time": 2.5, "distance": 10},
            {"nth": 4,  "score":  8.0, "point_x":  0.05, "point_y":  0.04, "shot_time": 3.1, "distance": 10},
            {"nth": 5,  "score":  9.0, "point_x": -0.02, "point_y": -0.03, "shot_time": 2.6, "distance": 10},
            {"nth": 6,  "score": 10.0, "point_x":  0.00, "point_y":  0.00, "shot_time": 2.4, "distance": 10},
            {"nth": 7,  "score":  9.5, "point_x":  0.03, "point_y": -0.02, "shot_time": 2.7, "distance": 10},
            {"nth": 8,  "score":  8.5, "point_x": -0.04, "point_y":  0.03, "shot_time": 2.9, "distance": 10},
            {"nth": 9,  "score": 10.0, "point_x":  0.01, "point_y":  0.01, "shot_time": 2.2, "distance": 10},
            {"nth": 10, "score":  9.0, "point_x": -0.01, "point_y": -0.02, "shot_time": 2.6, "distance": 10},
        ],
    },
    {
        "hd_id": "test_session_002",
        "user_id": "test_user_001",
        "shots": [
            {"nth": 1,  "score":  7.0, "point_x":  0.08, "point_y":  0.06, "shot_time": 3.5, "distance": 10},
            {"nth": 2,  "score":  6.5, "point_x": -0.10, "point_y":  0.07, "shot_time": 4.0, "distance": 10},
            {"nth": 3,  "score":  8.0, "point_x":  0.06, "point_y": -0.05, "shot_time": 3.3, "distance": 10},
            {"nth": 4,  "score":  5.0, "point_x":  0.12, "point_y":  0.09, "shot_time": 4.2, "distance": 10},
            {"nth": 5,  "score":  7.5, "point_x": -0.07, "point_y": -0.08, "shot_time": 3.8, "distance": 10},
            {"nth": 6,  "score":  8.0, "point_x":  0.04, "point_y":  0.05, "shot_time": 3.4, "distance": 10},
            {"nth": 7,  "score":  6.0, "point_x":  0.09, "point_y": -0.06, "shot_time": 3.9, "distance": 10},
            {"nth": 8,  "score":  7.0, "point_x": -0.08, "point_y":  0.07, "shot_time": 4.1, "distance": 10},
            {"nth": 9,  "score":  8.5, "point_x":  0.03, "point_y":  0.02, "shot_time": 3.2, "distance": 10},
            {"nth": 10, "score":  6.5, "point_x": -0.05, "point_y": -0.04, "shot_time": 3.7, "distance": 10},
        ],
    },
]


def build_sync_payload(sessions: list) -> dict:
    records = []
    create_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    for session in sessions:
        for shot in session["shots"]:
            records.append({
                "hd_id":     session["hd_id"],
                "nth":       shot["nth"],
                "score":     shot["score"],
                "point_x":   shot["point_x"],
                "point_y":   shot["point_y"],
                "shot_time": shot["shot_time"],
                "user_id":   session["user_id"],
                "distance":  shot["distance"],
                "create_at": create_at,
            })
    return {"records": records}


# ── 테스트 함수 ───────────────────────────────────────────────────────────────
def test_post_sync():
    print("\n=== POST /sync 테스트 ===")
    payload = build_sync_payload(DUMMY_SESSIONS)
    print(f"전송 레코드 수: {len(payload['records'])}")

    resp = requests.post(f"{BASE_URL}/sync", json=payload)
    print(f"상태 코드: {resp.status_code}")
    print(f"응답: {json.dumps(resp.json(), ensure_ascii=False, indent=2)}")
    return resp.status_code == 200


def test_get_data_all():
    user_id = DUMMY_SESSIONS[0]["user_id"]
    print(f"\n=== GET /data?user_id={user_id} (전체 세션) ===")

    resp = requests.get(f"{BASE_URL}/data", params={"user_id": user_id})
    print(f"상태 코드: {resp.status_code}")
    body = resp.json()
    print(f"total_records: {body.get('total_records')}")
    print(f"첫 레코드: {json.dumps(body['records'][0], ensure_ascii=False, indent=2) if body.get('records') else '없음'}")
    return resp.status_code == 200


def test_get_data_session():
    user_id  = DUMMY_SESSIONS[0]["user_id"]
    session_id = DUMMY_SESSIONS[0]["hd_id"]
    print(f"\n=== GET /data?user_id={user_id}&session_id={session_id} ===")

    resp = requests.get(f"{BASE_URL}/data", params={"user_id": user_id, "session_id": session_id})
    print(f"상태 코드: {resp.status_code}")
    body = resp.json()
    print(f"total_records: {body.get('total_records')}")
    return resp.status_code == 200


def test_post_sync_duplicate():
    """동일 데이터를 재전송해 중복 스킵 동작을 확인."""
    print("\n=== POST /sync 중복 테스트 ===")
    payload = build_sync_payload([DUMMY_SESSIONS[0]])

    resp = requests.post(f"{BASE_URL}/sync", json=payload)
    print(f"상태 코드: {resp.status_code}")
    body = resp.json()
    print(f"응답: {json.dumps(body, ensure_ascii=False, indent=2)}")
    assert body.get("skipped", 0) == len(DUMMY_SESSIONS[0]["shots"]), "중복 스킵이 올바르지 않습니다."
    return resp.status_code == 200


# ── 메인 ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results = {
        "POST /sync (신규)":     test_post_sync(),
        "GET /data (전체)":      test_get_data_all(),
        "GET /data (세션 지정)": test_get_data_session(),
        "POST /sync (중복)":     test_post_sync_duplicate(),
    }

    print("\n\n=== 테스트 결과 요약 ===")
    for name, ok in results.items():
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")
