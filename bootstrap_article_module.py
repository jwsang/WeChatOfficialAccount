from pathlib import Path
from textwrap import dedent

BASE = Path(__file__).resolve().parent
FILES: dict[str, str] = {
    "app/models/article_draft.py": dedent(
        '''
        from datetime import UTC, datetime

        from sqlalchemy import DateTime, Integer, String, Text
        from sqlalchemy.orm import Mapped, mapped_column

        from app.models.base import Base


        class ArticleDraft(Base):
            __tablename__ = "article_drafts"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            article_title: Mapped[str] = mapped_column(String(200), nullable=False)
            cover_material_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
            article_summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
            author_name: Mapped[str] = mapped_column(String(100), default="", nullable=False)
            source_url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
            content_html: Mapped[str] = mapped_column(Text, default="", nullable=False)
            publish_payload: Mapped[str] = mapped_column(Text, default="", nullable=False)
            template_code: Mapped[str] = mapped_column(String(50), default="image_gallery", nullable=False)
            draft_status: Mapped[str] = mapped_column(String(30), default="editing", nullable=False)
            wx_draft_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
            wx_publish_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
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
    "app/models/draft_material_relation.py": dedent(
        '''
        from sqlalchemy import Integer, Text
        from sqlalchemy.orm import Mapped, mapped_column

        from app.models.base import Base


        class DraftMaterialRelation(Base):
            __tablename__ = "draft_material_relations"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            draft_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            material_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            sort_index: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
            caption_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
        '''
    ).strip() + "\n",
    "app/schemas/article.py": dedent(
        '''
        from datetime import datetime
        from typing import Any, Literal

        from pydantic import BaseModel, Field


        class ArticleMaterialInput(BaseModel):
            material_id: int
            caption_text: str = ""


        class ArticleMaterialRead(BaseModel):
            material_id: int
            material_name: str
            local_file_path: str
            local_thumbnail_path: str
            source_site_code: str
            source_type: str
            sort_index: int
            caption_text: str = ""


        class ArticleGenerateRequest(BaseModel):
            title: str = Field(min_length=1, max_length=200)
            summary: str = Field(default="", max_length=500)
            author_name: str = Field(default="", max_length=100)
            source_url: str = Field(default="", max_length=500)
            cover_material_id: int | None = None
            template_code: Literal["image_gallery", "minimal_gallery", "mixed_graphic"] = "image_gallery"
            auto_sort: Literal["manual", "created_desc", "created_asc"] = "manual"
            materials: list[ArticleMaterialInput] = Field(min_length=1)


        class ArticleDraftRead(BaseModel):
            id: int | None = None
            article_title: str
            cover_material_id: int
            article_summary: str
            author_name: str
            source_url: str
            content_html: str
            publish_payload: dict[str, Any]
            template_code: str
            draft_status: str
            wx_draft_id: str | None = None
            wx_publish_id: str | None = None
            materials: list[ArticleMaterialRead]
            created_at: datetime | None = None
            updated_at: datetime | None = None
        '''
    ).strip() + "\n",
    "app/repositories/article_repository.py": dedent(
        '''
        from sqlalchemy import select
        from sqlalchemy.orm import Session

        from app.models.article_draft import ArticleDraft
        from app.models.draft_material_relation import DraftMaterialRelation
        from app.models.material_image import MaterialImage


        class ArticleRepository:
            def __init__(self, db: Session):
                self.db = db

            def get_materials_by_ids(self, material_ids: list[int]) -> list[MaterialImage]:
                statement = select(MaterialImage).where(MaterialImage.id.in_(material_ids))
                return list(self.db.scalars(statement).all())

            def create_draft(self, payload: dict) -> ArticleDraft:
                draft = ArticleDraft(**payload)
                self.db.add(draft)
                self.db.flush()
                return draft

            def create_relations(self, payloads: list[dict]) -> list[DraftMaterialRelation]:
                relations = [DraftMaterialRelation(**payload) for payload in payloads]
                self.db.add_all(relations)
                self.db.flush()
                return relations

            def increase_material_usage(self, material_ids: list[int]) -> None:
                materials = self.get_materials_by_ids(material_ids)
                material_map = {material.id: material for material in materials}
                for material_id in material_ids:
                    material = material_map.get(material_id)
                    if material:
                        material.used_count += 1
                        self.db.add(material)

            def get_draft(self, draft_id: int) -> ArticleDraft | None:
                return self.db.get(ArticleDraft, draft_id)

            def list_relations(self, draft_id: int) -> list[DraftMaterialRelation]:
                statement = (
                    select(DraftMaterialRelation)
                    .where(DraftMaterialRelation.draft_id == draft_id)
                    .order_by(DraftMaterialRelation.sort_index.asc(), DraftMaterialRelation.id.asc())
                )
                return list(self.db.scalars(statement).all())

            def commit(self) -> None:
                self.db.commit()

            def rollback(self) -> None:
                self.db.rollback()

            def refresh(self, instance) -> None:
                self.db.refresh(instance)
        '''
    ).strip() + "\n",
    "app/services/article_service.py": dedent(
        '''
        from __future__ import annotations

        import json

        from fastapi import HTTPException, status
        from sqlalchemy.orm import Session

        from app.models.article_draft import ArticleDraft
        from app.models.material_image import MaterialImage
        from app.repositories.article_repository import ArticleRepository
        from app.schemas.article import ArticleDraftRead, ArticleGenerateRequest, ArticleMaterialRead


        class ArticleService:
            def __init__(self, db: Session):
                self.repository = ArticleRepository(db)

            def generate_preview(self, payload: ArticleGenerateRequest) -> ArticleDraftRead:
                ordered_materials = self._resolve_materials(payload)
                cover_material = self._resolve_cover_material(payload.cover_material_id, ordered_materials)
                content_html = self._build_content_html(payload, ordered_materials, cover_material)
                publish_payload = self._build_publish_payload(payload, ordered_materials, cover_material, content_html)
                return self._serialize_preview(payload, ordered_materials, cover_material.id, content_html, publish_payload)

            def save_draft(self, payload: ArticleGenerateRequest) -> ArticleDraftRead:
                ordered_materials = self._resolve_materials(payload)
                cover_material = self._resolve_cover_material(payload.cover_material_id, ordered_materials)
                content_html = self._build_content_html(payload, ordered_materials, cover_material)
                publish_payload = self._build_publish_payload(payload, ordered_materials, cover_material, content_html)

                try:
                    draft = self.repository.create_draft(
                        {
                            "article_title": payload.title,
                            "cover_material_id": cover_material.id,
                            "article_summary": payload.summary,
                            "author_name": payload.author_name,
                            "source_url": payload.source_url,
                            "content_html": content_html,
                            "publish_payload": json.dumps(publish_payload, ensure_ascii=False),
                            "template_code": payload.template_code,
                            "draft_status": "editing",
                            "wx_draft_id": None,
                            "wx_publish_id": None,
                        }
                    )
                    self.repository.create_relations(
                        [
                            {
                                "draft_id": draft.id,
                                "material_id": material.id,
                                "sort_index": sort_index,
                                "caption_text": caption_text,
                            }
                            for sort_index, material, caption_text in ordered_materials
                        ]
                    )
                    self.repository.increase_material_usage([material.id for _, material, _ in ordered_materials])
                    self.repository.commit()
                    self.repository.refresh(draft)
                except Exception:
                    self.repository.rollback()
                    raise

                relations = self.repository.list_relations(draft.id)
                relation_map = {relation.material_id: relation for relation in relations}
                materials = [
                    self._serialize_material(material, relation_map[material.id].sort_index, relation_map[material.id].caption_text)
                    for _, material, _ in ordered_materials
                ]
                return self._serialize_draft(draft, materials, publish_payload)

            def get_draft(self, draft_id: int) -> ArticleDraftRead:
                draft = self.repository.get_draft(draft_id)
                if not draft:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章草稿不存在")

                relations = self.repository.list_relations(draft_id)
                materials = self.repository.get_materials_by_ids([relation.material_id for relation in relations])
                material_map = {material.id: material for material in materials}
                material_reads = [
                    self._serialize_material(material_map[relation.material_id], relation.sort_index, relation.caption_text)
                    for relation in relations
                    if relation.material_id in material_map
                ]
                publish_payload = self._parse_publish_payload(draft.publish_payload)
                return self._serialize_draft(draft, material_reads, publish_payload)

            def _resolve_materials(self, payload: ArticleGenerateRequest) -> list[tuple[int, MaterialImage, str]]:
                selected_ids = [item.material_id for item in payload.materials]
                unique_ids = list(dict.fromkeys(selected_ids))
                material_list = self.repository.get_materials_by_ids(unique_ids)
                material_map = {material.id: material for material in material_list}

                missing_ids = [material_id for material_id in unique_ids if material_id not in material_map]
                if missing_ids:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"素材不存在：{', '.join(str(item) for item in missing_ids)}",
                    )

                for material in material_map.values():
                    if material.material_status == "deleted":
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"素材已删除：{material.id}")

                ordered: list[tuple[int, MaterialImage, str]] = [
                    (index, material_map[item.material_id], item.caption_text.strip())
                    for index, item in enumerate(payload.materials, start=1)
                ]

                if payload.auto_sort == "created_desc":
                    ordered = sorted(
                        ordered,
                        key=lambda item: (item[1].created_at, item[1].id),
                        reverse=True,
                    )
                elif payload.auto_sort == "created_asc":
                    ordered = sorted(
                        ordered,
                        key=lambda item: (item[1].created_at, item[1].id),
                    )

                return [
                    (sort_index, material, caption_text)
                    for sort_index, (_, material, caption_text) in enumerate(ordered, start=1)
                ]

            def _resolve_cover_material(
                self,
                cover_material_id: int | None,
                ordered_materials: list[tuple[int, MaterialImage, str]],
            ) -> MaterialImage:
                if not ordered_materials:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="至少选择一张素材")

                material_map = {material.id: material for _, material, _ in ordered_materials}
                final_cover_id = cover_material_id or ordered_materials[0][1].id
                cover_material = material_map.get(final_cover_id)
                if not cover_material:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="封面素材必须来自已选素材")
                return cover_material

            def _build_content_html(
                self,
                payload: ArticleGenerateRequest,
                ordered_materials: list[tuple[int, MaterialImage, str]],
                cover_material: MaterialImage,
            ) -> str:
                wrapper_style = self._wrapper_style(payload.template_code)
                header_html = f"""
                <section style=\"padding: 20px 0 16px; text-align: center;\">
                    <h1 style=\"margin: 0 0 12px; font-size: 28px; line-height: 1.4; color: #111827;\">{payload.title}</h1>
                    <div style=\"font-size: 14px; color: #64748b;\">作者：{payload.author_name or '系统生成'}</div>
                    <div style=\"margin-top: 12px; font-size: 15px; color: #334155; line-height: 1.8;\">{payload.summary or '精选图片内容，适配公众号阅读场景。'}</div>
                </section>
                <section style=\"margin-bottom: 24px;\">
                    <img src=\"/data/{cover_material.local_file_path}\" alt=\"{cover_material.material_name}\" style=\"width: 100%; border-radius: 16px; display: block;\" />
                </section>
                """.strip()

                blocks: list[str] = []
                for sort_index, material, caption_text in ordered_materials:
                    caption = caption_text or material.material_name
                    if payload.template_code == "minimal_gallery":
                        block = f"""
                        <section style=\"padding: 28px 0; border-top: 1px solid #e2e8f0;\">
                            <img src=\"/data/{material.local_file_path}\" alt=\"{material.material_name}\" style=\"width: 100%; display: block; background: #f8fafc;\" />
                            <p style=\"margin: 16px 0 0; text-align: center; color: #475569; font-size: 14px; line-height: 1.8;\">{sort_index}. {caption}</p>
                        </section>
                        """.strip()
                    elif payload.template_code == "mixed_graphic":
                        block = f"""
                        <section style=\"padding: 20px 0; border-top: 1px dashed #cbd5e1;\">
                            <p style=\"margin: 0 0 14px; color: #334155; font-size: 15px; line-height: 1.9;\">{caption}</p>
                            <img src=\"/data/{material.local_file_path}\" alt=\"{material.material_name}\" style=\"width: 100%; border-radius: 12px; display: block;\" />
                        </section>
                        """.strip()
                    else:
                        block = f"""
                        <section style=\"padding: 24px 0; border-top: 1px solid #e5e7eb;\">
                            <img src=\"/data/{material.local_file_path}\" alt=\"{material.material_name}\" style=\"width: 100%; border-radius: 14px; display: block;\" />
                            <p style=\"margin: 14px 0 0; text-align: center; color: #475569; font-size: 14px; line-height: 1.8;\">{caption}</p>
                        </section>
                        """.strip()
                    blocks.append(block)

                source_html = (
                    f'<p style="margin-top: 24px; color: #64748b; font-size: 13px; text-align: center;">原文链接：<a href="{payload.source_url}" target="_blank">{payload.source_url}</a></p>'
                    if payload.source_url
                    else ""
                )

                return f"""
                <article style=\"{wrapper_style}\">
                    {header_html}
                    {''.join(blocks)}
                    {source_html}
                </article>
                """.strip()

            def _build_publish_payload(
                self,
                payload: ArticleGenerateRequest,
                ordered_materials: list[tuple[int, MaterialImage, str]],
                cover_material: MaterialImage,
                content_html: str,
            ) -> dict:
                return {
                    "articles": [
                        {
                            "title": payload.title,
                            "author": payload.author_name,
                            "digest": payload.summary,
                            "content": content_html,
                            "content_source_url": payload.source_url,
                            "thumb_media_material_id": None,
                            "cover_material_id": cover_material.id,
                            "template_code": payload.template_code,
                            "article_materials": [
                                {
                                    "material_id": material.id,
                                    "material_name": material.material_name,
                                    "sort_index": sort_index,
                                    "caption_text": caption_text,
                                    "local_file_path": material.local_file_path,
                                    "source_site_code": material.source_site_code,
                                }
                                for sort_index, material, caption_text in ordered_materials
                            ],
                        }
                    ]
                }

            def _serialize_preview(
                self,
                payload: ArticleGenerateRequest,
                ordered_materials: list[tuple[int, MaterialImage, str]],
                cover_material_id: int,
                content_html: str,
                publish_payload: dict,
            ) -> ArticleDraftRead:
                return ArticleDraftRead(
                    id=None,
                    article_title=payload.title,
                    cover_material_id=cover_material_id,
                    article_summary=payload.summary,
                    author_name=payload.author_name,
                    source_url=payload.source_url,
                    content_html=content_html,
                    publish_payload=publish_payload,
                    template_code=payload.template_code,
                    draft_status="preview",
                    wx_draft_id=None,
                    wx_publish_id=None,
                    materials=[
                        self._serialize_material(material, sort_index, caption_text)
                        for sort_index, material, caption_text in ordered_materials
                    ],
                    created_at=None,
                    updated_at=None,
                )

            def _serialize_draft(
                self,
                draft: ArticleDraft,
                materials: list[ArticleMaterialRead],
                publish_payload: dict,
            ) -> ArticleDraftRead:
                return ArticleDraftRead(
                    id=draft.id,
                    article_title=draft.article_title,
                    cover_material_id=draft.cover_material_id or 0,
                    article_summary=draft.article_summary,
                    author_name=draft.author_name,
                    source_url=draft.source_url,
                    content_html=draft.content_html,
                    publish_payload=publish_payload,
                    template_code=draft.template_code,
                    draft_status=draft.draft_status,
                    wx_draft_id=draft.wx_draft_id,
                    wx_publish_id=draft.wx_publish_id,
                    materials=materials,
                    created_at=draft.created_at,
                    updated_at=draft.updated_at,
                )

            def _serialize_material(self, material: MaterialImage, sort_index: int, caption_text: str) -> ArticleMaterialRead:
                return ArticleMaterialRead(
                    material_id=material.id,
                    material_name=material.material_name,
                    local_file_path=material.local_file_path,
                    local_thumbnail_path=material.local_thumbnail_path,
                    source_site_code=material.source_site_code,
                    source_type=material.source_type,
                    sort_index=sort_index,
                    caption_text=caption_text,
                )

            def _parse_publish_payload(self, raw_payload: str) -> dict:
                try:
                    payload = json.loads(raw_payload) if raw_payload else {}
                    return payload if isinstance(payload, dict) else {}
                except json.JSONDecodeError:
                    return {}

            def _wrapper_style(self, template_code: str) -> str:
                if template_code == "minimal_gallery":
                    return "max-width: 760px; margin: 0 auto; padding: 36px 24px; background: #ffffff; color: #0f172a;"
                if template_code == "mixed_graphic":
                    return "max-width: 760px; margin: 0 auto; padding: 32px 24px; background: linear-gradient(180deg, #ffffff, #f8fafc); color: #0f172a;"
                return "max-width: 760px; margin: 0 auto; padding: 32px 24px; background: #ffffff; color: #0f172a;"
        '''
    ).strip() + "\n",
    "app/api/article_routes.py": dedent(
        '''
        from fastapi import APIRouter, Depends, status
        from sqlalchemy.orm import Session

        from app.db.session import get_db
        from app.schemas.article import ArticleDraftRead, ArticleGenerateRequest
        from app.services.article_service import ArticleService


        router = APIRouter(prefix="/api/articles", tags=["articles"])


        def get_article_service(db: Session = Depends(get_db)) -> ArticleService:
            return ArticleService(db)


        @router.post("/preview", response_model=ArticleDraftRead)
        def generate_article_preview(
            payload: ArticleGenerateRequest,
            service: ArticleService = Depends(get_article_service),
        ):
            return service.generate_preview(payload)


        @router.post("/drafts", response_model=ArticleDraftRead, status_code=status.HTTP_201_CREATED)
        def save_article_draft(
            payload: ArticleGenerateRequest,
            service: ArticleService = Depends(get_article_service),
        ):
            return service.save_draft(payload)


        @router.get("/drafts/{draft_id}", response_model=ArticleDraftRead)
        def get_article_draft(
            draft_id: int,
            service: ArticleService = Depends(get_article_service),
        ):
            return service.get_draft(draft_id)
        '''
    ).strip() + "\n",
    "tests/test_articles.py": dedent(
        '''
        import io

        from fastapi.testclient import TestClient
        from PIL import Image

        from app.main import app


        client = TestClient(app)


        def build_image_bytes(color: tuple[int, int, int]) -> bytes:
            image = Image.new("RGB", (640, 480), color=color)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            return buffer.getvalue()


        def ensure_article_materials() -> list[dict]:
            upload_response = client.post(
                "/api/materials/upload",
                data={
                    "title": "组稿素材",
                    "keywords": "文章生成 测试",
                    "remark": "文章生成测试素材",
                    "tags": "文章 组稿 测试",
                },
                files=[
                    ("files", ("article-1.png", build_image_bytes((12, 120, 220)), "image/png")),
                    ("files", ("article-2.png", build_image_bytes((120, 220, 12)), "image/png")),
                    ("files", ("article-3.png", build_image_bytes((220, 120, 12)), "image/png")),
                ],
            )
            assert upload_response.status_code == 200
            uploaded = upload_response.json()["uploaded"]
            assert len(uploaded) == 3
            return uploaded


        def test_article_generate_and_save_flow():
            materials = ensure_article_materials()
            first, second, third = materials

            preview_response = client.post(
                "/api/articles/preview",
                json={
                    "title": "春日花海图集",
                    "summary": "适合公众号发布的纯图片欣赏内容。",
                    "author_name": "Roo",
                    "source_url": "https://example.com/source",
                    "cover_material_id": second["id"],
                    "template_code": "image_gallery",
                    "auto_sort": "manual",
                    "materials": [
                        {"material_id": second["id"], "caption_text": "第二张作为封面"},
                        {"material_id": first["id"], "caption_text": "第一张作为正文"},
                        {"material_id": third["id"], "caption_text": "第三张作为结尾"},
                    ],
                },
            )
            assert preview_response.status_code == 200
            preview_body = preview_response.json()
            assert preview_body["draft_status"] == "preview"
            assert preview_body["cover_material_id"] == second["id"]
            assert len(preview_body["materials"]) == 3
            assert "春日花海图集" in preview_body["content_html"]
            assert preview_body["publish_payload"]["articles"][0]["template_code"] == "image_gallery"

            before_detail = client.get(f"/api/materials/{first['id']}")
            assert before_detail.status_code == 200
            before_used_count = before_detail.json()["used_count"]

            save_response = client.post(
                "/api/articles/drafts",
                json={
                    "title": "春日花海图集",
                    "summary": "适合公众号发布的纯图片欣赏内容。",
                    "author_name": "Roo",
                    "source_url": "https://example.com/source",
                    "cover_material_id": second["id"],
                    "template_code": "minimal_gallery",
                    "auto_sort": "created_desc",
                    "materials": [
                        {"material_id": first["id"], "caption_text": "第一张作为正文"},
                        {"material_id": second["id"], "caption_text": "第二张作为封面"},
                        {"material_id": third["id"], "caption_text": "第三张作为结尾"},
                    ],
                },
            )
            assert save_response.status_code == 201
            save_body = save_response.json()
            assert save_body["id"] >= 1
            assert save_body["draft_status"] == "editing"
            assert save_body["template_code"] == "minimal_gallery"
            assert len(save_body["materials"]) == 3
            assert save_body["publish_payload"]["articles"][0]["cover_material_id"] == second["id"]

            draft_id = save_body["id"]
            detail_response = client.get(f"/api/articles/drafts/{draft_id}")
            assert detail_response.status_code == 200
            detail_body = detail_response.json()
            assert detail_body["id"] == draft_id
            assert detail_body["article_title"] == "春日花海图集"
            assert len(detail_body["materials"]) == 3
            assert detail_body["materials"][0]["sort_index"] == 1
            assert "https://example.com/source" in detail_body["content_html"]

            after_detail = client.get(f"/api/materials/{first['id']}")
            assert after_detail.status_code == 200
            assert after_detail.json()["used_count"] == before_used_count + 1
        '''
    ).strip() + "\n",
    "app/models/__init__.py": dedent(
        '''
        from app.models.article_draft import ArticleDraft
        from app.models.base import Base
        from app.models.crawl_task import CrawlTask
        from app.models.crawl_task_log import CrawlTaskLog
        from app.models.draft_material_relation import DraftMaterialRelation
        from app.models.material_image import MaterialImage
        from app.models.site_config import SiteConfig
        '''
    ).strip() + "\n",
    "app/main.py": dedent(
        '''
        from fastapi import FastAPI, Request
        from fastapi.responses import HTMLResponse
        from fastapi.staticfiles import StaticFiles
        from fastapi.templating import Jinja2Templates

        from app.api.article_routes import router as article_router
        from app.api.crawl_routes import router as crawl_router
        from app.api.material_routes import router as material_router
        from app.api.site_routes import router as site_router
        from app.core.config import DATA_DIR, STATIC_DIR, TEMPLATE_DIR, settings
        from app.db.session import engine
        from app.models import Base


        Base.metadata.create_all(bind=engine)

        app = FastAPI(title=settings.app_name, version="0.4.0")
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
        app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")
        templates = Jinja2Templates(directory=TEMPLATE_DIR)
        app.include_router(site_router)
        app.include_router(crawl_router)
        app.include_router(material_router)
        app.include_router(article_router)


        @app.get("/", response_class=HTMLResponse)
        def index(request: Request):
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={"app_name": settings.app_name},
            )
        '''
    ).strip() + "\n",
}

for relative_path, content in FILES.items():
    target = BASE / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

print(f"generated {len(FILES)} files for article module")
