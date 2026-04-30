"""日期索引服务。"""

import re
from app.config import BRIEFING_HTML_DIR

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def list_dates() -> list[str]:
    """扫描可用日报日期并按倒序返回。"""
    if not BRIEFING_HTML_DIR.exists():
        return []

    dates = [p.stem for p in BRIEFING_HTML_DIR.glob("*.html") if DATE_RE.match(p.stem)]
    return sorted(set(dates), reverse=True)
