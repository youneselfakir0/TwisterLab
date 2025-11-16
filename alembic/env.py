import logging
import os

# Import our database models for autogeneration
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

sys.path.insert(0, os.path.dirname(__file__))
from models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# Get database URL from environment variable, fallback to alembic.ini
# This allows for flexible configuration in different environments


def _read_env_file(varname: str) -> str | None:
    file_path = os.getenv(f"{varname}__FILE") or os.getenv(f"{varname}_FILE")
    if not file_path:
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


DATABASE_URL = _read_env_file("DATABASE_URL") or os.getenv("DATABASE_URL")
POSTGRES_PASSWORD = _read_env_file("POSTGRES_PASSWORD") or os.getenv("POSTGRES_PASSWORD")

# If DATABASE_URL lacks an embedded password and POSTGRES_PASSWORD is provided,
# inject the password into the URL so Alembic can use it to connect.
if DATABASE_URL and POSTGRES_PASSWORD:
    try:
        if "postgresql://" in DATABASE_URL and "@" in DATABASE_URL:
            user_part, rest = DATABASE_URL.split("@", 1)
            if ":" not in user_part:
                prefix = user_part.split("//", 1)[0]
                username = user_part.split("//", 1)[1]
                DATABASE_URL = f"{prefix}//{username}:{POSTGRES_PASSWORD}@{rest}"
    except Exception:
        # If anything went wrong, fall back to the existing DATABASE_URL value
        pass
if not DATABASE_URL:
    DATABASE_URL = config.get_main_option("sqlalchemy.url")
    if DATABASE_URL and "localhost" in DATABASE_URL:
        logger = logging.getLogger(__name__)
        logger.warning("DATABASE_URL missing; using alembic.ini (not recommended).")

    # Update the config with the potentially environment-sourced URL
    # Ensure DATABASE_URL is a string and not None
    config.set_main_option("sqlalchemy.url", DATABASE_URL or "")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
