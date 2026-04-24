"""长文本按 UTF-8 字节上限切分，避免单次 TTS 请求过长。"""
from __future__ import annotations


def utf8_byte_chunks(text: str, max_bytes: int = 6000) -> list[str]:
    """按 UTF-8 字节上限切分，保留换行语义。"""
    text = text.strip()
    if not text:
        return []
    parts: list[str] = []
    buf: list[str] = []
    size = 0
    for para in text.split("\n"):
        line = para + "\n"
        b = line.encode("utf-8")
        if len(b) > max_bytes:
            if buf:
                parts.append("".join(buf).rstrip())
                buf = []
                size = 0
            for chunk in _hard_split(line, max_bytes):
                parts.append(chunk)
            continue
        if size + len(b) > max_bytes and buf:
            parts.append("".join(buf).rstrip())
            buf = []
            size = 0
        buf.append(line)
        size += len(b)
    if buf:
        parts.append("".join(buf).rstrip())
    return [p for p in parts if p.strip()]


def _hard_split(line: str, max_bytes: int) -> list[str]:
    out: list[str] = []
    cur = ""
    for ch in line:
        trial = cur + ch
        if len(trial.encode("utf-8")) > max_bytes and cur:
            out.append(cur)
            cur = ch
        else:
            cur = trial
    if cur.strip():
        out.append(cur)
    return out
