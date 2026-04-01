from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.article_draft import ArticleDraft
from app.models.crawl_task import CrawlTask
from app.models.crawl_task_log import CrawlTaskLog
from app.models.material_image import MaterialImage
from app.models.publish_record import PublishRecord
from app.models.model_config import ModelConfig
from app.repositories.history_repository import HistoryRepository
from app.schemas.history import (
    HistoryArticleSummaryRead,
    HistoryCrawlRecordRead,
    HistoryDailyTagStatRead,
    HistoryLogRead,
    HistoryMaterialSummaryRead,
    HistoryModelSummaryRead,
    HistoryOverviewRead,
    HistorySiteMaterialStatRead,
    HistoryTagHotRead,
    PublishRecordRead,
)


class HistoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = HistoryRepository(db)

    def get_overview(self) -> HistoryOverviewRead:
        drafts = self.repository.list_drafts()
        materials = self.repository.list_materials()
        crawl_tasks = self.repository.list_crawl_tasks(limit=20)
        crawl_logs = self.repository.list_crawl_logs(limit=20)
        publish_records = self.repository.list_publish_records(limit=20)
        models = self.db.query(ModelConfig).all()

        draft_map = {draft.id: draft for draft in drafts}
        active_drafts = [draft for draft in drafts if draft.draft_status != "deleted"]
        active_materials = [material for material in materials if material.material_status != "deleted"]

        article_summary = self._build_article_summary(active_drafts)
        material_summary = self._build_material_summary(active_materials)
        model_summary = self._build_model_summary(models)

        return HistoryOverviewRead(
            article_summary=article_summary,
            material_summary=material_summary,
            model_summary=model_summary,
            crawl_history=[self._serialize_crawl_task(task) for task in crawl_tasks],
            material_site_stats=self._build_site_material_stats(active_materials),
            material_hot_tags=self._build_hot_tags(active_materials),
            material_daily_tags=self._build_daily_tag_stats(active_materials),
            recent_publish_records=[
                self._serialize_publish_record(record, draft_map.get(record.draft_id)) for record in publish_records
            ],
            log_center=self._build_log_center(crawl_logs, publish_records, draft_map),
        )

    def _build_model_summary(self, models: list[ModelConfig]) -> HistoryModelSummaryRead:
        total_models = len(models)
        provider_counts = Counter(model.provider for model in models)
        default_model = next((model for model in models if model.is_default), None)
        return HistoryModelSummaryRead(
            total_models=total_models,
            provider_counts=dict(provider_counts),
            default_model_name=default_model.name if default_model else None,
        )

    def _build_article_summary(self, drafts: list[ArticleDraft]) -> HistoryArticleSummaryRead:
        total_generated = len(drafts)
        total_published = sum(1 for draft in drafts if draft.draft_status == "published")
        total_drafts = sum(1 for draft in drafts if draft.draft_status != "published")
        return HistoryArticleSummaryRead(
            total_generated=total_generated,
            total_published=total_published,
            total_drafts=total_drafts,
        )

    def _build_material_summary(self, materials: list[MaterialImage]) -> HistoryMaterialSummaryRead:
        total_materials = len(materials)
        unused_materials = sum(1 for material in materials if material.used_count == 0)
        reused_materials = sum(1 for material in materials if material.used_count > 0)
        total_reuse_count = sum(material.used_count for material in materials)
        return HistoryMaterialSummaryRead(
            total_materials=total_materials,
            unused_materials=unused_materials,
            reused_materials=reused_materials,
            total_reuse_count=total_reuse_count,
        )

    def _build_site_material_stats(self, materials: list[MaterialImage]) -> list[HistorySiteMaterialStatRead]:
        stats: dict[str, dict[str, int]] = defaultdict(lambda: {"material_count": 0, "reused_count": 0, "total_used_count": 0})
        for material in materials:
            site_stats = stats[material.source_site_code]
            site_stats["material_count"] += 1
            if material.used_count > 0:
                site_stats["reused_count"] += 1
            site_stats["total_used_count"] += material.used_count
        return [
            HistorySiteMaterialStatRead(
                source_site_code=site_code,
                material_count=values["material_count"],
                reused_count=values["reused_count"],
                total_used_count=values["total_used_count"],
            )
            for site_code, values in sorted(stats.items(), key=lambda item: (-item[1]["material_count"], item[0]))
        ]

    def _build_hot_tags(self, materials: list[MaterialImage]) -> list[HistoryTagHotRead]:
        counter: Counter[str] = Counter()
        for material in materials:
            counter.update(self._split_tags(material.tag_codes))
        return [HistoryTagHotRead(tag=tag, count=count) for tag, count in counter.most_common(10)]

    def _build_daily_tag_stats(self, materials: list[MaterialImage]) -> list[HistoryDailyTagStatRead]:
        grouped: dict[str, Counter[str]] = defaultdict(Counter)
        for material in materials:
            date_key = material.created_at.date().isoformat()
            grouped[date_key].update(self._split_tags(material.tag_codes))
        rows: list[HistoryDailyTagStatRead] = []
        for date_key, counter in sorted(grouped.items(), key=lambda item: item[0], reverse=True):
            rows.append(
                HistoryDailyTagStatRead(
                    date=date_key,
                    tag_category_count=len(counter),
                    hot_tags=[tag for tag, _ in counter.most_common(3)],
                )
            )
        return rows

    def _build_log_center(
        self,
        crawl_logs: list[CrawlTaskLog],
        publish_records: list[PublishRecord],
        draft_map: dict[int, ArticleDraft],
    ) -> list[HistoryLogRead]:
        items: list[HistoryLogRead] = []
        for log in crawl_logs:
            items.append(
                HistoryLogRead(
                    log_type="crawl",
                    status=log.status,
                    title=f"抓取任务 #{log.crawl_task_id} / {log.site_code}",
                    message=log.message,
                    occurred_at=log.created_at,
                    related_id=log.crawl_task_id,
                )
            )
        for record in publish_records:
            draft = draft_map.get(record.draft_id)
            items.append(
                HistoryLogRead(
                    log_type="publish",
                    status=record.publish_status,
                    title=f"发布草稿 #{record.draft_id} / {draft.article_title if draft else '未知草稿'}",
                    message=record.publish_message,
                    occurred_at=record.published_at or record.created_at,
                    related_id=record.draft_id,
                )
            )
            if record.publish_status != "success":
                items.append(
                    HistoryLogRead(
                        log_type="system",
                        status="warning",
                        title=f"发布异常 / 草稿 #{record.draft_id}",
                        message=record.publish_message,
                        occurred_at=record.published_at or record.created_at,
                        related_id=record.draft_id,
                    )
                )
        items.sort(key=lambda item: item.occurred_at, reverse=True)
        return items[:20]

    def _serialize_crawl_task(self, task: CrawlTask) -> HistoryCrawlRecordRead:
        duration_ms = 0
        if task.started_at and task.finished_at:
            duration_ms = max(int((task.finished_at - task.started_at).total_seconds() * 1000), 0)
        return HistoryCrawlRecordRead(
            id=task.id,
            keyword=task.keyword,
            target_site_codes=self._split_site_codes(task.target_sites),
            total_count=task.total_count,
            success_count=task.success_count,
            duplicate_count=task.duplicate_count,
            fail_count=task.fail_count,
            status=task.status,
            duration_ms=duration_ms,
            started_at=task.started_at,
            finished_at=task.finished_at,
            created_at=task.created_at,
            summary_message=task.summary_message,
        )

    def _serialize_publish_record(self, record: PublishRecord, draft: ArticleDraft | None) -> PublishRecordRead:
        return PublishRecordRead(
            id=record.id,
            draft_id=record.draft_id,
            draft_title=draft.article_title if draft else "",
            publish_status=record.publish_status,
            publish_message=record.publish_message,
            wx_result=self._parse_json(record.wx_result),
            published_at=record.published_at,
            created_at=record.created_at,
        )

    def _split_site_codes(self, raw_value: str) -> list[str]:
        return [item for item in raw_value.split(",") if item]

    def _split_tags(self, raw_tags: str) -> list[str]:
        normalized = raw_tags.replace("，", "|").replace(",", "|").replace(" ", "|")
        return [tag.strip() for tag in normalized.split("|") if tag.strip()]

    def _parse_json(self, raw_value: str) -> dict:
        try:
            value = json.loads(raw_value) if raw_value else {}
        except json.JSONDecodeError:
            return {}
        return value if isinstance(value, dict) else {}
