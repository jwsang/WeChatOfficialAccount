from app.api.ai_assist_routes import router as ai_assist_router
from app.api.article_routes import router as article_router
from app.api.auth_routes import router as auth_router
from app.api.crawl_routes import router as crawl_router
from app.api.history_routes import router as history_router
from app.api.material_routes import router as material_router
from app.api.model_config_routes import router as model_config_router
from app.api.site_routes import router as site_router

__all__ = [
    "ai_assist_router",
    "article_router",
    "auth_router",
    "crawl_router",
    "history_router",
    "material_router",
    "model_config_router",
    "site_router"
]