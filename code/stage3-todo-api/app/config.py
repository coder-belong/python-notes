# app/config.py（3.12 新建；3.13 加 jwt_secret / token_days；3.16 加 cors_origins、vercel 和检查）
from __future__ import annotations

from pydantic import model_validator          # 拼装补充：3.16 用到了 @model_validator，笔记没写这行导入
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_SECRET = "dev-secret-change-me"           # 拼装补充：3.16 的 check_secret 用到 DEV_SECRET，笔记没定义，取 3.13 里 jwt_secret 的默认值


class Settings(BaseSettings):                 # 继承 BaseSettings：字段从环境变量读
    """所有配置都在这里：先读环境变量，没有再读 .env，都没有用默认值。"""

    # 这个类自己的设置，两项：
    #   env_file=".env"：除了环境变量，还去读 .env 文件里的配置
    #   extra="ignore"：.env 里写了、但下面没定义成字段的项，直接跳过
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://localhost:5432/todo"   # 对应环境变量 DATABASE_URL（不区分大小写）
    debug: bool = False                       # DEBUG=true 会自动转成 True

    # 3.13
    jwt_secret: str = DEV_SECRET              # 签 token 的密钥，线上一定要换成随机长字符串
    token_days: int = 7                       # token 几天后过期

    # 3.16
    cors_origins: list[str] = ["http://localhost:5173"]   # 允许跨域的前端网址；环境变量写成 JSON：CORS_ORIGINS='["https://todo.example.com"]'
    vercel: bool = False                      # Vercel 上会自动设置 VERCEL=1

    @model_validator(mode="after")            # 所有字段读完之后再执行这个检查
    def check_secret(self) -> Settings:
        if self.vercel and self.jwt_secret == DEV_SECRET:   # 线上还在用开发密钥，等于谁都能伪造 token
            raise ValueError("线上必须设置 JWT_SECRET 环境变量")   # 直接启动失败，比悄悄上线好
        return self                           # 检查通过，原样返回


settings = Settings()   # 整个项目共用这一个，别处 from app.config import settings
