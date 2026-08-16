@echo off
cd /d "%~dp0"
echo Starting QR server on http://localhost:8787 ...
start "QR Decoder Server" /min cmd /c "node server.js"
timeout /t 2 /nobreak >nul
start "" "http://localhost:8787"
