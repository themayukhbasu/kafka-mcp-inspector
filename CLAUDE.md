# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Kafka MCP Inspector** is an MCP (Model Context Protocol) server that enables natural language queries to Kafka clusters through Claude AI. This is a portfolio/educational project designed to be cloned and run locally in under 10 minutes.

**Core Value**: Ask Claude about your Kafka cluster as if you're talking to a senior engineer with deep operational knowledge.

## Architecture

The system consists of:
- **MCP Server** (FastMCP/Python) - Exposes Kafka tools via JSON-RPC 2.0 over stdio
- **Kafka Broker** - Message streaming platform
- **Schema Registry** - Schema management for Avro/JSON messages
- **Zookeeper** - Coordination service

All components run in Docker containers. The MCP server connects to Kafka/Schema Registry and provides tools that Claude can invoke.

## Technology Stack

- **Python 3.11+** with modern tooling
- **uv** (0.4.0+) - Fast Python package manager (replaces pip/poetry/virtualenv)
- **FastMCP** (0.1.0+) - Simplified MCP server framework
- **confluent-kafka-python** (2.3.0+) - Kafka client
- **python-schema-registry-client** (2.5.0+) - Schema Registry integration

## Development Commands

### Initial Setup
```bash
# Install uv if not present
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python dependencies
uv sync

# Start Kafka stack (includes auto-seeding demo data)
docker-compose up -d

# Wait for services to be ready
sleep 60

# Verify seeding completed
docker-compose logs seed-data
```

### Running MCP Server
```bash
# Run locally for testing
uv run python -m mcp_server.server

# Run with custom config
KAFKA_BOOTSTRAP_SERVERS=localhost:9092 SCHEMA_REGISTRY_URL=http://localhost:8081 uv run python -m mcp_server.server
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=mcp_server --cov-report=html

# Run specific test
uv run pytest tests/test_kafka_tools.py::test_list_topics_returns_demo_topics
```

### Dependency Management
```bash
# Add package
uv add <package-name>

# Add dev dependency
uv add --dev <package-name>

# Update dependencies
uv lock --upgrade

# Sync after pulling changes
uv sync
```

### Docker Operations
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f kafka

# Stop services
docker-compose down

# Fresh start (remove volumes)
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build
```

### Kafka CLI Commands (via Docker)
```bash
# List topics
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Describe topic
docker-compose exec kafka kafka-topics --describe --topic user-events --bootstrap-server localhost:9092

# List consumer groups
docker-compose exec kafka kafka-consumer-groups --list --bootstrap-server localhost:9092

# Check consumer lag
docker-compose exec kafka kafka-consumer-groups --describe --group slow-consumer --bootstrap-server localhost:9092
```

## Code Architecture

### Project Structure
```
kafka-mcp-inspector/
├── mcp_server/
│   ├── server.py          # Main FastMCP server with tool definitions
│   └── kafka_tools.py     # Kafka operation wrappers
├── demo_data/
│   ├── seed_topics.py     # Create demo topics
│   ├── seed_messages.py   # Populate with realistic data
│   └── schemas/           # Avro schema definitions
├── tests/
│   ├── test_kafka_tools.py
│   └── test_mcp_server.py
└── claude_desktop_config/
    └── mcp_config_example.json
```

### MCP Tools Implementation

Priority 1 (MVP):
1. `list_topics()` - List all topics with partition/replication info
2. `describe_topic(topic_name: str)` - Detailed topic metadata
3. `get_consumer_lag(group_id: str)` - Lag breakdown per partition
4. `peek_messages(topic: str, count: int = 5)` - Sample recent messages

Priority 2:
5. `list_consumer_groups()` - Active consumer groups
6. `get_schema(topic: str)` - Fetch schema from registry
7. `find_message_by_key(topic: str, key: str)` - Search for specific message
8. `health_check()` - Broker health, under-replicated partitions

### Tool Implementation Pattern
```python
@mcp.tool()
def get_consumer_lag(group_id: str) -> dict:
    """
    Get consumer lag for all topics in a consumer group.

    Returns lag in number of messages for each partition.

    Args:
        group_id: The consumer group ID to analyze
    """
    try:
        # 1. Validate input
        # 2. Call Kafka API
        # 3. Process results into clean structure
        # 4. Return simple dict (no complex objects)
        return {
            "group_id": group_id,
            "total_lag": 1234,
            "partitions": [...]
        }
    except Exception as e:
        return {"error": str(e), "group_id": group_id}
```

## Code Guidelines

### Design Principles
- **Keep it simple**: Prefer readability over cleverness
- **Single responsibility**: Each tool does one thing well
- **Never crash**: Every tool should return a result, even if it's an error
- **Helpful errors**: "Consumer group 'xyz' not found" not "KeyError"
- **Fail gracefully**: If Schema Registry is down, other tools still work

### Best Practices
- Use typing hints for clarity
- Docstrings for all MCP tools (Claude uses them for tool descriptions)
- Keep files under 300 lines
- Avoid async/await unless necessary (adds complexity for demo project)
- Simple functions with clear inputs/outputs over complex class hierarchies
- Configuration via environment variables (no complex config files)

### What to Avoid
- Complex class hierarchies
- Abstract base classes (single Kafka cluster)
- Over-engineering features beyond requirements
- Premature optimization
- Multiple config file formats
- Committing `.venv/` directory

## Demo Data

The project includes pre-seeded demo data for immediate testing:

**Topics**:
1. `user-events` (Avro) - 3 partitions, ~2000 messages
2. `order-processing` (JSON) - 2 partitions, ~1000 messages
3. `system-logs` (String) - 1 partition, ~500 messages

**Consumer Groups**:
1. `order-processor` - Fully caught up (0 lag)
2. `slow-consumer` - ~1500 message lag on user-events
3. `analytics-pipeline` - ~200 message lag

This pre-seeding ensures users get immediate interesting results without manual setup.

## Claude Desktop Integration

Users configure the MCP server in `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac):

```json
{
  "mcpServers": {
    "kafka-inspector": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/kafka-mcp-inspector",
        "run",
        "python",
        "-m",
        "mcp_server.server"
      ],
      "env": {
        "KAFKA_BOOTSTRAP_SERVERS": "localhost:9092",
        "SCHEMA_REGISTRY_URL": "http://localhost:8081"
      }
    }
  }
}
```

After configuration changes, Claude Desktop must be restarted to pick up new tools.

## Environment Variables

- `KAFKA_BOOTSTRAP_SERVERS` - Kafka broker addresses (default: `kafka:9092`)
- `SCHEMA_REGISTRY_URL` - Schema Registry URL (default: `http://schema-registry:8081`)

## Testing Philosophy

Focus on:
- Demo data integrity (verify seeding works)
- Basic tool functionality (each tool returns expected structure)
- Error handling (tools don't crash on invalid input)

Not focused on:
- Performance testing
- Complex integration scenarios
- Edge cases for production systems

## Why uv?

This project uses `uv` instead of pip/poetry to demonstrate modern Python tooling:
- 10-100x faster dependency resolution
- Reproducible builds via `uv.lock`
- Single tool replaces pip, pip-tools, virtualenv
- Better error messages
- Growing adoption in Python ecosystem

Always use `uv run` prefix for Python commands in documentation.

## Project Goals

This is a **portfolio/educational project**. Priorities:
1. **Simplicity** - Clone and run in under 10 minutes
2. **Code quality** - Clean, readable, well-documented
3. **Impressive demos** - Showcase both Kafka expertise and MCP integration
4. **Modern tooling** - Using uv demonstrates staying current

Not focused on production deployment, multi-cluster management, or complex auth.