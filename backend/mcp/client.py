from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


class McpClientError(RuntimeError):
    pass


@dataclass
class McpTool:
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


class McpHttpClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self._request_id = 0
        self._session_id: str | None = None
        self._tool_cache: list[McpTool] | None = None

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def _post(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        include_session: bool = True,
    ) -> dict[str, Any] | str:
        payload: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
        }
        if params is not None:
            payload["params"] = params

        headers = {
            "accept": "application/json, text/event-stream",
            "content-type": "application/json",
        }
        if include_session and self._session_id:
            headers["mcp-session-id"] = self._session_id

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            self._session_id = response.headers.get("mcp-session-id", self._session_id)
            if not response.content:
                return ""
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                return response.json()
            return response.text

    async def _notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params

        headers = {
            "accept": "application/json, text/event-stream",
            "content-type": "application/json",
        }
        if self._session_id:
            headers["mcp-session-id"] = self._session_id

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            self._session_id = response.headers.get("mcp-session-id", self._session_id)

    async def initialize(self) -> None:
        if self._session_id:
            return

        response = await self._post(
            "initialize",
            {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {
                    "name": "meridian-support-backend",
                    "version": "0.1.0",
                },
            },
            include_session=False,
        )
        if not isinstance(response, dict) or "result" not in response:
            raise McpClientError("Failed to initialize MCP session")
        await self._notify("notifications/initialized", {})

    async def list_tools(self, *, refresh: bool = False) -> list[McpTool]:
        await self.initialize()
        if self._tool_cache is not None and not refresh:
            return self._tool_cache

        response = await self._post("tools/list", {})
        if not isinstance(response, dict):
            raise McpClientError("Unexpected MCP tools/list response")

        tools = response.get("result", {}).get("tools", [])
        self._tool_cache = [
            McpTool(
                name=tool["name"],
                description=tool.get("description", ""),
                input_schema=tool.get("inputSchema", {}),
                output_schema=tool.get("outputSchema", {}),
            )
            for tool in tools
        ]
        return self._tool_cache

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        await self.initialize()
        response = await self._post(
            "tools/call",
            {"name": name, "arguments": arguments},
        )
        if not isinstance(response, dict):
            raise McpClientError(f"Unexpected MCP tools/call response for {name}")

        result = response.get("result", {})
        if result.get("isError"):
            text_blocks = result.get("content", [])
            message = text_blocks[0].get("text", "Unknown MCP tool error")
            raise McpClientError(message)
        return result
