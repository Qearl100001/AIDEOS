"""端到端编排：抓取→简报与 HTML→对话 article→口播 MP3。

默认串联 `pipeline.main` → `tools.generate_article` → TTS（豆包优先，失败或未配置时可 Edge）。

产出与网页：
  - 简报：`web/dist/briefing/{DATE}.html`（首页侧边栏按此扫描日期）
  - 文章与音频：`data/output/{DATE}-article.md`、`{DATE}-dialogue-*.mp3`
  - 本地预览：`uvicorn app.main:app --reload` 后打开 http://127.0.0.1:8000/

用法：
  python -m tools.run_full_daily
  python -m tools.run_full_daily --skip-scrape --date 2026-04-30
  python -m tools.run_full_daily --tts-backend edge
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _run_step(label: str, argv: list[str]) -> None:
    print(f"\n{'='*60}\n  [full_daily] {label}\n{'='*60}")
    env = os.environ.copy()
    r = subprocess.run(
        [sys.executable, *argv],
        cwd=str(PROJECT_ROOT),
        env=env,
    )
    if r.returncode != 0:
        raise RuntimeError(f"{label} 失败 (exit {r.returncode})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="全日流水线：简报 + 文章 + 语音（供本地 FastAPI 站点读取）",
    )
    parser.add_argument(
        "--date",
        default=None,
        metavar="YYYY-MM-DD",
        help="业务日期（默认今天）；写入 BRIEFING_DATE",
    )
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="跳过抓取（等同 pipeline.main --skip-scrape）",
    )
    parser.add_argument(
        "--skip-article",
        action="store_true",
        help="不生成对话式 article.md",
    )
    parser.add_argument(
        "--skip-tts",
        action="store_true",
        help="不生成 MP3",
    )
    parser.add_argument(
        "--tts-backend",
        choices=("auto", "doubao", "edge"),
        default="auto",
        help="auto：先试豆包，失败或无密钥则 Edge；doubao/edge：只跑一种",
    )
    args = parser.parse_args(argv)

    date = args.date or _today()
    os.environ["BRIEFING_DATE"] = date

    pipeline_argv = ["-m", "pipeline.main", "--date", date]
    if args.skip_scrape:
        pipeline_argv.append("--skip-scrape")

    try:
        _run_step("步骤 1～2：抓取与简报（含 HTML）", pipeline_argv)

        if not args.skip_article:
            _run_step(
                "步骤 3：对话式 article.md",
                ["-m", "tools.generate_article", "--date", date],
            )

        if args.skip_tts:
            print("\n[full_daily] 已跳过 TTS（--skip-tts）")
            return 0

        if args.skip_article:
            print("\n[full_daily] 未生成 article.md，跳过 TTS（请去掉 --skip-article 或手动跑 article_tts）")
            return 0

        if args.tts_backend == "edge":
            _run_step(
                "步骤 4：口播 MP3（Edge）",
                ["-m", "tools.tts_dialogue", "--preset", "edge", "--date", date],
            )
        elif args.tts_backend == "doubao":
            _run_step(
                "步骤 4：口播 MP3（豆包）",
                ["-m", "tools.article_tts", "--date", date],
            )
        else:
            # auto
            r = subprocess.run(
                [sys.executable, "-m", "tools.article_tts", "--date", date],
                cwd=str(PROJECT_ROOT),
                env=os.environ.copy(),
            )
            if r.returncode != 0:
                print(
                    "[full_daily] 豆包 TTS 未成功，改用 Edge preset…",
                    file=sys.stderr,
                )
                _run_step(
                    "步骤 4：口播 MP3（Edge 备选）",
                    ["-m", "tools.tts_dialogue", "--preset", "edge", "--date", date],
                )

        print(f"\n{'='*60}")
        print("  [full_daily] 全部完成")
        print(f"  日期: {date}")
        print(f"  简报页: web/dist/briefing/{date}.html")
        print(f"  文章: data/output/{date}-article.md")
        print(f"  音频（其一即可）: data/output/{date}-dialogue-doubao.mp3 或 …-dialogue-edge.mp3")
        print("  网页: 在项目根执行 uvicorn app.main:app --reload → http://127.0.0.1:8000/")
        print(f"{'='*60}\n")

    except RuntimeError as e:
        print(f"\n[full_daily] ❌ {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
