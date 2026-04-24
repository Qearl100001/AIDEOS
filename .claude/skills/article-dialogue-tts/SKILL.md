---
name: article-dialogue-tts
description: >-
  DFOS 步骤 4：将 data/output/{DATE}-article.md（Q/A 对话口播母本）按 Q 男声、A 女声
  调用豆包语音（火山引擎）HTTP TTS，合并为单个 MP3。触发词：口播、TTS、语音合成、article 音频、
  对话录音、豆包、火山、步骤 4、dialogue-briefing、DOUBAO。勿用 briefing.md 当母本。
---

# Article Dialogue TTS（结构化长文 → 双音色 → 单 MP3）

## 目录结构

| 路径 | 用途 |
|------|------|
| `SKILL.md` | 唯一入口（本文件） |
| `references/api-doubao.md` | 豆包鉴权、环境变量、官方文档链接 |
| `references/paths.md` | 与 `tools/tts_paths.py` 一致的路径约定 |
| `references/voices.md` | `speaker`、Q/A 映射 |
| `examples/article-snippet.md` | 母本话轮格式示例 |
| `scripts/synthesize_article.py` | 可执行封装（项目根运行） |

## 何时使用

- 已完成 **`data/output/{DATE}-article.md`**（步骤 3，体裁见 `briefing-article-style`）
- 用户要 **整篇对话口播**、**豆包/火山合成**、**一个完整 MP3**
- 用户提到 **步骤 4**、**dialogue-briefing**、**DOUBAO**、**豆包语音**

## 主命令（项目根目录）

```bash
pip install -r requirements.txt

# 新版控制台（推荐）：API Key + 资源 ID，见
# https://www.volcengine.com/docs/6561/1329505?lang=zh
export DOUBAO_API_KEY="你的 API Key"
export DOUBAO_RESOURCE_ID="seed-tts-2.0"

# 或使用旧版：AppId + Access Key
# export DOUBAO_APP_ID="..."
# export DOUBAO_ACCESS_TOKEN="..."

export DOUBAO_VOICE_Q="zh_male_m191_uranus_bigtts"
export DOUBAO_VOICE_A="zh_female_shuangkuaisisi_uranus_bigtts"

python -m tools.article_tts
# 或指定日期
BRIEFING_DATE=2026-04-21 python -m tools.article_tts --date 2026-04-21
```

等价脚本入口：

```bash
python .claude/skills/article-dialogue-tts/scripts/synthesize_article.py --date 2026-04-21
```

## 输出

- `data/output/{DATE}-dialogue-doubao.mp3`（默认 `--output-stem dialogue-doubao`）

## 你必须遵守

- **唯一母本**：`{DATE}-article.md`；**禁止**用 `briefing.md` 替代或再写一篇平行长对话当主稿。
- **话轮格式**：`**Q**：` / **`A**：`（与 `briefing-article-style` 一致）；解析规则与 `tools/tts_dialogue/parse.py` 相同。
- **密钥**：只通过环境变量注入，**勿**写入仓库、**勿**贴进聊天。
- **备用方案**：无豆包密钥时，可仍用 `python -m tools.tts_dialogue --preset edge`（Edge TTS）。

## 你需要向助手 / 开发提供的信息

详见 [references/what-you-provide.md](references/what-you-provide.md)。

## 深入阅读

- [references/api-doubao.md](references/api-doubao.md)
- [references/paths.md](references/paths.md)
- [references/voices.md](references/voices.md)
