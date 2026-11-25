# stage5-rag-demo：阶段五「RAG 与知识库」练习代码

用一家虚构的「豆豆咖啡」的三份文档（`docs/` 里的会员规则、门店信息 Markdown，退款规则 PDF）做知识库问答。检索用关键词（BM25），不需要向量模型。

## 准备

```bash
cd code/stage5-rag-demo
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install openai jieba rank-bm25 pypdf
```

## 文件和小节

| 小节 | 文件 | 运行 |
|---|---|---|
| 公共 | `llm.py`：和阶段四一样 | — |
| 5.1 RAG 是什么 | `rag_min.py` 不给资料 / 全部塞进去 / 资料里没有 | `python rag_min.py` |
| 5.2 解析和切分 | `load_docs.py` 读 PDF 和 Markdown、清理、按小标题切段 | `python load_docs.py` |
| 5.3 BM25 | `search.py` jieba 分词 + BM25 检索 | `python search.py` |
| 5.4 完整问答 | `rag.py` 查询改写、检索、回答带出处 | `python rag.py` |
| 5.5 检索评估 | `eval_search.py` 10 条评测集，原句和改写的召回率；`chunk_eval.py` 几种切分方式的召回率对比（不调模型） | `python eval_search.py` |
