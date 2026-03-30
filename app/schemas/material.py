from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


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
        "favorite",
        "unfavorite",
        "not_recommended",
        "restore",
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
