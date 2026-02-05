from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys
import tempfile
from pathlib import Path

from api.app.routers import shootinganalysis

# 경로 설정 (PyInstaller 패키징 고려)
if getattr(sys, 'frozen', False):
    # PyInstaller로 패키징된 경우
    BASE_DIR = Path(sys._MEIPASS)
else:
    # 일반 실행의 경우
    BASE_DIR = Path(__file__).parent.parent.parent

# 프론트엔드 빌드 디렉토리 경로
FRONTEND_BUILD_DIR = BASE_DIR / "frontend" / "build"

# 결과 및 업로드 디렉토리 설정
UPLOADS_DIR = Path(tempfile.gettempdir()) / "shooting_ai_system" / "uploads"
RESULTS_DIR = Path(tempfile.gettempdir()) / "shooting_ai_system" / "results"

print("app.main.py 진입")
app = FastAPI(
    title="Shooting Analysis System",
    description="두유 농도계 시스템",
    version="2.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 특정 도메인으로 제한하는 것이 좋습니다
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(shootinganalysis.router, prefix="/api/shootinganalysis", tags=["Shooting Analysis"])

# 정적 파일 서빙 (처리된 이미지 등을 저장)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/results", StaticFiles(directory=str(RESULTS_DIR)), name="results")

# 프론트엔드 정적 파일 서빙
if FRONTEND_BUILD_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_BUILD_DIR / "static")), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        # API 경로는 이미 라우터에서 처리됨
        if full_path.startswith("api/"):
            return {"detail": "Not Found"}
            
        # 정적 파일 경로는 이미 위에서 처리됨
        if full_path.startswith("static/"):
            return {"detail": "Not Found"}
            
        # 그 외의 모든 경로는 index.html로 리다이렉트 (SPA 라우팅을 위함)
        return FileResponse(str(FRONTEND_BUILD_DIR / "index.html"))
else:
    @app.get("/")
    async def root():
        return {"message": "프론트엔드 빌드 디렉토리를 찾을 수 없습니다. React 앱을 빌드하세요."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False) 