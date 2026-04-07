from fastapi import FastAPI

from agent_eval_platform.api.dependencies import init_database
from agent_eval_platform.api.routes.catalog import router as catalog_router


def create_app() -> FastAPI:
    init_database()
    app = FastAPI(title="Agent Evaluation Platform")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(catalog_router)
    return app
