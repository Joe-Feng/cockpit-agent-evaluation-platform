# Local Development Runbook

## 1. Bootstrap dependencies

1. Run `uv sync --extra dev`.
2. Copy `.env.example` to `.env` if you need custom settings.

## 2. Start local services

1. Start infrastructure with `docker compose up -d`.
2. Start the API with `uv run uvicorn apps.api.main:app --reload`.
3. Start the dashboard with `npm --prefix apps/web install && npm --prefix apps/web run dev`.

The Vite dev server proxies `/api` traffic to `http://127.0.0.1:8000`.

## 3. Run verification

1. Backend targeted checks: `uv run pytest tests/analysis/test_trends_alerts.py tests/api/test_dashboard_api.py tests/e2e/test_platform_smoke.py -q`
2. Frontend shell check: `npm --prefix apps/web run test -- --run`
3. Local smoke script: `uv run python scripts/smoke_local.py`

## 4. What to look for

1. `/health` returns `{"status": "ok"}`.
2. `/api/v1/dashboard/targets/cockpit_agents` returns a dashboard payload shape even before real run data exists.
3. `/api/v1/alerts/events` returns an `items` array and stays empty until regressions are detected.
