#!/usr/bin/env bash
# B50 QQ 机器人 - 一键启动（Linux / macOS）
# 前提：NapCat（OneBot v11 WS 服务端，监听 127.0.0.1:3001）可用，
#       bot/.venv 已按 README 建好。
set -e
cd "$(dirname "$0")"

echo "============================================"
echo "  B50 QQ 机器人 - 一键启动"
echo "============================================"

if [ -f napcat/start_napcat.sh ] && [ -d napcat/shell ] && [ -f napcat/shell/napcat.mjs ]; then
    echo "  1/2 启动 NapCat（QQ 协议端）..."
    (bash napcat/start_napcat.sh &)
    echo "  等待 NapCat 就绪（15 秒）..."
    sleep 15
else
    echo "  [提示] 本机未找到 NapCat 部署，跳过；"
    echo "         请确认 127.0.0.1:3001 的 OneBot WS 服务可用（Docker 等）"
fi

echo "  2/2 启动 NoneBot2（B50 插件）..."
exec bash bot/start.sh
