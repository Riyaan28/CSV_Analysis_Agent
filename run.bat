@echo off
echo ========================================
echo   Starting RAG Agent Locally
echo ========================================
echo.

:: Check if Ollama is running
echo [1/3] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Ollama not running. Starting Ollama...
    start /B ollama serve
    timeout /t 3 /nobreak >nul
    echo [+] Ollama started
) else (
    echo [+] Ollama is running
)
echo.

:: Check if virtual environment exists
echo [2/3] Checking virtual environment...
if not exist ".\venv\Scripts\python.exe" (
    echo [X] Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)
echo [+] Virtual environment found
echo.

:: Start Streamlit
echo [3/3] Starting Streamlit app...
echo.
echo ========================================
echo   App running at: http://localhost:8501
echo ========================================
echo.
.\venv\Scripts\python.exe -m streamlit run app.py
