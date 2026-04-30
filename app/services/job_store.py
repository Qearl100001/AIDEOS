"""TTS 任务状态内存存储。"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from threading import Lock
from time import time
from typing import Any


@dataclass
class JobState:
    """任务状态。"""

    job_id: str
    date: str
    status: str
    message: str
    audio_url: str | None
    started_at: float
    finished_at: float | None = None


_LOCK = Lock()
_JOBS: dict[str, JobState] = {}
_DATE_RUNNING: dict[str, str] = {}


def create_job(job_id: str, date: str, message: str) -> JobState:
    """创建 running 任务。"""
    state = JobState(
        job_id=job_id,
        date=date,
        status="running",
        message=message,
        audio_url=None,
        started_at=time(),
    )
    with _LOCK:
        _JOBS[job_id] = state
        _DATE_RUNNING[date] = job_id
    return state


def get_job(job_id: str) -> JobState | None:
    """按 job_id 获取任务。"""
    with _LOCK:
        return _JOBS.get(job_id)


def get_running_job_for_date(date: str) -> JobState | None:
    """获取日期对应 running 任务。"""
    with _LOCK:
        job_id = _DATE_RUNNING.get(date)
        return _JOBS.get(job_id) if job_id else None


def finish_job(job_id: str, status: str, message: str, audio_url: str | None) -> None:
    """结束任务并写入结果。"""
    with _LOCK:
        state = _JOBS.get(job_id)
        if not state:
            return
        state.status = status
        state.message = message
        state.audio_url = audio_url
        state.finished_at = time()
        _DATE_RUNNING.pop(state.date, None)


def to_dict(state: JobState) -> dict[str, Any]:
    """状态对象转字典。"""
    return asdict(state)
