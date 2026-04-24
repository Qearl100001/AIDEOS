#!/usr/bin/env python3
"""
article.md 转 Notion 风格 HTML
用法: python md_to_notion.py [--date YYYY-MM-DD] [--audio MP3_PATH]
"""

import html
import re
import sys
import os
import argparse
from datetime import datetime

# 模板路径（相对于脚本位置）
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(TEMPLATE_DIR, "notion-style-template.html")

# 对话行：**Q**（Qearl）： / Q： 等
_RE_Q_LINE = re.compile(
    r"^(?:\*\*)?Q(?:\*\*)?(?:[（(][^）)]*[）)])?\s*[：:]\s*(.*)$"
)
_RE_A_LINE = re.compile(
    r"^(?:\*\*)?A(?:\*\*)?(?:（[^）]*）|\([^)]*\))?\s*[：:]\s*(.*)$"
)


def _is_q_line(s: str) -> bool:
    return bool(_RE_Q_LINE.match(s.strip()))


def _is_a_line(s: str) -> bool:
    return bool(_RE_A_LINE.match(s.strip()))


def _q_body(s: str) -> str:
    m = _RE_Q_LINE.match(s.strip())
    return m.group(1).strip() if m else ""


def _a_body(s: str) -> str:
    m = _RE_A_LINE.match(s.strip())
    return m.group(1).strip() if m else ""


def _is_summary_section_heading(line: str) -> bool:
    """仅匹配真正的「总结」小节标题，避免正文里「总结陈词」等误触发。"""
    if not line.startswith("## "):
        return False
    rest = line[3:].strip()
    return (
        rest == "总结"
        or rest.startswith("总结 ")
        or rest.startswith("总结：")
        or rest.startswith("总结:")
    )


def _is_references_heading_line(st: str) -> bool:
    """## 参考链接 / ## 参考来源 等文末引用小节（与 convert_references_section 一致）。"""
    if not st.startswith("## ") or st.startswith("###"):
        return False
    rest = st[3:].strip()
    keys = ("参考链接", "参考来源", "参考资料", "参考文献")
    return any(rest == k or rest.startswith(f"{k} ") for k in keys)


def _strip_reference_block_from_body(body: str) -> str:
    """文末参考小节由 convert_references_section 单独渲染，避免正文里再出一遍。"""
    lines = body.split("\n")
    out: list[str] = []
    skipping = False
    for line in lines:
        st = line.strip()
        if _is_references_heading_line(st):
            skipping = True
            continue
        if skipping:
            continue
        out.append(line)
    return "\n".join(out)


def _project_root_from_script() -> str:
    """脚本位于 .claude/skills/briefing-article-style/scripts/ → 仓库根。"""
    return os.path.abspath(os.path.join(TEMPLATE_DIR, "..", "..", "..", ".."))


def _resolve_project_root_for_io(input_path: str) -> str:
    """优先根据 article.md 路径推断仓库根（data/output/ 的父级的父级）。"""
    ap = os.path.abspath(input_path)
    needle = os.sep + "data" + os.sep + "output"
    if needle in ap:
        idx = ap.rfind(needle)
        return ap[:idx]
    return _project_root_from_script()


def _guess_article_audio(project_root: str, date_str: str) -> str | None:
    """未指定 --audio 时，在 data/output 下按常见 TTS 产物名探测 MP3。"""
    out_dir = os.path.join(project_root, "data", "output")
    if not os.path.isdir(out_dir):
        return None
    preferred = (
        f"{date_str}-dialogue-doubao.mp3",
        f"{date_str}-dialogue-stereo.mp3",
        f"{date_str}-dialogue.mp3",
        f"{date_str}-dialogue-final.mp3",
        f"{date_str}-dialogue-noiz.mp3",
    )
    for name in preferred:
        p = os.path.join(out_dir, name)
        if os.path.isfile(p):
            return p
    prefix = f"{date_str}-"
    try:
        for fn in sorted(os.listdir(out_dir)):
            if fn.startswith(prefix) and fn.lower().endswith(".mp3"):
                return os.path.join(out_dir, fn)
    except OSError:
        pass
    return None


def _date_from_article_path(path: str) -> str | None:
    m = re.search(r"(\d{4}-\d{2}-\d{2})-article\.md$", os.path.basename(path))
    return m.group(1) if m else None


def _apply_inline_emphasis(text: str) -> str:
    """**x** → <mark>（与原有 dialogue 处理一致）。"""
    return re.sub(r"\*\*(.+?)\*\*", r"<mark>\1</mark>", text)


def load_template():
    """加载 HTML 模板"""
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def parse_article_markdown(content):
    """解析 article.md 内容，返回结构化数据"""
    lines = content.strip().split('\n')

    # 提取标题（先找 # 作为主标题，再找第一个 ## 作为副标题/主题）
    title = ""
    subtitle = ""
    audio_section = ""
    body_start = 0

    for i, line in enumerate(lines):
        # 先找 # 作为主标题（大标题）
        if line.startswith('# ') and not title:
            title = line[2:].strip()
            body_start = i + 1
            continue
        # 再找第一个 ## 作为副标题（主题块标题）；正文从该标题下一行开始，避免重复输出
        if line.startswith('## ') and not line.startswith('###'):
            subtitle = line[3:].strip()
            body_start = i + 1
            break
        if line.strip() == '---':
            body_start = i + 1

    # 如果没有 #，用第一个 ## 作为标题
    if not title:
        for i, line in enumerate(lines):
            if line.startswith('## ') and not line.startswith('###'):
                title = line[3:].strip()
                body_start = i + 1
                break

    # 解析正文内容
    body_lines = lines[body_start:] if body_start else lines[1:]
    body_content = '\n'.join(body_lines)

    # 如果 title 为空，尝试从第一段提取
    if not title:
        for line in lines:
            if line.strip() and not line.startswith('#') and not line.startswith('**') and not line.startswith('---'):
                title = line.strip()[:60]
                break

    return {
        'title': title,
        'subtitle': subtitle,
        'audio': audio_section,
        'body': body_content
    }


def convert_to_html(
    data,
    audio_path=None,
    audio_duration="8:24",
    audio_src: str | None = None,
):
    """转换为 Notion 风格 HTML。

    audio_path: 存在则渲染播音模块；audio_src 为相对 HTML 路径时可实际播放（<audio src>）。
    """
    template = load_template()

    if not template:
        # 使用内置简化模板
        template = get_default_template()

    html_doc = template

    # 替换标题
    html_doc = html_doc.replace('<title>...</title>', f'<title>{data["title"]}</title>')
    html_doc = html_doc.replace('<h1>...</h1>', f'<h1>{data["title"]}</h1>')

    # 替换副标题
    subtitle_html = f'<p class="subtitle">{data["subtitle"]}</p>'
    html_doc = html_doc.replace('<p class="subtitle">2026年4月20日 | AI+设计日报</p>', subtitle_html)

    # 处理音频区域
    if audio_path:
        src_attr = ""
        audio_el = ""
        if audio_src:
            src_attr = f' src="{html.escape(audio_src)}"'
            audio_el = f'<audio id="article-audio" preload="metadata"{src_attr} style="display:none"></audio>'
        audio_html = f'''
        <div class="audio-section">
            <h3>语音播客</h3>
            <div class="audio-player">
                <button type="button" class="play-btn" onclick="togglePlay()" aria-label="播放/暂停">
                    <svg viewBox="0 0 24 24" id="play-icon">
                        <polygon points="5,3 19,12 5,21"></polygon>
                    </svg>
                </button>
                <div class="audio-info">
                    <div class="audio-title">{html.escape(data["title"])}</div>
                    <div class="audio-meta">时长 {html.escape(audio_duration)} · AI+设计日报</div>
                </div>
                <div class="audio-wave">
                    <span></span><span></span><span></span><span></span><span></span>
                </div>
                {audio_el}
            </div>
        </div>'''
        html_doc = html_doc.replace('<div class="audio-section">...</div>', audio_html)
    else:
        # 无音频时隐藏
        html_doc = re.sub(r'<div class="audio-section">.*?</div>\s*', "", html_doc, flags=re.DOTALL)

    # 转换正文内容（参考链接块单独渲染，避免重复）
    body_for_html = _strip_reference_block_from_body(data["body"])
    body_html = convert_markdown_body(body_for_html)
    html_doc = html_doc.replace('<p class="dialogue-q">...</p>\n    <div class="dialogue-a">...</div>', body_html)
    # 默认模板占位：总结由正文内「## 总结」生成；参考链接在 main 里注入
    html_doc = re.sub(r'<div class="summary">\s*\.\.\.\s*</div>\s*', "", html_doc)
    html_doc = re.sub(r'<div class="references">\s*\.\.\.\s*</div>\s*', "", html_doc)

    return html_doc


def convert_markdown_body(md_content):
    """将 markdown 正文转换为 HTML（支持 **Q**/**A**、Q：/A：、## 总结 收束段、叙述性开场）。"""
    lines = md_content.strip().split("\n")
    html_parts: list[str] = []
    i = 0

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        if not line:
            i += 1
            continue

        if line == "---":
            i += 1
            continue

        # 「## 总结」整段进入灰色 summary 块（不误匹配正文中的「总结」二字）
        if line.startswith("## ") and _is_summary_section_heading(line):
            i += 1
            summary_body: list[str] = []
            while i < len(lines):
                nl = lines[i].strip()
                if nl.startswith("## ") or nl == "---":
                    break
                if lines[i].strip():
                    summary_body.append(lines[i].strip())
                i += 1
            html_parts.append(convert_summary_section(summary_body))
            continue

        # ## Q：… 与 **Q：** 统一为对话块（避免 ## 被当成普通 h2）
        inner_q: str | None = None
        if line.startswith("## ") and not line.startswith("###"):
            _inner = line[3:].strip()
            if _is_q_line(_inner):
                inner_q = _inner
        elif _is_q_line(line):
            inner_q = line.strip()

        if inner_q is not None:
            q_text = _apply_inline_emphasis(_q_body(inner_q))
            html_parts.append(f'<p class="dialogue-q">{q_text}</p>')
            i += 1
            a_lines: list[str] = []
            while i < len(lines):
                nt = lines[i].strip()
                if not nt:
                    i += 1
                    continue
                if nt == "---":
                    break
                if nt.startswith("## ") and not nt.startswith("###"):
                    inner_h = nt[3:].strip()
                    if _is_q_line(inner_h):
                        break
                    if _is_a_line(inner_h):
                        i += 1
                        continue
                    break
                if _is_q_line(nt):
                    break
                if _is_a_line(nt):
                    a_lines.append(_a_body(nt))
                    i += 1
                    continue
                a_lines.append(nt)
                i += 1

            if a_lines:
                processed_a = []
                for a_line in a_lines:
                    a_line = _apply_inline_emphasis(a_line)
                    a_line = re.sub(
                        r"\[\^(\d+)\]",
                        r'<span class="ref" title="参考链接 [^\1]">[^\1]</span>',
                        a_line,
                    )
                    processed_a.append(f"<p>{a_line}</p>")

                a_html = f'''<div class="dialogue-a">
        <span class="content">
            {"".join(processed_a)}
        </span>
    </div>'''
                html_parts.append(a_html)

            continue

        if line.startswith("## "):
            title = line[3:].strip()
            html_parts.append(f"<h2>{html.escape(title)}</h2>")
            i += 1
            continue

        # 单独的 A 行（极少见）：按回答样式输出
        if _is_a_line(line):
            a_html = _apply_inline_emphasis(_a_body(line))
            a_html = re.sub(
                r"\[\^(\d+)\]",
                r'<span class="ref" title="参考链接 [^\1]">[^\1]</span>',
                a_html,
            )
            html_parts.append(
                f'''<div class="dialogue-a">
        <span class="content">
            <p>{a_html}</p>
        </span>
    </div>'''
            )
            i += 1
            continue

        # 叙述性段落（开场白等），直到空行或结构边界
        para_chunks: list[str] = []
        while i < len(lines):
            cur = lines[i].strip()
            if not cur:
                break
            if cur.startswith("## ") or cur == "---":
                break
            if _is_q_line(cur) or _is_a_line(cur):
                break
            para_chunks.append(lines[i].strip())
            i += 1
        for chunk in para_chunks:
            if chunk:
                html_parts.append(f"<p>{_apply_inline_emphasis(chunk)}</p>")

    return "\n    ".join(html_parts)


def convert_summary_section(lines):
    """转换总结段落（lines 为总结标题下的正文行，不含 ## 行）。"""
    content_parts = []
    for line in lines:
        if line.startswith("## "):
            continue
        t = _apply_inline_emphasis(line.strip())
        if t:
            content_parts.append(f"<p>{t}</p>")

    return f'''<div class="summary">
        <h3>总结</h3>
        {"".join(content_parts)}
    </div>'''


def convert_references_section(md_content: str) -> str:
    """转换参考链接段落（支持 `- [...]` / `1. [...]`；标题可为 参考链接 / 参考来源）。"""
    lines = md_content.split("\n")
    ref_items: list[str] = []
    in_refs = False
    section_title = "参考链接"

    for line in lines:
        st = line.strip()
        if st.startswith("## ") and _is_references_heading_line(st):
            in_refs = True
            section_title = st[3:].strip()
            continue
        if in_refs:
            if st.startswith("## ") and not _is_references_heading_line(st):
                break
            if not st:
                continue
            match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", line)
            if match:
                title, url = match.groups()
                ref_items.append(
                    f'<li><a href="{html.escape(url)}" target="_blank">'
                    f"{html.escape(title)}</a></li>"
                )

    if ref_items:
        return f'''<div class="references">
        <h3>{html.escape(section_title)}</h3>
        <ul>
            {chr(10).join(ref_items)}
        </ul>
    </div>'''
    return ""


def get_default_template():
    """获取默认模板（当文件不存在时）"""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>...</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.7; color: #37352f; max-width: 900px; margin: 0 auto; padding: 60px 40px; }
        h1 { font-size: 40px; font-weight: 700; margin-bottom: 8px; }
        .subtitle { font-size: 16px; color: #787774; margin-bottom: 24px; }
        .audio-section { margin: 0 0 32px 0; padding: 20px 24px; background: #f7f6f3; border-radius: 8px; display: flex; align-items: center; gap: 20px; cursor: pointer; }
        .audio-section:hover { background: #efeeeb; }
        .play-btn { width: 48px; height: 48px; border-radius: 50%; background: #37352f; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .play-btn svg { width: 18px; height: 18px; fill: #fff; margin-left: 3px; }
        .audio-info { flex: 1; }
        .audio-title { font-size: 15px; font-weight: 600; color: #37352f; }
        .audio-meta { font-size: 13px; color: #787774; }
        .audio-wave { display: flex; align-items: center; gap: 3px; height: 24px; }
        .audio-wave span { width: 3px; background: #d9d9d9; border-radius: 2px; }
        .audio-wave span:nth-child(1) { height: 10px; } .audio-wave span:nth-child(2) { height: 16px; } .audio-wave span:nth-child(3) { height: 20px; } .audio-wave span:nth-child(4) { height: 14px; } .audio-wave span:nth-child(5) { height: 18px; }
        @keyframes wave { 0%, 100% { transform: scaleY(0.5); } 50% { transform: scaleY(1); } }
        h2 { font-size: 20px; font-weight: 600; margin: 32px 0 12px; padding-top: 20px; line-height: 1.3; border-top: 1px solid #eee; }
        .dialogue-q { background: #f7f6f3; padding: 16px 20px; border-radius: 4px; margin: 24px 0 12px; font-weight: 500; line-height: 1.6; }
        .dialogue-q::before { content: "Q："; color: #787774; font-weight: 600; margin-right: 4px; }
        .dialogue-a { padding: 0; margin: 0 0 16px 0; line-height: 1.8; }
        .dialogue-a::before { content: "A："; color: #eb5757; font-weight: 600; margin-right: 4px; float: left; }
        .dialogue-a .content { margin-left: 28px; }
        .dialogue-a .content p { margin-bottom: 10px; }
        mark { background-color: #fff5b8; padding: 2px 4px; border-radius: 2px; color: #37352f; font-weight: 500; }
        .ref { font-size: 12px; color: #787774; vertical-align: super; }
        .summary { background: #f7f6f3; padding: 24px; border-radius: 6px; margin: 40px 0; }
        .summary h3 { margin-top: 0; font-size: 16px; }
        .references { margin-top: 48px; padding-top: 32px; }
        .references h3 { font-size: 14px; text-transform: uppercase; color: #787774; margin-bottom: 16px; }
        .references ul { list-style: none; padding-left: 0; }
        .references li { margin-bottom: 12px; }
        .references a { color: #0066cc; text-decoration: none; font-size: 14px; }
        @media (max-width: 768px) { body { padding: 32px 20px; } h1 { font-size: 32px; } h2 { font-size: 24px; } }
    </style>
</head>
<body>
    <h1>...</h1>
    <p class="subtitle">2026年4月20日 | AI+设计日报</p>
    <div class="audio-section">...</div>
    <p class="dialogue-q">...</p>
    <div class="dialogue-a">...</div>
    <div class="summary">...</div>
    <div class="references">...</div>
    <script>
    function togglePlay() {
      const audio = document.getElementById('article-audio');
      const icon = document.getElementById('play-icon');
      const playSvg = '<polygon points="5,3 19,12 5,21"></polygon>';
      const pauseSvg = '<rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect>';
      if (audio && audio.getAttribute('src')) {
        if (audio.paused) {
          audio.play();
          icon.innerHTML = pauseSvg;
        } else {
          audio.pause();
          icon.innerHTML = playSvg;
        }
        return;
      }
      let isPlaying = icon.dataset.mockPlaying === '1';
      isPlaying = !isPlaying;
      icon.dataset.mockPlaying = isPlaying ? '1' : '0';
      icon.innerHTML = isPlaying ? pauseSvg : playSvg;
    }
    if (document.getElementById('article-audio')) {
      document.getElementById('article-audio').addEventListener('ended', function() {
        const icon = document.getElementById('play-icon');
        if (icon) icon.innerHTML = '<polygon points="5,3 19,12 5,21"></polygon>';
      });
    }
    </script>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description='将 article.md 转换为 Notion 风格 HTML')
    parser.add_argument('--date', '-d', default=None, help='日期，格式 YYYY-MM-DD（默认今天）')
    parser.add_argument('--audio', '-a', default=None, help='音频文件路径')
    parser.add_argument('--duration', default='8:24', help='音频时长，默认 8:24')
    parser.add_argument('--input', '-i', default=None, help='输入文件路径')
    parser.add_argument('--output', '-o', default=None, help='输出文件路径')

    args = parser.parse_args()

    # 确定日期
    date_str = args.date or datetime.now().strftime('%Y-%m-%d')

    # 确定输入输出路径
    if args.input:
        input_path = args.input
    else:
        input_path = f'data/output/{date_str}-article.md'

    if args.output:
        output_path = args.output
    else:
        output_path = input_path.replace('.md', '.html')

    # 检查输入文件
    if not os.path.exists(input_path):
        print(f"错误：找不到输入文件 {input_path}")
        sys.exit(1)

    date_for_audio = _date_from_article_path(input_path) or date_str
    project_root = _resolve_project_root_for_io(input_path)
    audio_abs = args.audio
    if audio_abs and not os.path.isfile(audio_abs):
        print(f"[md_to_notion] 警告：--audio 文件不存在，将尝试自动探测: {audio_abs}")
        audio_abs = None
    if not audio_abs:
        audio_abs = _guess_article_audio(project_root, date_for_audio)
    audio_src = None
    if audio_abs and os.path.isfile(audio_abs):
        out_dir = os.path.dirname(os.path.abspath(output_path))
        audio_src = os.path.relpath(os.path.abspath(audio_abs), start=out_dir)
        if not args.audio:
            print(f"[md_to_notion] 自动选用音频: {audio_abs}")

    # 读取 md 文件
    print(f"读取: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 解析
    data = parse_article_markdown(md_content)
    print(f"标题: {data['title']}")

    # 转换（有音频文件则展示播音模块并挂接 <audio src>）
    html = convert_to_html(
        data,
        audio_path=audio_abs,
        audio_duration=args.duration,
        audio_src=audio_src,
    )

    ref_html = convert_references_section(md_content)
    if ref_html.strip():
        html = html.replace("</body>", ref_html + "\n</body>", 1)

    # 写入输出
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"完成: {output_path}")


if __name__ == '__main__':
    main()