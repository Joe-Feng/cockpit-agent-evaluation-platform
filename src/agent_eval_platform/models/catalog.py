from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from agent_eval_platform.db import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class TargetRecord(TimestampMixin, Base):
    __tablename__ = "targets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    adapter_types: Mapped[str] = mapped_column(String(256), nullable=False)
    raw_profile_json: Mapped[str] = mapped_column(Text, nullable=False)


class EnvironmentRecord(TimestampMixin, Base):
    __tablename__ = "environments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    raw_profile_json: Mapped[str] = mapped_column(Text, nullable=False)


class SuiteRecord(TimestampMixin, Base):
    __tablename__ = "suites"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    mode: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_definition_json: Mapped[str] = mapped_column(Text, nullable=False)


class CaseRecord(TimestampMixin, Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    suite_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    raw_definition_json: Mapped[str] = mapped_column(Text, nullable=False)
