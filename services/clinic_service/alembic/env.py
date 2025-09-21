from __future__ import with_statement
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.db.session import Base  # noqa: E402
from app.models import clinic_model  # noqa: F401,E402

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy.ext.asyncio import create_async_engine

    connectable = create_async_engine(config.get_main_option("sqlalchemy.url"))

    async def do_run_migrations(connection):
        await connection.run_sync(
            lambda conn: context.configure(
                connection=conn, target_metadata=target_metadata, compare_type=True
            )
        )
        await connection.run_sync(lambda conn: context.begin_transaction())
        await connection.run_sync(lambda conn: context.run_migrations())

    import asyncio

    async def run():
        async with connectable.connect() as connection:
            await do_run_migrations(connection)

    asyncio.run(run())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
