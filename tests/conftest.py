import pytest
from sqlalchemy.orm import Session, sessionmaker

from agent_eval_platform.config import Settings
from agent_eval_platform.db import Base, create_engine_from_settings
from agent_eval_platform.models import analysis, catalog, run  # noqa: F401


@pytest.fixture
def settings() -> Settings:
    return Settings(database_url="sqlite+pysqlite:///:memory:")


@pytest.fixture
def engine(settings: Settings):
    engine = create_engine_from_settings(settings)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session(engine) -> Session:
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with factory() as db:
        yield db
