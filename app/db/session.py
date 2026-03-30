from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def ensure_sqlite_schema_compatibility() -> None:
    if not settings.database_url.startswith("sqlite"):
        return

    with engine.begin() as connection:
        inspector = inspect(connection)
        if "site_configs" not in inspector.get_table_names():
            return

        columns = {column["name"] for column in inspector.get_columns("site_configs")}
        if "rule_config" not in columns:
            connection.execute(text("ALTER TABLE site_configs ADD COLUMN rule_config TEXT NOT NULL DEFAULT '{}'"))


ensure_sqlite_schema_compatibility()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
