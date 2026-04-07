from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from agent_eval_platform.config import Settings


class Base(DeclarativeBase):
    pass


def create_engine_from_settings(settings: Settings) -> Engine:
    if settings.database_url.startswith("sqlite+pysqlite:///:memory:"):
        return create_engine(
            settings.database_url,
            future=True,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_engine(settings.database_url, future=True)


def create_session_factory(settings: Settings) -> sessionmaker:
    engine = create_engine_from_settings(settings)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


from agent_eval_platform import models  # noqa: E402,F401
