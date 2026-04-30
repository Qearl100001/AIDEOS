"""结构化文章 API。"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.article_service import get_article_markdown, render_article_html
from app.services.briefing_sidebar_meta import sidebar_meta_for_date

router = APIRouter()


class GenerateArticleRequest(BaseModel):
    date: str


@router.post("/article")
def generate_article(req: GenerateArticleRequest) -> dict:
    """触发生成指定日期的结构化文章。"""
    import subprocess
    import os

    date = req.date
    meta = sidebar_meta_for_date(date)
    if not meta.get("has_deep_dive"):
        raise HTTPException(
            status_code=400,
            detail="该日简报没有深挖条目，无法生成对话式文章",
        )

    env = os.environ.copy()
    env["BRIEFING_DATE"] = date

    try:
        result = subprocess.run(
            ["python3", "-m", "tools.generate_article", "--date", date],
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            capture_output=True,
            text=True,
            env=env,
            timeout=180,
        )
        if result.returncode != 0:
            raise Exception(result.stderr or "生成失败")
        return {"date": date, "status": "ok", "message": "文章已生成"}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="生成超时")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/article/{date}")
def api_article(date: str) -> dict:
    """返回指定日期结构化文章。"""
    try:
        md_text = get_article_markdown(date)
        return {
            "date": date,
            "raw_markdown": md_text,
            "rendered_html": render_article_html(md_text),
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
