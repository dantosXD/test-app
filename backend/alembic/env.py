from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Determine database URL based on TESTING environment variable
import os
# Import the Settings class, not the instance, to avoid premature .env loading if not desired
from app.config import Settings

IS_TESTING = os.environ.get("TESTING", "false").lower() == "true"

if IS_TESTING:
    # Get DB URL from env var set by pytest.ini for tests
    db_url_for_alembic = os.environ.get("DATABASE_URL", "sqlite:///./test.db")
    # print(f"ALEMBIC ENV (TESTING): Using DATABASE_URL: {db_url_for_alembic}")
else:
    # For normal operations, instantiate settings to load from .env or defaults
    app_settings = Settings()
    db_url_for_alembic = app_settings.DATABASE_URL
    # print(f"ALEMBIC ENV (NORMAL): Using DATABASE_URL: {db_url_for_alembic}")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    """
    from app.database import Base # This is DeclarativeBase from database.py
    import app.models # Ensure all models are imported so Base.metadata is populated
    context_target_metadata = Base.metadata

    context.configure(
        url=db_url_for_alembic, # Use the determined URL
        target_metadata=context_target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True # Added for SQLite compatibility if needed, good practice
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    """
    from app.database import Base # This is DeclarativeBase
    import app.models # Ensure all models are imported
    context_target_metadata = Base.metadata

    connectable = engine_from_config(
        {"sqlalchemy.url": db_url_for_alembic}, # Use the determined URL
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=context_target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=True # Added for SQLite compatibility if needed, good practice
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
