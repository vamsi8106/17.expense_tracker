# ------------ Base Stage ------------
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH="/app"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates openssl \
    && rm -rf /var/lib/apt/lists/*

# Install uv properly
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Verify installation (important)
RUN which uv && uv --version

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev
RUN uv add uvicorn[standard]
ENV PATH="/app/.venv/bin:${PATH}"

COPY src ./src

# ------------ FINAL STAGE ------------
FROM base AS final

# Copy .env into container
COPY .env /app/.env

# Load .env for all child processes (Streamlit, Uvicorn, MCP server)
ENV ENV_FILE="/app/.env"

EXPOSE 8000
EXPOSE 8501

CMD ["/bin/bash", "-c", "\
    export $(grep -v '^#' /app/.env | xargs) && \
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000 & \
    streamlit run src/frontend/app.py --server.port=8501 --server.address=0.0.0.0 \
"]

# CMD ["/bin/bash", "-c", "\
#     uvicorn src.api.main:app --host 0.0.0.0 --port 8000 & \
#     streamlit run src/frontend/app.py --server.port=8501 --server.address=0.0.0.0 \
# "]

# CMD ["run.sh"]
