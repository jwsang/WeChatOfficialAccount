from pathlib import Path
from textwrap import dedent

BASE = Path(__file__).resolve().parent
FILES: dict[str, str] = {
    "app/__init__.py": "",
    "app/api/__init__.py": "",
    "app/core/__init__.py": "",
    "app/db/__init__.py": "",
    "app/models/__init__.py": dedent(
        '''
        from app.models.base import Base
        from app.models.site_config import SiteConfig
        '''
    ).strip() + "\n",
    "app/repositories/__init__.py": "",
    "app/schemas/__init__.py": "",
    "app/services/__init__.py": "",
    "app/core/config.py": dedent(
        '''
        from pathlib import Path

        import yaml
        from pydantic import Field
        from pydantic_settings import BaseSettings, SettingsConfigDict


        BASE_DIR = Path(__file__).resolve().parents[2]
        CONFIG_FILE = BASE_DIR / "config" / "config.yml"
        DATA_DIR = BASE_DIR / "data"
        STATIC_DIR = BASE_DIR / "app" / "static"
        TEMPLATE_DIR = BASE_DIR / "app" / "templates"


        def load_yaml_config() -> dict:
            if not CONFIG_FILE.exists():
                return {}
            with CONFIG_FILE.open("r", encoding="utf-8") as file:
                return yaml.safe_load(file) or {}


        _yaml_config = load_yaml_config()


        class Settings(BaseSettings):
            app_name: str = "文章素材管理"
            app_env: str = "development"
            debug: bool = True
            database_url: str = Field(
                default=f"sqlite:///{(DATA_DIR / 'app.db').as_posix()}"
            )
            wechat_app_id: str = _yaml_config.get("wechat", {}).get("AppID", "")
            wechat_app_secret: str = _yaml_config.get("wechat", {}).get("AppSecret", "")
            api_key: str = _yaml_config.get("API-Key", "") or _yaml_config.get("API-Key ", "")

            model_config = SettingsConfigDict(
                env_file=".env",
                env_file_encoding="utf-8",
                extra="ignore",
            )


        settings = Settings()

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        STATIC_DIR.mkdir(parents=True, exist_ok=True)
        TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        '''
    ).strip() + "\n",
    "app/db/session.py": dedent(
        '''
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from app.core.config import settings


        connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
        engine = create_engine(settings.database_url, connect_args=connect_args)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
        '''
    ).strip() + "\n",
    "app/models/base.py": dedent(
        '''
        from sqlalchemy.orm import DeclarativeBase


        class Base(DeclarativeBase):
            pass
        '''
    ).strip() + "\n",
    "app/models/site_config.py": dedent(
        '''
        from datetime import datetime

        from sqlalchemy import Boolean, DateTime, Integer, String, Text
        from sqlalchemy.orm import Mapped, mapped_column

        from app.models.base import Base


        class SiteConfig(Base):
            __tablename__ = "site_configs"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            name: Mapped[str] = mapped_column(String(100), nullable=False)
            code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
            domain: Mapped[str] = mapped_column(String(255), nullable=False)
            enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
            search_rule: Mapped[str] = mapped_column(Text, default="", nullable=False)
            parse_rule: Mapped[str] = mapped_column(Text, default="", nullable=False)
            page_rule: Mapped[str] = mapped_column(Text, default="", nullable=False)
            remark: Mapped[str] = mapped_column(Text, default="", nullable=False)
            crawl_method: Mapped[str] = mapped_column(String(100), default="HTML解析", nullable=False)
            last_crawled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
            created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
            updated_at: Mapped[datetime] = mapped_column(
                DateTime,
                default=datetime.utcnow,
                onupdate=datetime.utcnow,
                nullable=False,
            )
        '''
    ).strip() + "\n",
    "app/schemas/site.py": dedent(
        '''
        from datetime import datetime

        from pydantic import BaseModel, ConfigDict, Field


        class SiteConfigBase(BaseModel):
            name: str = Field(..., min_length=1, max_length=100)
            code: str = Field(..., min_length=1, max_length=100)
            domain: str = Field(..., min_length=1, max_length=255)
            enabled: bool = True
            search_rule: str = ""
            parse_rule: str = ""
            page_rule: str = ""
            remark: str = ""
            crawl_method: str = Field(default="HTML解析", min_length=1, max_length=100)


        class SiteConfigCreate(SiteConfigBase):
            pass


        class SiteConfigUpdate(BaseModel):
            name: str | None = Field(default=None, min_length=1, max_length=100)
            domain: str | None = Field(default=None, min_length=1, max_length=255)
            enabled: bool | None = None
            search_rule: str | None = None
            parse_rule: str | None = None
            page_rule: str | None = None
            remark: str | None = None
            crawl_method: str | None = Field(default=None, min_length=1, max_length=100)


        class SiteConfigRead(SiteConfigBase):
            id: int
            last_crawled_at: datetime | None
            created_at: datetime
            updated_at: datetime

            model_config = ConfigDict(from_attributes=True)


        class SiteTestRequest(BaseModel):
            keyword: str = Field(..., min_length=1, max_length=100)


        class SiteTestResponse(BaseModel):
            site_code: str
            keyword: str
            success: bool
            preview_results: list[dict]
            message: str
        '''
    ).strip() + "\n",
    "app/repositories/site_repository.py": dedent(
        '''
        from sqlalchemy import select
        from sqlalchemy.orm import Session

        from app.models.site_config import SiteConfig
        from app.schemas.site import SiteConfigCreate, SiteConfigUpdate


        class SiteRepository:
            def __init__(self, db: Session):
                self.db = db

            def list_sites(self) -> list[SiteConfig]:
                statement = select(SiteConfig).order_by(SiteConfig.created_at.desc())
                return list(self.db.scalars(statement).all())

            def get_by_id(self, site_id: int) -> SiteConfig | None:
                return self.db.get(SiteConfig, site_id)

            def get_by_code(self, code: str) -> SiteConfig | None:
                statement = select(SiteConfig).where(SiteConfig.code == code)
                return self.db.scalar(statement)

            def create(self, payload: SiteConfigCreate) -> SiteConfig:
                site = SiteConfig(**payload.model_dump())
                self.db.add(site)
                self.db.commit()
                self.db.refresh(site)
                return site

            def update(self, site: SiteConfig, payload: SiteConfigUpdate) -> SiteConfig:
                for key, value in payload.model_dump(exclude_unset=True).items():
                    setattr(site, key, value)
                self.db.add(site)
                self.db.commit()
                self.db.refresh(site)
                return site

            def delete(self, site: SiteConfig) -> None:
                self.db.delete(site)
                self.db.commit()
        '''
    ).strip() + "\n",
    "app/services/site_service.py": dedent(
        '''
        from datetime import datetime

        from fastapi import HTTPException, status
        from sqlalchemy.orm import Session

        from app.repositories.site_repository import SiteRepository
        from app.schemas.site import (
            SiteConfigCreate,
            SiteConfigRead,
            SiteConfigUpdate,
            SiteTestResponse,
        )


        class SiteService:
            def __init__(self, db: Session):
                self.repository = SiteRepository(db)

            def list_sites(self) -> list[SiteConfigRead]:
                return [SiteConfigRead.model_validate(site) for site in self.repository.list_sites()]

            def create_site(self, payload: SiteConfigCreate) -> SiteConfigRead:
                if self.repository.get_by_code(payload.code):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="站点标识已存在",
                    )
                site = self.repository.create(payload)
                return SiteConfigRead.model_validate(site)

            def update_site(self, site_id: int, payload: SiteConfigUpdate) -> SiteConfigRead:
                site = self.repository.get_by_id(site_id)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="站点不存在")
                updated = self.repository.update(site, payload)
                return SiteConfigRead.model_validate(updated)

            def delete_site(self, site_id: int) -> None:
                site = self.repository.get_by_id(site_id)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="站点不存在")
                self.repository.delete(site)

            def test_site(self, site_id: int, keyword: str) -> SiteTestResponse:
                site = self.repository.get_by_id(site_id)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="站点不存在")

                preview_results = [
                    {
                        "title": f"{site.name} - {keyword} 示例结果 1",
                        "image_url": f"https://{site.domain}/preview/{site.code}/1.jpg",
                        "source_page_url": f"https://{site.domain}/search?q={keyword}",
                    },
                    {
                        "title": f"{site.name} - {keyword} 示例结果 2",
                        "image_url": f"https://{site.domain}/preview/{site.code}/2.jpg",
                        "source_page_url": f"https://{site.domain}/search?q={keyword}&page=2",
                    },
                ]

                self.repository.update(site, SiteConfigUpdate())
                site.last_crawled_at = datetime.utcnow()
                self.repository.db.add(site)
                self.repository.db.commit()
                self.repository.db.refresh(site)

                return SiteTestResponse(
                    site_code=site.code,
                    keyword=keyword,
                    success=True,
                    preview_results=preview_results,
                    message="测试抓取成功，已返回样例结果",
                )
        '''
    ).strip() + "\n",
    "app/api/site_routes.py": dedent(
        '''
        from fastapi import APIRouter, Depends, Response, status
        from sqlalchemy.orm import Session

        from app.db.session import get_db
        from app.schemas.site import (
            SiteConfigCreate,
            SiteConfigRead,
            SiteConfigUpdate,
            SiteTestRequest,
            SiteTestResponse,
        )
        from app.services.site_service import SiteService


        router = APIRouter(prefix="/api/sites", tags=["sites"])


        def get_site_service(db: Session = Depends(get_db)) -> SiteService:
            return SiteService(db)


        @router.get("", response_model=list[SiteConfigRead])
        def list_sites(service: SiteService = Depends(get_site_service)):
            return service.list_sites()


        @router.post("", response_model=SiteConfigRead, status_code=status.HTTP_201_CREATED)
        def create_site(payload: SiteConfigCreate, service: SiteService = Depends(get_site_service)):
            return service.create_site(payload)


        @router.put("/{site_id}", response_model=SiteConfigRead)
        def update_site(site_id: int, payload: SiteConfigUpdate, service: SiteService = Depends(get_site_service)):
            return service.update_site(site_id, payload)


        @router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
        def delete_site(site_id: int, service: SiteService = Depends(get_site_service)):
            service.delete_site(site_id)
            return Response(status_code=status.HTTP_204_NO_CONTENT)


        @router.post("/{site_id}/test", response_model=SiteTestResponse)
        def test_site(site_id: int, payload: SiteTestRequest, service: SiteService = Depends(get_site_service)):
            return service.test_site(site_id, payload.keyword)
        '''
    ).strip() + "\n",
    "app/main.py": dedent(
        '''
        from fastapi import FastAPI, Request
        from fastapi.responses import HTMLResponse
        from fastapi.staticfiles import StaticFiles
        from fastapi.templating import Jinja2Templates

        from app.api.site_routes import router as site_router
        from app.core.config import STATIC_DIR, TEMPLATE_DIR, settings
        from app.db.session import engine
        from app.models import Base


        Base.metadata.create_all(bind=engine)

        app = FastAPI(title=settings.app_name, version="0.1.0")
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
        templates = Jinja2Templates(directory=TEMPLATE_DIR)
        app.include_router(site_router)


        @app.get("/", response_class=HTMLResponse)
        def index(request: Request):
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={"app_name": settings.app_name},
            )
        '''
    ).strip() + "\n",
    "app/templates/index.html": dedent(
        '''
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>{{ app_name }}</title>
            <link rel="stylesheet" href="/static/css/style.css" />
        </head>
        <body>
            <main class="container">
                <header class="hero">
                    <h1>{{ app_name }}</h1>
                    <p>当前已完成第一阶段项目骨架与站点管理模块接口。</p>
                </header>
                <section class="card">
                    <h2>已实现能力</h2>
                    <ul>
                        <li>FastAPI + SQLite 基础项目结构</li>
                        <li>素材来源站点管理 API</li>
                        <li>站点新增、编辑、删除、列表、测试抓取</li>
                    </ul>
                </section>
                <section class="card">
                    <h2>可用接口</h2>
                    <ul>
                        <li>GET /api/sites</li>
                        <li>POST /api/sites</li>
                        <li>PUT /api/sites/{site_id}</li>
                        <li>DELETE /api/sites/{site_id}</li>
                        <li>POST /api/sites/{site_id}/test</li>
                    </ul>
                </section>
            </main>
        </body>
        </html>
        '''
    ).strip() + "\n",
    "app/static/css/style.css": dedent(
        '''
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: "Microsoft YaHei", sans-serif;
            background: #f5f7fb;
            color: #1f2937;
        }

        .container {
            max-width: 960px;
            margin: 0 auto;
            padding: 32px 20px 48px;
        }

        .hero,
        .card {
            background: #ffffff;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
            margin-bottom: 20px;
        }

        h1,
        h2 {
            margin-top: 0;
        }

        ul {
            padding-left: 20px;
            line-height: 1.8;
        }
        '''
    ).strip() + "\n",
    "tests/test_sites.py": dedent(
        '''
        from fastapi.testclient import TestClient

        from app.main import app


        client = TestClient(app)


        def test_site_crud_flow():
            create_response = client.post(
                "/api/sites",
                json={
                    "name": "OpenVerse",
                    "code": "openverse",
                    "domain": "api.openverse.org",
                    "enabled": True,
                    "search_rule": "/v1/images?q={keyword}",
                    "parse_rule": "results[].url",
                    "page_rule": "page={page}",
                    "remark": "默认开放图片站点",
                    "crawl_method": "API接口",
                },
            )
            assert create_response.status_code == 201
            site_id = create_response.json()["id"]

            list_response = client.get("/api/sites")
            assert list_response.status_code == 200
            assert any(site["code"] == "openverse" for site in list_response.json())

            update_response = client.put(
                f"/api/sites/{site_id}",
                json={"remark": "已更新", "enabled": False},
            )
            assert update_response.status_code == 200
            assert update_response.json()["remark"] == "已更新"
            assert update_response.json()["enabled"] is False

            test_response = client.post(
                f"/api/sites/{site_id}/test",
                json={"keyword": "春日花海"},
            )
            assert test_response.status_code == 200
            assert test_response.json()["success"] is True
            assert len(test_response.json()["preview_results"]) == 2

            delete_response = client.delete(f"/api/sites/{site_id}")
            assert delete_response.status_code == 204
        '''
    ).strip() + "\n",
}

for relative_path, content in FILES.items():
    target = BASE / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

print(f"generated {len(FILES)} files")
