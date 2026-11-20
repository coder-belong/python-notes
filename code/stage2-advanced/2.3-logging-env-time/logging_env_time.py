import logging
import os
from datetime import UTC, datetime, timedelta

# 程序入口配置一次：INFO 及以上都输出；format 是每行日志的格式（时间 级别 logger 名: 内容）
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)           # 每个文件一个 logger，名字是模块名

log.debug("调试细节")                        # 级别低于 INFO，不输出
log.info("开始处理 %s 条", 3)                # 2026-11-13 14:28:48,622 INFO __main__: 开始处理 3 条
log.warning("快满了")                        # 2026-11-13 14:28:48,622 WARNING __main__: 快满了
log.error("失败了")                          # 2026-11-13 14:28:48,622 ERROR __main__: 失败了

# 环境变量：密码、地址这类配置不写死在代码里
db_url = os.environ.get("DATABASE_URL", "postgresql+psycopg://localhost:5432/todo")   # 读环境变量 DATABASE_URL，没配就用默认值
print(db_url)                               # 没配时：postgresql+psycopg://localhost:5432/todo

# 时间
now = datetime.now(UTC)                     # 带时区的当前时间，存库和返回接口都用 UTC
print(now.isoformat())                      # 2026-11-10T07:00:00.123456+00:00
print(now.strftime("%Y-%m-%d %H:%M:%S"))    # 2026-11-10 07:00:00
print(now - timedelta(days=3))              # 3 天前
