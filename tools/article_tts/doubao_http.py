"""豆包语音合成大模型 HTTP V3 单向流式接口（Chunked JSON 行）。

与文档 [语音合成大模型 · WebSocket V3 总览](https://www.volcengine.com/docs/6561/1329505?lang=zh)
同属 V3；HTTP 请求/响应格式见
[HTTP Chunked/SSE 单向流式-V3](https://www.volcengine.com/docs/6561/1598757?lang=zh)。

- 地址：`POST https://openspeech.bytedance.com/api/v3/tts/unidirectional`
- 鉴权（二选一）：`X-Api-Key` + `X-Api-Resource-Id`，或
  `X-Api-App-Id` + `X-Api-Access-Key` + `X-Api-Resource-Id`
"""
from __future__ import annotations

import base64
import json
import uuid
from typing import Any

import requests

TTS_V3_URL = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"


def _v3_headers(
    *,
    api_key: str,
    app_id: str,
    access_token: str,
    resource_id: str,
) -> dict[str, str]:
    h: dict[str, str] = {
        "Content-Type": "application/json",
        "X-Api-Resource-Id": resource_id,
        "X-Api-Request-Id": str(uuid.uuid4()),
    }
    if api_key:
        h["X-Api-Key"] = api_key
    else:
        h["X-Api-App-Id"] = app_id
        h["X-Api-Access-Key"] = access_token
    return h


def _parse_v3_line(line: str, audio_parts: list[bytes]) -> None:
    line = line.strip()
    if not line:
        return
    if line.startswith("event:"):
        return
    if line.startswith("data:"):
        line = line[5:].strip()
    obj: dict[str, Any] = json.loads(line)
    code = obj.get("code")
    if code is not None and code != 0 and code != 20000000:
        raise RuntimeError(
            f"[article_tts] 豆包 V3 错误 code={code} message={obj.get('message')!r}"
        )
    if code == 20000000:
        return
    data = obj.get("data")
    if isinstance(data, str) and data:
        audio_parts.append(base64.b64decode(data))


def _consume_v3_body(body: str, audio_parts: list[bytes]) -> None:
    """解析整段响应文本（多行 JSON 或 SSE）。"""
    for raw_line in body.splitlines():
        s = raw_line.strip()
        if not s:
            continue
        try:
            _parse_v3_line(s, audio_parts)
        except json.JSONDecodeError:
            continue


def synthesize_text_to_mp3(
    *,
    api_key: str,
    app_id: str,
    access_token: str,
    resource_id: str,
    text: str,
    speaker: str,
    uid: str = "dfos-article-tts",
    speech_rate: int = 0,
    loudness_rate: int = 0,
    sample_rate: int = 24000,
    session: requests.Session | None = None,
    timeout_sec: int = 180,
) -> bytes:
    """单次会话合成一段文本，返回 MP3 二进制。"""
    if not text.strip():
        return b""

    payload: dict[str, Any] = {
        "user": {"uid": uid},
        "req_params": {
            "text": text,
            "speaker": speaker,
            "audio_params": {
                "format": "mp3",
                "sample_rate": sample_rate,
                "speech_rate": speech_rate,
                "loudness_rate": loudness_rate,
            },
        },
    }

    sess = session or requests.Session()
    headers = _v3_headers(
        api_key=api_key,
        app_id=app_id,
        access_token=access_token,
        resource_id=resource_id,
    )

    r = sess.post(
        TTS_V3_URL,
        headers=headers,
        json=payload,
        stream=True,
        timeout=timeout_sec,
    )

    if r.status_code >= 400:
        try:
            detail = r.json()
        except json.JSONDecodeError:
            detail = r.text[:800]
        raise RuntimeError(
            f"[article_tts] 豆包 V3 HTTP {r.status_code}: {detail!r}"
        )

    buf = bytearray()
    try:
        for chunk in r.iter_content(chunk_size=65536):
            if chunk:
                buf.extend(chunk)
    finally:
        r.close()

    try:
        body_text = buf.decode("utf-8")
    except UnicodeDecodeError as e:
        raise RuntimeError("[article_tts] 豆包 V3 响应非 UTF-8 文本") from e

    audio_parts: list[bytes] = []
    _consume_v3_body(body_text, audio_parts)
    if audio_parts:
        return b"".join(audio_parts)

    raise RuntimeError("[article_tts] 豆包 V3 响应中未解析到音频数据")
