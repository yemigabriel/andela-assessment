from typing import Literal

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Customer support question")
    session_id: str | None = Field(
        default=None,
        description="Existing conversation session identifier",
    )


class QueryResponse(BaseModel):
    answer: str
    session_id: str


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: str


class HealthResponse(BaseModel):
    status: str
