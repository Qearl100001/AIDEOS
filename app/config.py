"""Web 端配置。"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BRIEFING_HTML_DIR = BASE_DIR / "web" / "dist" / "briefing"
WEB_DIST_DIR = BASE_DIR / "web" / "dist"
OUTPUT_DIR = BASE_DIR / "data" / "output"
