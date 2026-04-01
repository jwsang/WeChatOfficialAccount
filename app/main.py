import os
import sys

from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

if __name__ == "__main__" and __package__ is None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from app.api.article_routes import legacy_router as article_legacy_router
from app.api.article_routes import router as article_router
from app.api.auth_routes import router as auth_router
from app.api.crawl_routes import router as crawl_router
from app.api.history_routes import router as history_router
from app.api.material_routes import router as material_router
from app.api.ai_assist_routes import router as ai_assist_router
from app.api.site_routes import router as site_router
from app.core.config import DATA_DIR, STATIC_DIR, TEMPLATE_DIR, settings
from app.db.session import SessionLocal, engine
from app.models import Base
from app.services.user_service import UserService


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="0.4.0")
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret, same_site="lax")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")
templates = Jinja2Templates(directory=TEMPLATE_DIR)
app.include_router(auth_router)
app.include_router(site_router)
app.include_router(crawl_router)
app.include_router(material_router)
app.include_router(ai_assist_router)
app.include_router(article_router)
app.include_router(article_legacy_router)
app.include_router(history_router)

with SessionLocal() as _db:
    UserService(_db).ensure_default_admin()


def is_authenticated(request: Request) -> bool:
    return bool(request.session.get("user_id"))


def render_page(request: Request, name: str, page: str):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request=request,
        name=name,
        context={"app_name": settings.app_name, "page": page},
    )


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"app_name": settings.app_name, "page": "login"},
    )


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return render_page(request, "history.html", "history")


@app.get("/sites", response_class=HTMLResponse)
def sites_page(request: Request):
    return render_page(request, "sites.html", "sites")


@app.get("/crawl", response_class=HTMLResponse)
def crawl_page(request: Request):
    return render_page(request, "crawl.html", "crawl")


@app.get("/ai-assist", response_class=HTMLResponse)
def ai_assist_page(request: Request):
    return render_page(request, "ai_assist.html", "ai_assist")


@app.get("/materials", response_class=HTMLResponse)
def materials_page(request: Request):
    return render_page(request, "materials.html", "materials")


@app.get("/articles", response_class=HTMLResponse)
def articles_page(request: Request):
    return render_page(request, "articles.html", "articles")


@app.get("/drafts", response_class=HTMLResponse)
def drafts_page(request: Request):
    return render_page(request, "drafts.html", "drafts")


@app.get("/history", response_class=HTMLResponse)
def history_page(request: Request):
    return render_page(request, "history.html", "history")


@app.get("/account", response_class=HTMLResponse)
def account_page(request: Request):
    return render_page(request, "account.html", "account")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=False,
    )
