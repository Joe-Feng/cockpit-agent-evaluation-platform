# Agent Evaluation Platform

Independent platform for registering agent targets, running evaluations, collecting artifacts, and publishing reports, trends, and alerts.

## Backend

1. Run `uv sync --extra dev`.
2. Copy `.env.example` to `.env`.
3. Start PostgreSQL and MinIO with `docker compose up -d`.
4. Run `uv run uvicorn apps.api.main:app --reload`.

## Frontend

1. Install web dependencies with `npm --prefix apps/web install`.
2. Start the dashboard with `npm --prefix apps/web run dev`.
3. Open the Vite URL shown in the terminal. API requests to `/api` are proxied to the local backend.

## Verification

1. Backend suite: `uv run pytest -q`
2. Frontend shell: `npm --prefix apps/web run test -- --run`
3. Production build: `npm --prefix apps/web run build`
4. Local smoke flow: `uv run python scripts/smoke_local.py`

## Benchmark Package Import

Benchmark-generated agent-eval packages can be imported into the catalog before you create a run.

Import request example:

```bash
curl -X POST http://localhost:8000/api/v1/imports/benchmark-agent-package \
  -H 'Content-Type: application/json' \
  -d @import-request.json
```

Recommended workflow:

1. Export one `benchmark-agent-export/v1` zip or JSON package from `cockpit-benchmark`.
2. POST one extracted package to `/api/v1/imports/benchmark-agent-package` with a valid `env_id` such as `local_mock`.
3. Create a run against the imported suite after the suite/case records are registered.

## Runbook

Detailed local setup notes live in `docs/runbooks/local-dev.md`.
