"""从 article.md 解析 **角色**:` 对话块并清洗文本。"""
from __future__ import annotations

import re

# 支持两种格式：
# 1. **Q**: （冒号在星号外）- briefing-article-style
# 2. **Q:** （冒角在星号内）- 旧格式
# 停止条件：遇到下一个 **Q**/**A**，或遇到 ## 小编总结 或 ---
DIALOGUE_PATTERN = re.compile(
    r"\*\*([QA])\*\*[:：]\s*(.+?)(?=\n---\n|\n## 小编总结|\n\*\*[QA]\*\*[:：]|\Z)",
    re.DOTALL | re.IGNORECASE,
)

# 匹配非对话段落：标题 ### 或 ## 之后，到下一个 **Q**/**A** 之前的文字
NARRATIVE_PATTERN = re.compile(
    r"(?:^# .+\n|^## .+\n|^### .+\n)(.+?)(?=\*\*[QA]\*\*[:：]|\Z)",
    re.DOTALL | re.MULTILINE,
)


def parse_dialogues(md: str) -> list[tuple[str, str]]:
    """返回 (speaker_token, raw_segment) 列表。"""
    return DIALOGUE_PATTERN.findall(md)


def parse_all_segments(md: str) -> list[tuple[str, str]]:
    """返回所有段落（包括对话+非对话），按出现顺序排列。

    speaker_token:
    - N: 叙述段落（旁白/小结）用女声
    - Q: 提问用男声
    - A: 回答用女声
    """
    # 先找出所有对话段的位置
    dialogue_matches = list(DIALOGUE_PATTERN.finditer(md))
    dialogue_spans = [(m.start(), m.end(), m.group(1), m.group(2).strip()) for m in dialogue_matches]

    if not dialogue_spans:
        return []

    # 用对话位置来分割非对话段落
    # 非对话段落 = 从上一次对话结束（或开头）到这一次对话开始之间的内容
    all_segments = []
    prev_end = 0

    # 首先处理开头的非对话内容（标题后的第一段叙述）
    first_start = dialogue_spans[0][0]
    first_end = dialogue_spans[0][1]
    first_speaker = dialogue_spans[0][2]
    first_content = dialogue_spans[0][3]
    prev_end = 0
    if first_start > 0:
        narrative_text = md[:first_start].strip()
        if narrative_text:
            cleaned = clean_segment_strip_role(narrative_text)
            if cleaned and len(cleaned) > 15:
                # 只过滤明确的参考来源格式，不过滤正常内容
                if not (cleaned.startswith("- ") or "参考来源" in cleaned):
                    all_segments.append(("N", cleaned))
        # 添加第一个对话
        all_segments.append((first_speaker, first_content))
        prev_end = first_end

    for i in range(1, len(dialogue_spans)):
        start, end, speaker, content = dialogue_spans[i]

        # 取上一次对话结束到这一次对话开始之间的内容
        if start > prev_end:
            narrative_text = md[prev_end:start].strip()
            if narrative_text:
                # 清理 markdown 标记，取正文
                cleaned = clean_segment_strip_role(narrative_text)
                if cleaned and len(cleaned) > 15:
                    # 只过滤明确的参考来源格式
                    if not (cleaned.startswith("- ") or "参考来源" in cleaned):
                        all_segments.append(("N", cleaned))

        # 添加对话段落
        all_segments.append((speaker, content))
        prev_end = end

    # 处理最后一段非对话内容（小结等）
    if prev_end < len(md):
        narrative_text = md[prev_end:].strip()
        if narrative_text:
            cleaned = clean_segment_strip_role(narrative_text)
            if cleaned and len(cleaned) > 15:
                # 只过滤明确的参考来源格式
                if not (cleaned.startswith("- ") or "参考来源" in cleaned):
                    all_segments.append(("N", cleaned))

    return all_segments


def clean_segment_simple(text: str) -> str:
    """与旧 `generate_dialogue_audio` 的 clean_text 一致（段内去 markdown 噪声）。"""
    t = re.sub(r"#.*", "", text)
    t = re.sub(r"\*\*", "", t)
    t = re.sub(r"---", "", t)
    t = re.sub(r"##.*", "", t)
    t = re.sub(r"\n\n+", "\n", t)
    # 额外清理剩余的星号
    t = re.sub(r"\*+", "", t)
    return t.strip()


def clean_segment_strip_role(text: str) -> str:
    """与旧 `clean_dialogue`（edge/noiz）一致：去掉段内可能的角色标记与版式。"""
    # 清理所有 ** 标记
    t = re.sub(r"\*\*", "", text)
    # 两种格式的角色清理
    t = re.sub(r"\*\*[QA]\*\*[:：]\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\*\*(?:Q|A|Qearl)[:：]\*\*\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\*\*\w+\*\*[:：]\s*", "", t)
    # 清理大标题 # （行首的单个 #）
    t = re.sub(r"^#\s+.*$", "", t, flags=re.MULTILINE)
    t = re.sub(r"#.*", "", t)
    t = re.sub(r"---", "", t)
    t = re.sub(r"##.*", "", t)
    t = re.sub(r"\n\n+", "\n", t)
    # 额外清理残留星号
    t = re.sub(r"\*+", "", t)
    # 清理参考来源行（只过滤参考来源格式的行，不过滤普通内容中的词）
    lines = t.split("\n")
    filtered = [l for l in lines if not (l.strip().startswith("- ") and any(kw in l for kw in ["VentureBeat", "参考来源", "Hacker"]))]
    # 如果是纯链接列表，单独处理
    if filtered and all(l.strip().startswith("[") or l.strip().startswith("-") or l.strip().startswith("http") for l in filtered if l.strip()):
        # 这是参考来源块，全部过滤
        filtered = []
    t = "\n".join(filtered)
    return t.strip()
