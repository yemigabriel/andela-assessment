from fastapi import APIRouter, HTTPException

from backend.models.chat import HealthResponse, QueryRequest, QueryResponse
from backend.services.container import get_agent_service, get_mcp_client


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    try:
        answer = await get_agent_service().answer(request.message)
        return QueryResponse(answer=answer)
    except Exception as exc:  # pragma: no cover - surfaced as API failure
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/mcp/tools")
async def list_mcp_tools() -> list[dict[str, str]]:
    tools = await get_mcp_client().list_tools()
    return [{"name": tool.name, "description": tool.description} for tool in tools]
