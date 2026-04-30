"""TTS API。"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from tools.tts_paths import audio_output_path

from app.services.tts_service import get_tts_status, start_tts_job

router = APIRouter()

# 首页播放器优先豆包产出；本地流水线若仅用 Edge，则回退到 dialogue-edge
_AUDIO_FALLBACK_STEMS = ("dialogue-doubao", "dialogue-edge")


def _resolved_audio_path(date: str):
    """返回当日第一个存在的口播 MP3（路径或 None）。"""
    for stem_suffix in _AUDIO_FALLBACK_STEMS:
        p = audio_output_path(stem_suffix, date)
        if p.is_file():
            return p
    return None

@router.post("/tts/{date}")
def api_tts_start(date: str) -> dict:
    """触发 TTS。"""
    try:
        return start_tts_job(date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/tts/{date}/status")
def api_tts_status(date: str, job_id: str) -> dict:
    """查询 TTS 状态。"""
    try:
        return get_tts_status(date, job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/audio/{date}/meta")
def api_audio_meta(date: str) -> dict:
    """查询当日口播 MP3 是否已存在（豆包优先，其次 Edge 等）。"""
    audio_path = _resolved_audio_path(date)
    exists = audio_path is not None
    return {
        "exists": exists,
        "filename": audio_path.name if audio_path else None,
        "stem": audio_path.stem.replace(f"{date}-", "", 1) if audio_path else None,
    }


@router.get("/audio/{date}")
def api_audio(date: str):
    """返回已生成音频文件。"""
    audio_path = _resolved_audio_path(date)
    if audio_path is None:
        raise HTTPException(
            status_code=404,
            detail="未找到当日口播音频（dialogue-doubao / dialogue-edge）",
        )
    return FileResponse(path=audio_path, media_type="audio/mpeg", filename=audio_path.name)
