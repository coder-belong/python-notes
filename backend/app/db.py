"""连数据库、建会话。本地用 SQLite，线上用 Postgres（Neon），代码一样，只是地址不同。"""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool

from .config import DATABASE_URL


def normalize_url(url: str) -> str:
    """Neon 给的地址是 postgres:// 或 postgresql:// 开头，SQLAlchemy 要写明用哪个驱动：postgresql+psycopg://"""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix) :]
    return url


url = normalize_url(DATABASE_URL)
if url.startswith("sqlite"):
    engine = create_engine(url, connect_args={"check_same_thread": False})
else:
    # Vercel 上每个请求可能由不同的实例处理，实例随时会被回收，自己维护连接池没有意义；
    # 每次用完就关，连接复用交给 Neon 的连接池（地址里带 -pooler 的那个）
    engine = create_engine(url, poolclass=NullPool)

SessionLocal = sessionmaker(engine)


class Base(DeclarativeBase):
    pass


def db_session() -> Iterator[Session]:
    """一个请求一个会话：正常结束提交，出错回滚，最后关闭。"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except BaseException:
        session.rollback()
        raise
    finally:
        session.close()


Db = Annotated[Session, Depends(db_session)]
