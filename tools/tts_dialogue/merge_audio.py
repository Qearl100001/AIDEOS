"""分段 mp3 合并：ffmpeg concat 或 moviepy。"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

MIN_BYTES = 1000


def filter_good_segments(paths: list[Path]) -> tuple[list[Path], list[Path]]:
    good: list[Path] = []
    bad: list[Path] = []
    for p in paths:
        if p.exists() and p.stat().st_size > MIN_BYTES:
            good.append(p)
        else:
            bad.append(p)
    return good, bad


def merge_ffmpeg_concat(segment_paths: list[Path], output_mp3: Path) -> None:
    """无损拼接（与旧 `generate_dialogue_audio` 一致）。"""
    if not segment_paths:
        raise ValueError("无有效分段，无法合并")

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        encoding="utf-8",
    ) as list_file:
        for p in segment_paths:
            # ffmpeg concat 需转义单引号
            ap = str(p.resolve()).replace("'", "'\\''")
            list_file.write(f"file '{ap}'\n")
        list_path = Path(list_file.name)

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_path),
                "-c",
                "copy",
                str(output_mp3),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        list_path.unlink(missing_ok=True)


def merge_moviepy(segment_paths: list[Path], output_mp3: Path, fps: int = 44100) -> None:
    """简单 MP3 拼接（二进制合并，MP3 帧独立可直连）。"""
    if not segment_paths:
        raise ValueError("无有效分段，无法合并")

    with open(output_mp3, 'wb') as out:
        for p in segment_paths:
            with open(p, 'rb') as inp:
                out.write(inp.read())
