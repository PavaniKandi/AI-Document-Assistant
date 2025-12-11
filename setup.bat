@echo off
echo.
echo 🚀 Document Q&A Application - Quick Setup
echo ===========================================
echo.

:: Check if Ollama is running
echo Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  Ollama is not running!
    echo Please start Ollama or download from https://ollama.ai
    pause
    exit /b 1
)
echo ✅ Ollama is running
echo.

:: Backend setup
echo Setting up backend...
cd backend

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment and install
call venv\Scripts\activate.bat
echo Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1

echo ✅ Backend ready
echo.

:: Frontend setup
cd ..\frontend

echo Installing Node dependencies...
call npm install >nul 2>&1

echo ✅ Frontend ready
echo.

echo ===========================================
echo Setup complete! Now run:
echo.
echo Terminal 1 (Backend):
echo   cd backend
echo   venv\Scripts\activate
echo   python app.py
echo.
echo Terminal 2 (Frontend):
echo   cd frontend
echo   npm run dev
echo.
echo Then open: http://localhost:3000
echo ===========================================
pause
