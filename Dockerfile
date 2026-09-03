FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md server.py ./
RUN pip install --no-cache-dir .

ENTRYPOINT ["mcp-server-decisions"]
