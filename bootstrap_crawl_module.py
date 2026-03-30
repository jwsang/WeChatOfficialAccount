from pathlib import Path
from textwrap import dedent

BASE = Path(__file__).resolve().parent
FILES: dict[str, str] = {
    "app/models/__init__.py": dedent(
        '''
        from app.models.base import Base
        from app.models.crawl_task import CrawlTask
        from app.models.crawl_task_log import CrawlTaskLog
        from app.models.material_image import MaterialImage
        from app.models.site_config import SiteConfig
        '''
    ).strip() + "\n",
    "app/models/crawl_task.py": dedent(
        '''
        from datetime import UTC, datetime

        from sqlalchemy import DateTime, Integer, String, Text
        from sqlalchemy.orm import Mapped, mapped_column

        from app.models.base import Base


        class CrawlTask(Base):
            __tablename__ = "crawl_tasks"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            keyword: Mapped[str] = mapped_column(String(200), nullable=False)
            target_scope: Mapped[str] = mapped_column(String(20), default="all", nullable=False)
            target_sites: Mapped[str] = mapped_column(Text, default="", nullable=False)
            per_site_limit: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
            max_pages: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
            status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
            total_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
            success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
            duplicate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
            fail_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
            started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
            finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
            created_by: Mapped[str] = mapped_column(String(100), default="system", nullable=False)
            summary_message: Mapped[str] = mapped_column(Text, default="", nullable=False)
            created_at: Mapped[datetime] = mapped_column(
                DateTime,
                default=lambda: datetime.now(UTC),
                nullable=False,
            )
            updated_at: Mapped[datetime] = mapped_column(
                DateTime,
                default=lambda: datetime.now(UTC),
                onupdate=lambda: datetime.now(UTC),
                nullable=False,
            )
        '''
    ).strip() + "\n",
    "app/models/crawl_task_log.py": dedent(
        '''
        from datetime import UTC, datetime

        from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
        from sqlalchemy.orm import Mapped, mapped_column

        from app.models.base import Base


        class CrawlTaskLog(Base):
            __tablename__ = "crawl_task_logs"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            crawl_task_id: Mapped[int] = mapped_column(ForeignKey("crawl_tasks.id"), nullable=False, index=True)
            site_code: Mapped[str] = mapped_column(String(100), nullable=False)
            status: Mapped[str] = mapped_column(String(30), nullable=False)
            duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
            message: Mapped[str] = mapped_column(Text, default="", nullable=False)
            created_at: Mapped[datetime] = mapped_column(
                DateTime,
                default=lambda: datetime.now(UTC),
                nullable=False,
            )
        '''
    ).strip() + "\n",
    "app/models/material_image.py": dedent(
        '''
        from datetime import UTC, datetime

        from sqlalchemy import DateTime, Integer, String, Text
        from sqlalchemy.orm import Mapped, mapped_column

        from app.models.base import Base


        class MaterialImage(Base):
            __tablename__ = "material_images"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            material_name: Mapped[str] = mapped_column(String(200), nullable=False)
            search_keyword: Mapped[str] = mapped_column(String(200), default="", nullable=False)
            source_site_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
            source_type: Mapped[str] = mapped_column(String(20), default="crawl", nullable=False)
            source_page_url: Mapped[str] = mapped_column(Text, default="", nullable=False)
            source_image_url: Mapped[str] = mapped_column(Text, default="", nullable=False)
            local_file_path: Mapped[str] = mapped_column(String(255), nullable=False)
            local_thumbnail_path: Mapped[str] = mapped_column(String(255), nullable=False)
            image_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
            image_width: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
            image_height: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
            material_status: Mapped[str] = mapped_column(String(30), default="available", nullable=False)
            audit_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
            used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
            tag_codes: Mapped[str] = mapped_column(Text, default="", nullable=False)
            crawl_task_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
            prompt_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
            created_at: Mapped[datetime] = mapped_column(
                DateTime,
                default=lambda: datetime.now(UTC),
                nullable=False,
            )
            updated_at: Mapped[datetime] = mapped_column(
                DateTime,
                default=lambda: datetime.now(UTC),
                onupdate=lambda: datetime.now(UTC),
                nullable=False,
            )
        '''
    ).strip() + "\n",
    "app/schemas/crawl_task.py": dedent(
        '''
        from datetime import datetime
        from typing import Literal

        from pydantic import BaseModel, Field


        class CrawlTaskCreate(BaseModel):
            keyword: str = Field(..., min_length=1, max_length=200)
            target_scope: Literal["all", "selected"] = "all"
            target_site_codes: list[str] = Field(default_factory=list)
            per_site_limit: int = Field(default=3, ge=1, le=10)
            max_pages: int = Field(default=1, ge=1, le=10)
            created_by: str = Field(default="system", min_length=1, max_length=100)


        class CrawlTaskRetryRequest(BaseModel):
            site_codes: list[str] = Field(default_factory=list)


        class CrawlTaskLogRead(BaseModel):
            id: int
            site_code: str
            status: str
            duration_ms: int
            message: str
            created_at: datetime


        class CrawlMaterialRead(BaseModel):
            id: int
            material_name: str
            search_keyword: str
            source_site_code: str
            source_page_url: str
            source_image_url: str
            local_file_path: str
            local_thumbnail_path: str
            image_hash: str
            image_width: int
            image_height: int
            material_status: str
            tag_codes: str
            created_at: datetime


        class CrawlTaskRead(BaseModel):
            id: int
            keyword: str
            target_scope: str
            target_site_codes: list[str]
            per_site_limit: int
            max_pages: int
            status: str
            total_count: int
            success_count: int
            duplicate_count: int
            fail_count: int
            started_at: datetime | None
            finished_at: datetime | None
            created_by: str
            summary_message: str
            created_at: datetime
            updated_at: datetime


        class CrawlTaskDetailRead(CrawlTaskRead):
            logs: list[CrawlTaskLogRead]
            materials: list[CrawlMaterialRead]
        '''
    ).strip() + "\n",
    "app/repositories/crawl_task_repository.py": dedent(
        '''
        from sqlalchemy import or_, select
        from sqlalchemy.orm import Session

        from app.models.crawl_task import CrawlTask
        from app.models.crawl_task_log import CrawlTaskLog
        from app.models.material_image import MaterialImage
        from app.models.site_config import SiteConfig


        class CrawlTaskRepository:
            def __init__(self, db: Session):
                self.db = db

            def list_tasks(self) -> list[CrawlTask]:
                statement = select(CrawlTask).order_by(CrawlTask.created_at.desc())
                return list(self.db.scalars(statement).all())

            def get_task(self, task_id: int) -> CrawlTask | None:
                return self.db.get(CrawlTask, task_id)

            def create_task(self, payload: dict) -> CrawlTask:
                task = CrawlTask(**payload)
                self.db.add(task)
                self.db.commit()
                self.db.refresh(task)
                return task

            def save_task(self, task: CrawlTask) -> CrawlTask:
                self.db.add(task)
                self.db.commit()
                self.db.refresh(task)
                return task

            def list_enabled_sites(self) -> list[SiteConfig]:
                statement = select(SiteConfig).where(SiteConfig.enabled.is_(True)).order_by(SiteConfig.name.asc())
                return list(self.db.scalars(statement).all())

            def list_enabled_sites_by_codes(self, codes: list[str]) -> list[SiteConfig]:
                if not codes:
                    return []
                statement = (
                    select(SiteConfig)
                    .where(SiteConfig.enabled.is_(True), SiteConfig.code.in_(codes))
                    .order_by(SiteConfig.name.asc())
                )
                return list(self.db.scalars(statement).all())

            def find_material_by_url_or_hash(self, source_image_url: str, image_hash: str) -> MaterialImage | None:
                statement = select(MaterialImage).where(
                    or_(
                        MaterialImage.source_image_url == source_image_url,
                        MaterialImage.image_hash == image_hash,
                    )
                )
                return self.db.scalar(statement)

            def create_material(self, payload: dict) -> MaterialImage:
                material = MaterialImage(**payload)
                self.db.add(material)
                self.db.commit()
                self.db.refresh(material)
                return material

            def list_materials_by_task(self, task_id: int) -> list[MaterialImage]:
                statement = (
                    select(MaterialImage)
                    .where(MaterialImage.crawl_task_id == task_id)
                    .order_by(MaterialImage.created_at.desc())
                )
                return list(self.db.scalars(statement).all())

            def create_log(self, payload: dict) -> CrawlTaskLog:
                log = CrawlTaskLog(**payload)
                self.db.add(log)
                self.db.commit()
                self.db.refresh(log)
                return log

            def list_logs_by_task(self, task_id: int) -> list[CrawlTaskLog]:
                statement = (
                    select(CrawlTaskLog)
                    .where(CrawlTaskLog.crawl_task_id == task_id)
                    .order_by(CrawlTaskLog.created_at.desc(), CrawlTaskLog.id.desc())
                )
                return list(self.db.scalars(statement).all())
        '''
    ).strip() + "\n",
    "app/services/crawl_service.py": dedent(
        '''
        from __future__ import annotations

        import hashlib
        from datetime import UTC, datetime
        from io import BytesIO
        from pathlib import Path
        from time import perf_counter
        from urllib.parse import quote_plus

        from fastapi import HTTPException, status
        from PIL import Image, ImageDraw
        from sqlalchemy.orm import Session

        from app.core.config import DATA_DIR
        from app.models.crawl_task import CrawlTask
        from app.models.material_image import MaterialImage
        from app.models.site_config import SiteConfig
        from app.repositories.crawl_task_repository import CrawlTaskRepository
        from app.schemas.crawl_task import (
            CrawlMaterialRead,
            CrawlTaskCreate,
            CrawlTaskDetailRead,
            CrawlTaskLogRead,
            CrawlTaskRead,
            CrawlTaskRetryRequest,
        )


        UPLOAD_DIR = DATA_DIR / "uploads"
        THUMBNAIL_DIR = DATA_DIR / "thumbnails"
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)


        class CrawlService:
            def __init__(self, db: Session):
                self.repository = CrawlTaskRepository(db)

            def list_tasks(self) -> list[CrawlTaskRead]:
                return [self._serialize_task(task) for task in self.repository.list_tasks()]

            def get_task_detail(self, task_id: int) -> CrawlTaskDetailRead:
                task = self.repository.get_task(task_id)
                if not task:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="抓取任务不存在")
                return self._build_detail(task)

            def create_task(self, payload: CrawlTaskCreate) -> CrawlTaskDetailRead:
                sites = self._resolve_sites(payload.target_scope, payload.target_site_codes)
                task = self.repository.create_task(
                    {
                        "keyword": payload.keyword,
                        "target_scope": payload.target_scope,
                        "target_sites": ",".join(site.code for site in sites),
                        "per_site_limit": payload.per_site_limit,
                        "max_pages": payload.max_pages,
                        "status": "pending",
                        "created_by": payload.created_by,
                        "summary_message": "任务已创建，等待执行",
                    }
                )
                self._run_task(task, sites)
                return self._build_detail(task)

            def retry_task(self, task_id: int, payload: CrawlTaskRetryRequest) -> CrawlTaskDetailRead:
                task = self.repository.get_task(task_id)
                if not task:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="抓取任务不存在")

                site_codes = payload.site_codes or self._split_site_codes(task.target_sites)
                target_scope = "selected" if site_codes else task.target_scope
                sites = self._resolve_sites(target_scope, site_codes)
                task.target_sites = ",".join(site.code for site in sites)
                self._run_task(task, sites)
                return self._build_detail(task)

            def _resolve_sites(self, target_scope: str, site_codes: list[str]) -> list[SiteConfig]:
                if target_scope == "all":
                    sites = self.repository.list_enabled_sites()
                    if not sites:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前没有启用的站点可用于抓取")
                    return sites

                normalized_codes = [code.strip() for code in site_codes if code.strip()]
                if not normalized_codes:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请选择至少一个启用站点")

                sites = self.repository.list_enabled_sites_by_codes(normalized_codes)
                if len(sites) != len(set(normalized_codes)):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="部分站点不存在或未启用")
                return sites

            def _run_task(self, task: CrawlTask, sites: list[SiteConfig]) -> None:
                task.status = "executing"
                task.total_count = 0
                task.success_count = 0
                task.duplicate_count = 0
                task.fail_count = 0
                task.started_at = datetime.now(UTC)
                task.finished_at = None
                task.summary_message = f"正在执行，目标站点数：{len(sites)}"
                self.repository.save_task(task)

                for site in sites:
                    started = perf_counter()
                    try:
                        results = self._simulate_site_results(task, site)
                        success_count = 0
                        duplicate_count = 0

                        for index, result in enumerate(results, start=1):
                            task.total_count += 1
                            image_bytes, thumbnail_bytes, width, height, image_hash = self._build_image_assets(
                                site=site,
                                keyword=task.keyword,
                                visual_seed=result["visual_seed"],
                            )

                            exists = self.repository.find_material_by_url_or_hash(
                                result["source_image_url"],
                                image_hash,
                            )
                            if exists:
                                duplicate_count += 1
                                task.duplicate_count += 1
                                continue

                            local_file_path, local_thumbnail_path = self._save_assets(
                                task_id=task.id,
                                site_code=site.code,
                                index=index,
                                image_hash=image_hash,
                                image_bytes=image_bytes,
                                thumbnail_bytes=thumbnail_bytes,
                            )

                            self.repository.create_material(
                                {
                                    "material_name": result["title"],
                                    "search_keyword": task.keyword,
                                    "source_site_code": site.code,
                                    "source_type": "crawl",
                                    "source_page_url": result["source_page_url"],
                                    "source_image_url": result["source_image_url"],
                                    "local_file_path": local_file_path,
                                    "local_thumbnail_path": local_thumbnail_path,
                                    "image_hash": image_hash,
                                    "image_width": width,
                                    "image_height": height,
                                    "material_status": "available",
                                    "audit_status": "pending",
                                    "used_count": 0,
                                    "tag_codes": self._build_tag_codes(task.keyword),
                                    "crawl_task_id": task.id,
                                    "prompt_text": task.keyword,
                                }
                            )
                            success_count += 1
                            task.success_count += 1

                        duration_ms = int((perf_counter() - started) * 1000)
                        site_status = "success" if success_count else "duplicate"
                        self.repository.create_log(
                            {
                                "crawl_task_id": task.id,
                                "site_code": site.code,
                                "status": site_status,
                                "duration_ms": duration_ms,
                                "message": f"站点 {site.name} 完成：新增 {success_count}，去重 {duplicate_count}，页数上限 {task.max_pages}",
                            }
                        )
                    except Exception as exc:
                        task.fail_count += 1
                        duration_ms = int((perf_counter() - started) * 1000)
                        self.repository.create_log(
                            {
                                "crawl_task_id": task.id,
                                "site_code": site.code,
                                "status": "failed",
                                "duration_ms": duration_ms,
                                "message": f"站点 {site.name} 抓取失败：{exc}",
                            }
                        )

                task.finished_at = datetime.now(UTC)
                if task.fail_count == 0 and (task.success_count > 0 or task.duplicate_count > 0):
                    task.status = "completed"
                elif task.fail_count > 0 and task.success_count > 0:
                    task.status = "partial_success"
                else:
                    task.status = "failed"
                task.summary_message = (
                    f"执行完成：目标站点 {len(sites)}，抓取 {task.total_count}，新增 {task.success_count}，"
                    f"去重 {task.duplicate_count}，失败 {task.fail_count}"
                )
                self.repository.save_task(task)

            def _simulate_site_results(self, task: CrawlTask, site: SiteConfig) -> list[dict]:
                results: list[dict] = []
                safe_keyword = quote_plus(task.keyword)
                for index in range(1, task.per_site_limit + 1):
                    page = ((index - 1) % task.max_pages) + 1
                    visual_seed = 1 if task.per_site_limit > 1 and index == task.per_site_limit else index
                    results.append(
                        {
                            "title": f"{task.keyword} - {site.name} 样例素材 {index}",
                            "source_image_url": f"https://{site.domain}/generated/{safe_keyword}/{index}.png",
                            "source_page_url": f"https://{site.domain}/search?q={safe_keyword}&page={page}",
                            "visual_seed": visual_seed,
                        }
                    )
                return results

            def _build_image_assets(self, site: SiteConfig, keyword: str, visual_seed: int) -> tuple[bytes, bytes, int, int, str]:
                width, height = 1280, 720
                image = Image.new("RGB", (width, height), color=self._build_color(site.code, keyword, visual_seed))
                draw = ImageDraw.Draw(image)
                draw.rounded_rectangle((40, 40, width - 40, height - 40), radius=28, outline=(255, 255, 255), width=4)
                draw.multiline_text(
                    (80, 90),
                    f"微信公众号素材\n{site.name}\n关键词：{keyword}\n序号：{visual_seed}",
                    fill=(255, 255, 255),
                    spacing=16,
                )

                full_buffer = BytesIO()
                image.save(full_buffer, format="PNG")
                image_bytes = full_buffer.getvalue()

                thumbnail = image.copy()
                thumbnail.thumbnail((360, 360))
                thumb_buffer = BytesIO()
                thumbnail.save(thumb_buffer, format="PNG")
                thumbnail_bytes = thumb_buffer.getvalue()

                image_hash = hashlib.sha256(image_bytes).hexdigest()
                return image_bytes, thumbnail_bytes, width, height, image_hash

            def _build_color(self, site_code: str, keyword: str, visual_seed: int) -> tuple[int, int, int]:
                seed = hashlib.md5(f"{site_code}-{keyword}-{visual_seed}".encode("utf-8")).hexdigest()
                return (int(seed[0:2], 16), int(seed[2:4], 16), int(seed[4:6], 16))

            def _save_assets(
                self,
                task_id: int,
                site_code: str,
                index: int,
                image_hash: str,
                image_bytes: bytes,
                thumbnail_bytes: bytes,
            ) -> tuple[str, str]:
                stem = f"task_{task_id}_{site_code}_{index}_{image_hash[:10]}"
                image_path = UPLOAD_DIR / f"{stem}.png"
                thumbnail_path = THUMBNAIL_DIR / f"{stem}.png"
                image_path.write_bytes(image_bytes)
                thumbnail_path.write_bytes(thumbnail_bytes)
                return image_path.relative_to(DATA_DIR).as_posix(), thumbnail_path.relative_to(DATA_DIR).as_posix()

            def _build_tag_codes(self, keyword: str) -> str:
                return "|".join(part for part in keyword.replace("，", " ").replace(",", " ").split() if part)

            def _split_site_codes(self, raw_value: str) -> list[str]:
                return [item for item in raw_value.split(",") if item]

            def _serialize_task(self, task: CrawlTask) -> CrawlTaskRead:
                return CrawlTaskRead(
                    id=task.id,
                    keyword=task.keyword,
                    target_scope=task.target_scope,
                    target_site_codes=self._split_site_codes(task.target_sites),
                    per_site_limit=task.per_site_limit,
                    max_pages=task.max_pages,
                    status=task.status,
                    total_count=task.total_count,
                    success_count=task.success_count,
                    duplicate_count=task.duplicate_count,
                    fail_count=task.fail_count,
                    started_at=task.started_at,
                    finished_at=task.finished_at,
                    created_by=task.created_by,
                    summary_message=task.summary_message,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                )

            def _serialize_log(self, log) -> CrawlTaskLogRead:
                return CrawlTaskLogRead(
                    id=log.id,
                    site_code=log.site_code,
                    status=log.status,
                    duration_ms=log.duration_ms,
                    message=log.message,
                    created_at=log.created_at,
                )

            def _serialize_material(self, material: MaterialImage) -> CrawlMaterialRead:
                return CrawlMaterialRead(
                    id=material.id,
                    material_name=material.material_name,
                    search_keyword=material.search_keyword,
                    source_site_code=material.source_site_code,
                    source_page_url=material.source_page_url,
                    source_image_url=material.source_image_url,
                    local_file_path=material.local_file_path,
                    local_thumbnail_path=material.local_thumbnail_path,
                    image_hash=material.image_hash,
                    image_width=material.image_width,
                    image_height=material.image_height,
                    material_status=material.material_status,
                    tag_codes=material.tag_codes,
                    created_at=material.created_at,
                )

            def _build_detail(self, task: CrawlTask) -> CrawlTaskDetailRead:
                return CrawlTaskDetailRead(
                    **self._serialize_task(task).model_dump(),
                    logs=[self._serialize_log(log) for log in self.repository.list_logs_by_task(task.id)],
                    materials=[self._serialize_material(item) for item in self.repository.list_materials_by_task(task.id)],
                )
        '''
    ).strip() + "\n",
    "app/api/crawl_routes.py": dedent(
        '''
        from fastapi import APIRouter, Depends, status
        from sqlalchemy.orm import Session

        from app.db.session import get_db
        from app.schemas.crawl_task import CrawlTaskCreate, CrawlTaskDetailRead, CrawlTaskRead, CrawlTaskRetryRequest
        from app.services.crawl_service import CrawlService


        router = APIRouter(prefix="/api/crawl-tasks", tags=["crawl-tasks"])


        def get_crawl_service(db: Session = Depends(get_db)) -> CrawlService:
            return CrawlService(db)


        @router.get("", response_model=list[CrawlTaskRead])
        def list_tasks(service: CrawlService = Depends(get_crawl_service)):
            return service.list_tasks()


        @router.post("", response_model=CrawlTaskDetailRead, status_code=status.HTTP_201_CREATED)
        def create_task(payload: CrawlTaskCreate, service: CrawlService = Depends(get_crawl_service)):
            return service.create_task(payload)


        @router.get("/{task_id}", response_model=CrawlTaskDetailRead)
        def get_task(task_id: int, service: CrawlService = Depends(get_crawl_service)):
            return service.get_task_detail(task_id)


        @router.post("/{task_id}/retry", response_model=CrawlTaskDetailRead)
        def retry_task(task_id: int, payload: CrawlTaskRetryRequest, service: CrawlService = Depends(get_crawl_service)):
            return service.retry_task(task_id, payload)
        '''
    ).strip() + "\n",
    "app/main.py": dedent(
        '''
        from fastapi import FastAPI, Request
        from fastapi.responses import HTMLResponse
        from fastapi.staticfiles import StaticFiles
        from fastapi.templating import Jinja2Templates

        from app.api.crawl_routes import router as crawl_router
        from app.api.site_routes import router as site_router
        from app.core.config import DATA_DIR, STATIC_DIR, TEMPLATE_DIR, settings
        from app.db.session import engine
        from app.models import Base


        Base.metadata.create_all(bind=engine)

        app = FastAPI(title=settings.app_name, version="0.2.0")
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
        app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")
        templates = Jinja2Templates(directory=TEMPLATE_DIR)
        app.include_router(site_router)
        app.include_router(crawl_router)


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
                    <p>当前已完成：项目骨架、素材来源站点管理、图片抓取任务模拟执行与结果可视化。</p>
                </header>

                <section class="grid two-columns">
                    <section class="card">
                        <div class="section-header">
                            <div>
                                <h2>站点配置表单</h2>
                                <p class="muted">维护站点名称、标识、域名、规则与抓取状态。</p>
                            </div>
                        </div>
                        <div id="form-message"></div>
                        <form id="site-form" class="form-grid">
                            <input type="hidden" id="site-id" />
                            <div class="field"><label for="name">站点名称</label><input id="name" required /></div>
                            <div class="field"><label for="code">站点标识</label><input id="code" required /></div>
                            <div class="field"><label for="domain">站点域名</label><input id="domain" required /></div>
                            <div class="field">
                                <label for="crawl_method">抓取方式说明</label>
                                <select id="crawl_method">
                                    <option value="API接口">API接口</option>
                                    <option value="HTML解析">HTML解析</option>
                                    <option value="RSS/Feed">RSS/Feed</option>
                                </select>
                            </div>
                            <div class="field"><label for="search_rule">搜索 URL / 接口模板</label><textarea id="search_rule"></textarea></div>
                            <div class="field"><label for="parse_rule">图片提取规则</label><textarea id="parse_rule"></textarea></div>
                            <div class="field"><label for="page_rule">分页规则</label><textarea id="page_rule"></textarea></div>
                            <div class="field"><label for="remark">备注</label><textarea id="remark"></textarea></div>
                            <div class="field">
                                <label for="enabled">抓取状态</label>
                                <select id="enabled">
                                    <option value="true">启用</option>
                                    <option value="false">停用</option>
                                </select>
                            </div>
                            <div class="actions">
                                <button type="submit" id="submit-button">保存站点</button>
                                <button type="button" class="ghost" id="reset-button">清空表单</button>
                            </div>
                        </form>
                    </section>

                    <section class="card">
                        <div class="section-header inline-between">
                            <div>
                                <h2>站点列表</h2>
                                <p class="muted">支持新增、编辑、启停、删除与测试抓取。</p>
                            </div>
                            <button class="secondary" id="refresh-button" type="button">刷新列表</button>
                        </div>
                        <div id="list-message"></div>
                        <div id="site-list" class="list-stack"></div>
                    </section>
                </section>

                <section class="card">
                    <div class="section-header">
                        <div>
                            <h2>测试抓取</h2>
                            <p class="muted">基于选中的站点返回样例结果，便于校验规则。</p>
                        </div>
                    </div>
                    <div class="toolbar">
                        <input id="test-keyword" placeholder="例如 春日花海" class="compact-input" />
                        <button id="test-button" type="button">执行测试抓取</button>
                    </div>
                    <div id="test-result" class="block-top"></div>
                </section>

                <section class="grid two-columns">
                    <section class="card">
                        <div class="section-header">
                            <div>
                                <h2>抓取任务创建</h2>
                                <p class="muted">支持全部站点/指定站点、每站抓取上限、页数上限与结果入库。</p>
                            </div>
                        </div>
                        <div id="crawl-form-message"></div>
                        <form id="crawl-form" class="form-grid">
                            <div class="field"><label for="crawl-keyword">关键词</label><input id="crawl-keyword" required /></div>
                            <div class="field">
                                <label for="crawl-scope">抓取范围</label>
                                <select id="crawl-scope">
                                    <option value="all">全部启用站点</option>
                                    <option value="selected">指定站点</option>
                                </select>
                            </div>
                            <div class="field">
                                <label>指定站点</label>
                                <div id="crawl-site-selector" class="checkbox-list"></div>
                            </div>
                            <div class="field"><label for="per-site-limit">每站抓取上限</label><input id="per-site-limit" type="number" min="1" max="10" value="3" /></div>
                            <div class="field"><label for="max-pages">抓取页数上限</label><input id="max-pages" type="number" min="1" max="10" value="2" /></div>
                            <div class="field"><label for="created-by">执行人</label><input id="created-by" value="admin" /></div>
                            <div class="actions">
                                <button type="submit">创建并执行任务</button>
                                <button type="button" class="ghost" id="crawl-reset-button">重置任务表单</button>
                            </div>
                        </form>
                    </section>

                    <section class="card">
                        <div class="section-header inline-between">
                            <div>
                                <h2>抓取任务列表</h2>
                                <p class="muted">展示任务状态、结果统计与重试入口。</p>
                            </div>
                            <button class="secondary" id="crawl-refresh-button" type="button">刷新任务</button>
                        </div>
                        <div id="crawl-list-message"></div>
                        <div id="crawl-task-list" class="list-stack"></div>
                    </section>
                </section>

                <section class="card">
                    <div class="section-header inline-between">
                        <div>
                            <h2>任务详情</h2>
                            <p class="muted">查看站点抓取日志、入库素材与缩略图。</p>
                        </div>
                        <button class="ghost" id="retry-task-button" type="button" disabled>重试当前任务</button>
                    </div>
                    <div id="crawl-task-detail" class="empty">请选择一条抓取任务查看详情。</div>
                </section>
            </main>
            <script src="/static/js/app.js"></script>
        </body>
        </html>
        '''
    ).strip() + "\n",
    "app/static/css/style.css": dedent(
        '''
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: "Microsoft YaHei", sans-serif;
            background: #f5f7fb;
            color: #111827;
        }
        .container { max-width: 1320px; margin: 0 auto; padding: 28px 20px 48px; }
        .hero, .card {
            background: #ffffff;
            border-radius: 18px;
            padding: 24px;
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.08);
            margin-bottom: 20px;
        }
        .grid { display: grid; gap: 20px; }
        .two-columns { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .section-header { margin-bottom: 14px; }
        .inline-between { display: flex; justify-content: space-between; align-items: flex-start; gap: 14px; }
        h1, h2, h3 { margin: 0 0 8px; }
        .muted { color: #64748b; font-size: 14px; margin: 0; }
        .form-grid, .list-stack { display: grid; gap: 14px; }
        .field { display: grid; gap: 6px; }
        .field label { font-size: 14px; font-weight: 700; color: #334155; }
        input, textarea, select {
            width: 100%;
            border: 1px solid #d1d5db;
            border-radius: 10px;
            padding: 10px 12px;
            font: inherit;
            background: #fff;
        }
        textarea { min-height: 82px; resize: vertical; }
        button {
            border: 0;
            border-radius: 10px;
            padding: 10px 16px;
            cursor: pointer;
            font: inherit;
            background: #2563eb;
            color: #fff;
        }
        button.secondary { background: #475569; }
        button.danger { background: #dc2626; }
        button.ghost { background: #e5e7eb; color: #111827; }
        button:disabled { opacity: .6; cursor: not-allowed; }
        .actions, .toolbar, .site-actions, .task-actions { display: flex; gap: 10px; flex-wrap: wrap; }
        .compact-input { max-width: 280px; }
        .message, .test-result, .empty {
            border-radius: 12px;
            padding: 12px 14px;
            font-size: 14px;
        }
        .block-top { margin-top: 14px; }
        .empty { background: #f8fafc; color: #475569; }
        .message.info, .test-result.info { background: #dbeafe; color: #1d4ed8; }
        .message.success, .test-result.success { background: #dcfce7; color: #166534; }
        .message.error, .test-result.error { background: #fee2e2; color: #991b1b; }
        .site-item, .task-item, .preview-item, .log-item, .material-item {
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 16px;
            background: #fff;
        }
        .site-item.active, .task-item.active {
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
        }
        .item-header {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            align-items: flex-start;
            margin-bottom: 12px;
        }
        .status {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            border-radius: 999px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: 700;
        }
        .status.enabled, .status.completed, .status.success { background: #dcfce7; color: #166534; }
        .status.disabled, .status.failed { background: #fee2e2; color: #991b1b; }
        .status.executing, .status.info, .status.duplicate { background: #dbeafe; color: #1d4ed8; }
        .status.partial_success { background: #fef3c7; color: #92400e; }
        .meta-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(120px, 1fr));
            gap: 10px 16px;
            font-size: 14px;
        }
        .meta-grid div { display: grid; gap: 4px; }
        .meta-grid strong { color: #0f172a; }
        .checkbox-list { display: grid; gap: 8px; }
        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 12px;
            border-radius: 10px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
        }
        .checkbox-item input { width: auto; }
        .preview-list, .log-list, .material-list { display: grid; gap: 12px; margin-top: 14px; }
        .preview-item a, .material-item a, .log-item a { color: #2563eb; text-decoration: none; word-break: break-all; }
        .detail-grid { display: grid; gap: 20px; }
        .material-list { grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); }
        .material-item img {
            width: 100%;
            aspect-ratio: 4 / 3;
            object-fit: cover;
            border-radius: 12px;
            margin-bottom: 10px;
            background: #e5e7eb;
        }
        @media (max-width: 1024px) {
            .two-columns { grid-template-columns: 1fr; }
            .inline-between, .item-header { flex-direction: column; align-items: stretch; }
            .meta-grid { grid-template-columns: 1fr; }
        }
        '''
    ).strip() + "\n",
    "app/static/js/app.js": dedent(
        '''
        const state = {
            selectedSiteId: null,
            selectedTaskId: null,
            sites: [],
            tasks: [],
        };

        const elements = {
            form: document.getElementById('site-form'),
            siteId: document.getElementById('site-id'),
            name: document.getElementById('name'),
            code: document.getElementById('code'),
            domain: document.getElementById('domain'),
            crawlMethod: document.getElementById('crawl_method'),
            searchRule: document.getElementById('search_rule'),
            parseRule: document.getElementById('parse_rule'),
            pageRule: document.getElementById('page_rule'),
            remark: document.getElementById('remark'),
            enabled: document.getElementById('enabled'),
            formMessage: document.getElementById('form-message'),
            listMessage: document.getElementById('list-message'),
            siteList: document.getElementById('site-list'),
            resetButton: document.getElementById('reset-button'),
            refreshButton: document.getElementById('refresh-button'),
            submitButton: document.getElementById('submit-button'),
            testKeyword: document.getElementById('test-keyword'),
            testButton: document.getElementById('test-button'),
            testResult: document.getElementById('test-result'),
            crawlForm: document.getElementById('crawl-form'),
            crawlScope: document.getElementById('crawl-scope'),
            crawlKeyword: document.getElementById('crawl-keyword'),
            crawlSiteSelector: document.getElementById('crawl-site-selector'),
            perSiteLimit: document.getElementById('per-site-limit'),
            maxPages: document.getElementById('max-pages'),
            createdBy: document.getElementById('created-by'),
            crawlFormMessage: document.getElementById('crawl-form-message'),
            crawlListMessage: document.getElementById('crawl-list-message'),
            crawlTaskList: document.getElementById('crawl-task-list'),
            crawlTaskDetail: document.getElementById('crawl-task-detail'),
            crawlRefreshButton: document.getElementById('crawl-refresh-button'),
            crawlResetButton: document.getElementById('crawl-reset-button'),
            retryTaskButton: document.getElementById('retry-task-button'),
        };

        function formatDate(value) {
            if (!value) return '暂无';
            return new Date(value).toLocaleString('zh-CN', { hour12: false });
        }

        function showMessage(target, text, type = 'info') {
            target.innerHTML = text ? `<div class="message ${type}">${text}</div>` : '';
        }

        function statusClass(status) {
            const map = {
                completed: 'completed',
                executing: 'executing',
                failed: 'failed',
                partial_success: 'partial_success',
                success: 'success',
                duplicate: 'duplicate',
                enabled: 'enabled',
                disabled: 'disabled',
            };
            return map[status] || 'info';
        }

        function request(url, options = {}) {
            return fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...(options.headers || {}),
                },
                ...options,
            }).then(async (response) => {
                if (response.status === 204) return null;
                const data = await response.json().catch(() => ({}));
                if (!response.ok) throw new Error(data.detail || '请求失败');
                return data;
            });
        }

        function resetSiteForm() {
            elements.form.reset();
            elements.siteId.value = '';
            elements.enabled.value = 'true';
            elements.code.disabled = false;
            elements.submitButton.textContent = '保存站点';
            state.selectedSiteId = null;
            showMessage(elements.formMessage, '已切换为新增站点模式。', 'info');
            renderSiteList();
        }

        function renderSiteSelector() {
            if (!state.sites.length) {
                elements.crawlSiteSelector.innerHTML = '<div class="empty">暂无可选站点，请先创建并启用站点。</div>';
                return;
            }
            elements.crawlSiteSelector.innerHTML = state.sites
                .filter((site) => site.enabled)
                .map((site) => `
                    <label class="checkbox-item">
                        <input type="checkbox" name="crawl-site-code" value="${site.code}" />
                        <span>${site.name}（${site.code}）</span>
                    </label>
                `)
                .join('') || '<div class="empty">当前没有启用站点。</div>';
        }

        function renderSiteList() {
            if (!state.sites.length) {
                elements.siteList.innerHTML = '<div class="empty">暂无站点数据。</div>';
                return;
            }
            elements.siteList.innerHTML = state.sites.map((site) => `
                <article class="site-item ${state.selectedSiteId === site.id ? 'active' : ''}">
                    <div class="item-header">
                        <div>
                            <h3>${site.name}</h3>
                            <div class="muted">标识：${site.code}</div>
                        </div>
                        <span class="status ${site.enabled ? 'enabled' : 'disabled'}">${site.enabled ? '启用' : '停用'}</span>
                    </div>
                    <div class="meta-grid">
                        <div><span class="muted">域名</span><strong>${site.domain}</strong></div>
                        <div><span class="muted">抓取方式</span><strong>${site.crawl_method}</strong></div>
                        <div><span class="muted">最近抓取</span><strong>${formatDate(site.last_crawled_at)}</strong></div>
                        <div><span class="muted">备注</span><strong>${site.remark || '无'}</strong></div>
                    </div>
                    <div class="site-actions block-top">
                        <button type="button" class="secondary" onclick="editSite(${site.id})">编辑</button>
                        <button type="button" class="ghost" onclick="toggleSite(${site.id}, ${site.enabled ? 'false' : 'true'})">${site.enabled ? '停用' : '启用'}</button>
                        <button type="button" class="danger" onclick="deleteSite(${site.id})">删除</button>
                    </div>
                </article>
            `).join('');
        }

        function renderTaskList() {
            if (!state.tasks.length) {
                elements.crawlTaskList.innerHTML = '<div class="empty">暂无抓取任务。</div>';
                return;
            }
            elements.crawlTaskList.innerHTML = state.tasks.map((task) => `
                <article class="task-item ${state.selectedTaskId === task.id ? 'active' : ''}">
                    <div class="item-header">
                        <div>
                            <h3>${task.keyword}</h3>
                            <div class="muted">任务 ID：${task.id} ｜ 执行人：${task.created_by}</div>
                        </div>
                        <span class="status ${statusClass(task.status)}">${task.status}</span>
                    </div>
                    <div class="meta-grid">
                        <div><span class="muted">抓取范围</span><strong>${task.target_scope === 'all' ? '全部启用站点' : task.target_site_codes.join('、') || '指定站点'}</strong></div>
                        <div><span class="muted">每站上限 / 页数</span><strong>${task.per_site_limit} / ${task.max_pages}</strong></div>
                        <div><span class="muted">统计</span><strong>抓取 ${task.total_count} ｜ 新增 ${task.success_count} ｜ 去重 ${task.duplicate_count}</strong></div>
                        <div><span class="muted">完成时间</span><strong>${formatDate(task.finished_at)}</strong></div>
                    </div>
                    <div class="muted block-top">${task.summary_message}</div>
                    <div class="task-actions block-top">
                        <button type="button" class="secondary" onclick="loadTaskDetail(${task.id})">查看详情</button>
                        <button type="button" class="ghost" onclick="retryTask(${task.id})">重试任务</button>
                    </div>
                </article>
            `).join('');
        }

        function renderTaskDetail(task) {
            state.selectedTaskId = task.id;
            elements.retryTaskButton.disabled = false;
            elements.retryTaskButton.dataset.taskId = task.id;
            const logs = task.logs.length
                ? `<div class="log-list">${task.logs.map((log) => `
                    <article class="log-item">
                        <div class="item-header">
                            <strong>${log.site_code}</strong>
                            <span class="status ${statusClass(log.status)}">${log.status}</span>
                        </div>
                        <div class="muted">耗时：${log.duration_ms} ms ｜ 时间：${formatDate(log.created_at)}</div>
                        <div class="block-top">${log.message}</div>
                    </article>
                `).join('')}</div>`
                : '<div class="empty">暂无抓取日志。</div>';

            const materials = task.materials.length
                ? `<div class="material-list">${task.materials.map((item) => `
                    <article class="material-item">
                        <img src="/data/${item.local_thumbnail_path}" alt="${item.material_name}" />
                        <strong>${item.material_name}</strong>
                        <div class="muted">站点：${item.source_site_code}</div>
                        <div class="muted">尺寸：${item.image_width} × ${item.image_height}</div>
                        <div class="muted">标签：${item.tag_codes || '无'}</div>
                        <div class="block-top"><a href="/data/${item.local_file_path}" target="_blank">查看原图</a></div>
                    </article>
                `).join('')}</div>`
                : '<div class="empty">暂无素材入库。</div>';

            elements.crawlTaskDetail.innerHTML = `
                <div class="detail-grid">
                    <article>
                        <div class="item-header">
                            <div>
                                <h3>${task.keyword}</h3>
                                <div class="muted">任务 ID：${task.id} ｜ 创建时间：${formatDate(task.created_at)}</div>
                            </div>
                            <span class="status ${statusClass(task.status)}">${task.status}</span>
                        </div>
                        <div class="meta-grid">
                            <div><span class="muted">抓取范围</span><strong>${task.target_scope === 'all' ? '全部启用站点' : task.target_site_codes.join('、')}</strong></div>
                            <div><span class="muted">每站上限 / 页数</span><strong>${task.per_site_limit} / ${task.max_pages}</strong></div>
                            <div><span class="muted">执行统计</span><strong>抓取 ${task.total_count} ｜ 新增 ${task.success_count} ｜ 去重 ${task.duplicate_count} ｜ 失败 ${task.fail_count}</strong></div>
                            <div><span class="muted">执行区间</span><strong>${formatDate(task.started_at)} ~ ${formatDate(task.finished_at)}</strong></div>
                        </div>
                        <div class="block-top">${task.summary_message}</div>
                    </article>
                    <article>
                        <h3>站点抓取日志</h3>
                        ${logs}
                    </article>
                    <article>
                        <h3>入库素材</h3>
                        ${materials}
                    </article>
                </div>
            `;
            renderTaskList();
        }

        function selectedSiteCodes() {
            return Array.from(document.querySelectorAll('input[name="crawl-site-code"]:checked')).map((item) => item.value);
        }

        function fillSiteForm(site) {
            state.selectedSiteId = site.id;
            elements.siteId.value = site.id;
            elements.name.value = site.name;
            elements.code.value = site.code;
            elements.code.disabled = true;
            elements.domain.value = site.domain;
            elements.crawlMethod.value = site.crawl_method;
            elements.searchRule.value = site.search_rule;
            elements.parseRule.value = site.parse_rule;
            elements.pageRule.value = site.page_rule;
            elements.remark.value = site.remark;
            elements.enabled.value = String(site.enabled);
            elements.submitButton.textContent = '更新站点';
            showMessage(elements.formMessage, `当前正在编辑站点：${site.name}`, 'info');
            renderSiteList();
        }

        async function loadSites() {
            showMessage(elements.listMessage, '正在加载站点列表...', 'info');
            try {
                state.sites = await request('/api/sites');
                renderSiteList();
                renderSiteSelector();
                showMessage(elements.listMessage, state.sites.length ? `已加载 ${state.sites.length} 个站点。` : '当前还没有站点，请先创建一个站点配置。', state.sites.length ? 'success' : 'info');
            } catch (error) {
                showMessage(elements.listMessage, error.message, 'error');
            }
        }

        async function loadTasks() {
            showMessage(elements.crawlListMessage, '正在加载抓取任务...', 'info');
            try {
                state.tasks = await request('/api/crawl-tasks');
                renderTaskList();
                showMessage(elements.crawlListMessage, state.tasks.length ? `已加载 ${state.tasks.length} 条抓取任务。` : '暂无抓取任务。', state.tasks.length ? 'success' : 'info');
            } catch (error) {
                showMessage(elements.crawlListMessage, error.message, 'error');
            }
        }

        async function saveSite(event) {
            event.preventDefault();
            const payload = {
                name: elements.name.value.trim(),
                code: elements.code.value.trim(),
                domain: elements.domain.value.trim(),
                enabled: elements.enabled.value === 'true',
                search_rule: elements.searchRule.value.trim(),
                parse_rule: elements.parseRule.value.trim(),
                page_rule: elements.pageRule.value.trim(),
                remark: elements.remark.value.trim(),
                crawl_method: elements.crawlMethod.value,
            };
            try {
                if (elements.siteId.value) {
                    await request(`/api/sites/${elements.siteId.value}`, {
                        method: 'PUT',
                        body: JSON.stringify({
                            name: payload.name,
                            domain: payload.domain,
                            enabled: payload.enabled,
                            search_rule: payload.search_rule,
                            parse_rule: payload.parse_rule,
                            page_rule: payload.page_rule,
                            remark: payload.remark,
                            crawl_method: payload.crawl_method,
                        }),
                    });
                    showMessage(elements.formMessage, '站点更新成功。', 'success');
                } else {
                    await request('/api/sites', { method: 'POST', body: JSON.stringify(payload) });
                    showMessage(elements.formMessage, '站点创建成功。', 'success');
                }
                resetSiteForm();
                await loadSites();
            } catch (error) {
                showMessage(elements.formMessage, error.message, 'error');
            }
        }

        async function runTest() {
            const keyword = elements.testKeyword.value.trim();
            if (!state.selectedSiteId) {
                elements.testResult.innerHTML = '<div class="test-result error">请先在站点列表中选择需要测试的站点。</div>';
                return;
            }
            if (!keyword) {
                elements.testResult.innerHTML = '<div class="test-result error">请输入测试关键词。</div>';
                return;
            }
            elements.testResult.innerHTML = '<div class="test-result info">测试抓取执行中...</div>';
            try {
                const result = await request(`/api/sites/${state.selectedSiteId}/test`, {
                    method: 'POST',
                    body: JSON.stringify({ keyword }),
                });
                const previews = result.preview_results.map((item) => `
                    <article class="preview-item">
                        <strong>${item.title}</strong>
                        <div class="muted">图片地址：<a target="_blank" href="${item.image_url}">${item.image_url}</a></div>
                        <div class="muted">来源页面：<a target="_blank" href="${item.source_page_url}">${item.source_page_url}</a></div>
                    </article>
                `).join('');
                elements.testResult.innerHTML = `<div class="test-result success">${result.message}<div class="preview-list">${previews}</div></div>`;
                await loadSites();
            } catch (error) {
                elements.testResult.innerHTML = `<div class="test-result error">${error.message}</div>`;
            }
        }

        async function createTask(event) {
            event.preventDefault();
            const payload = {
                keyword: elements.crawlKeyword.value.trim(),
                target_scope: elements.crawlScope.value,
                target_site_codes: selectedSiteCodes(),
                per_site_limit: Number(elements.perSiteLimit.value || 3),
                max_pages: Number(elements.maxPages.value || 1),
                created_by: elements.createdBy.value.trim() || 'system',
            };
            if (payload.target_scope === 'selected' && !payload.target_site_codes.length) {
                showMessage(elements.crawlFormMessage, '指定站点模式下至少选择一个启用站点。', 'error');
                return;
            }
            try {
                showMessage(elements.crawlFormMessage, '正在创建并执行抓取任务...', 'info');
                const detail = await request('/api/crawl-tasks', {
                    method: 'POST',
                    body: JSON.stringify(payload),
                });
                showMessage(elements.crawlFormMessage, '抓取任务执行完成。', 'success');
                await loadTasks();
                renderTaskDetail(detail);
            } catch (error) {
                showMessage(elements.crawlFormMessage, error.message, 'error');
            }
        }

        async function loadTaskDetail(taskId) {
            try {
                const detail = await request(`/api/crawl-tasks/${taskId}`);
                renderTaskDetail(detail);
            } catch (error) {
                showMessage(elements.crawlListMessage, error.message, 'error');
            }
        }

        async function retryTask(taskId) {
            try {
                showMessage(elements.crawlListMessage, `正在重试任务 ${taskId}...`, 'info');
                const detail = await request(`/api/crawl-tasks/${taskId}/retry`, {
                    method: 'POST',
                    body: JSON.stringify({ site_codes: [] }),
                });
                showMessage(elements.crawlListMessage, `任务 ${taskId} 已重试完成。`, 'success');
                await loadTasks();
                renderTaskDetail(detail);
            } catch (error) {
                showMessage(elements.crawlListMessage, error.message, 'error');
            }
        }

        window.editSite = function(siteId) {
            const site = state.sites.find((item) => item.id === siteId);
            if (site) fillSiteForm(site);
        };

        window.toggleSite = async function(siteId, enabled) {
            try {
                await request(`/api/sites/${siteId}`, {
                    method: 'PUT',
                    body: JSON.stringify({ enabled }),
                });
                await loadSites();
                showMessage(elements.listMessage, `站点已${enabled ? '启用' : '停用'}。`, 'success');
            } catch (error) {
                showMessage(elements.listMessage, error.message, 'error');
            }
        };

        window.deleteSite = async function(siteId) {
            const site = state.sites.find((item) => item.id === siteId);
            if (!site) return;
            if (!window.confirm(`确认删除站点“${site.name}”吗？此操作不可恢复。`)) return;
            try {
                await request(`/api/sites/${siteId}`, { method: 'DELETE' });
                if (Number(elements.siteId.value) === siteId) resetSiteForm();
                await loadSites();
                showMessage(elements.listMessage, '站点删除成功。', 'success');
            } catch (error) {
                showMessage(elements.listMessage, error.message, 'error');
            }
        };

        window.loadTaskDetail = loadTaskDetail;
        window.retryTask = retryTask;

        elements.form.addEventListener('submit', saveSite);
        elements.resetButton.addEventListener('click', resetSiteForm);
        elements.refreshButton.addEventListener('click', loadSites);
        elements.testButton.addEventListener('click', runTest);
        elements.crawlForm.addEventListener('submit', createTask);
        elements.crawlRefreshButton.addEventListener('click', loadTasks);
        elements.crawlResetButton.addEventListener('click', () => {
            elements.crawlForm.reset();
            elements.perSiteLimit.value = 3;
            elements.maxPages.value = 2;
            elements.createdBy.value = 'admin';
            showMessage(elements.crawlFormMessage, '任务表单已重置。', 'info');
        });
        elements.retryTaskButton.addEventListener('click', () => {
            const taskId = Number(elements.retryTaskButton.dataset.taskId || 0);
            if (taskId) retryTask(taskId);
        });

        resetSiteForm();
        loadSites();
        loadTasks();
        '''
    ).strip() + "\n",
    "tests/conftest.py": dedent(
        '''
        import os
        import sys
        from pathlib import Path

        ROOT_DIR = Path(__file__).resolve().parents[1]
        TEST_DB = ROOT_DIR / "data" / "test.db"
        if TEST_DB.exists():
            TEST_DB.unlink()

        os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"

        if str(ROOT_DIR) not in sys.path:
            sys.path.insert(0, str(ROOT_DIR))
        '''
    ).strip() + "\n",
    "tests/test_crawl_tasks.py": dedent(
        '''
        from pathlib import Path

        from fastapi.testclient import TestClient

        from app.main import app


        client = TestClient(app)


        def create_site(name: str, code: str, domain: str):
            response = client.post(
                "/api/sites",
                json={
                    "name": name,
                    "code": code,
                    "domain": domain,
                    "enabled": True,
                    "search_rule": "/search?q={keyword}",
                    "parse_rule": "results[].url",
                    "page_rule": "page={page}",
                    "remark": f"{name} 默认测试站点",
                    "crawl_method": "API接口",
                },
            )
            assert response.status_code == 201


        def test_crawl_task_flow():
            create_site("OpenVerse", "openverse", "api.openverse.org")
            create_site("Wikimedia", "wikimedia", "commons.wikimedia.org")

            create_response = client.post(
                "/api/crawl-tasks",
                json={
                    "keyword": "春日花海",
                    "target_scope": "selected",
                    "target_site_codes": ["openverse", "wikimedia"],
                    "per_site_limit": 3,
                    "max_pages": 2,
                    "created_by": "pytest",
                },
            )
            assert create_response.status_code == 201
            body = create_response.json()
            assert body["status"] == "completed"
            assert body["total_count"] == 6
            assert body["success_count"] == 4
            assert body["duplicate_count"] == 2
            assert len(body["logs"]) == 2
            assert len(body["materials"]) == 4

            for material in body["materials"]:
                assert (Path("data") / material["local_file_path"]).exists()
                assert (Path("data") / material["local_thumbnail_path"]).exists()

            task_id = body["id"]
            detail_response = client.get(f"/api/crawl-tasks/{task_id}")
            assert detail_response.status_code == 200
            assert detail_response.json()["id"] == task_id

            retry_response = client.post(f"/api/crawl-tasks/{task_id}/retry", json={"site_codes": []})
            assert retry_response.status_code == 200
            retry_body = retry_response.json()
            assert retry_body["status"] == "completed"
            assert retry_body["total_count"] == 6
            assert retry_body["duplicate_count"] == 6
            assert len(retry_body["materials"]) == 4
        '''
    ).strip() + "\n",
}

for relative_path, content in FILES.items():
    target = BASE / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

print(f"generated {len(FILES)} files for crawl module")
