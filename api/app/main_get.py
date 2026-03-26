"""
GET 전용 서버 - 분석 앱/프론트엔드가 사용
포트: 8000

실행 (api/ 디렉토리에서):
    python app/main_get.py
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys
import tempfile
from pathlib import Path
from dotenv import load_dotenv

from app.routers import shooting_get

load_dotenv()

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent.parent.parent  # api/app/ → api/ → Shooting/

FRONTEND_BUILD_DIR = BASE_DIR / "frontend" / "build"
UPLOADS_DIR = Path(tempfile.gettempdir()) / "shooting_ai_system" / "uploads"
RESULTS_DIR = Path(tempfile.gettempdir()) / "shooting_ai_system" / "results"

app = FastAPI(
    title="Shooting Analysis - GET Server",
    description="사격 데이터 조회 및 분석 서버",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(shooting_get.router, prefix="/api/shootinganalysis", tags=["Shooting GET"])

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/results", StaticFiles(directory=str(RESULTS_DIR)), name="results")

if FRONTEND_BUILD_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_BUILD_DIR / "static")), name="static")

    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        if full_path.startswith("api/") or full_path.startswith("static/"):
            return {"detail": "Not Found"}
        return FileResponse(str(FRONTEND_BUILD_DIR / "index.html"))
else:
    @app.get("/")
    async def root():
        return {"message": "GET 서버 실행 중 (포트 8000)"}


if __name__ == "__main__":
    uvicorn.run("app.main_get:app", host="0.0.0.0", port=8000, reload=True)
