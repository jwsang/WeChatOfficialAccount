from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.site_repository import SiteRepository
from app.schemas.site import (
    SiteConfigCreate,
    SiteConfigRead,
    SiteConfigUpdate,
    SiteRuleConfig,
    SiteTestResponse,
)


class SiteService:
    def __init__(self, db: Session):
        self.repository = SiteRepository(db)

    def list_sites(self) -> list[SiteConfigRead]:
        return [SiteConfigRead.model_validate(site) for site in self.repository.list_sites()]

    def create_site(self, payload: SiteConfigCreate) -> SiteConfigRead:
        if self.repository.get_by_code(payload.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="站点标识已存在",
            )
        site = self.repository.create(self._sync_legacy_rules(payload))
        return SiteConfigRead.model_validate(site)

    def update_site(self, site_id: int, payload: SiteConfigUpdate) -> SiteConfigRead:
        site = self.repository.get_by_id(site_id)
        if not site:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="站点不存在")
        updated = self.repository.update(site, self._sync_legacy_rules(payload))
        return SiteConfigRead.model_validate(updated)

    def delete_site(self, site_id: int) -> None:
        site = self.repository.get_by_id(site_id)
        if not site:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="站点不存在")
        self.repository.delete(site)

    def test_site(self, site_id: int, keyword: str) -> SiteTestResponse:
        site = self.repository.get_by_id(site_id)
        if not site:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="站点不存在")

        rule_config = self._load_rule_config(site.rule_config)
        search_url = self._build_search_url(site.domain, site.code, keyword, rule_config)
        page_two_url = self._build_search_url(site.domain, site.code, keyword, rule_config, page=rule_config.pagination_start + 1)
        image_base = f"https://{site.domain}/preview/{site.code}"
        preview_results = [
            {
                "title": f"{site.name} - {keyword} 示例结果 1",
                "image_url": f"{image_base}/1.jpg",
                "source_page_url": search_url,
            },
            {
                "title": f"{site.name} - {keyword} 示例结果 2",
                "image_url": f"{image_base}/2.jpg",
                "source_page_url": page_two_url,
            },
        ]

        self.repository.update(site, SiteConfigUpdate())
        site.last_crawled_at = datetime.now(UTC)
        self.repository.db.add(site)
        self.repository.db.commit()
        self.repository.db.refresh(site)

        return SiteTestResponse(
            site_code=site.code,
            keyword=keyword,
            success=True,
            preview_results=preview_results,
            message="测试抓取成功，已返回样例结果",
            applied_rule_config=rule_config,
        )

    def _sync_legacy_rules(self, payload: SiteConfigCreate | SiteConfigUpdate) -> SiteConfigCreate | SiteConfigUpdate:
        data = payload.model_dump(exclude_unset=isinstance(payload, SiteConfigUpdate))
        rule_config_value = data.get("rule_config")
        if rule_config_value is not None:
            rule_config = self._load_rule_config(rule_config_value)
            data["rule_config"] = rule_config
            if not data.get("search_rule"):
                data["search_rule"] = self._format_search_rule(rule_config)
            if not data.get("parse_rule"):
                data["parse_rule"] = self._format_parse_rule(rule_config)
            if not data.get("page_rule"):
                data["page_rule"] = self._format_page_rule(rule_config)
        return payload.__class__(**data)

    def _load_rule_config(self, raw_value: SiteRuleConfig | dict | None) -> SiteRuleConfig:
        if isinstance(raw_value, SiteRuleConfig):
            return raw_value
        return SiteRuleConfig.model_validate(raw_value or {})

    def _format_search_rule(self, rule_config: SiteRuleConfig) -> str:
        if not rule_config.search_url_template:
            return ""
        return f"{rule_config.request_method} {rule_config.search_url_template}"

    def _format_parse_rule(self, rule_config: SiteRuleConfig) -> str:
        parts = [
            f"结果容器: {rule_config.result_container_path or '未配置'}",
            f"图片字段: {rule_config.image_url_path or '未配置'}",
            f"详情字段: {rule_config.source_page_url_path or '未配置'}",
            f"标题字段: {rule_config.title_path or '未配置'}",
        ]
        return " | ".join(parts)

    def _format_page_rule(self, rule_config: SiteRuleConfig) -> str:
        parts = [
            f"起始页: {rule_config.pagination_start}",
            f"页码参数: {rule_config.pagination_param}",
        ]
        if rule_config.pagination_size_param:
            parts.append(f"每页参数: {rule_config.pagination_size_param}")
        return " | ".join(parts)

    def _build_search_url(
        self,
        domain: str,
        site_code: str,
        keyword: str,
        rule_config: SiteRuleConfig,
        page: int | None = None,
    ) -> str:
        page_value = page if page is not None else rule_config.pagination_start
        template = rule_config.search_url_template or f"https://{domain}/search?q={{keyword}}&{rule_config.pagination_param}={{page}}"
        resolved = (
            template.replace("{keyword}", keyword)
            .replace("{page}", str(page_value))
            .replace("{site_code}", site_code)
            .replace("{domain}", domain)
        )
        if resolved.startswith(("http://", "https://")):
            return resolved
        if resolved.startswith("/"):
            return f"https://{domain}{resolved}"
        return f"https://{domain}/{resolved.lstrip('/')}"
