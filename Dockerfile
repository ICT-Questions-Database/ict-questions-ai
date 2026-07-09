FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN mkdir -p src && touch src/__init__.py

RUN pip install uv && uv sync --no-dev

COPY . .

RUN uv sync --no-dev

EXPOSE 8001

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]