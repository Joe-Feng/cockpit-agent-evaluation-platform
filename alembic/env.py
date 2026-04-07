from alembic import context
from sqlalchemy import engine_from_config, pool

from agent_eval_platform.config import Settings
from agent_eval_platform.db import Base
from agent_eval_platform.models import analysis, catalog, run  # noqa: F401

config = context.config
target_metadata = Base.metadata


def resolve_database_url() -> str:
    settings = Settings()
    if "database_url" in settings.model_fields_set:
        return settings.database_url
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    context.configure(
        url=resolve_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = dict(config.get_section(config.config_ini_section, {}) or {})
    configuration["sqlalchemy.url"] = resolve_database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
