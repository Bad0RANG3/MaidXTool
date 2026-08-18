FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    B50_DATA_DIR=/data

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app --home /app app

# 可选的 PyPI 镜像源（国内构建加速）：
#   docker build --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple -t maidx-tool:latest .
ARG PIP_INDEX_URL=https://pypi.org/simple

COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir --index-url "${PIP_INDEX_URL}" -r requirements.txt \
        "nonebot2>=2.0.0" \
        "nonebot-adapter-onebot>=2.4.0" \
        "fastapi>=0.100" \
        "uvicorn>=0.23" \
        "websockets>=10.0"

COPY --chown=app:app . .
COPY --chown=app:app docker/entrypoint.sh /usr/local/bin/b50-bot

RUN mkdir -p /data \
    && chown -R app:app /data \
    && chmod +x /usr/local/bin/b50-bot

USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import sys; sys.exit(0 if b'bot/bot.py' in open('/proc/1/cmdline', 'rb').read() else 1)"

ENTRYPOINT ["b50-bot"]
CMD ["python", "bot/bot.py"]
