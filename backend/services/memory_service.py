from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from backend.config import Settings
from backend.models.chat import ConversationMessage


class MemoryService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.memory_dir = settings.memory_dir
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self._s3_client = (
            boto3.client("s3", region_name=settings.aws_region)
            if settings.memory_s3_bucket
            else None
        )

    def create_session_id(self) -> str:
        return str(uuid4())

    async def load_messages(self, session_id: str) -> list[ConversationMessage]:
        path = self._session_path(session_id)
        if path.exists():
            return await asyncio.to_thread(self._read_local_messages, path)

        if self._s3_client and self.settings.memory_s3_bucket:
            return await asyncio.to_thread(self._download_from_s3, session_id, path)

        return []

    async def append_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str,
    ) -> list[ConversationMessage]:
        path = self._session_path(session_id)
        existing_messages = await self.load_messages(session_id)
        updated_messages = [
            *existing_messages,
            self._build_message("user", user_message),
            self._build_message("assistant", assistant_message),
        ]
        await asyncio.to_thread(self._write_local_messages, path, updated_messages)
        if self._s3_client and self.settings.memory_s3_bucket:
            await asyncio.to_thread(self._upload_to_s3, session_id, updated_messages)
        return updated_messages

    def format_history(self, messages: list[ConversationMessage]) -> str:
        if not messages:
            return ""
        return "\n".join(
            f"{message.role} [{message.timestamp}]: {message.content}"
            for message in messages
        )

    def _session_path(self, session_id: str) -> Path:
        return self.memory_dir / f"{session_id}.json"

    def _build_message(self, role: str, content: str) -> ConversationMessage:
        return ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def _read_local_messages(self, path: Path) -> list[ConversationMessage]:
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return [ConversationMessage.model_validate(item) for item in payload]

    def _write_local_messages(
        self,
        path: Path,
        messages: list[ConversationMessage],
    ) -> None:
        payload = [message.model_dump() for message in messages]
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    def _upload_to_s3(
        self,
        session_id: str,
        messages: list[ConversationMessage],
    ) -> None:
        if not self._s3_client or not self.settings.memory_s3_bucket:
            return
        body = json.dumps([message.model_dump() for message in messages], indent=2)
        try:
            self._s3_client.put_object(
                Bucket=self.settings.memory_s3_bucket,
                Key=f"memory/{session_id}.json",
                Body=body.encode("utf-8"),
                ContentType="application/json",
            )
        except (BotoCoreError, ClientError) as exc:
            raise RuntimeError(f"Failed to upload memory to S3: {exc}") from exc

    def _download_from_s3(
        self,
        session_id: str,
        path: Path,
    ) -> list[ConversationMessage]:
        if not self._s3_client or not self.settings.memory_s3_bucket:
            return []
        try:
            response = self._s3_client.get_object(
                Bucket=self.settings.memory_s3_bucket,
                Key=f"memory/{session_id}.json",
            )
        except self._s3_client.exceptions.NoSuchKey:
            return []
        except (BotoCoreError, ClientError) as exc:
            raise RuntimeError(f"Failed to download memory from S3: {exc}") from exc

        body = response["Body"].read().decode("utf-8")
        payload = json.loads(body)
        messages = [ConversationMessage.model_validate(item) for item in payload]
        self._write_local_messages(path, messages)
        return messages
