from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, text

from app import models  # noqa: F401  (registers tables on Base.metadata)
from app.config import settings
from app.db import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)
if config.config_file_name:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(url=settings.database_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        # Several backend replicas start at once and each runs `alembic upgrade head`.
        # A Postgres advisory lock lets exactly one migrate; the others wait, then see
        # the schema is already at head and do nothing.
        is_postgres = connection.dialect.name == "postgresql"
        if is_postgres:
            connection.execute(text("SELECT pg_advisory_lock(727001)"))
            connection.commit()
        try:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()
        finally:
            if is_postgres:
                connection.execute(text("SELECT pg_advisory_unlock(727001)"))
                connection.commit()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
