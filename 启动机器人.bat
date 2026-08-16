@echo off
chcp 65001 >nul
cd /d %~dp0

echo ============================================
echo  B50 QQ 机器人 - 一键启动
echo ============================================
echo  1/2 启动 NapCat（QQ 小号协议端，独立窗口）...
start "NapCat QQ" cmd /c "napcat\start_napcat.bat"

echo  等待 NapCat 就绪（15 秒）...
timeout /t 15 /nobreak >nul

echo  2/2 启动 NoneBot2（B50 插件，独立窗口）...
start "NoneBot B50 Bot" cmd /c "cd /d bot && start_bot.bat"

echo.
echo  两个窗口都保持打开即机器人运行中。
echo  关闭窗口 = 停止对应服务。
echo  首次启动后如 NapCat 未登录，请打开 http://127.0.0.1:6099/webui 扫码。
timeout /t 8 >nul
