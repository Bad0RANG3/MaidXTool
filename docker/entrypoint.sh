#!/bin/sh
set -eu

if [ ! -f /app/sdgb/settings.py ]; then
    echo >&2 "[B50 Bot] Missing /app/sdgb/settings.py."
    echo >&2 "Copy sdgb/.settings.py to sdgb/settings.py, fill in the arcade settings, then start the container again."
    exit 64
fi

mkdir -p "${B50_DATA_DIR:-/data}"
exec "$@"
