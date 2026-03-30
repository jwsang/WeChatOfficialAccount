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
