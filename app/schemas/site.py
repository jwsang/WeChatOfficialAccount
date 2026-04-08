from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SiteRuleConfig(BaseModel):
    # HTML 解析模式字段
    search_url_template: str = ""
    result_container_path: str = ""
    image_url_path: str = ""
    source_page_url_path: str = ""
    title_path: str = ""
    pagination_param: str = "page"
    pagination_start: int = 1
    pagination_size_param: str = "limit"
    request_method: Literal["GET", "POST"] = "GET"
    request_headers: dict[str, str] = Field(default_factory=dict)
    request_query_template: dict[str, str] = Field(default_factory=dict)
    extra_notes: str = ""
    
    # API 接口模式字段（兼容旧版配置）
    api_key: str = ""
    items_path: str = ""
    title_field: str = ""
    image_field: str = ""
    page_field: str = ""
    
    # 通用爬虫字段（CSS 选择器）
    item_selector: str = ""
    image_selector: str = ""
    link_selector: str = ""


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
    rule_config: SiteRuleConfig = Field(default_factory=SiteRuleConfig)


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
    rule_config: SiteRuleConfig | None = None


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
    applied_rule_config: SiteRuleConfig


class SiteAiPrefillRequest(BaseModel):
    domain: str = Field(..., min_length=1, max_length=255)
    model_id: int | None = None


class SiteAiPrefillSuggestion(BaseModel):
    name: str = ""
    code: str = ""
    domain: str = ""
    enabled: bool = True
    search_rule: str = ""
    parse_rule: str = ""
    page_rule: str = ""
    remark: str = ""
    crawl_method: str = "HTML解析"
    rule_config: SiteRuleConfig = Field(default_factory=SiteRuleConfig)


class SiteAiPrefillResponse(BaseModel):
    domain: str
    success: bool
    message: str
    suggestion: SiteAiPrefillSuggestion
