@echo off
echo.
echo  ========================================
echo   SENTINEL Intel - OSINT Platform v2.0
echo   Starting Backend + Frontend...
echo  ========================================
echo.

:: Start backend
echo [1/2] Starting FastAPI backend on http://127.0.0.1:8000 ...
cd /d "%~dp0"
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
start "SENTINEL Backend" cmd /k "cd /d "%~dp0" && venv\Scripts\activate && pip install -r backend\requirements.txt && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload || pause"

:: Wait for backend to start (takes a while because it loads AI models)
echo [1.5/2] Waiting for backend to load AI models (this can take 30-60 seconds on first run)...
timeout /t 30 /nobreak > nul

:: Start frontend
echo [2/2] Starting React frontend on http://localhost:5173 ...
if not exist "%~dp0\frontend\node_modules" (
    echo Installing frontend dependencies (this will only happen once)...
    cmd /c "cd /d "%~dp0\frontend" && npm install"
)
start "SENTINEL Frontend" cmd /k "cd /d "%~dp0\frontend" && npm run dev"

echo.
echo  ========================================
echo   SENTINEL Intel is starting up!
echo.
echo   Dashboard:  http://localhost:5173
echo   API Docs:   http://127.0.0.1:8000/docs
echo   Backend:    http://127.0.0.1:8000
echo  ========================================
echo.
pause
