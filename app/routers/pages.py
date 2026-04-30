"""页面路由。"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.briefing_sidebar_meta import sidebar_meta_map
from app.services.date_index import list_dates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def page_index(request: Request):
    """首页：左侧日期、右侧简报。"""
    dates = list_dates()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "dates": dates,
            "date_meta": sidebar_meta_map(dates),
            "initial_date": dates[0] if dates else None,
        },
    )


@router.get("/article/{date}", response_class=HTMLResponse)
def page_article(request: Request, date: str):
    """结构化文章页面。"""
    return templates.TemplateResponse(
        request=request,
        name="article.html",
        context={"request": request, "date": date},
    )
