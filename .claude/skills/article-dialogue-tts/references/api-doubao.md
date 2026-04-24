# 豆包语音合成大模型 HTTP V3（单向流式）

## 官方文档

- V3 能力总览（含 WebSocket 双向等）：<https://www.volcengine.com/docs/6561/1329505?lang=zh>
- **HTTP Chunked / SSE 单向流式-V3**（本仓库实现所依）：<https://www.volcengine.com/docs/6561/1598757?lang=zh>
- 大模型音色列表：<https://www.volcengine.com/docs/6561/1257544?lang=zh>
- 控制台 API Key：<https://www.volcengine.com/docs/6561/2119699?lang=zh>

## 本仓库实现

- 模块：`tools/article_tts/doubao_http.py`
- 入口：`python -m tools.article_tts`
- 请求：`POST https://openspeech.bytedance.com/api/v3/tts/unidirectional`
- 鉴权（与文档 2.1 节一致，**二选一**）：
  - **新版控制台**：`X-Api-Key` + `X-Api-Resource-Id`（必填）
  - **旧版控制台**：`X-Api-App-Id` + `X-Api-Access-Key` + `X-Api-Resource-Id`
- 请求体：`user.uid` + `req_params.text` / `req_params.speaker` / `req_params.audio_params`（`format`、`sample_rate`、`speech_rate`、`loudness_rate` 等）
- 响应：多行 JSON（或带 `data:` 前缀的 SSE 行），逐行解析 `code`；`data` 为 base64 音频片段；`code == 20000000` 表示会话成功结束

## 依赖

- `requests`（见 `requirements.txt`）
- 分段 MP3 合并：`imageio-ffmpeg`（随包提供 ffmpeg 可执行文件，`merge_ffmpeg_concat`），见 `tools/tts_dialogue/merge_audio.py`

## 常见错误（摘自文档错误码表）

| code / message | 说明 |
|----------------|------|
| `20000000` | 合成结束成功 |
| `40402003` | 文本超长 |
| `45000000` | 音色未授权或 `speaker` 错误 |
| `55000000` + `resource ID is mismatched with speaker` | **`X-Api-Resource-Id` 与 `speaker` 产品线不一致**（例如 `seed-tts-2.0` 下混用 `*_uranus_bigtts` 与 `*_moon_bigtts`）；请改用音色列表中同一模型线下的 ID |
| （并发类 message） | 并发超限，需降并发或增购 |
