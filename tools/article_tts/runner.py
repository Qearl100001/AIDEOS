"""从 `*-article.md` 解析 Q/A，豆包语音合成大模型 V3 分段合成并合并为单 MP3。"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

from tools.article_tts.doubao_http import synthesize_text_to_mp3
from tools.article_tts.text_chunks import utf8_byte_chunks
from tools.tts_dialogue.merge_audio import filter_good_segments, merge_ffmpeg_concat
from tools.tts_dialogue.parse import clean_segment_strip_role, parse_dialogues
from tools.tts_paths import article_md_path, audio_output_path, default_date

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")


def pick_voice_q_a(speaker: str, voice_q: str, voice_a: str) -> str:
    """Q / Qearl → 男声，A → 女声（与 briefing-article-style 话轮一致）。"""
    u = speaker.strip().upper()
    if u == "Q" or u == "QEARL" or "QEARL" in u:
        return voice_q
    if u == "A":
        return voice_a
    return voice_a


def _strip_env_cred(raw: str) -> str:
    """去掉首尾空白、BOM、ASCII/中文成对引号。"""
    s = raw.strip().strip("\ufeff")
    pairs = (
        ('"', '"'),
        ("'", "'"),
        ("\u201c", "\u201d"),
        ("\u2018", "\u2019"),
    )
    for a, b in pairs:
        if len(s) >= 2 and s.startswith(a) and s.endswith(b):
            s = s[len(a) : -len(b)].strip()
    return s


def load_doubao_config() -> tuple[
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    int,
    int,
    int,
]:
    """api_key, app_id, access_token, resource_id, voice_q, voice_a, uid, speech_rate, loudness_rate, sample_rate。"""
    api_key = _strip_env_cred(os.environ.get("DOUBAO_API_KEY", ""))
    app_id = _strip_env_cred(os.environ.get("DOUBAO_APP_ID", ""))
    access_token = _strip_env_cred(os.environ.get("DOUBAO_ACCESS_TOKEN", ""))
    resource_id = _strip_env_cred(
        os.environ.get("DOUBAO_RESOURCE_ID", "seed-tts-2.0")
    )
    voice_q = _strip_env_cred(
        os.environ.get("DOUBAO_VOICE_Q", "zh_male_m191_uranus_bigtts")
    )
    voice_a = _strip_env_cred(
        os.environ.get("DOUBAO_VOICE_A", "zh_female_shuangkuaisisi_moon_bigtts")
    )
    uid = _strip_env_cred(os.environ.get("DOUBAO_UID", "dfos-article-tts"))
    try:
        speech_rate = int(os.environ.get("DOUBAO_SPEECH_RATE", "0"))
    except ValueError:
        speech_rate = 0
    try:
        loudness_rate = int(os.environ.get("DOUBAO_LOUDNESS_RATE", "0"))
    except ValueError:
        loudness_rate = 0
    try:
        sample_rate = int(os.environ.get("DOUBAO_SAMPLE_RATE", "24000"))
    except ValueError:
        sample_rate = 24000

    if api_key:
        pass
    elif app_id and access_token:
        pass
    else:
        print(
            "[article_tts] 请配置：DOUBAO_API_KEY（新版控制台），"
            "或同时设置 DOUBAO_APP_ID + DOUBAO_ACCESS_TOKEN（旧版）；"
            "并设置 DOUBAO_RESOURCE_ID（如 seed-tts-2.0）",
            file=sys.stderr,
        )
        sys.exit(1)

    return (
        api_key,
        app_id,
        access_token,
        resource_id,
        voice_q,
        voice_a,
        uid,
        speech_rate,
        loudness_rate,
        sample_rate,
    )


def synthesize_segment_files(
    segments: list[tuple[str, str]],
    seg_dir: Path,
    api_key: str,
    app_id: str,
    access_token: str,
    resource_id: str,
    voice_q: str,
    voice_a: str,
    uid: str,
    speech_rate: int,
    loudness_rate: int,
    sample_rate: int,
    session: requests.Session,
) -> list[Path]:
    paths: list[Path] = []
    for i, (speaker, raw) in enumerate(segments):
        text = clean_segment_strip_role(raw)
        if not text.strip():
            continue
        speaker_id = pick_voice_q_a(speaker, voice_q, voice_a)
        sub_chunks = utf8_byte_chunks(text, max_bytes=4000)
        if len(sub_chunks) == 1:
            out = seg_dir / f"seg_{i:04d}.mp3"
            data = synthesize_text_to_mp3(
                api_key=api_key,
                app_id=app_id,
                access_token=access_token,
                resource_id=resource_id,
                text=sub_chunks[0],
                speaker=speaker_id,
                uid=uid,
                speech_rate=speech_rate,
                loudness_rate=loudness_rate,
                sample_rate=sample_rate,
                session=session,
            )
            out.write_bytes(data)
            paths.append(out)
            print(f"  [{i+1}/{len(segments)}] {speaker} ({speaker_id}): {text[:48]}…")
        else:
            sub_paths: list[Path] = []
            for j, chunk in enumerate(sub_chunks):
                sub = seg_dir / f"seg_{i:04d}_p{j:02d}.mp3"
                sub.write_bytes(
                    synthesize_text_to_mp3(
                        api_key=api_key,
                        app_id=app_id,
                        access_token=access_token,
                        resource_id=resource_id,
                        text=chunk,
                        speaker=speaker_id,
                        uid=uid,
                        speech_rate=speech_rate,
                        loudness_rate=loudness_rate,
                        sample_rate=sample_rate,
                        session=session,
                    )
                )
                sub_paths.append(sub)
                time.sleep(0.2)
            merged = seg_dir / f"seg_{i:04d}.mp3"
            merge_ffmpeg_concat(sub_paths, merged)
            for p in sub_paths:
                p.unlink(missing_ok=True)
            paths.append(merged)
            print(
                f"  [{i+1}/{len(segments)}] {speaker} ({speaker_id}) 多段合并: {text[:48]}…"
            )
        time.sleep(0.25)
    return paths


def run_article_tts(
    date_str: str | None = None, output_stem: str = "dialogue-doubao"
) -> Path:
    d = date_str or default_date()
    md_path = article_md_path(d)
    if not md_path.is_file():
        print(f"[article_tts] 未找到口播母本: {md_path}", file=sys.stderr)
        sys.exit(1)

    (
        api_key,
        app_id,
        access_token,
        resource_id,
        voice_q,
        voice_a,
        uid,
        speech_rate,
        loudness_rate,
        sample_rate,
    ) = load_doubao_config()
    text = md_path.read_text(encoding="utf-8")
    matches = parse_dialogues(text)
    print(f"[article_tts] 输入: {md_path}")
    print(
        f"[article_tts] resource_id={resource_id}，Q speaker={voice_q}，A speaker={voice_a}"
    )
    print(f"[article_tts] 解析到 {len(matches)} 段对话")
    if not matches:
        print("[article_tts] 未解析到 **角色**: 段落，退出", file=sys.stderr)
        sys.exit(2)

    seg_dir = Path(tempfile.mkdtemp(prefix="dfos-article-tts-"))
    session = requests.Session()
    try:
        seg_paths = synthesize_segment_files(
            matches,
            seg_dir,
            api_key,
            app_id,
            access_token,
            resource_id,
            voice_q,
            voice_a,
            uid,
            speech_rate,
            loudness_rate,
            sample_rate,
            session,
        )
        good, bad = filter_good_segments(seg_paths)
        print(f"[article_tts] 有效分段: {len(good)}，失败/过小: {len(bad)}")
        if not good:
            print("[article_tts] 没有可用分段", file=sys.stderr)
            sys.exit(3)
        final_out = audio_output_path(output_stem, d)
        merge_ffmpeg_concat(good, final_out)
        print(f"[article_tts] 已写入: {final_out}")
        mb = final_out.stat().st_size / 1024 / 1024
        print(f"[article_tts] 约 {mb:.1f} MB")
        return final_out
    finally:
        session.close()
        for p in seg_dir.glob("*"):
            p.unlink(missing_ok=True)
        seg_dir.rmdir()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="article.md → 豆包 V3 双音色口播 → 单文件 MP3",
    )
    p.add_argument(
        "--date",
        dest="date",
        default=None,
        help="YYYY-MM-DD（默认当天或 BRIEFING_DATE）",
    )
    p.add_argument(
        "--output-stem",
        default="dialogue-doubao",
        help="输出 data/output/{DATE}-{stem}.mp3 的文件名中段",
    )
    args = p.parse_args(argv)
    run_article_tts(args.date, args.output_stem)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
