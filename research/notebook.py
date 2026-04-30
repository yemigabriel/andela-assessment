import asyncio
import json
import os
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Any

import httpx


MCP_SERVER_URL = os.getenv(
    "MCP_SERVER_URL",
    "https://order-mcp-74afyau24q-uc.a.run.app/mcp",
)


@dataclass
class JsonRpcResult:
    method: str
    request: dict[str, Any]
    response: dict[str, Any] | str


class McpHttpProbe:
    def __init__(self, url: str) -> None:
        self.url = url
        self.request_id = 0
        self.session_id: str | None = None

    def _next_id(self) -> int:
        self.request_id += 1
        return self.request_id

    async def _post(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        include_session: bool = True,
    ) -> JsonRpcResult:
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
        if include_session and self.session_id:
            headers["mcp-session-id"] = self.session_id

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.url, json=payload, headers=headers)
            response.raise_for_status()
            self.session_id = response.headers.get("mcp-session-id", self.session_id)
            content_type = response.headers.get("content-type", "")
            if not response.content:
                body = ""
            elif "application/json" in content_type:
                body = response.json()
            else:
                body = response.text
            return JsonRpcResult(method=method, request=payload, response=body)

    async def _notify(
        self,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> JsonRpcResult:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params

        headers = {
            "accept": "application/json, text/event-stream",
            "content-type": "application/json",
        }
        if self.session_id:
            headers["mcp-session-id"] = self.session_id

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.url, json=payload, headers=headers)
            response.raise_for_status()
            self.session_id = response.headers.get("mcp-session-id", self.session_id)
            content_type = response.headers.get("content-type", "")
            if not response.content:
                body = ""
            elif "application/json" in content_type:
                try:
                    body = response.json()
                except JSONDecodeError:
                    body = response.text
            else:
                body = response.text
            return JsonRpcResult(method=method, request=payload, response=body)


def pretty_print(title: str, data: Any) -> None:
    print(f"\n=== {title} ===")
    if isinstance(data, str):
        print(data)
        return
    print(json.dumps(data, indent=2, sort_keys=True, default=str))


async def main() -> None:
    probe = McpHttpProbe(MCP_SERVER_URL)

    print(f"MCP_SERVER_URL={MCP_SERVER_URL}")

    # MCP servers commonly require initialize before other requests.
    initialize = await probe._post(
        "initialize",
        {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "andela-assessment-probe", "version": "0.1.0"},
        },
        include_session=False,
    )
    pretty_print("initialize request", initialize.request)
    pretty_print("initialize response", initialize.response)
    if probe.session_id:
        print(f"session_id={probe.session_id}")

    notifications_initialized = await probe._notify("notifications/initialized", {})
    pretty_print(
        "notifications/initialized request", notifications_initialized.request
    )
    pretty_print(
        "notifications/initialized response", notifications_initialized.response
    )

    # Attempt formal tool discovery first.
    tools_list = await probe._post("tools/list", {})
    pretty_print("tools/list request", tools_list.request)
    pretty_print("tools/list response", tools_list.response)

    # Test one product-related tool and one order-related tool using the discovered names.
    for tool_name, arguments in [
        ("list_products", {}),
        ("list_orders", {}),
    ]:
        result = await probe._post(
            "tools/call",
            {"name": tool_name, "arguments": arguments},
        )
        pretty_print(f"tools/call request for {tool_name}", result.request)
        pretty_print(f"tools/call response for {tool_name}", result.response)


if __name__ == "__main__":
    asyncio.run(main())
