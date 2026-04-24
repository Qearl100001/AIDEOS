# 你需要提供什么（给助手或自己配置）

以下内容**不要发密钥原文到聊天或提交到 Git**；只在本地终端或 CI Secret 中配置。

## 必配（火山引擎豆包语音 · 语音合成大模型 V3）

实现遵循 [V3 文档总览](https://www.volcengine.com/docs/6561/1329505?lang=zh) 与 [HTTP 单向流式说明](https://www.volcengine.com/docs/6561/1598757?lang=zh)。

**鉴权二选一：**

| 环境变量 | 含义 |
|----------|------|
| `DOUBAO_API_KEY` | 新版控制台 **API Key**（对应请求头 `X-Api-Key`） |
| `DOUBAO_APP_ID` + `DOUBAO_ACCESS_TOKEN` | 旧版控制台 **AppId** + **Access Key**（`X-Api-App-Id`、`X-Api-Access-Key`） |

| 环境变量 | 含义 |
|----------|------|
| `DOUBAO_RESOURCE_ID` | **资源 ID**，决定模型版本与计费，如 `seed-tts-2.0`、`seed-tts-1.0`（须与音色列表一致） |

## 选配

| 环境变量 | 含义 | 默认（示例，以控制台与 [音色列表](https://www.volcengine.com/docs/6561/1257544?lang=zh) 为准） |
|----------|------|---------------------------|
| `DOUBAO_VOICE_Q` | **Q**（男声）`req_params.speaker` | `zh_male_m191_uranus_bigtts` |
| `DOUBAO_VOICE_A` | **A**（女声）`req_params.speaker` | `zh_female_shuangkuaisisi_uranus_bigtts`（与默认 Q 同属 `uranus` 线，勿与 `moon` 混用） |
| `DOUBAO_UID` | `user.uid` | `dfos-article-tts` |
| `DOUBAO_SPEECH_RATE` | 语速 [-50, 100] | `0` |
| `DOUBAO_LOUDNESS_RATE` | 音量 [-50, 100] | `0` |
| `DOUBAO_SAMPLE_RATE` | 采样率，如 24000 | `24000` |

若报 `45000000` 或音色相关错误，请核对 **`DOUBAO_RESOURCE_ID` 与 `speaker` 是否同属 1.0 或 2.0 音色列表**。

## 日期

| 环境变量 / 参数 | 含义 |
|------------------|------|
| `BRIEFING_DATE` | `YYYY-MM-DD`，与文章文件名日期一致 |
| `python -m tools.article_tts --date YYYY-MM-DD` | 同上 |

## 给助手时建议怎么说

- 「已在本机配置好 `DOUBAO_API_KEY`（或 AppId+Token）与 `DOUBAO_RESOURCE_ID`，请跑 `python -m tools.article_tts --date …`」
- **只发音色 `speaker` 名称，不要发 Key**
