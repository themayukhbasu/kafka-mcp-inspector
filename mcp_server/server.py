"""Kafka MCP Inspector - Main MCP Server"""
import os
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from confluent_kafka.admin import AdminClient


# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Initialize MCP server
app = Server("kafka-mcp-inspector")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="list_topics",
            description="List all Kafka topics with basic information including partition count and replication factor",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "list_topics":
        return await get_kafka_topics()
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def get_kafka_topics() -> list[TextContent]:
    """List all Kafka topics."""
    try:
        # Create Kafka AdminClient
        admin_client = AdminClient({
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS
        })

        # Get cluster metadata
        metadata = admin_client.list_topics(timeout=10)

        # Build topics list
        topics = []
        for topic_name, topic_metadata in metadata.topics.items():
            # Skip internal topics
            if not topic_name.startswith("_"):
                topics.append({
                    "name": topic_name,
                    "partitions": len(topic_metadata.partitions),
                    "replication_factor": len(topic_metadata.partitions[0].replicas) if topic_metadata.partitions else 0
                })

        # Sort by name
        topics.sort(key=lambda x: x["name"])

        # Format response
        if not topics:
            response_text = "No topics found in the Kafka cluster."
        else:
            response_text = f"Found {len(topics)} topic(s):\n\n"
            for topic in topics:
                response_text += f"- **{topic['name']}**\n"
                response_text += f"  - Partitions: {topic['partitions']}\n"
                response_text += f"  - Replication Factor: {topic['replication_factor']}\n\n"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Error listing topics: {str(e)}\n\n"
        error_msg += f"Make sure Kafka is running at {KAFKA_BOOTSTRAP_SERVERS}"
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())