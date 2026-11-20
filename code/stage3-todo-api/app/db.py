# app/db.py（3.7 新建；3.9 末尾加 db_session / Db；3.12 开头改成读 settings；3.16 engine 加 NullPool）
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from app.config import settings              # 不用再 load_dotenv、os.environ.get

engine = create_engine(
    settings.database_url,
    echo=settings.debug,                                 # debug 时打印每条 SQL
    poolclass=NullPool if settings.vercel else None,     # Vercel 上不用连接池，用完就关；None = 用默认的连接池
)
SessionLocal = sessionmaker(engine, autoflush=False, expire_on_commit=False)  # 会话工厂


class Base(DeclarativeBase):
    """所有表模型的父类，固定写法。"""
    pass


# app/db.py（续，3.9）
from collections.abc import Iterator  # noqa: E402
from typing import Annotated  # noqa: E402

from fastapi import Depends  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402


def db_session() -> Iterator[Session]:
    """一个请求一个会话：正常结束提交，出错回滚，最后关闭。"""
    session = SessionLocal()
    try:
        yield session          # ① 把 session 交给接口，在这里暂停
        session.commit()       # ② 接口正常返回后，从这里继续：commit，这次请求的 INSERT / UPDATE / DELETE 才真正写进去
    except BaseException:
        session.rollback()     # ③ 接口抛了异常，撤销这次请求的所有修改
        raise
    finally:
        session.close()        # ④ 不管怎样都关闭


Db = Annotated[Session, Depends(db_session)]   # 起个短名字，接口里写 session: Db 就行
