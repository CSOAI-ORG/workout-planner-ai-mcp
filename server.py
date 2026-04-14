#!/usr/bin/env python3
"""MEOK AI Labs — workout-planner-ai-mcp MCP Server. Generate personalized workout plans by goal and equipment."""

import asyncio
import json
from datetime import datetime
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent)
import mcp.types as types

# In-memory store (replace with DB in production)
_store = {}

server = Server("workout-planner-ai-mcp")

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    return []

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(name="generate_workout", description="Generate a workout plan", inputSchema={"type":"object","properties":{"goal":{"type":"string"},"equipment":{"type":"array","items":{"type":"string"}}},"required":["goal"]}),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Any | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    args = arguments or {}
    if name == "generate_workout":
            goal = args["goal"]
            eq = args.get("equipment", ["bodyweight"])
            plan = {"warmup": "5 min jog", "main": [f"{goal} exercise with {eq[0]}" for _ in range(3)], "cooldown": "Stretching"}
            return [TextContent(type="text", text=json.dumps(plan, indent=2))]
    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}, indent=2))]

async def main():
    async with stdio_server(server._read_stream, server._write_stream) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="workout-planner-ai-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={})))

if __name__ == "__main__":
    asyncio.run(main())
