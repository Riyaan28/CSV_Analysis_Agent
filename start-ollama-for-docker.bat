@echo off
echo ====================================
echo Configuring Ollama for Docker Access
echo ====================================
echo.

echo Setting OLLAMA_HOST to allow Docker connections...
setx OLLAMA_HOST "0.0.0.0:11434"

echo.
echo ====================================
echo IMPORTANT: Restart Ollama for changes to take effect
echo ====================================
echo.
echo Steps:
echo 1. Close Ollama (right-click system tray icon and Quit)
echo 2. Start Ollama again from Start Menu
echo 3. Then run: docker-compose up -d
echo.
echo After Ollama restarts, it will listen on 0.0.0.0:11434
echo and Docker containers will be able to connect!
echo.
pause
