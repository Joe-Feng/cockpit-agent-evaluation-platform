from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from agent_eval_platform.config import Settings
from agent_eval_platform.db import Base, create_session_factory
from agent_eval_platform.repositories.catalog import CatalogRepository
from agent_eval_platform.services.catalog import CatalogService

_settings = Settings()
_session_factory = create_session_factory(_settings)


def init_database() -> None:
    Base.metadata.create_all(bind=_session_factory.kw["bind"])


def get_session() -> Generator[Session, None, None]:
    with _session_factory() as session:
        yield session


def get_catalog_service(session: Session = Depends(get_session)) -> CatalogService:
    return CatalogService(CatalogRepository(session))
