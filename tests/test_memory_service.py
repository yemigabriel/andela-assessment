from __future__ import annotations

from pathlib import Path

import pytest

from backend.config import Settings
from backend.services.memory_service import MemoryService


@pytest.mark.asyncio
async def test_append_turn_persists_expected_json_shape(tmp_path: Path) -> None:
    service = MemoryService(
        Settings(
            openai_api_key="test-key",
            memory_dir=tmp_path,
            memory_s3_bucket=None,
        )
    )

    session_id = "session-123"
    messages = await service.append_turn(
        session_id,
        user_message="Hello",
        assistant_message="Hi there",
    )

    assert len(messages) == 2
    saved_file = service.memory_dir / f"{session_id}.json"
    assert saved_file.exists()
    saved_payload = saved_file.read_text(encoding="utf-8")
    assert '"role": "user"' in saved_payload
    assert '"role": "assistant"' in saved_payload
    assert '"content": "Hello"' in saved_payload
    assert '"content": "Hi there"' in saved_payload


@pytest.mark.asyncio
async def test_load_messages_returns_existing_local_session(tmp_path: Path) -> None:
    service = MemoryService(
        Settings(
            openai_api_key="test-key",
            memory_dir=tmp_path,
            memory_s3_bucket=None,
        )
    )

    session_id = "session-456"
    await service.append_turn(
        session_id,
        user_message="Check order",
        assistant_message="Please share the order ID.",
    )

    loaded_messages = await service.load_messages(session_id)

    assert [message.role for message in loaded_messages] == ["user", "assistant"]
    assert loaded_messages[0].content == "Check order"
    assert loaded_messages[1].content == "Please share the order ID."
