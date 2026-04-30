"""简报相关 API。"""

from fastapi import APIRouter, HTTPException

from app.services.briefing_service import get_briefing_html
from app.services.date_index import list_dates

router = APIRouter()


@router.get("/dates")
def api_dates() -> dict:
    """返回可用日期列表。"""
    dates = list_dates()
    return {"dates": dates, "latest": dates[0] if dates else None}


@router.get("/briefing/{date}")
def api_briefing(date: str) -> dict:
    """返回指定日期简报 HTML。"""
    try:
        html = get_briefing_html(date)
        return {"date": date, "html": html}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
