# 发音人（`req_params.speaker`）与 Q/A 映射

## 规则

- **`Q`**：环境变量 **`DOUBAO_VOICE_Q`**
- **`A`**：环境变量 **`DOUBAO_VOICE_A`**
- 历史话轮 **`Qearl`** 与 **`Q`** 相同，走男声配置

`speaker` 必须与 **`DOUBAO_RESOURCE_ID`** 匹配（例如 `seed-tts-2.0` 仅可选用「豆包语音合成模型 2.0」音色，见 [音色列表](https://www.volcengine.com/docs/6561/1257544?lang=zh)）。

## 如何更换

1. 在控制台确认已开通的资源与 **`X-Api-Resource-Id`**
2. 在文档音色表中复制对应的 **`speaker`** 字符串
3. 写入 `DOUBAO_VOICE_Q` / `DOUBAO_VOICE_A`
