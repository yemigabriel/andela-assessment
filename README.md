# Meridian Electronics Support Chatbot

Production-oriented customer support chatbot for Meridian Electronics.

Architecture:
- `frontend/` Next.js UI
- `backend/` FastAPI API + OpenAI Agents SDK orchestration
- `backend/mcp/` direct MCP-over-HTTP integration
- `infra/` Terraform for AWS deployment
- `scripts/` local run, test, and deploy entrypoints
- `research/` MCP validation notebook and script

System flow:
- Browser UI -> FastAPI backend -> OpenAI Agents SDK -> MCP server -> response

## Core stack

Backend:
- FastAPI
- OpenAI Agents SDK
- Boto3
- Mangum for Lambda

Frontend:
- Next.js App Router
- React

Infra:
- AWS Lambda
- API Gateway HTTP API
- S3
- CloudFront
- Terraform

Testing:
- Pytest

## Project structure

```text
backend/
  api/
  mcp/
  models/
  services/
frontend/
  app/
infra/
research/
scripts/
tests/
```

## Implemented API

Backend routes:
- `GET /health`
- `POST /query`
- `GET /mcp/tools`

`POST /query` request body:

```json
{
  "message": "Check my order status",
  "session_id": "optional-session-id"
}
```

Response body:

```json
{
  "answer": "Assistant response",
  "session_id": "active-session-id"
}
```

## MCP integration

MCP endpoint:
- `https://order-mcp-74afyau24q-uc.a.run.app/mcp`

Validated tools discovered during research:
- `list_products`
- `get_product`
- `search_products`
- `get_customer`
- `verify_customer_pin`
- `list_orders`
- `get_order`
- `create_order`

Research artifacts:
- [research/notebook.ipynb](/Users/yemigabriel/Documents/Python/andela-assessment/research/notebook.ipynb)


## Conversation memory

Local memory format:

```json
[
  {
    "role": "user",
    "content": "Hello",
    "timestamp": "2026-04-30T15:30:53.379414+00:00"
  },
  {
    "role": "assistant",
    "content": "Hi there",
    "timestamp": "2026-04-30T15:30:53.379430+00:00"
  }
]
```

Behavior:
- local-first persistence
- saves to `/memory/{session_id}.json` in local development
- saves to `/tmp/memory` in Lambda
- uploads to S3 at `memory/{session_id}.json`
- reloads history when `session_id` is provided

## Environment variables

Local backend:

```env
OPENAI_API_KEY=...
CORS_ALLOW_ORIGINS=http://localhost:3000
```

Terraform variables can be passed through shell env:

```bash
export TF_VAR_openai_api_key="..."
export TF_VAR_cors_allow_origins="http://localhost:3000"
```

## Local development

Backend:

```bash
bash scripts/run.sh
```

Frontend:

```bash
bash scripts/frontend.sh
```

Tests:

```bash
bash scripts/test.sh
```

MCP research:

```bash
uv run python research/notebook.py
```

## Frontend behavior

The frontend is a thin client:
- no business logic
- posts messages to backend `POST /query`
- reuses `session_id` across turns
- renders user and assistant messages only

Important deployment detail:
- the static frontend bundle must be built with the deployed API Gateway URL
- Terraform now injects that URL directly into the build step

## Docker

Files:
- [backend/Dockerfile](/Users/yemigabriel/Documents/Python/andela-assessment/backend/Dockerfile)
- [frontend/Dockerfile](/Users/yemigabriel/Documents/Python/andela-assessment/frontend/Dockerfile)
- [docker-compose.yml](/Users/yemigabriel/Documents/Python/andela-assessment/docker-compose.yml)
- [requirements.txt](/Users/yemigabriel/Documents/Python/andela-assessment/requirements.txt)

Notes:
- backend image runs `uvicorn backend.main:app`
- frontend image builds a static-exported Next.js app
- compose is intended for simple local container orchestration

## AWS deployment

Terraform resources:
- frontend S3 bucket
- memory S3 bucket
- Lambda backend
- API Gateway HTTP API
- CloudFront distribution

Key files:
- [infra/providers.tf](/Users/yemigabriel/Documents/Python/andela-assessment/infra/providers.tf)
- [infra/variables.tf](/Users/yemigabriel/Documents/Python/andela-assessment/infra/variables.tf)
- [infra/main.tf](/Users/yemigabriel/Documents/Python/andela-assessment/infra/main.tf)
- [infra/outputs.tf](/Users/yemigabriel/Documents/Python/andela-assessment/infra/outputs.tf)


Deploy command:

```bash
bash scripts/deploy.sh
```

What `scripts/deploy.sh` does:
1. builds `dist/backend.zip`
2. installs Lambda-compatible Linux wheels with `uv pip`
3. copies backend source into the zip
4. runs `terraform init`
5. runs `terraform apply`

## CI

Workflow:
- [ci.yml](/Users/yemigabriel/Documents/Python/andela-assessment/.github/workflows/ci.yml)

On push / pull request:
- installs backend dependencies with `uv`
- runs `bash scripts/test.sh`
- installs frontend dependencies with `npm ci`
- runs `npm run build`

## Technical decisions

Why use OpenAI Agents SDK:
- tool-first orchestration
- clean mapping from discovered MCP tools to agent tools
- minimal custom planning code

Why memory is local-first:
- simple local development
- simple JSON format
- S3 sync layered on without changing the app contract

