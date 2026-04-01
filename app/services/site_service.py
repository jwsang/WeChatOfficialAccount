import json
import re
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import load_yaml_config, settings
from app.repositories.article_repository import ArticleRepository
from app.repositories.site_repository import SiteRepository
from app.services.model_service import ModelConfigService
from app.schemas.site import (
    SiteAiPrefillResponse,
    SiteAiPrefillSuggestion,
    SiteConfigCreate,
    SiteConfigRead,
    SiteConfigUpdate,
    SiteRuleConfig,
    SiteTestResponse,
)


SITE_AI_CONFIG_KEY = "ai_assist.config"


class SiteService:
    def __init__(self, db: Session):
        self.repository = SiteRepository(db)
        self.setting_repository = ArticleRepository(db)

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

    def ai_prefill_site(self, domain: str, model_id: int | None = None) -> SiteAiPrefillResponse:
        normalized_domain = self._normalize_domain(domain)
        suggestion = self._generate_site_prefill_by_ai(normalized_domain, model_id)
        sanitized = self._sanitize_site_ai_suggestion(suggestion, normalized_domain)
        return SiteAiPrefillResponse(
            domain=normalized_domain,
            success=True,
            message="AI 已完成站点配置建议生成，请人工确认后保存",
            suggestion=sanitized,
        )

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

    def _generate_site_prefill_by_ai(self, domain: str, model_id: int | None = None) -> SiteAiPrefillSuggestion | dict[str, Any]:
        ai_config = self._resolve_ai_prefill_config(model_id)
        api_key = str(ai_config.get("api_key") or "").strip()
        if not api_key:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请先在 AI 辅助页面配置 API Key 或在模型管理中添加有效的模型")

        payload = self._call_ai_site_prefill(
            base_url=str(ai_config.get("base_url") or "").strip(),
            model=str(ai_config.get("model") or "").strip(),
            api_key=api_key,
            timeout_seconds=int(ai_config.get("timeout_seconds") or 120),
            domain=domain,
        )
        if isinstance(payload, dict) and isinstance(payload.get("suggestion"), dict):
            return payload["suggestion"]
        return payload

    def _resolve_ai_prefill_config(self, model_id: int | None = None) -> dict[str, Any]:
        # 如果提供了 model_id，则直接使用模型管理中的配置
        if model_id:
            model_config = ModelConfigService.get_model_config_by_id(self.repository.db, model_id)
            if model_config:
                return {
                    "base_url": model_config.api_base or ModelConfigService.get_default_api_base(model_config.provider),
                    "model": model_config.model_identifier,
                    "api_key": model_config.api_key,
                    "timeout_seconds": 120,
                }

        # 否则尝试获取默认模型配置
        default_model = ModelConfigService.get_default_model_config(self.repository.db)
        if default_model:
            return {
                "base_url": default_model.api_base or ModelConfigService.get_default_api_base(default_model.provider),
                "model": default_model.model_identifier,
                "api_key": default_model.api_key,
                "timeout_seconds": 120,
            }

        # 最后回退到旧有的配置逻辑
        yaml_config = load_yaml_config()
        openai_config = yaml_config.get("openAi") if isinstance(yaml_config, dict) else {}
        openai_config = openai_config if isinstance(openai_config, dict) else {}

        config: dict[str, Any] = {
            "base_url": str(openai_config.get("url") or "https://www.qiuner.top/v1").strip().rstrip("/"),
            "model": str(openai_config.get("model") or "gpt-5.2").strip(),
            "timeout_seconds": 120,
            "api_key": str(
                openai_config.get("Key")
                or openai_config.get("key")
                or settings.api_key
                or ""
            ).strip(),
        }

        raw_saved = self.setting_repository.get_setting_value(SITE_AI_CONFIG_KEY, "")
        if raw_saved.strip():
            try:
                saved = json.loads(raw_saved)
            except json.JSONDecodeError:
                saved = {}
            if isinstance(saved, dict):
                if str(saved.get("base_url") or "").strip():
                    config["base_url"] = str(saved.get("base_url")).strip().rstrip("/")
                if str(saved.get("model") or "").strip():
                    config["model"] = str(saved.get("model")).strip()
                if str(saved.get("api_key") or "").strip():
                    config["api_key"] = str(saved.get("api_key")).strip()
                timeout_value = saved.get("timeout_seconds")
                if isinstance(timeout_value, int) and timeout_value > 0:
                    config["timeout_seconds"] = timeout_value

        return config

    def _call_ai_site_prefill(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str,
        timeout_seconds: int,
        domain: str,
    ) -> dict[str, Any]:
        normalized_base_url = base_url.rstrip("/")
        if not normalized_base_url:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="AI 接口地址不能为空")
        if not model.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="AI 模型不能为空")

        system_prompt = (
            "你是站点抓取配置助手。请仅返回 JSON，不要输出任何解释。"
            "JSON 必须包含字段：name, code, domain, enabled, search_rule, parse_rule, page_rule, remark, crawl_method, rule_config。"
            "rule_config 必须包含字段：search_url_template, result_container_path, image_url_path, source_page_url_path, "
            "title_path, pagination_param, pagination_start, pagination_size_param, request_method, request_headers, "
            "request_query_template, extra_notes。"
            "crawl_method 仅允许：API接口、HTML解析、RSS/Feed。request_method 仅允许：GET、POST。"
            "输出必须是可被 JSON.parse 解析的对象。"
        )
        user_prompt = (
            f"请为域名 {domain} 生成公众号素材抓取站点配置建议。"
            "请优先给出 API 或页面搜索规则，路径可用合理占位。"
            "code 使用小写字母数字下划线。"
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        request_payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                response = client.post(
                    f"{normalized_base_url}/chat/completions",
                    headers=headers,
                    json=request_payload,
                )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI 站点建议生成失败：{exc}",
            ) from exc

        try:
            body = response.json()
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI 接口返回非 JSON 数据") from exc

        if not response.is_success:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI 接口调用失败（HTTP {response.status_code}）：{body}",
            )

        choices = body.get("choices")
        if not isinstance(choices, list) or not choices:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI 接口返回内容缺失 choices")

        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if isinstance(content, list):
            content = "".join(
                str(item.get("text") or "")
                for item in content
                if isinstance(item, dict)
            )
        payload = self._extract_json_dict(content)
        if not isinstance(payload, dict):
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI 返回内容解析失败")
        return payload

    def _extract_json_dict(self, content: Any) -> dict[str, Any]:
        if isinstance(content, dict):
            return content
        if not isinstance(content, str):
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI 返回内容为空")

        text = content.strip()
        if not text:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI 返回内容为空")

        fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*\})\s*```", text, flags=re.IGNORECASE)
        if fenced:
            text = fenced.group(1).strip()

        try:
            payload = json.loads(text)
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass

        fallback = re.search(r"\{[\s\S]*\}", text)
        if fallback:
            try:
                payload = json.loads(fallback.group(0))
                if isinstance(payload, dict):
                    return payload
            except json.JSONDecodeError:
                pass

        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI 返回 JSON 结构解析失败")

    def _sanitize_site_ai_suggestion(
        self,
        raw_suggestion: SiteAiPrefillSuggestion | dict[str, Any],
        domain: str,
    ) -> SiteAiPrefillSuggestion:
        if isinstance(raw_suggestion, SiteAiPrefillSuggestion):
            payload = raw_suggestion.model_dump()
        else:
            payload = dict(raw_suggestion or {})

        try:
            rule_config = self._load_rule_config(payload.get("rule_config"))
        except (ValidationError, TypeError, ValueError):
            rule_config = SiteRuleConfig()

        crawl_method = str(payload.get("crawl_method") or "HTML解析").strip()
        if crawl_method not in {"API接口", "HTML解析", "RSS/Feed"}:
            crawl_method = "HTML解析"

        raw_code = str(payload.get("code") or self._build_site_code_from_domain(domain)).strip()
        code = self._ensure_unique_code(self._normalize_code(raw_code))

        name = str(payload.get("name") or "").strip()
        if not name:
            seed = domain.split(".")[0] if domain else "新站点"
            name = f"{seed}站点"

        search_rule = str(payload.get("search_rule") or "").strip() or self._format_search_rule(rule_config)
        parse_rule = str(payload.get("parse_rule") or "").strip() or self._format_parse_rule(rule_config)
        page_rule = str(payload.get("page_rule") or "").strip() or self._format_page_rule(rule_config)
        remark = str(payload.get("remark") or "").strip() or f"AI 根据域名 {domain} 自动生成，请人工复核"

        return SiteAiPrefillSuggestion(
            name=name[:100],
            code=code[:100],
            domain=domain,
            enabled=self._to_bool(payload.get("enabled"), default=True),
            search_rule=search_rule,
            parse_rule=parse_rule,
            page_rule=page_rule,
            remark=remark,
            crawl_method=crawl_method,
            rule_config=rule_config,
        )

    def _to_bool(self, value: Any, default: bool = True) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on"}:
                return True
            if normalized in {"0", "false", "no", "off"}:
                return False
        if isinstance(value, (int, float)):
            return bool(value)
        return default

    def _normalize_domain(self, raw_domain: str) -> str:
        candidate = str(raw_domain or "").strip().lower()
        if not candidate:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请输入站点域名")

        parsed = urlparse(candidate if "://" in candidate else f"https://{candidate}")
        host = (parsed.netloc or parsed.path or "").strip().lower()
        host = host.split("/")[0].split(":")[0].strip(".")
        if not host:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="站点域名格式不正确")

        try:
            host = host.encode("idna").decode("ascii")
        except UnicodeError:
            pass

        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", host):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="站点域名格式不正确")
        if "." not in host:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请输入有效域名，例如 example.com")
        return host

    def _build_site_code_from_domain(self, domain: str) -> str:
        segments = [segment for segment in domain.split(".") if segment and segment != "www"]
        if not segments:
            return "site"
        return self._normalize_code("_".join(segments))

    def _normalize_code(self, raw_value: str) -> str:
        normalized = re.sub(r"[^a-z0-9_]+", "_", str(raw_value or "").lower().replace("-", "_"))
        normalized = re.sub(r"_+", "_", normalized).strip("_")
        return (normalized or "site")[:100]

    def _ensure_unique_code(self, base_code: str) -> str:
        normalized_base = self._normalize_code(base_code)
        candidate = normalized_base
        index = 2
        while self.repository.get_by_code(candidate):
            suffix = f"_{index}"
            candidate = f"{normalized_base[: max(1, 100 - len(suffix))]}{suffix}"
            index += 1
        return candidate

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
