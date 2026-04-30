from __future__ import annotations

from typing import Any

from agents import Agent, Runner, function_tool, set_default_openai_key
from pydantic import BaseModel, Field

from backend.config import Settings
from backend.mcp.client import McpHttpClient
from backend.services.memory_service import MemoryService


class OrderItemInput(BaseModel):
    sku: str
    quantity: int = Field(..., gt=0)
    unit_price: str
    currency: str = "USD"


class AgentService:
    def __init__(
        self,
        settings: Settings,
        mcp_client: McpHttpClient,
        memory_service: MemoryService,
    ) -> None:
        self.settings = settings
        self.mcp_client = mcp_client
        self.memory_service = memory_service
        set_default_openai_key(settings.openai_api_key)

    async def answer(
        self,
        message: str,
        *,
        session_id: str | None = None,
    ) -> tuple[str, str]:
        active_session_id = session_id or self.memory_service.create_session_id()
        history = await self.memory_service.load_messages(active_session_id)
        agent = self._build_agent()
        prompt = self._build_agent_input(message, history)
        result = await Runner.run(agent, input=prompt)
        answer = str(result.final_output)
        await self.memory_service.append_turn(active_session_id, message, answer)
        return active_session_id, answer

    def _build_agent(self) -> Agent:
        @function_tool
        async def list_products(
            category: str | None = None,
            is_active: bool | None = None,
        ) -> str:
            """List products with optional category and active-status filters."""
            payload: dict[str, Any] = {}
            if category is not None:
                payload["category"] = category
            if is_active is not None:
                payload["is_active"] = is_active
            result = await self.mcp_client.call_tool("list_products", payload)
            return result["structuredContent"]["result"]

        @function_tool
        async def get_product(sku: str) -> str:
            """Get detailed product information for a specific SKU."""
            result = await self.mcp_client.call_tool("get_product", {"sku": sku})
            return result["structuredContent"]["result"]

        @function_tool
        async def search_products(query: str) -> str:
            """Search products by keyword in the name or description."""
            result = await self.mcp_client.call_tool("search_products", {"query": query})
            return result["structuredContent"]["result"]

        @function_tool
        async def get_customer(customer_id: str) -> str:
            """Look up customer details by customer UUID."""
            result = await self.mcp_client.call_tool(
                "get_customer", {"customer_id": customer_id}
            )
            return result["structuredContent"]["result"]

        @function_tool
        async def verify_customer_pin(email: str, pin: str) -> str:
            """Verify a customer identity using their email and 4-digit PIN."""
            result = await self.mcp_client.call_tool(
                "verify_customer_pin",
                {"email": email, "pin": pin},
            )
            return result["structuredContent"]["result"]

        @function_tool
        async def list_orders(
            customer_id: str | None = None,
            status: str | None = None,
        ) -> str:
            """List orders with optional customer and status filters."""
            payload: dict[str, Any] = {}
            if customer_id is not None:
                payload["customer_id"] = customer_id
            if status is not None:
                payload["status"] = status
            result = await self.mcp_client.call_tool("list_orders", payload)
            return result["structuredContent"]["result"]

        @function_tool
        async def get_order(order_id: str) -> str:
            """Get detailed information for a specific order UUID."""
            result = await self.mcp_client.call_tool("get_order", {"order_id": order_id})
            return result["structuredContent"]["result"]

        @function_tool
        async def create_order(
            customer_id: str,
            items: list[OrderItemInput],
        ) -> str:
            """Create an order only after the customer is verified and item details are known."""
            result = await self.mcp_client.call_tool(
                "create_order",
                {
                    "customer_id": customer_id,
                    "items": [item.model_dump() for item in items],
                },
            )
            return result["structuredContent"]["result"]

        instructions = """
You are Meridian Electronics' customer support assistant.

Rules:
- Never invent customers, products, inventory, orders, or authentication results.
- Use MCP-backed tools for any product lookup, order lookup, customer lookup, PIN verification, or order creation.
- If required information is missing, ask a concise follow-up question instead of guessing.
- Only create an order after the customer has been verified and the user has given enough item detail.
- Keep answers concise, helpful, and accurate.
""".strip()

        return Agent(
            name=self.settings.agent_name,
            instructions=instructions,
            model=self.settings.openai_model,
            tools=[
                list_products,
                get_product,
                search_products,
                get_customer,
                verify_customer_pin,
                list_orders,
                get_order,
                create_order,
            ],
        )

    def _build_agent_input(self, message: str, history: list[Any]) -> str:
        conversation_history = self.memory_service.format_history(history)
        if not conversation_history:
            return message
        return (
            "Conversation history:\n"
            f"{conversation_history}\n\n"
            "Latest user message:\n"
            f"{message}"
        )
