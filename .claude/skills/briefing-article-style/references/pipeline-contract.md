# 步骤 3 与流水线契约

## 与 `tools/generate_article.py` 对齐

| 项目 | Skill 要求 | 代码实现（`generate_article.py` + `article_pick.py`） |
|------|------------|------------------------------------------------------|
| 条数 | **只写一条**资讯背后的产品/话题 | `pick_primary_article_item` 从 `processing.json` 选 **1 条** |
| 选题顺序 | new_tool 优先 → tier → 分数 | 同左：`TIER_RANK` + `final_score` |
| 输出文件 | `data/output/{DATE}-article.md` | `OUTPUT_DIR / f"{date}-article.md"` |
| 体裁 | Q / A 对话式，非 KeyPoints/Background 分栏长文 | `build_article_dialogue()` 系统 prompt |

若人工编辑偏离脚本选题，须在文首或编辑说明中标注，避免口播与日报条目不一致却无说明。

## 事实与输入

- **主输入**：`data/intermediate/{DATE}-processing.json`（生成脚本按 `article_pick` 择一条）。
- **辅助**：`data/output/{DATE}-briefing.md`、`data/output/product-profiles/`（若已跑 **product-research-agent**）、外源摘要（若有）。
- 事实以 `processing.json` 的 **`key_facts`** 与**可核验的官方来源**为准；`briefing.md` 是扫读用，不可替代 processing 作为唯一事实源。

## TTS

- `{DATE}-article.md` 为 **口播/TTS 唯一母本**。
- 勿另存与 `article.md` **同用途**的平行第二篇对话长文。

## 与生成脚本的协同

大改话轮规则时，建议同步检查 `build_article_dialogue()` 的系统 prompt，避免脚本产出与 skill 要求长期分叉。
