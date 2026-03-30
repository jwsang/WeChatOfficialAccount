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


class ArticleDraftUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(default="", max_length=500)
    author_name: str = Field(default="", max_length=100)
    source_url: str = Field(default="", max_length=500)
    cover_material_id: int | None = None
    template_code: Literal["image_gallery", "minimal_gallery", "mixed_graphic"] = "image_gallery"
    auto_sort: Literal["manual", "created_desc", "created_asc"] = "manual"
    materials: list[ArticleMaterialInput] = Field(min_length=1)
    content_html: str = ""
    draft_status: Literal["editing", "pending_publish"] = "editing"


class ArticleDraftListItemRead(BaseModel):
    id: int
    article_title: str
    article_summary: str
    cover_material_id: int | None = None
    cover_material_name: str = ""
    cover_local_thumbnail_path: str = ""
    template_code: str
    draft_status: str
    material_count: int = 0
    wx_draft_id: str | None = None
    wx_publish_id: str | None = None
    created_at: datetime
    updated_at: datetime


class WechatConfigStatusRead(BaseModel):
    app_id_configured: bool
    app_secret_configured: bool
    auth_ready: bool
    mode: str = "mock"
    message: str


class WechatPublishActionRead(BaseModel):
    action: Literal["sync", "publish"]
    draft: "ArticleDraftRead"
    uploaded_material_count: int = 0
    message: str


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
