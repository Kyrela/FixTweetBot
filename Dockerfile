# Build stage
FROM --platform=$BUILDPLATFORM python:3.11-slim AS builder

# Add build dependencies for both architectures
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    libffi-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Use absolute paths for Python and pip
RUN /usr/local/bin/python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip wheel setuptools && \
    /opt/venv/bin/pip install --no-cache-dir cryptography PyNaCl && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

RUN echo 'import re; re.NOFLAG = 0' > /opt/venv/lib/python3.11/site-packages/discord_markdown_ast_parser/patch.py && \
    sed -i '1i from .patch import *' /opt/venv/lib/python3.11/site-packages/discord_markdown_ast_parser/lexer.py

FROM python:3.11-slim

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        netcat-traditional \
        default-libmysqlclient-dev \
        gettext-base && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

RUN chown -R appuser:appuser /app

USER appuser

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --chown=appuser:appuser docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD nc -z localhost 3306 || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "main.py"]
