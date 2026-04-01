from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MaterialCreate(BaseModel):
    material_name: str = Field(min_length=1, max_length=200)
    search_keyword: str = Field(default="", max_length=200)
    source_site_code: str = Field(default="manual", max_length=100)
    source_type: str = Field(default="manual", max_length=50)
    source_page_url: str = Field(default="")
    source_image_url: str = Field(default="")
    local_file_path: str = Field(min_length=1, max_length=500)
    local_thumbnail_path: str = Field(default="", max_length=500)
    image_hash: str = Field(min_length=1, max_length=64)
    image_width: int = Field(ge=1)
    image_height: int = Field(ge=1)
    material_status: str = Field(default="available", max_length=50)
    audit_status: str = Field(default="pending", max_length=50)
    used_count: int = Field(default=0, ge=0)
    tag_codes: str = Field(default="", max_length=500)
    crawl_task_id: int | None = None
    prompt_text: str = Field(default="")


class MaterialUpdate(BaseModel):
    material_name: str | None = Field(default=None, min_length=1, max_length=200)
    search_keyword: str | None = Field(default=None, max_length=200)
    source_site_code: str | None = Field(default=None, max_length=100)
    source_type: str | None = Field(default=None, max_length=50)
    source_page_url: str | None = Field(default=None)
    source_image_url: str | None = Field(default=None)
    local_file_path: str | None = Field(default=None, max_length=500)
    local_thumbnail_path: str | None = Field(default=None, max_length=500)
    image_hash: str | None = Field(default=None, max_length=64)
    image_width: int | None = Field(default=None, ge=1)
    image_height: int | None = Field(default=None, ge=1)
    material_status: str | None = Field(default=None, max_length=50)
    audit_status: str | None = Field(default=None, max_length=50)
    used_count: int | None = Field(default=None, ge=0)
    tag_codes: str | None = Field(default=None, max_length=500)
    crawl_task_id: int | None = None
    prompt_text: str | None = Field(default=None)


class MaterialRead(BaseModel):
    id: int
    material_name: str
    search_keyword: str
    source_site_code: str
    source_type: str
    source_page_url: str
    source_image_url: str
    local_file_path: str
    local_thumbnail_path: str
    image_hash: str
    image_width: int
    image_height: int
    material_status: str
    audit_status: str
    used_count: int
    tag_codes: str
    crawl_task_id: int | None
    prompt_text: str
    created_at: datetime
    updated_at: datetime


class MaterialTagSummaryRead(BaseModel):
    tag: str
    count: int


class MaterialUploadRead(BaseModel):
    uploaded: list[MaterialRead]
    duplicate_count: int = 0


class MaterialActionRequest(BaseModel):
    action: Literal[
        "audit",
        "delete",
    ]


class MaterialListFilters(BaseModel):
    query_text: str = ""
    keyword: str = ""
    source_site_code: str = ""
    source_type: str = ""
    material_status: str = ""
    audit_status: str = ""
    tag: str = ""
