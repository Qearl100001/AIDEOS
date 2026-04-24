# 文章输出规则（固定规范）

## 1. 内容显示对照表

| 内容 | 文章HTML显示 | TTS朗读 | 说明 |
|------|--------------|---------|------|
| **大标题 #** | ✅ | ❌ | 行首单个 `#` 标题不读 |
| 开头背景介绍 | ✅ | ✅ | 正文内容正常朗读 |
| 正文对话内容 | ✅ | ✅ | Q/A 对话正常朗读 |
| 参考来源列表 | ✅ | ❌ | 显示在文末，不朗读 |
| 日期标注 (截至...) | ❌ | ❌ | 完全删除 |
| 主持人介绍 | ❌ | ❌ | `**Q**: 主持人...` 删除 |
| Markdown加粗 ** | 显示 | ❌ | 仅显示符号内容，不读 `**` |
| 分隔线 --- | ✅ | ❌ | 不朗读 |

## 2. 输出流程

### Step 1: 生成文章 (article.md)
- 标题格式：`# 产品名：副标题`
- 结构：开头背景 → 正文 → 结尾总结
- 参考来源放在文末，标记为 `## 参考来源`

### Step 2: 生成音频 (TTS)
- 使用 `edge` 预设
- 自动跳过：大标题、参考来源、日期标注、主持人介绍、星号
- 语气词：每5段加1-2个「那个」「对的」

### Step 3: 生成网页 (HTML)
- 显示完整内容（包括参考来源）
- 嵌入音频播放器

## 3. 示例

### article.md 内容
```
# Anthropic Cowork：桌面 AI 代理走向普通人的下一步

今天的简报里，最值得深挖的是 Anthropic 发布的 Cowork...

## Cowork 是什么？

**Q**: 先说说这个 Cowork 到底是什么？

**A**: 好的。Cowork 是 Anthropic 最新的...

（正文）

## 参考来源

- VentureBeat: Anthropic launches Cowork
- Anthropic 官方介绍
- 社区讨论 - Hacker News
```

### TTS 朗读内容（跳过不读的）
```
今天的简报里，最值得深挖的是 Anthropic 发布的 Cowork...

先说说这个 Cowork 到底是什么？

好的。Cowork 是 Anthropic 最新的...

（正文，不含参考来源）
```

### HTML 显示
- 完整显示所有内容
- 参考来源在文末可见

## 4. 实施文件

- 解析规则：`tools/tts_dialogue/parse.py` → `clean_segment_strip_role()`
- 语气词规则：`tools/tts_dialogue/prefixes.py` → `prefix_sparse_edge()`
- 模板：`skills/briefing-article-style/scripts/md_to_notion.py`

## 5. 生成命令

```bash
# 生成音频
python3 -m tools.tts_dialogue --date 2026-04-22 --preset edge

# 生成网页
python3 .claude/skills/briefing-article-style/scripts/md_to_notion.py --date 2026-04-22
```