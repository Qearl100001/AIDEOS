"""分段 MP3 合并：优先使用 imageio-ffmpeg 自带的 ffmpeg 做 concat（无需系统 PATH 中的 ffmpeg）。

兜底：`merge_mp3_segments` 二进制拼接（同编码 TTS 分段时可用）。
"""
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


def _ffmpeg_exe() -> str:
    """imageio-ffmpeg 随包提供的 ffmpeg 可执行文件路径。"""
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def merge_mp3_segments(segment_paths: list[Path], output_mp3: Path) -> None:
    """将多段 MP3 按顺序写入同一文件（标准库二进制拼接）。"""
    if not segment_paths:
        raise ValueError("无有效分段，无法合并")

    with open(output_mp3, "wb") as out:
        for p in segment_paths:
            with open(p, "rb") as inp:
                out.write(inp.read())


def merge_ffmpeg_concat(segment_paths: list[Path], output_mp3: Path) -> None:
    """ffmpeg concat demuxer（`-c copy`），可执行文件来自 `imageio-ffmpeg`。"""
    if not segment_paths:
        raise ValueError("无有效分段，无法合并")

    ffmpeg = _ffmpeg_exe()
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        encoding="utf-8",
    ) as list_file:
        for p in segment_paths:
            ap = str(p.resolve()).replace("'", "'\\''")
            list_file.write(f"file '{ap}'\n")
        list_path = Path(list_file.name)

    try:
        proc = subprocess.run(
            [
                ffmpeg,
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
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"ffmpeg concat 失败 (code={proc.returncode}): "
                f"{(proc.stderr or proc.stdout or '')[:800]}"
            )
    finally:
        list_path.unlink(missing_ok=True)


def merge_moviepy(segment_paths: list[Path], output_mp3: Path, fps: int = 44100) -> None:
    """兼容旧名；与 `merge_ffmpeg_concat` 相同，使用 imageio-ffmpeg。`fps` 保留签名，未使用。"""
    _ = fps
    merge_ffmpeg_concat(segment_paths, output_mp3)
