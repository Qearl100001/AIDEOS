"""FastAPI 入口。"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import WEB_DIST_DIR
from app.routers import api_article, api_briefing, api_tts, pages

app = FastAPI(title="DFOS Web")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/dist", StaticFiles(directory=str(WEB_DIST_DIR)), name="dist")

app.include_router(pages.router)
app.include_router(api_briefing.router, prefix="/api", tags=["briefing"])
app.include_router(api_article.router, prefix="/api", tags=["article"])
app.include_router(api_tts.router, prefix="/api", tags=["tts"])
