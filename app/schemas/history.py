from datetime import datetime

from pydantic import BaseModel, Field


class HistoryArticleSummaryRead(BaseModel):
    total_generated: int
    total_published: int
    total_drafts: int


class HistoryMaterialSummaryRead(BaseModel):
    total_materials: int
    unused_materials: int
    reused_materials: int
    total_reuse_count: int


class HistorySiteMaterialStatRead(BaseModel):
    source_site_code: str
    material_count: int
    reused_count: int
    total_used_count: int


class HistoryTagHotRead(BaseModel):
    tag: str
    count: int


class HistoryDailyTagStatRead(BaseModel):
    date: str
    tag_category_count: int
    hot_tags: list[str] = Field(default_factory=list)


class HistoryCrawlRecordRead(BaseModel):
    id: int
    keyword: str
    target_site_codes: list[str]
    total_count: int
    success_count: int
    duplicate_count: int
    fail_count: int
    status: str
    duration_ms: int
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    summary_message: str


class PublishRecordRead(BaseModel):
    id: int
    draft_id: int
    draft_title: str
    publish_status: str
    publish_message: str
    wx_result: dict = Field(default_factory=dict)
    published_at: datetime | None
    created_at: datetime


class HistoryLogRead(BaseModel):
    log_type: str
    status: str
    title: str
    message: str
    occurred_at: datetime
    related_id: int | None = None


class HistoryOverviewRead(BaseModel):
    article_summary: HistoryArticleSummaryRead
    material_summary: HistoryMaterialSummaryRead
    crawl_history: list[HistoryCrawlRecordRead]
    material_site_stats: list[HistorySiteMaterialStatRead]
    material_hot_tags: list[HistoryTagHotRead]
    material_daily_tags: list[HistoryDailyTagStatRead]
    recent_publish_records: list[PublishRecordRead]
    log_center: list[HistoryLogRead]
