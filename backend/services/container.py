from functools import lru_cache

from backend.config import get_settings
from backend.mcp.client import McpHttpClient
from backend.services.agent_service import AgentService


@lru_cache
def get_mcp_client() -> McpHttpClient:
    return McpHttpClient(get_settings().mcp_server_url)


@lru_cache
def get_agent_service() -> AgentService:
    return AgentService(get_settings(), get_mcp_client())
