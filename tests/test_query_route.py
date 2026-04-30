from __future__ import annotations

from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient
import pytest

from backend.main import app
from backend.api import routes


@pytest.mark.asyncio
async def test_query_endpoint_returns_answer_and_session_id(monkeypatch) -> None:
    agent_service = AsyncMock()
    agent_service.answer = AsyncMock(return_value=("session-abc", "Tool-backed answer"))
    monkeypatch.setattr(routes, "get_agent_service", lambda: agent_service)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/query", json={"message": "Need help"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Tool-backed answer",
        "session_id": "session-abc",
    }
    agent_service.answer.assert_awaited_once_with("Need help", session_id=None)
