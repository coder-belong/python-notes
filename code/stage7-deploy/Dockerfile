# Dockerfile：把阶段三的 todo 后端打成镜像（构建时的「上下文」是 ../stage3-todo-api，见 docker-compose.yml）
FROM python:3.12-slim

# 不生成 .pyc；日志直接输出，不在缓冲区攒着
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

# 先只复制依赖清单装依赖：代码改了、依赖没变时，这一层直接用缓存，构建快很多
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt uvicorn alembic \
    -i https://mirrors.aliyun.com/pypi/simple/

# 再复制代码
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini .

# 不用 root 跑：万一被攻破，权限小一点
RUN useradd --create-home appuser && mkdir -p uploads && chown appuser uploads
USER appuser

EXPOSE 8000
# 启动时先把数据库升级到最新的表结构（3.15 节），再启动服务
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
