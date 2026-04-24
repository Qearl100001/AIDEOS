# 音频输出规则（口播母本）

## 文件来源
- 输入：`data/output/{DATE}-article.md`
- 输出：`data/output/{DATE}-dialogue-*.mp3`

---

## 内容清洗规则

### 1. 删除不读的元信息
- ❌ 删除日期标注：`(截至 2026-04-22...)`
- ❌ 删除参考来源整块：参考来源/VentureBeat: .../Anthropic 官方介绍
- ❌ 删除主持人介绍：`**Q**: 主持人...**A**: 嘉宾...`

### 2. 星号处理
- 所有 `**` Markdown 加粗标记不朗读
- 清理规则：去掉所有 `**`后再合成

---

## 语气词规则

### 稀疏添加（每5段加1-2个）

| 角色 | 语气词 | 场景 |
|------|--------|------|
| **Q（男声）** | 「那个」「对的」 | 每5段加1个，有时加认同 |
| **A（女声）** | 「那个」 | 每5段加1个 |

---

## 输出预设

推荐使用 `edge` 预设：
- 稀疏语气词
- 男女双声（Yunxi + Xiaoxiao）
- 适中语速

```bash
python3 -m tools.tts_dialogue --date 2026-04-22 --preset edge
```

---

## 豆包语音配置

- 环境变量：`DOUBAO_APP_ID`、`DOUBAO_ACCESS_TOKEN` 等（见 `article-dialogue-tts` skill）
- 控制台与音色以火山引擎文档为准