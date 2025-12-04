FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Copy application code
COPY mcp_server ./mcp_server
COPY demo_data ./demo_data

# Install dependencies
RUN uv sync --frozen --no-cache

# Default command
CMD ["uv", "run", "python", "-m", "demo_data.seed_topics"]
