# pgvector_demo.py：把段落和向量存进 PostgreSQL，用 SQL 做向量检索
import os

import psycopg

from embed import DIM, embed
from load_docs import load_chunks

# 本机 Docker 里的 pgvector 容器（启动命令见 README），密码只是本机演示用
DSN = os.environ.get("RAG_DSN", "postgresql://postgres:notes-demo@localhost:5433/rag")


def to_pg(vec: list[float]) -> str:
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"   # pgvector 认这种「[0.1,0.2,…]」格式的文字


with psycopg.connect(DSN, autocommit=True) as conn:
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")   # 打开 pgvector 扩展：多出 vector 类型和相似度运算符
    conn.execute("DROP TABLE IF EXISTS chunks")
    conn.execute(f"""
        CREATE TABLE chunks (
            id        serial PRIMARY KEY,
            source    text NOT NULL,              -- 来自哪个文件：业务字段，可以和向量一起过滤
            title     text NOT NULL,
            body      text NOT NULL,
            embedding vector({DIM}) NOT NULL      -- 向量列，长度要和向量模型一致
        )""")

    chunks = load_chunks()
    vecs = embed([c.title + "：" + c.text for c in chunks])
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO chunks (source, title, body, embedding) VALUES (%s, %s, %s, %s::vector)",
            [(c.source, c.title, c.text, to_pg(v)) for c, v in zip(chunks, vecs)],
        )
    # HNSW 索引：数据多了以后不用一行行比，近似地快速找最近的几个；vector_cosine_ops 表示按余弦距离
    conn.execute("CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops)")
    print("存进去了：", conn.execute("SELECT count(*) FROM chunks").fetchone()[0], "段")

    def search(question: str, source: str | None = None, k: int = 2):
        q = to_pg(embed([question])[0])
        # <=> 是余弦距离（越小越近），1 - 距离 = 相似度；WHERE 可以照常加业务条件
        return conn.execute(
            f"""SELECT title, source, round((1 - (embedding <=> %s::vector))::numeric, 2) AS sim
                FROM chunks {"WHERE source = %s" if source else ""}
                ORDER BY embedding <=> %s::vector LIMIT {k}""",
            (q, source, q) if source else (q, q),
        ).fetchall()

    print(search("店里有网吗"))
    print(search("能退款吗"))
    print(search("能退款吗", source="会员.md"))   # 只在某个文件里搜：向量和业务数据在同一个库，一个 WHERE 就行
