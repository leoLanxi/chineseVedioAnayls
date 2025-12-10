import re
from typing import List, Tuple

def clean_zh_text(text: str) -> str:
    t = text
    t = re.sub(r"[\u0000-\u001f]", "", t)
    t = t.replace("\u3000", " ")
    t = re.sub(r"[A-Za-z0-9_]+", "", t)
    t = re.sub(r"[\[\(（【 ].*?[ \]\)）】]", "", t)
    t = re.sub(r"([\u4e00-\u9fa5]{1})\1{1,}", r"\1", t)
    t = re.sub(r"(然后)+", "然后", t)
    t = re.sub(r"(就是)+", "就是", t)
    t = re.sub(r"(那个)+", "那个", t)
    t = re.sub(r"(嗯|啊|呃|哦|吧|呀|嘛){2,}", lambda m: m.group(1), t)
    t = re.sub(r"\s+", "", t)
    t = re.sub(r"([。！？；,…]){2,}", r"\1", t)
    return t.strip()

def split_sentences(text: str) -> List[str]:
    s = re.split(r"([。！？!?])", text)
    r = []
    for i in range(0, len(s), 2):
        seg = s[i].strip()
        if not seg:
            continue
        p = seg
        if i + 1 < len(s):
            p += s[i + 1]
        r.append(p)
    return r

def group_paragraphs(sentences: List[str], target_len: int = 80) -> List[str]:
    ps = []
    buf = []
    cur = 0
    for sen in sentences:
        l = len(sen)
        if cur + l <= target_len or not buf:
            buf.append(sen)
            cur += l
        else:
            ps.append("".join(buf))
            buf = [sen]
            cur = l
    if buf:
        ps.append("".join(buf))
    return ps

def wrap_cn_line(text: str, max_len: int = 20) -> List[str]:
    if len(text) <= max_len:
        return [text]
    lines = []
    start = 0
    while start < len(text):
        end = min(start + max_len, len(text))
        if end < len(text):
            k = text.rfind("，", start, end)
            if k == -1:
                k = text.rfind("、", start, end)
            if k == -1:
                k = text.rfind("。", start, end)
            if k != -1 and k > start + max_len * 0.5:
                end = k + 1
        lines.append(text[start:end])
        start = end
    return lines

def build_srt_content(items: List[Tuple[int, int, str]]) -> str:
    def fmt(t: int) -> str:
        ms = t % 1000
        s = (t // 1000) % 60
        m = (t // 60000) % 60
        h = t // 3600000
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    out = []
    idx = 1
    for st, et, tx in items:
        lines = wrap_cn_line(tx, 24)
        out.append(str(idx))
        out.append(f"{fmt(st)} --> {fmt(et)}")
        out.extend(lines)
        out.append("")
        idx += 1
    return "\n".join(out).strip()

