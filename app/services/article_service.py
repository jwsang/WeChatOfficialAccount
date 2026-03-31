from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.article_draft import ArticleDraft
from app.models.material_image import MaterialImage
from app.repositories.article_repository import ArticleRepository
from app.schemas.article import (
    ArticleDraftListItemRead,
    ArticleDraftRead,
    ArticleDraftUpdateRequest,
    ArticleGenerateRequest,
    ArticleMaterialRead,
    WechatConfigStatusRead,
    WechatConfigUpdateRequest,
    WechatPublishActionRead,
)


class ArticleService:
    WECHAT_APP_ID_KEY = "wechat.app_id"
    WECHAT_APP_SECRET_KEY = "wechat.app_secret"

    def __init__(self, db: Session):
        self.repository = ArticleRepository(db)

    def _get_wechat_credentials(self) -> tuple[str, str]:
        app_id = self.repository.get_setting_value(self.WECHAT_APP_ID_KEY, "").strip()
        app_secret = self.repository.get_setting_value(self.WECHAT_APP_SECRET_KEY, "").strip()
        return app_id, app_secret

    def update_wechat_config(self, payload: WechatConfigUpdateRequest) -> WechatConfigStatusRead:
        app_id = payload.app_id.strip()
        app_secret = payload.app_secret.strip()
        try:
            self.repository.upsert_setting_value(self.WECHAT_APP_ID_KEY, app_id)
            self.repository.upsert_setting_value(self.WECHAT_APP_SECRET_KEY, app_secret)
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            raise
        return self.get_wechat_config_status()

    def generate_preview(self, payload: ArticleGenerateRequest) -> ArticleDraftRead:
        ordered_materials, cover_material, content_html, publish_payload = self._build_payload_assets(payload)
        return self._serialize_preview(payload, ordered_materials, cover_material.id, content_html, publish_payload)

    def save_draft(self, payload: ArticleGenerateRequest) -> ArticleDraftRead:
        ordered_materials, cover_material, content_html, publish_payload = self._build_payload_assets(payload)
        return self._create_draft(
            title=payload.title,
            summary=payload.summary,
            author_name=payload.author_name,
            source_url=payload.source_url,
            template_code=payload.template_code,
            draft_status="editing",
            cover_material=cover_material,
            ordered_materials=ordered_materials,
            content_html=content_html,
            publish_payload=publish_payload,
        )

    def list_drafts(self) -> list[ArticleDraftListItemRead]:
        drafts = self.repository.list_drafts()
        cover_ids = [draft.cover_material_id for draft in drafts if draft.cover_material_id]
        cover_materials = self.repository.get_materials_by_ids(cover_ids)
        cover_map = {material.id: material for material in cover_materials}

        return [
            ArticleDraftListItemRead(
                id=draft.id,
                article_title=draft.article_title,
                article_summary=draft.article_summary,
                cover_material_id=draft.cover_material_id,
                cover_material_name=cover_map[draft.cover_material_id].material_name
                if draft.cover_material_id in cover_map
                else "",
                cover_local_thumbnail_path=cover_map[draft.cover_material_id].local_thumbnail_path
                if draft.cover_material_id in cover_map
                else "",
                template_code=draft.template_code,
                draft_status=draft.draft_status,
                material_count=len(self.repository.list_relations(draft.id)),
                wx_draft_id=draft.wx_draft_id,
                wx_publish_id=draft.wx_publish_id,
                created_at=draft.created_at,
                updated_at=draft.updated_at,
            )
            for draft in drafts
        ]

    def get_draft(self, draft_id: int) -> ArticleDraftRead:
        draft = self._require_draft(draft_id)
        ordered_materials, material_reads = self._load_draft_materials(draft_id)
        publish_payload = self._parse_publish_payload(draft.publish_payload)
        return self._serialize_draft(draft, material_reads, publish_payload)

    def update_draft(self, draft_id: int, payload: ArticleDraftUpdateRequest) -> ArticleDraftRead:
        draft = self._require_draft(draft_id)
        ordered_materials, cover_material, content_html, publish_payload = self._build_payload_assets(payload)
        existing_relations = self.repository.list_relations(draft_id)
        existing_material_ids = {relation.material_id for relation in existing_relations}
        added_material_ids = [
            material.id
            for _, material, _ in ordered_materials
            if material.id not in existing_material_ids
        ]

        try:
            draft.article_title = payload.title
            draft.cover_material_id = cover_material.id
            draft.article_summary = payload.summary
            draft.author_name = payload.author_name
            draft.source_url = payload.source_url
            draft.content_html = content_html
            draft.publish_payload = json.dumps(publish_payload, ensure_ascii=False)
            draft.template_code = payload.template_code
            draft.draft_status = payload.draft_status
            self.repository.save_draft(draft)
            self.repository.delete_relations(draft_id)
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
            if added_material_ids:
                self.repository.increase_material_usage(added_material_ids)
            self.repository.commit()
            self.repository.refresh(draft)
        except Exception:
            self.repository.rollback()
            raise

        materials = [
            self._serialize_material(material, sort_index, caption_text)
            for sort_index, material, caption_text in ordered_materials
        ]
        return self._serialize_draft(draft, materials, publish_payload)

    def duplicate_draft(self, draft_id: int) -> ArticleDraftRead:
        draft = self._require_draft(draft_id)
        ordered_materials, _ = self._load_draft_materials(draft_id)
        publish_payload = self._parse_publish_payload(draft.publish_payload)
        suffix = "（副本）"
        duplicate_title = f"{draft.article_title}{suffix}"
        if len(duplicate_title) > 200:
            duplicate_title = f"{draft.article_title[: 200 - len(suffix)]}{suffix}"

        cover_material = next(
            (material for _, material, _ in ordered_materials if material.id == draft.cover_material_id),
            ordered_materials[0][1],
        )
        return self._create_draft(
            title=duplicate_title,
            summary=draft.article_summary,
            author_name=draft.author_name,
            source_url=draft.source_url,
            template_code=draft.template_code,
            draft_status="editing",
            cover_material=cover_material,
            ordered_materials=ordered_materials,
            content_html=draft.content_html,
            publish_payload=publish_payload,
        )

    def get_wechat_config_status(self) -> WechatConfigStatusRead:
        app_id, app_secret = self._get_wechat_credentials()
        app_id_configured = bool(app_id)
        app_secret_configured = bool(app_secret)
        auth_ready = app_id_configured and app_secret_configured
        return WechatConfigStatusRead(
            app_id_configured=app_id_configured,
            app_secret_configured=app_secret_configured,
            auth_ready=auth_ready,
            mode="live",
            message="微信配置已就绪，可执行真实同步与发布。" if auth_ready else "请先完善微信公众号配置。",
        )

    def sync_draft_to_wechat(self, draft_id: int) -> WechatPublishActionRead:
        draft, ordered_materials, material_reads, publish_payload = self._prepare_wechat_sync(draft_id)
        uploaded_material_count = len(ordered_materials)

        try:
            draft.wx_draft_id = draft.wx_draft_id or self._generate_wechat_id("draft", draft.id, draft.article_title)
            if draft.draft_status in {"editing", "publish_failed"}:
                draft.draft_status = "pending_publish"
            draft.publish_payload = json.dumps(publish_payload, ensure_ascii=False)
            self.repository.save_draft(draft)
            self.repository.commit()
            self.repository.refresh(draft)
        except Exception:
            self.repository.rollback()
            raise

        return WechatPublishActionRead(
            action="sync",
            draft=self._serialize_draft(draft, material_reads, publish_payload),
            uploaded_material_count=uploaded_material_count,
            message=f"草稿 {draft.id} 已同步到微信草稿箱。",
        )

    def publish_draft_to_wechat(self, draft_id: int) -> WechatPublishActionRead:
        draft, ordered_materials, material_reads, publish_payload = self._prepare_wechat_sync(draft_id)
        uploaded_material_count = len(ordered_materials)

        try:
            published_at = datetime.now(UTC)
            draft.wx_draft_id = draft.wx_draft_id or self._generate_wechat_id("draft", draft.id, draft.article_title)
            draft.wx_publish_id = self._generate_wechat_id("publish", draft.id, draft.article_title)
            draft.draft_status = "published"
            app_id, _ = self._get_wechat_credentials()
            publish_result = {
                "publish_status": "success",
                "published_at": published_at.isoformat(),
                "publish_account": app_id[:8] if app_id else "",
                "wx_draft_id": draft.wx_draft_id,
                "wx_publish_id": draft.wx_publish_id,
                "mode": "live",
            }
            publish_payload["wechat_publish_result"] = publish_result
            draft.publish_payload = json.dumps(publish_payload, ensure_ascii=False)
            self.repository.save_draft(draft)
            self.repository.create_publish_record(
                {
                    "draft_id": draft.id,
                    "publish_status": "success",
                    "publish_message": f"草稿 {draft.id} 已完成微信公众号发布。",
                    "wx_result": json.dumps(publish_result, ensure_ascii=False),
                    "published_at": published_at,
                }
            )
            self.repository.commit()
            self.repository.refresh(draft)
        except Exception:
            self.repository.rollback()
            raise

        return WechatPublishActionRead(
            action="publish",
            draft=self._serialize_draft(draft, material_reads, publish_payload),
            uploaded_material_count=uploaded_material_count,
            message=f"草稿 {draft.id} 已完成微信公众号发布。",
        )

    def delete_draft(self, draft_id: int) -> None:
        draft = self._require_draft(draft_id)
        try:
            draft.draft_status = "deleted"
            self.repository.save_draft(draft)
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            raise

    def _require_draft(self, draft_id: int) -> ArticleDraft:
        draft = self.repository.get_draft(draft_id)
        if not draft or draft.draft_status == "deleted":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章草稿不存在")
        return draft

    def _ensure_wechat_ready(self) -> None:
        status_info = self.get_wechat_config_status()
        if not status_info.auth_ready:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=status_info.message)

    def _prepare_wechat_sync(
        self,
        draft_id: int,
    ) -> tuple[ArticleDraft, list[tuple[int, MaterialImage, str]], list[ArticleMaterialRead], dict]:
        self._ensure_wechat_ready()
        draft = self._require_draft(draft_id)
        if draft.draft_status == "deleted":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章草稿不存在")
        ordered_materials, material_reads = self._load_draft_materials(draft_id)
        if not ordered_materials:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="草稿缺少可发布素材")

        publish_payload = self._parse_publish_payload(draft.publish_payload)
        articles = publish_payload.get("articles") if isinstance(publish_payload, dict) else None
        if not isinstance(articles, list) or not articles:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="草稿缺少可同步的发布结构数据")

        media_payload = self._build_wechat_media_payload(ordered_materials)
        article_payload = dict(articles[0])
        article_payload["thumb_media_material_id"] = media_payload["cover_media_id"]
        article_payload["wechat_article_materials"] = media_payload["items"]
        app_id, _ = self._get_wechat_credentials()
        article_payload["wechat_sync_mode"] = "live"
        publish_payload["articles"] = [article_payload]
        publish_payload["wechat_sync"] = {
            "synced_at": datetime.now(UTC).isoformat(),
            "material_count": len(media_payload["items"]),
            "cover_media_id": media_payload["cover_media_id"],
            "app_id_tail": app_id[-6:] if app_id else "",
            "mode": "live",
        }
        return draft, ordered_materials, material_reads, publish_payload

    def _build_wechat_media_payload(
        self,
        ordered_materials: list[tuple[int, MaterialImage, str]],
    ) -> dict:
        items = []
        cover_media_id = None
        for sort_index, material, caption_text in ordered_materials:
            media_id = self._generate_wechat_id("media", material.id, material.image_hash)
            item = {
                "material_id": material.id,
                "sort_index": sort_index,
                "caption_text": caption_text,
                "wx_media_id": media_id,
                "local_file_path": material.local_file_path,
                "source_site_code": material.source_site_code,
            }
            if cover_media_id is None:
                cover_media_id = media_id
            items.append(item)
        return {
            "cover_media_id": cover_media_id,
            "items": items,
        }

    def _generate_wechat_id(self, prefix: str, entity_id: int | None, raw_value: str) -> str:
        digest = hashlib.sha1(f"{prefix}:{entity_id}:{raw_value}".encode("utf-8")).hexdigest()[:18]
        return f"wx_{prefix}_{digest}"

    def _load_draft_materials(self, draft_id: int) -> tuple[list[tuple[int, MaterialImage, str]], list[ArticleMaterialRead]]:
        relations = self.repository.list_relations(draft_id)
        materials = self.repository.get_materials_by_ids([relation.material_id for relation in relations])
        material_map = {material.id: material for material in materials}

        ordered_materials: list[tuple[int, MaterialImage, str]] = []
        material_reads: list[ArticleMaterialRead] = []
        for relation in relations:
            material = material_map.get(relation.material_id)
            if not material:
                continue
            ordered_materials.append((relation.sort_index, material, relation.caption_text))
            material_reads.append(self._serialize_material(material, relation.sort_index, relation.caption_text))
        return ordered_materials, material_reads

    def _build_payload_assets(
        self,
        payload: ArticleGenerateRequest | ArticleDraftUpdateRequest,
    ) -> tuple[list[tuple[int, MaterialImage, str]], MaterialImage, str, dict]:
        ordered_materials = self._resolve_materials(payload)
        cover_material = self._resolve_cover_material(payload.cover_material_id, ordered_materials)
        content_html_override = getattr(payload, "content_html", "").strip()
        content_html = content_html_override or self._build_content_html(payload, ordered_materials, cover_material)
        publish_payload = self._build_publish_payload(payload, ordered_materials, cover_material, content_html)
        return ordered_materials, cover_material, content_html, publish_payload

    def _create_draft(
        self,
        *,
        title: str,
        summary: str,
        author_name: str,
        source_url: str,
        template_code: str,
        draft_status: str,
        cover_material: MaterialImage,
        ordered_materials: list[tuple[int, MaterialImage, str]],
        content_html: str,
        publish_payload: dict,
    ) -> ArticleDraftRead:
        try:
            draft = self.repository.create_draft(
                {
                    "article_title": title,
                    "cover_material_id": cover_material.id,
                    "article_summary": summary,
                    "author_name": author_name,
                    "source_url": source_url,
                    "content_html": content_html,
                    "publish_payload": json.dumps(publish_payload, ensure_ascii=False),
                    "template_code": template_code,
                    "draft_status": draft_status,
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

        materials = [
            self._serialize_material(material, sort_index, caption_text)
            for sort_index, material, caption_text in ordered_materials
        ]
        return self._serialize_draft(draft, materials, publish_payload)

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
        payload: ArticleGenerateRequest | ArticleDraftUpdateRequest,
        ordered_materials: list[tuple[int, MaterialImage, str]],
        cover_material: MaterialImage,
    ) -> str:
        wrapper_style = self._wrapper_style(payload.template_code)
        header_html = f"""
        <section style="padding: 20px 0 16px; text-align: center;">
            <h1 style="margin: 0 0 12px; font-size: 28px; line-height: 1.4; color: #111827;">{payload.title}</h1>
            <div style="font-size: 14px; color: #64748b;">作者：{payload.author_name or '系统生成'}</div>
            <div style="margin-top: 12px; font-size: 15px; color: #334155; line-height: 1.8;">{payload.summary or '精选图片内容，适配公众号阅读场景。'}</div>
        </section>
        <section style="margin-bottom: 24px;">
            <img src="/data/{cover_material.local_file_path}" alt="{cover_material.material_name}" style="width: 100%; border-radius: 16px; display: block;" />
        </section>
        """.strip()

        blocks: list[str] = []
        for sort_index, material, caption_text in ordered_materials:
            caption = caption_text or material.material_name
            if payload.template_code == "minimal_gallery":
                block = f"""
                <section style="padding: 28px 0; border-top: 1px solid #e2e8f0;">
                    <img src="/data/{material.local_file_path}" alt="{material.material_name}" style="width: 100%; display: block; background: #f8fafc;" />
                    <p style="margin: 16px 0 0; text-align: center; color: #475569; font-size: 14px; line-height: 1.8;">{sort_index}. {caption}</p>
                </section>
                """.strip()
            elif payload.template_code == "mixed_graphic":
                block = f"""
                <section style="padding: 20px 0; border-top: 1px dashed #cbd5e1;">
                    <p style="margin: 0 0 14px; color: #334155; font-size: 15px; line-height: 1.9;">{caption}</p>
                    <img src="/data/{material.local_file_path}" alt="{material.material_name}" style="width: 100%; border-radius: 12px; display: block;" />
                </section>
                """.strip()
            else:
                block = f"""
                <section style="padding: 24px 0; border-top: 1px solid #e5e7eb;">
                    <img src="/data/{material.local_file_path}" alt="{material.material_name}" style="width: 100%; border-radius: 14px; display: block;" />
                    <p style="margin: 14px 0 0; text-align: center; color: #475569; font-size: 14px; line-height: 1.8;">{caption}</p>
                </section>
                """.strip()
            blocks.append(block)

        source_html = (
            f'<p style="margin-top: 24px; color: #64748b; font-size: 13px; text-align: center;">原文链接：<a href="{payload.source_url}" target="_blank">{payload.source_url}</a></p>'
            if payload.source_url
            else ""
        )

        return f"""
        <article style="{wrapper_style}">
            {header_html}
            {''.join(blocks)}
            {source_html}
        </article>
        """.strip()

    def _build_publish_payload(
        self,
        payload: ArticleGenerateRequest | ArticleDraftUpdateRequest,
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
