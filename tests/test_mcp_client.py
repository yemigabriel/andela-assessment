from __future__ import annotations

import json

import httpx
import pytest

from backend.mcp.client import McpHttpClient


def build_response(
    payload: dict | None,
    *,
    session_id: str | None = None,
    content: bytes | None = None,
) -> httpx.Response:
    headers = {"content-type": "application/json"}
    if session_id:
        headers["mcp-session-id"] = session_id
    request = httpx.Request("POST", "https://example.com/mcp")
    if payload is not None:
        return httpx.Response(200, headers=headers, json=payload, request=request)
    return httpx.Response(200, headers=headers, content=content or b"", request=request)


@pytest.mark.asyncio
async def test_list_tools_initializes_and_parses_tools(monkeypatch) -> None:
    responses = [
        build_response(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"serverInfo": {"name": "order-mcp", "version": "1.0.0"}},
            },
            session_id="session-1",
        ),
        build_response(None, content=b""),
        build_response(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "result": {
                    "tools": [
                        {
                            "name": "list_orders",
                            "description": "List orders",
                            "inputSchema": {"type": "object"},
                            "outputSchema": {"type": "object"},
                        }
                    ]
                },
            },
        ),
    ]

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

        async def post(self, *args, **kwargs):
            return responses.pop(0)

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    client = McpHttpClient("https://example.com/mcp")
    tools = await client.list_tools()

    assert len(tools) == 1
    assert tools[0].name == "list_orders"
    assert tools[0].description == "List orders"


@pytest.mark.asyncio
async def test_call_tool_returns_result_payload(monkeypatch) -> None:
    responses = [
        build_response(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"serverInfo": {"name": "order-mcp", "version": "1.0.0"}},
            },
            session_id="session-1",
        ),
        build_response(None, content=b""),
        build_response(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "result": {
                    "isError": False,
                    "structuredContent": {"result": "Found 1 order"},
                    "content": [{"type": "text", "text": "Found 1 order"}],
                },
            },
        ),
    ]

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

        async def post(self, *args, **kwargs):
            return responses.pop(0)

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    client = McpHttpClient("https://example.com/mcp")
    result = await client.call_tool("list_orders", {})

    assert result["structuredContent"]["result"] == "Found 1 order"
