from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MaterialVideoCreate(BaseModel):
    material_name: str = Field(min_length=1, max_length=200)
    search_keyword: str = Field(default="", max_length=200)
    source_site_code: str = Field(default="manual", max_length=100)
    source_type: str = Field(default="manual", max_length=50)
    source_page_url: str = Field(default="")
    source_video_url: str = Field(default="")
    local_file_path: str = Field(min_length=1, max_length=500)
    local_thumbnail_path: str = Field(default="", max_length=500)
    video_hash: str = Field(min_length=1, max_length=64)
    video_width: int = Field(ge=1)
    video_height: int = Field(ge=1)
    video_duration: float = Field(default=0.0, ge=0.0)
    file_size: int = Field(default=0, ge=0)
    video_format: str = Field(default="mp4", max_length=20)
    material_status: str = Field(default="available", max_length=50)
    audit_status: str = Field(default="pending", max_length=50)
    used_count: int = Field(default=0, ge=0)
    tag_codes: str = Field(default="", max_length=500)
    crawl_task_id: int | None = None


class MaterialVideoRead(BaseModel):
    id: int
    material_name: str
    search_keyword: str
    source_site_code: str
    source_type: str
    source_page_url: str
    source_video_url: str
    local_file_path: str
    local_thumbnail_path: str
    video_hash: str
    video_width: int
    video_height: int
    video_duration: float
    file_size: int
    video_format: str
    material_status: str
    audit_status: str
    used_count: int
    tag_codes: str
    crawl_task_id: int | None
    created_at: datetime
    updated_at: datetime


class MaterialVideoUploadRead(BaseModel):
    uploaded: list[MaterialVideoRead]
    duplicate_count: int = 0


class MaterialVideoListFilters(BaseModel):
    query_text: str = ""
    keyword: str = ""
    source_site_code: str = ""
    source_type: str = ""
    material_status: str = ""
    audit_status: str = ""
    tag: str = ""
