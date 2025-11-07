# PowerShell script to run the RAG Agent app locally
Write-Host "🚀 Starting RAG Agent..." -ForegroundColor Green

# Check if Ollama is running
Write-Host "Checking Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Ollama not running. Starting Ollama..." -ForegroundColor Yellow
    Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Write-Host "✅ Ollama started" -ForegroundColor Green
}

# Check if virtual environment exists
if (-Not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found! Please run: python -m venv venv" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment and run Streamlit
Write-Host "Starting Streamlit app..." -ForegroundColor Cyan
Write-Host "➜ Local:   http://localhost:8501" -ForegroundColor Green
Write-Host ""
.\venv\Scripts\python.exe -m streamlit run app.py
