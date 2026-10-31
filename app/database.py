from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./bus_alert.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 專用設定
)

SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def list_tables():
    """回傳資料庫目前有哪些資料表，用來確認建表是否成功。"""
    return inspect(engine).get_table_names()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()