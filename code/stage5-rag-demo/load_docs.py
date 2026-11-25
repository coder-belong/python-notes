# load_docs.py
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass            # 自动生成 __init__：Chunk("会员.md", "积分", "每消费…") 就能创建
class Chunk:          # 切好的一小段：检索、引用出处都以它为单位
    source: str       # 来自哪个文件
    title: str        # 所在的小标题
    text: str         # 正文


def read_text(path: Path) -> str:
    if path.suffix == ".pdf":
        reader = PdfReader(path)
        text = "\n".join(page.extract_text() for page in reader.pages)   # 每一页的文字拼起来
    else:
        text = path.read_text(encoding="utf-8")
    # PDF 里的「⾖」「⼀」看着像汉字，其实是另一种字符（部首），搜「豆」搜不到它，换回普通汉字。
    # 只换这一段编码范围：整段都 normalize 的话，中文逗号「，」也会被换成英文逗号
    text = re.sub(r"[\u2e80-\u2fdf]", lambda m: unicodedata.normalize("NFKC", m.group()), text)
    lines = [line.strip() for line in text.splitlines()]   # 去掉每行首尾空格
    return "\n".join(line for line in lines if line)       # 去掉空行


def split(source: str, text: str, max_len: int = 200) -> list[Chunk]:
    chunks = []
    # 按「## 小标题」切：每个小标题下面是一段完整的意思
    for part in re.split(r"^## ", text, flags=re.M)[1:]:   # re.M：^ 匹配每一行的开头；[1:]：第一段是大标题，跳过
        title, _, body = part.partition("\n")              # 第一行是小标题，后面是正文
        body = body.replace("\n", "")
        for i in range(0, len(body), max_len):             # 正文太长再按长度切
            chunks.append(Chunk(source, title, body[i : i + max_len]))
    return chunks


def load_chunks(folder: str = "docs") -> list[Chunk]:
    chunks = []
    for path in sorted(Path(folder).iterdir()):            # 文件夹里的每个文件
        chunks += split(path.name, read_text(path))
    return chunks


if __name__ == "__main__":
    raw = PdfReader("docs/退款.pdf").pages[0].extract_text()
    print(repr(raw[:40]))                   # 直接从 PDF 取出来的文字
    print(repr(read_text(Path("docs/退款.pdf"))[:40]))   # 清理之后
    for c in load_chunks():
        print(c.source, c.title, c.text[:20])
