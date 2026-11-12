"""配置：都从环境变量读。本地放在 backend/.env 里，Vercel 上在项目的 Environment Variables 里填。"""

import os

from dotenv import load_dotenv

load_dotenv()

# 数据库地址。本地不填就用 SQLite 文件；线上填 Neon 给的 postgres://... 地址
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# 签发登录 token 用的密钥。谁拿到它就能伪造任何人的 token，所以线上必须换成一串随机字符
JWT_SECRET = os.getenv("JWT_SECRET", "")
if not JWT_SECRET:
    if os.getenv("VERCEL"):  # Vercel 上运行时会自动有这个环境变量
        raise RuntimeError("线上没有配置 JWT_SECRET")
    JWT_SECRET = "dev-only-secret-do-not-use-in-production"

# token 多少天后过期，过期要重新登录
TOKEN_DAYS = 30
