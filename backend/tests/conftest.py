import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command
import os
import sys

# Add the project root (backend directory) to sys.path
# conftest.py is in backend/tests/, so project root is one level up from tests/ (which is backend/)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
print(f"CONTEST: Inserted into sys.path: {project_root}")
print(f"CONTEST: Current sys.path: {sys.path}")

from main import app # Changed from app.main to main
from app.database import Base as AppDeclarativeBase, get_db
from app.config import settings # Still needed for other settings in tests, but not for DB URL

# Explicitly define Test DB URL for SQLite, overriding any .env or default settings via pytest.ini
# Pytest.ini sets DATABASE_URL=sqlite:///./test.db as an environment variable.
# app.config.settings SHOULD pick this up if TESTING=True is also set.
# However, to be absolutely sure for test setup, we can directly use what pytest.ini sets.
TEST_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test.db") # Get from env set by pytest.ini

ALEMBIC_CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'alembic.ini')


# @pytest.fixture(scope="session", autouse=True) # Fallback: Temporarily disable migrations
# def apply_migrations_session_scope():
#     # Ensure the test database file exists and is a file before trying to remove
#     if "sqlite:///" in TEST_DATABASE_URL:
#         db_file_path = TEST_DATABASE_URL.split("///")[1]
#         if os.path.exists(db_file_path) and os.path.isfile(db_file_path):
#             os.remove(db_file_path)
#         # Create parent directory if it doesn't exist (e.g. if test.db is in a subdirectory)
#         db_dir = os.path.dirname(db_file_path)
#         if db_dir and not os.path.exists(db_dir):
#             os.makedirs(db_dir)

#     print(f"Using Alembic config: {ALEMBIC_CONFIG_FILE_PATH}")
#     print(f"Using Test Database URL for migrations: {TEST_DATABASE_URL}")

#     alembic_cfg = AlembicConfig(ALEMBIC_CONFIG_FILE_PATH)
#     alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)

#     # Ensure script_location is absolute or correctly relative to alembic.ini
#     # If alembic.ini uses %(here)s, that refers to dir of alembic.ini
#     # No need to change script_location if it's relative and correct in the INI.

#     alembic_command.upgrade(alembic_cfg, "head") # Fallback: Temporarily disable migrations
#     yield
#     # Teardown: Optionally, remove the test.db after session
#     # if "sqlite:///" in TEST_DATABASE_URL:
#     #     db_file_path = TEST_DATABASE_URL.split("///")[1]
#     #     if os.path.exists(db_file_path) and os.path.isfile(db_file_path):
#     #         os.remove(db_file_path)
#     pass # Fallback: Temporarily disable migrations


# @pytest.fixture(scope="function") # Fallback: Temporarily disable db_session
# def db_session(apply_migrations_session_scope): # Depends on session-scoped migrations
#     engine = create_engine(
#         TEST_DATABASE_URL,
#         connect_args={"check_same_thread": False}, # Needed for SQLite
#         poolclass=StaticPool,
#     )
#     # AppDeclarativeBase.metadata.create_all(bind=engine) # Alembic handles this

#     TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#         # Clean up data from tables after each test for isolation if needed
#         # For SQLite in-memory or file-per-session, this might not be strictly necessary
#         # but good practice for other DBs or persistent test DBs.
#         # for table in reversed(AppDeclarativeBase.metadata.sorted_tables):
#         #     db.execute(table.delete())
#         # db.commit()


# @pytest.fixture(scope="function") # Fallback: Temporarily disable client
# def client(db_session):
#     def override_get_db():
#         try:
#             yield db_session
#         finally:
#             # db_session.close() # Session is managed by db_session fixture's finally block
#             pass # Important: do not close here if db_session fixture handles it.

#     app.dependency_overrides[get_db] = override_get_db

#     # Use context manager for TestClient
#     with TestClient(app) as test_client:
#         yield test_client

#     del app.dependency_overrides[get_db] # Clean up override

# Minimal client fixture that does not depend on DB for unit tests if needed
@pytest.fixture(scope="function")
def client_no_db():
    with TestClient(app) as test_client:
        yield test_client
