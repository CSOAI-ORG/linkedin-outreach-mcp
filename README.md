<div align="center">

# Linkedin Outreach MCP

**MCP server for linkedin outreach mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-linkedin-outreach-mcp)](https://pypi.org/project/meok-linkedin-outreach-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Linkedin Outreach MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `generate_connection_request` | Generate a personalized LinkedIn connection request (max 300 characters). |
| `generate_inmessage` | Generate a professional LinkedIn InMail or direct message. |
| `generate_post` | Generate an engaging LinkedIn post with hashtags. |
| `analyze_profile` | Analyze a LinkedIn profile description to extract actionable outreach insights. |
| `generate_outreach_sequence` | Generate a 5-touch LinkedIn outreach sequence with timing recommendations. |
| `generate_comment` | Generate an insightful comment for a LinkedIn post. |

## Installation

```bash
pip install meok-linkedin-outreach-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "linkedin-outreach-mcp": {
      "command": "python",
      "args": ["-m", "meok_linkedin_outreach_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 6 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
