FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_CACHE_DIR=/tmp/uv-cache PYTHONUNBUFFERED=1
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .
RUN groupadd --system app && useradd --system --gid app app && chown -R app:app /app /tmp/uv-cache
USER app
EXPOSE 8000
CMD ["uv", "run", "--frozen", "python", "-m", "app.start"]
