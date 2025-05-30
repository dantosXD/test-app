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

# Import settings once globally
from app.config import settings

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    """
    from app.database import Base
    import app.models
    context_target_metadata = Base.metadata
    
    context.configure(
        url=settings.DATABASE_URL, 
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
    from app.database import Base
    import app.models
    context_target_metadata = Base.metadata
    
    connectable = engine_from_config(
        {"sqlalchemy.url": settings.DATABASE_URL}, 
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
