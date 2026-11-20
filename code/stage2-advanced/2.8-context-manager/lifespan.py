from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("启动：建表、建连接池")       # 服务启动时执行一次
    yield                                # 服务运行中
    print("关闭：释放连接池")           # 服务停止时执行一次


app = FastAPI(lifespan=lifespan)
