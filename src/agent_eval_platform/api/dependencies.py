from collections.abc import Generator
from pathlib import Path

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from agent_eval_platform.config import Settings
from agent_eval_platform.db import Base, create_session_factory
from agent_eval_platform.repositories.catalog import CatalogRepository
from agent_eval_platform.services.catalog import CatalogService
from agent_eval_platform.storage.artifacts import LocalArtifactStorage


class RuntimeState:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.session_factory = create_session_factory(settings)
        self.artifact_storage = LocalArtifactStorage(Path(settings.local_artifact_dir))


def create_runtime(settings: Settings | None = None) -> RuntimeState:
    return RuntimeState(settings or Settings())


def init_database(runtime: RuntimeState) -> None:
    Base.metadata.create_all(bind=runtime.session_factory.kw["bind"])


def get_runtime(request: Request) -> RuntimeState:
    return request.app.state.runtime


def get_session(runtime: RuntimeState = Depends(get_runtime)) -> Generator[Session, None, None]:
    with runtime.session_factory() as session:
        yield session


def get_catalog_service(session: Session = Depends(get_session)) -> CatalogService:
    return CatalogService(CatalogRepository(session))
