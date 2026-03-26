"""
POST 전용 서버 - 사격 장비 / 데이터 수집 앱이 사용
포트: 8001

실행 (api/ 디렉토리에서):
    python app/main_post.py
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routers import shooting_post

load_dotenv()

app = FastAPI(
    title="Shooting Analysis - POST Server",
    description="사격 원천 데이터 수신 및 저장 서버",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

app.include_router(shooting_post.router, prefix="/api/shootinganalysis", tags=["Shooting POST"])


@app.get("/")
async def root():
    return {"message": "POST 서버 실행 중 (포트 8001)"}


if __name__ == "__main__":
    uvicorn.run("app.main_post:app", host="0.0.0.0", port=8001, reload=True)
