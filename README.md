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

## Runbook

Detailed local setup notes live in `docs/runbooks/local-dev.md`.
