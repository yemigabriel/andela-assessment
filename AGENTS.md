# AGENTS.md

## Purpose

This is a **time-boxed AI engineering assessment**.

Goal:
Build a **production-ready customer support chatbot** for Meridian Electronics using an MCP server.

The system must:

* Integrate with MCP over HTTP
* Use an LLM to call tools correctly
* Be deployable and usable via a UI
* Be structured so it can go to production without rewrite

---

## Core Principles

* Working system > perfect system
* MCP integration is the priority
* Do not hallucinate data — always use tools
* Keep implementation simple but structured
* Build once — no rewrites

---

## Architecture

System flow:

Frontend (Next.js) → Backend (FastAPI) → Agent → MCP Server → Response

Layers:

* frontend/: UI only (no business logic)
* backend/: API, agent, MCP integration, OPENAI Agents SDK
* infra/: Terraform 
* scripts/: run, test, deploy
* .github/workflows/: CI

---

## Backend Rules

* Use FastAPI

* Endpoints:

  * POST /query
  * GET /health

* Structure:

  * api/ → routes
  * services/ → agent orchestration
  * mcp/ → MCP HTTP client
  * models/ → request/response schemas

* Use async everywhere possible

---

## MCP First Workflow (MANDATORY)

Before implementing any agent or API logic, you MUST:

Verify MCP connectivity
Discover available tools (if supported)
Manually test each core tool via HTTP
Inspect:
tool names
required parameters
response structure

Only after successful validation should you proceed to build the agent.

**MCP Testing Rules**
Do NOT assume tool names or schemas
Do NOT hardcode tool behavior without testing
Log all MCP responses during testing
If tool discovery is unavailable, probe manually
MCP Testing Script

Create a notebook  `/research/notebook.py` to:

- call MCP endpoint directly
- log and test tools

**Failure Handling**

If MCP calls fail:

Stop implementation
Debug request/response format
Adjust payload structure

Do NOT continue building on incorrect assumptions.

## MCP Integration

MCP server:

MCP_SERVER_URL=https://order-mcp-74afyau24q-uc.a.run.app/mcp

Rules:

* Discover tools first before building logic
* Always call MCP for:

    - order lookup
    - checking product availability
    - authentication
    - placing orders

* Never fabricate tool responses

* Handle missing inputs by asking user

---


## Frontend Rules

* Use Next.js

* Minimal UI:

  * chat input
  * response display

* Communicate via:
  POST /query

* No business logic in frontend

---

## Git Rules

Branch:

* feature/ai-assessment

Commit types:

* feat:
* fix:
* refactor:
* infra:
* chore:

Rules:

* One logical change per commit
* Code must run before commit
* Commit frequently

---

## Code Quality Rules (SOLID + Clean Code)

* Single Responsibility per function/module
* Keep functions small and readable
* Use clear and descriptive naming
* Avoid deep nesting
* Handle errors explicitly
* Prefer composition over complexity
* Avoid premature optimization
* You are required to commit after every single logical task is completed. Do not batch multiple features into one commit

---

## Rule: Mandatory Checkpoints

* After every git commit/completion of a task, you must stop all execution.
* Request Review: Explicitly state: "I have committed [Task X]. Please review the changes. May I proceed to the next task?"
* No Parallelism: You are strictly forbidden from starting a new task, editing a new file, or running a new command until I provide explicit confirmation (e.g., "Yes," "Proceed," or "LGTM").

---

## .gitignore

Ignore:

Python:

* **pycache**/
* *.pyc
* .venv/

Node:

* node_modules/
* .next/

Env:

* .env*
* *.pem
* *.key

Terraform:

* .terraform/
* *.tfstate*

System:

* .DS_Store
* .vscode/

Never commit secrets.

---

## CI/CD (GitHub Actions)

On push:

* Install backend dependencies
* Install frontend dependencies
* Build frontend

Keep workflow simple and fast.

---

## Terraform Rules

Goal: signal production readiness with core AWS services

Include:

* S3 bucket for static assets
* Lambda function for backend logic
* API Gateway to expose Lambda
* CloudFront distribution for frontend delivery from S3

Rules:

* Keep configs small and readable
* Use minimal resources required for functionality
* Avoid complex modules unless necessary
* Prefer managed defaults over custom networking
* Ensure resources are loosely coupled and deployable independently

---

## Deployment

* Deploy to AWS (Lambda + API Gateway)
* Must be publicly accessible via a stable endpoint
* Backend must work independently and be reachable over HTTP

---

## Scripts

All execution must go through scripts:

* Run backend:
  bash scripts/run.sh

* Run frontend:
  bash scripts/frontend.sh

* Deploy:
  bash scripts/deploy.sh

---

## Testing

* Include meaningful tests
* Focus on core functionality
* Tests must run via script
* Ensure:

  * MCP call works
  * agent returns response

---

## Constraints

* Time: 2 hours
* Prioritize working system first
* UI polish is secondary

---




## Success Criteria

* Chatbot works end-to-end
* MCP tools are correctly used
* System is deployed and accessible
* Code is structured and readable
* No hallucinated data

---

## Final Reminder

Focus on:

* MCP integration
* correct tool usage
* working deployment
* clear structure
