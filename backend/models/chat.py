from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Customer support question")


class QueryResponse(BaseModel):
    answer: str


class HealthResponse(BaseModel):
    status: str
