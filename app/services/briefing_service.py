"""日报读取服务。"""

from app.config import BRIEFING_HTML_DIR


def get_briefing_html(date: str) -> str:
    """读取指定日期的简报 HTML。"""
    path = BRIEFING_HTML_DIR / f"{date}.html"
    if not path.exists():
        raise FileNotFoundError(f"未找到该日期日报: {date}")

    return path.read_text(encoding="utf-8")
