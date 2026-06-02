"""Jira MCP Server — minimal, secure, project-level configuration."""

import asyncio
from pathlib import Path

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

load_dotenv(Path(__file__).parent.parent / ".env")

from src.tools.issues import JIRA_TOOLS, handle_jira

app = Server("jira-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return JIRA_TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        result = await handle_jira(name, arguments)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]


async def run():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
