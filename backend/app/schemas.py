"""请求体的格式和校验。"""

from typing import Annotated

from pydantic import BaseModel, Field

# 用户名：2～20 个字符，字母、数字、下划线、汉字（\w 包含汉字）
Username = Annotated[str, Field(min_length=2, max_length=20, pattern=r"^\w+$")]
Password = Annotated[str, Field(min_length=6, max_length=128)]
Seconds = Annotated[int, Field(ge=0, le=10_000_000)]  # 上限只是防止乱传
Day = Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")]
SectionId = Annotated[str, Field(max_length=64)]
GuestId = Annotated[str, Field(pattern=r"^[a-z0-9]{12,32}$")]  # 前端随机生成的访客 id


class AuthIn(BaseModel):
    username: Username
    password: Password
    guest_id: GuestId | None = None  # 登录前是访客的话带上，记下「这个访客后来注册了」


class SyncIn(BaseModel):
    """前端上次同步之后新增的学习记录（增量，不是总数）。"""

    batch_id: str = Field(min_length=8, max_length=64)  # 前端生成的随机 id，重试时不变
    days: dict[Day, Seconds] = {}  # 每天新增的秒数
    pomodoros: dict[Day, Annotated[int, Field(ge=0, le=100)]] = {}  # 每天新增的番茄数
    sections: dict[SectionId, Seconds] = {}  # 每节新增的秒数
    done: dict[SectionId, bool] = {}  # 「学完了」改成了什么


class GuestSyncIn(BaseModel):
    """访客上报的学习时长：每天的总秒数（不是增量），重复发也不会多算。"""

    guest_id: GuestId
    days: dict[Day, Annotated[int, Field(ge=0, le=86_400)]] = Field(default={}, max_length=31)
