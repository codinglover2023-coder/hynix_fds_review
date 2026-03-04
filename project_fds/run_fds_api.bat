@echo off
chcp 65001 >nul
echo ============================================
echo  FDS Review API - Local Dev Server
echo ============================================

cd /d "%~dp0project_fds"

REM 가상환경 활성화 (있으면)
if exist ".venv\Scripts\activate.bat" (
    echo [*] 가상환경 활성화 중...
    call .venv\Scripts\activate.bat
) else if exist "%~dp0.venv\Scripts\activate.bat" (
    echo [*] 상위 가상환경 활성화 중...
    call "%~dp0.venv\Scripts\activate.bat"
)

REM 의존성 설치
echo [*] 의존성 설치 중...
pip install -r requirements.txt -q

REM 서버 실행
echo [*] FastAPI 서버 시작 (http://127.0.0.1:8000)
echo [*] Swagger UI: http://127.0.0.1:8000/docs
echo ============================================
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

pause
