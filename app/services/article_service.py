"""结构化文章读取与渲染服务。"""

from __future__ import annotations

import re

from markdown_it import MarkdownIt

from app.config import OUTPUT_DIR

_md = MarkdownIt()

_QA_PATTERN = re.compile(
    r"<p><strong>(Q|A)</strong>\s*[:：]\s*(.*?)</p>",
    re.DOTALL,
)


def get_article_markdown(date: str) -> str:
    """读取指定日期结构化文章 Markdown。"""
    path = OUTPUT_DIR / f"{date}-article.md"
    if not path.exists():
        raise FileNotFoundError(f"未找到该日期结构化文章: {date}")

    return path.read_text(encoding="utf-8")


def _enrich_qa_blocks(html: str) -> str:
    """将 **Q** / **A** 段落包装为结构化访谈块（对齐口播母本版式）。"""
    first_a = True

    def repl(match: re.Match[str]) -> str:
        nonlocal first_a
        role, body = match.group(1), match.group(2)
        if role == "Q":
            return (
                '<div class="dfos-qa dfos-qa--q">'
                '<span class="dfos-qa-mark">Q</span>'
                f'<div class="dfos-qa-body"><p>{body}</p></div></div>'
            )
        cls = "dfos-qa dfos-qa--a"
        if first_a:
            cls += " dfos-qa--a-lead"
            first_a = False
        return (
            f'<div class="{cls}">'
            '<span class="dfos-qa-mark">A</span>'
            f'<div class="dfos-qa-body"><p>{body}</p></div></div>'
        )

    return _QA_PATTERN.sub(repl, html)


def _strong_to_dfos_key(html: str) -> str:
    """将全部正文加粗转为重点高亮（与 mark.dfos-key 一致）；不含嵌套标签的简单 strong。"""
    return re.sub(
        r"<strong>([^<]+)</strong>",
        r'<mark class="dfos-key">\1</mark>',
        html,
    )


def render_article_html(md_text: str) -> str:
    """将 Markdown 渲染为 HTML，并做 Q/A 结构与重点标记增强。"""
    raw = _md.render(md_text)
    enriched = _enrich_qa_blocks(raw)
    return _strong_to_dfos_key(enriched)
