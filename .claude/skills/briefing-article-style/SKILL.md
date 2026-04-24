---
name: briefing-article-style
description: >-
  Constrains dialogue-structured briefing articles for AI+design daily output,
  using a LatePost-style interview rhythm (layered Q&A, verification hooks,
  explicit uncertainty). Produces Markdown as the single TTS source (article.md).
  Use when generating or editing data/output/*-article.md, briefing-article,
  dialogue structure, 口播母本, 晚点式访谈对话, or long-form
  single-product analysis dialogue, or LateTalk-style domain transcript reference.
  See examples/good-output.md (I/O对照), bad-output.md, edge-cases.md for format.
---

# Briefing Article Style（对话式结构化长文）

## 何时使用

- 生成或润色 `data/output/{DATE}-article.md`
- 用户提到「对话式文章」「口播稿」「与 briefing 配套的长文」「晚点式访谈」体裁

## 与简报的分工

| 文件 | 用途 |
|------|------|
| `briefing.md` | 短讯 + 编辑视角，快速扫读 |
| `article.md` | **对话式深度稿**，且为 **TTS 唯一母本** |

## 核心流程

1. **路由**：根据 YAML `description` 与上文「何时使用」判断本任务是否应遵循本 skill（写/改 `*-article.md`、口播母本、单产品对话长文等）。
2. **读入口**：完整阅读本 `SKILL.md` 的「必须遵守」「结构与风格（摘要）」「禁止」；子文件不自动等价于已读。
3. **动笔前（输入/输出对照）**：必读 [examples/good-output.md](examples/good-output.md)；再扫 [examples/bad-output.md](examples/bad-output.md) 与 [examples/edge-cases.md](examples/edge-cases.md)，减少格式与事实口径错误。
4. **按需深入**：
   - Q/A 句式与小标题规则 → [references/dialogue-qa-patterns.md](references/dialogue-qa-patterns.md)（**核心参考**）
   - 总结段怎么写 → [references/summary-section.md](references/summary-section.md)
   - 选题/路径/TTS/输入源 → [references/pipeline-contract.md](references/pipeline-contract.md)
5. **交付**：产出或修改 `data/output/{DATE}-article.md`，事实以当日 `data/intermediate/{DATE}-processing.json`（尤其 `key_facts`）与可核验来源为准；若跑过 `python -m tools.generate_article`，勿与脚本选题 silently 打架（改题须标注，见 pipeline-contract）。

## 必须遵守（执行前扫一眼）

- **输出与选题**：仅 `data/output/{DATE}-article.md`；**单条**深度（与 `article_pick` 一致）；人工改题须在文首或编辑说明标注。详见 [references/pipeline-contract.md](references/pipeline-contract.md)。
- **话轮**：`Q：` + `A：` 形式；主题块 **2–4** 个，每块前 **`## 小节标题`**，小标题**必须是观点句**（如 `## 它不是取代设计师，而是取代设计流程`），块内多轮 Q&A；**至少一处** `Q` 追问到分歧、限制条件或**不适用场景**。详见 [references/dialogue-qa-patterns.md](references/dialogue-qa-patterns.md)。
- **事实**：以 `processing.json` 的 `key_facts` 与可核验官方来源为准；传闻、未核对数字不得写死。
- **篇幅**：**1500–4000** 字，口播一轮可完成。

## 结构与风格（摘要）

1. **标题**：简洁有力，可带日期副标。  
2. **角色行**（文首两行）：简化为 `Q：` + `A：` 形式（如「**Q**：主持人」「**A**：嘉宾」），不预设具体角色身份。  
3. **开场**：200–400 字，抛出当日主线；推荐含「时效锚点」（为何此刻值得聊 / 截至某日公开信息）。  
4. **主题块**：多轮对话，遵守话轮与问法轮换（细则见 `references/dialogue-qa-patterns.md`）。  
   - **小标题即观点**：每个 `##` 后面直接是结论句，不是「功能介绍」
   - **A 回答要详细**：每个观点都要给足理由，可引用文章、案例、数据；不要只给结论
5. **结尾**：明确判断或「待观察」边界，可呼应 `context/viewpoint.md`、`context/expectations.md`。  
6. **What's Next**：可嵌入结尾对话，不必单独成章。  
7. **参考链接**：文末附 2-5 条参考来源（官方文档、新闻报道、社区讨论等）。  
8. **语气**：口语与信息密度平衡，书面语打底；忌营销腔；术语中英可并用。

## 深入阅读（按需打开）

| 文件 | 内容 |
|------|------|
| [references/dialogue-qa-patterns.md](references/dialogue-qa-patterns.md) | **主持人 Q 句式清单** + 回答者 A 风格 + 追问清单 |
| [references/summary-section.md](references/summary-section.md) | 总结段怎么写（判断类型 + 自检清单） |
| [references/pipeline-contract.md](references/pipeline-contract.md) | 与 `generate_article.py` 对齐、输入路径、TTS 约定 |
| [references/notion-style-template.html](references/notion-style-template.html) | HTML 输出模板（Notion 风格） |

## 自动化工具

| 工具 | 用法 |
|------|------|
| `scripts/md_to_notion.py` | 将 `article.md` 转为 Notion 风格 HTML |

## 示例（写稿前推荐阅读）

| 文件 | 用途 |
|------|------|
| [examples/good-output.md](examples/good-output.md) | **输入 / 输出对照**：成功长什么样（虚构 PixelMeld） |
| [examples/bad-output.md](examples/bad-output.md) | **反例**：要避免的话轮与体裁错误 |
| [examples/edge-cases.md](examples/edge-cases.md) | **边界**：素材不足、改题、润色、TTS |
| [examples/output-example.md](examples/output-example.md) | 仅输出片段（与 good-output 重复时可不单独打开） |
| [examples/input-example.md](examples/input-example.md) | 仅输入 JSON（已并入 good-output 第一节） |

## 禁止

- 另存一篇与 `article.md` 平行的「第二对话长文」作为同一用途交付。  
- 把社区传闻、匿名帖、未核对数字写成已证实事实。  
- 连续多轮 `Q` 仅重复「你怎么看」，无场景、求证或边界追问。
