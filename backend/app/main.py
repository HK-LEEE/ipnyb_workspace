from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .routers import auth
from .database import create_tables

# FastAPI 앱 생성
app = FastAPI(
    title="Jupyter Data Platform API",
    description="Jupyter 기반 데이터 분석 플랫폼",
    version="1.0.0"
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 테이블 생성
create_tables()

# 라우터 추가
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# 정적 파일 서빙 (업로드된 파일용)
if not os.path.exists("data"):
    os.makedirs("data")
    
app.mount("/static", StaticFiles(directory="data"), name="static")

@app.get("/")
async def root():
    return {
        "message": "Jupyter Data Platform API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "API가 정상적으로 작동 중입니다."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 