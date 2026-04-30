"""侧栏日报列表辅助数据：processing 条数统计 + 首条深挖标题 + 文章状态。"""

from __future__ import annotations

import json
import re

from app.config import BASE_DIR, BRIEFING_HTML_DIR
_INTERMEDIATE = BASE_DIR / "data" / "intermediate"
_OUTPUT = BASE_DIR / "data" / "output"

# 简报 HTML 中第一条「深挖」小标题
_RE_FIRST_DEEP_H3 = re.compile(
    r'<h3>\s*<span\s+class="deep-dive-tag"[^>]*>.*?</span>\s*([^<]+?)\s*</h3>',
    re.IGNORECASE | re.DOTALL,
)


def _processing_has_deep_dive(items: list[dict]) -> bool:
    """processing 中是否存在适合深挖的条目（与简报「深挖」一致，优先 strong）。"""
    for row in items:
        if (row.get("deep_dive_fit") or "") == "strong":
            return True
    return False


def sidebar_meta_for_date(date_str: str) -> dict[str, int | str | bool | None]:
    """返回 entry_count、deep_dive_line（仅简报 HTML）、briefing_has_deep_section、article_exists、has_deep_dive。"""
    out: dict[str, int | str | bool | None] = {
        "entry_count": None,
        "deep_dive_line": None,
        "article_exists": None,
        "has_deep_dive": False,
        "briefing_has_deep_section": False,
    }
    proc_path = _INTERMEDIATE / f"{date_str}-processing.json"
    items: list[dict] | None = None
    if proc_path.is_file():
        try:
            raw = json.loads(proc_path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                items = raw
                out["entry_count"] = len(raw)
        except (json.JSONDecodeError, OSError):
            items = None

    html_text = ""
    html_path = BRIEFING_HTML_DIR / f"{date_str}.html"
    html_has_deep_tag = False
    if html_path.is_file():
        try:
            html_text = html_path.read_text(encoding="utf-8")
            html_has_deep_tag = "deep-dive-tag" in html_text
            m = _RE_FIRST_DEEP_H3.search(html_text)
            if m:
                line = re.sub(r"\s+", " ", m.group(1)).strip()
                if line:
                    out["deep_dive_line"] = line
        except OSError:
            html_text = ""

    # 侧栏第二行仅代表简报 HTML 是否真有「值得深挖」区块（勿用 processing 回填，否则无深挖版面也会假显示摘要）
    out["briefing_has_deep_section"] = html_has_deep_tag

    # 检查文章是否存在
    article_path = _OUTPUT / f"{date_str}-article.md"
    out["article_exists"] = article_path.is_file()

    # 生成对话文章：简报 HTML 有深挖区块，或 processing 标 strong（与 pipeline/article_pick 一致）
    out["has_deep_dive"] = bool(
        html_has_deep_tag
        or (items is not None and _processing_has_deep_dive(items)),
    )

    return out


def sidebar_meta_map(dates: list[str]) -> dict[str, dict[str, int | str | bool | None]]:
    """日期列表 → 各日 meta，供模板渲染。"""
    return {d: sidebar_meta_for_date(d) for d in dates}
