"""真实 TTS 触发与查询服务。"""

from __future__ import annotations

import re
import subprocess
import threading
import uuid
from pathlib import Path

from tools.tts_paths import audio_output_path

from app.services import job_store

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _run_tts_worker(job_id: str, date: str) -> None:
    """后台执行 article_tts 并回写状态。"""
    cmd = ["python3", "-m", "tools.article_tts", "--date", date]
    try:
        proc = subprocess.run(
            cmd,
            cwd=Path(__file__).resolve().parents[2],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            stdout = (proc.stdout or "").strip()
            detail = stderr or stdout or f"退出码 {proc.returncode}"
            job_store.finish_job(
                job_id=job_id,
                status="failed",
                message=f"TTS 失败：{detail[-800:]}",
                audio_url=None,
            )
            return

        out = audio_output_path("dialogue-doubao", date)
        if out.exists():
            job_store.finish_job(
                job_id=job_id,
                status="success",
                message="语音生成完成",
                audio_url=f"/api/audio/{date}",
            )
            return
        job_store.finish_job(
            job_id=job_id,
            status="failed",
            message="TTS 执行完成但未找到输出音频",
            audio_url=None,
        )
    except Exception as exc:  # noqa: BLE001
        job_store.finish_job(
            job_id=job_id,
            status="failed",
            message=f"TTS 异常：{exc}",
            audio_url=None,
        )


def start_tts_job(date: str) -> dict:
    """启动日期对应的 TTS 任务。"""
    if not DATE_RE.match(date):
        raise ValueError("日期格式错误，应为 YYYY-MM-DD")

    running = job_store.get_running_job_for_date(date)
    if running:
        return job_store.to_dict(running)

    job_id = uuid.uuid4().hex
    state = job_store.create_job(job_id=job_id, date=date, message="任务已启动")
    t = threading.Thread(target=_run_tts_worker, args=(job_id, date), daemon=True)
    t.start()
    return job_store.to_dict(state)


def get_tts_status(date: str, job_id: str) -> dict:
    """查询指定 job_id 状态。"""
    state = job_store.get_job(job_id)
    if not state or state.date != date:
        raise KeyError("任务不存在")
    return job_store.to_dict(state)
