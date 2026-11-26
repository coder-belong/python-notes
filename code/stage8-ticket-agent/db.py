# db.py：三张表：订单（业务数据）、任务（每次提问的执行记录）、退款记录
from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

engine = create_engine("sqlite:///ticket.db")   # 演示用 SQLite；换 PostgreSQL 只改这个地址（3.15 节）


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    user: Mapped[str] = mapped_column(String(20))
    item: Mapped[str] = mapped_column(String(100))
    amount: Mapped[float]
    status: Mapped[str] = mapped_column(String(20))          # 配送中 / 已送达 / 已退款
    late_minutes: Mapped[int] = mapped_column(default=0)     # 比预计送达晚了多少分钟


class Task(Base):
    """一次提问的全部执行过程：中途停下等确认、服务重启，都能从这里接着跑（6.17 节的思路，这里自己存）。"""

    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[str] = mapped_column(String(20))
    question: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="running")   # running / waiting_confirm / done / failed
    messages: Mapped[list] = mapped_column(JSON, default=list)          # 发给模型的完整消息历史
    steps: Mapped[list] = mapped_column(JSON, default=list)             # Trace：每一步做了什么、花了多少（6.3 节）
    pending: Mapped[dict | None] = mapped_column(JSON, default=None)    # 等确认的那个工具调用
    answer: Mapped[str | None] = mapped_column(String(4000), default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Refund(Base):
    __tablename__ = "refunds"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"))
    amount: Mapped[float]
    reason: Mapped[str] = mapped_column(String(200))


def init_db() -> None:
    Base.metadata.create_all(engine)              # 已经有的表不动：服务重启后任务记录还在
    with Session(engine) as s:
        if s.get(Order, "A1024"):                 # 演示数据只放一次
            return
        s.add_all([
            Order(id="A1024", user="xiaolin", item="拿铁（大杯）外卖", amount=28.0, status="已送达", late_minutes=42),
            Order(id="A1025", user="xiaolin", item="美式 x2", amount=36.0, status="已送达", late_minutes=5),
            Order(id="B2001", user="other", item="桂花酒酿奶茶", amount=18.0, status="配送中"),
        ])
        s.commit()
