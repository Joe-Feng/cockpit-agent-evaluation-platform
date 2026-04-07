from fastapi import FastAPI

from agent_eval_platform.api.dependencies import create_runtime, init_database
from agent_eval_platform.api.routes.catalog import router as catalog_router
from agent_eval_platform.config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    runtime = create_runtime(settings)
    init_database(runtime)
    app = FastAPI(title="Agent Evaluation Platform")
    app.state.runtime = runtime

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(catalog_router)
    return app
