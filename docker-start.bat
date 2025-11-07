@echo off
REM Docker Quick Start Script for CSV Analysis Agent

echo ====================================
echo CSV Analysis Agent - Docker Setup
echo ====================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [1/4] Docker is running...
echo.

REM Check if Ollama is running on host
echo [2/4] Checking Ollama connection...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo Ollama is running on host machine
    echo Container will connect to host.docker.internal:11434
) else (
    echo WARNING: Ollama not detected on localhost:11434
    echo Make sure Ollama is running before using the app
)
echo.

REM Build and start containers
echo [3/4] Building and starting containers...
docker-compose up -d --build

if %errorlevel% equ 0 (
    echo.
    echo [4/4] Success! Container is starting...
    echo.
    echo ====================================
    echo Application is now running!
    echo ====================================
    echo.
    echo Open your browser and go to:
    echo http://localhost:8501
    echo.
    echo To view logs:    docker-compose logs -f
    echo To stop:         docker-compose down
    echo.
    timeout /t 3 >nul
    start http://localhost:8501
) else (
    echo.
    echo ERROR: Failed to start containers
    echo Check the error messages above
    pause
)
