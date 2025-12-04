# Setup Guide - Kafka MCP Inspector

## What's Been Implemented

The minimal MVP is complete! Here's what you have:

- ✅ Python project with uv dependency management
- ✅ Docker Compose stack (Kafka + Zookeeper)
- ✅ MCP server with `list_topics` tool
- ✅ Demo topics created (user-events, system-logs, order-processing)
- ✅ All services tested and working

## Testing Locally

### 1. Verify Kafka is Running

```bash
docker-compose ps
```

You should see:
- kafka-mcp-broker (Up)
- kafka-mcp-zookeeper (Up)
- kafka-mcp-seed-data (Exited - this is normal)

### 2. Test the MCP Server

```bash
uv run python -c "from mcp_server.server import list_topics; import asyncio; print(asyncio.run(list_topics()))"
```

You should see the 3 demo topics listed with their partition counts.

## Configure Claude Desktop

### Step 1: Find Your Configuration File

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Step 2: Add the MCP Server Configuration

Open the config file and add (or merge with existing content):

```json
{
  "mcpServers": {
    "kafka-inspector": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/mayukhbasu/Desktop/coding/git-projects/kafka-mcp-inspector/kafka-mcp-inspector",
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

**IMPORTANT**: Use the full absolute path to your project directory!

### Step 3: Restart Claude Desktop

Quit Claude Desktop completely and restart it.

### Step 4: Test in Claude

Open a new chat in Claude and try:

- "What tools do you have available?"
- "List the topics in my Kafka cluster"
- "What topics exist in Kafka?"

You should see Claude call the `list_topics` tool and show you the 3 demo topics!

## Troubleshooting

### Kafka not starting
```bash
# Stop everything and start fresh
docker-compose down -v
docker-compose up -d

# Wait 60 seconds for services to be ready
sleep 60

# Check logs
docker-compose logs kafka
docker-compose logs seed-data
```

### MCP server not connecting to Kafka
```bash
# Verify Kafka is accessible
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Test connection from host
uv run python -c "from confluent_kafka.admin import AdminClient; print(AdminClient({'bootstrap.servers': 'localhost:9092'}).list_topics(timeout=5).topics)"
```

### Claude Desktop not finding the MCP server
- Make sure you used the **absolute path** in the config
- Restart Claude Desktop completely (quit, don't just close the window)
- Check the Claude logs: `~/Library/Logs/Claude/` (macOS)

## Next Steps

Once the MVP is working, you can expand it:

1. **Add more tools**:
   - `peek_messages(topic, count)` - Sample recent messages
   - `describe_topic(topic_name)` - Detailed topic metadata
   - `get_consumer_lag(group_id)` - Consumer lag analysis

2. **Add Schema Registry** (optional):
   - Uncomment schema-registry service in docker-compose.yml
   - Add `get_schema(topic)` tool

3. **Add message seeding**:
   - Create `demo_data/seed_messages.py`
   - Populate topics with realistic test data

4. **Write tests**:
   - Create `tests/test_kafka_tools.py`
   - Test each MCP tool

5. **Enhance README**:
   - Add screenshots
   - Add example queries
   - Create architecture diagram

## Quick Commands Reference

```bash
# Start Kafka
docker-compose up -d

# Stop Kafka
docker-compose down

# Fresh start (removes all data)
docker-compose down -v && docker-compose up -d

# View logs
docker-compose logs -f kafka

# Run MCP server for testing
uv run python -m mcp_server.server

# Add a new dependency
uv add <package-name>

# Update dependencies
uv sync
```

## Current Architecture

```
┌─────────────────────┐
│   Claude Desktop    │
│   (MCP Client)      │
└──────────┬──────────┘
           │ stdio (JSON-RPC 2.0)
           ▼
┌─────────────────────┐
│   MCP Server        │  <- You are here!
│   (FastMCP/Python)  │
└──────────┬──────────┘
           │
    ┌──────┴────────┐
    ▼               ▼
┌─────────┐   ┌──────────┐
│  Kafka  │   │Zookeeper │
│ Broker  │   │          │
└─────────┘   └──────────┘
```

## Success!

You now have a working MCP server that Claude can use to query your Kafka cluster!
