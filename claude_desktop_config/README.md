# Claude Desktop Configuration

To use the Kafka MCP Inspector with Claude Desktop:

1. Locate your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Copy the contents of `mcp_config_example.json` from this directory

3. **IMPORTANT**: Update the path `/ABSOLUTE/PATH/TO/kafka-mcp-inspector` to the actual absolute path where you cloned this repository

4. Paste into your `claude_desktop_config.json` file (merge with existing config if you have other MCP servers)

5. Restart Claude Desktop

6. You should now see the Kafka Inspector tools available in Claude

## Verification

After restarting Claude Desktop, you can verify the integration by asking Claude:
- "What tools do you have available?"
- "List the topics in my Kafka cluster"
