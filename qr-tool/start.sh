#!/usr/bin/env bash
# QR 解码页（http://127.0.0.1:8787）
set -e
cd "$(dirname "$0")"

echo "Starting QR server on http://localhost:8787 ..."
node server.js &
sleep 2
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:8787 >/dev/null 2>&1 || true
fi
wait
