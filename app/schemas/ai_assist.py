from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.material import MaterialRead


class AiAssistConfigRead(BaseModel):
    base_url: str
    model: str
    default_size: str = "1024x1024"
    default_quality: str = "standard"
    default_style: str = "vivid"
    default_count: int = Field(default=4, ge=1, le=6)
    timeout_seconds: int = Field(default=120, ge=20, le=300)
    default_negative_prompt: str = ""
    has_api_key: bool = False
    api_key_masked: str = ""


class AiAssistConfigUpdateRequest(BaseModel):
    base_url: str = Field(..., min_length=1, max_length=255)
    model: str = Field(..., min_length=1, max_length=120)
    default_size: str = Field(default="1024x1024", min_length=3, max_length=30)
    default_quality: str = Field(default="standard", min_length=1, max_length=30)
    default_style: str = Field(default="vivid", min_length=1, max_length=30)
    default_count: int = Field(default=4, ge=1, le=6)
    timeout_seconds: int = Field(default=120, ge=20, le=300)
    default_negative_prompt: str = Field(default="", max_length=2000)
    api_key: str = ""


class AiAssistGeneratedImageRead(BaseModel):
    temp_id: str
    preview_url: str
    local_file_path: str
    width: int
    height: int
    created_at: datetime
    prompt: str


class AiAssistGenerateRead(BaseModel):
    generated: list[AiAssistGeneratedImageRead]


class AiAssistAddToMaterialRequest(BaseModel):
    temp_ids: list[str]
    title_prefix: str = "AI素材"
    keywords: str = ""
    tags: str = "AI"
    remark: str = ""


class AiAssistAddToMaterialRead(BaseModel):
    uploaded: list[MaterialRead]
    duplicate_count: int = 0
    missing_count: int = 0
