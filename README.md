# Kafka MCP Inspector

> **Ask Claude about your Kafka cluster in natural language**

An MCP (Model Context Protocol) server that bridges AI assistants like Claude with Apache Kafka. Query your Kafka clusters, inspect topics, and diagnose issues using conversational AI instead of memorizing CLI commands.

## Why?

Instead of this:
```bash
kafka-topics --bootstrap-server localhost:9092 --list
kafka-topics --bootstrap-server localhost:9092 --describe --topic user-events
kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group analytics
```

Just ask Claude:
- "What topics are in my Kafka cluster?"
- "Show me details about the user-events topic"
- "Is there any consumer lag?"

## Features

**Current (MVP)**
- ✅ List all Kafka topics with partition and replication info
- ✅ Docker Compose setup with auto-seeded demo data
- ✅ Works with Claude Desktop out of the box

**Coming Soon**
- 🔜 Peek at recent messages in topics
- 🔜 Consumer lag monitoring and diagnosis
- 🔜 Schema Registry integration
- 🔜 Topic and consumer group details

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [uv](https://docs.astral.sh/uv/getting-started/installation/) Python package manager
- [Claude Desktop](https://claude.ai/download) (or another MCP-compatible client)

### Installation (5 minutes)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/kafka-mcp-inspector.git
   cd kafka-mcp-inspector
   ```

2. **Install Python dependencies**
   ```bash
   uv sync
   ```

3. **Start Kafka and seed demo data**
   ```bash
   docker-compose up -d
   ```

   Wait about 60 seconds for Kafka to start and topics to be created.

4. **Verify it's working**
   ```bash
   # Check that 3 demo topics were created
   docker-compose logs seed-data

   # Test the MCP server locally
   uv run python -c "from mcp_server.server import list_topics; import asyncio; print(asyncio.run(list_topics()))"
   ```

5. **Configure Claude Desktop**

   Edit your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

   Add this configuration (replace `/absolute/path/to` with your actual path):
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
           "KAFKA_BOOTSTRAP_SERVERS": "localhost:9092"
         }
       }
     }
   }
   ```

6. **Restart Claude Desktop** and start asking questions!

## Example Queries

Once configured, try asking Claude:

- **"What topics exist in my Kafka cluster?"**
  - Returns list of all topics with partition counts

- **"List all the Kafka topics"**
  - Shows topic names and metadata

- **"What tools do you have for Kafka?"**
  - Displays available MCP tools

## Architecture

```
┌─────────────────────┐
│   Claude Desktop    │  ← You ask questions here
│   (MCP Client)      │
└──────────┬──────────┘
           │ stdio
           │ (JSON-RPC 2.0)
           ▼
┌─────────────────────┐
│   MCP Server        │  ← This project
│   (Python/FastMCP)  │
└──────────┬──────────┘
           │
    ┌──────┴────────┐
    ▼               ▼
┌─────────┐   ┌──────────┐
│  Kafka  │   │Zookeeper │  ← Docker containers
│ Broker  │   │          │
└─────────┘   └──────────┘
```

**How it works:**
1. You ask Claude a question about Kafka
2. Claude recognizes it needs Kafka info and calls the MCP server
3. The MCP server queries your Kafka cluster via the Admin API
4. Results are returned to Claude, which formats them naturally

## Demo Data

The project includes pre-seeded demo topics:
- **user-events** (2 partitions) - Simulated user activity events
- **order-processing** (2 partitions) - E-commerce order data
- **system-logs** (1 partition) - Application logs

This ensures you can test the MCP server immediately without manual setup.

## Project Structure

```
kafka-mcp-inspector/
├── mcp_server/
│   ├── __init__.py
│   └── server.py              # MCP server with tools
├── demo_data/
│   ├── __init__.py
│   └── seed_topics.py         # Creates demo topics
├── claude_desktop_config/
│   └── mcp_config_example.json # Configuration template
├── docker-compose.yml         # Kafka + Zookeeper
├── pyproject.toml            # Python dependencies (uv)
├── uv.lock                   # Locked dependencies
└── README.md                 # You are here
```

## Troubleshooting

### Kafka won't start

```bash
# Clean restart
docker-compose down -v
docker-compose up -d

# Check logs
docker-compose logs kafka
```

### Claude Desktop can't find the MCP server

- Verify you used the **absolute path** in your config (not `~` or relative paths)
- Make sure you restarted Claude Desktop after config changes
- Check Claude logs: `~/Library/Logs/Claude/` (macOS)

### MCP server can't connect to Kafka

```bash
# Verify Kafka is accessible from host
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

If you see topics listed, Kafka is working. If not, wait a bit longer for startup.

### "uv: command not found"

Install uv first:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Development

### Add a new MCP tool

1. Edit `mcp_server/server.py`
2. Add your tool function with the `@app.call_tool()` decorator
3. Register it in `@app.list_tools()`
4. Restart the MCP server
5. Restart Claude Desktop

### Add new Python dependencies

```bash
uv add <package-name>
uv sync
```

### Run tests

```bash
uv run pytest
```

## What is MCP?

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open standard for connecting AI assistants to external tools and data sources. Think of it like a USB-C port for AI - one standard interface that works across different AI clients and tools.

This project is an MCP **server** that exposes Kafka operations as **tools** that Claude can call.

## Tech Stack

- **Python 3.11+** - Modern Python with type hints
- **uv** - Fast, reliable Python package management (10-100x faster than pip)
- **MCP SDK** - Model Context Protocol implementation
- **confluent-kafka-python** - High-performance Kafka client
- **Docker** - Containerized Kafka environment

## Why uv?

This project uses `uv` instead of pip/poetry to showcase modern Python tooling:
- ⚡ 10-100x faster dependency resolution
- 🔒 Reproducible builds via `uv.lock`
- 🛠️ Single tool replaces pip, pip-tools, virtualenv
- 📦 Growing adoption in the Python ecosystem

## Roadmap

- [ ] Add message peeking functionality
- [ ] Consumer group lag monitoring
- [ ] Schema Registry integration
- [ ] Message search by key/value
- [ ] Topic health diagnostics
- [ ] Support for multiple Kafka clusters
- [ ] Web UI for non-Claude users

## Contributing

This is a portfolio/educational project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Claude Desktop
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [Anthropic's MCP SDK](https://github.com/anthropics/model-context-protocol)
- Powered by [Confluent Kafka](https://github.com/confluentinc/confluent-kafka-python)
- Package management by [Astral's uv](https://github.com/astral-sh/uv)

---

**Questions?** Open an issue or reach out!

**Like this project?** Give it a ⭐ on GitHub!
