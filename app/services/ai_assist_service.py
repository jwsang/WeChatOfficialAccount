from __future__ import annotations

import base64
import hashlib
import json
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
from fastapi import HTTPException, UploadFile, status
from PIL import Image
from sqlalchemy.orm import Session

from app.core.config import DATA_DIR, load_yaml_config, settings
from app.repositories.article_repository import ArticleRepository
from app.repositories.material_repository import MaterialRepository
from app.schemas.ai_assist import (
    AiAssistAddToMaterialRead,
    AiAssistAddToMaterialRequest,
    AiAssistConfigRead,
    AiAssistConfigUpdateRequest,
    AiAssistGenerateRead,
    AiAssistGeneratedImageRead,
)


AI_ASSIST_CONFIG_KEY = "ai_assist.config"
AI_ASSIST_GENERATED_INDEX_KEY = "ai_assist.generated.index"
AI_GENERATED_DIR = DATA_DIR / "ai_generated"
THUMBNAIL_DIR = DATA_DIR / "thumbnails"
AI_GENERATED_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)


class AiAssistService:
    def __init__(self, db: Session):
        self.setting_repository = ArticleRepository(db)
        self.material_repository = MaterialRepository(db)

    def get_config(self) -> AiAssistConfigRead:
        config = self._load_config_dict()
        api_key = str(config.get("api_key") or "").strip()
        has_api_key = bool(api_key)
        return AiAssistConfigRead(
            base_url=str(config.get("base_url") or "").strip(),
            model=str(config.get("model") or "").strip(),
            default_size=str(config.get("default_size") or "1024x1024").strip() or "1024x1024",
            default_quality=str(config.get("default_quality") or "standard").strip() or "standard",
            default_style=str(config.get("default_style") or "vivid").strip() or "vivid",
            default_count=int(config.get("default_count") or 4),
            timeout_seconds=int(config.get("timeout_seconds") or 120),
            default_negative_prompt=str(config.get("default_negative_prompt") or "").strip(),
            has_api_key=has_api_key,
            api_key_masked=self._mask_key(api_key),
        )

    def update_config(self, payload: AiAssistConfigUpdateRequest) -> AiAssistConfigRead:
        config = self._load_config_dict()
        config["base_url"] = payload.base_url.strip().rstrip("/")
        config["model"] = payload.model.strip()
        config["default_size"] = payload.default_size.strip()
        config["default_quality"] = payload.default_quality.strip()
        config["default_style"] = payload.default_style.strip()
        config["default_count"] = payload.default_count
        config["timeout_seconds"] = payload.timeout_seconds
        config["default_negative_prompt"] = payload.default_negative_prompt.strip()

        next_api_key = payload.api_key.strip()
        if next_api_key:
            config["api_key"] = next_api_key
        elif not str(config.get("api_key") or "").strip():
            config["api_key"] = ""

        try:
            self.setting_repository.upsert_setting_value(AI_ASSIST_CONFIG_KEY, json.dumps(config, ensure_ascii=False))
            self.setting_repository.commit()
        except Exception:
            self.setting_repository.rollback()
            raise
        return self.get_config()

    async def generate_images(
        self,
        *,
        prompt: str,
        negative_prompt: str,
        count: int,
        size: str,
        quality: str,
        style: str,
        reference_image: UploadFile | None,
    ) -> AiAssistGenerateRead:
        normalized_prompt = prompt.strip()
        if not normalized_prompt:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请输入图片生成提示词")

        config = self._load_config_dict()
        api_key = str(config.get("api_key") or "").strip()
        if not api_key:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请先在 AI 辅助页面配置 API Key")

        reference_bytes: bytes | None = None
        if reference_image is not None:
            reference_bytes = await reference_image.read()
            if not reference_bytes:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="参考图文件不能为空")

        image_bytes_list = await self._call_image_api(
            base_url=str(config.get("base_url") or "").strip(),
            model=str(config.get("model") or "").strip(),
            api_key=api_key,
            timeout_seconds=int(config.get("timeout_seconds") or 120),
            prompt=normalized_prompt,
            negative_prompt=negative_prompt.strip(),
            count=max(1, min(count, 6)),
            size=size.strip() or str(config.get("default_size") or "1024x1024").strip(),
            quality=quality.strip() or str(config.get("default_quality") or "standard").strip(),
            style=style.strip() or str(config.get("default_style") or "vivid").strip(),
            reference_image_bytes=reference_bytes,
        )

        generated_index = self._load_generated_index()
        generated: list[AiAssistGeneratedImageRead] = []

        for idx, image_bytes in enumerate(image_bytes_list, start=1):
            temp_id = f"ai_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}_{idx}_{uuid4().hex[:8]}"
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            width, height = image.size

            image_path = AI_GENERATED_DIR / f"{temp_id}.png"
            image.save(image_path, format="PNG")

            local_file_path = image_path.relative_to(DATA_DIR).as_posix()
            preview_url = f"/data/{local_file_path}"
            created_at = datetime.now(UTC)

            generated_index[temp_id] = {
                "local_file_path": local_file_path,
                "preview_url": preview_url,
                "width": width,
                "height": height,
                "prompt": normalized_prompt,
                "created_at": created_at.isoformat(),
            }

            generated.append(
                AiAssistGeneratedImageRead(
                    temp_id=temp_id,
                    preview_url=preview_url,
                    local_file_path=local_file_path,
                    width=width,
                    height=height,
                    created_at=created_at,
                    prompt=normalized_prompt,
                )
            )

        self._persist_generated_index(generated_index)
        return AiAssistGenerateRead(generated=generated)

    def add_generated_to_materials(self, payload: AiAssistAddToMaterialRequest) -> AiAssistAddToMaterialRead:
        temp_ids = [str(item).strip() for item in payload.temp_ids if str(item).strip()]
        if not temp_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请至少选择一张生成结果")

        generated_index = self._load_generated_index()
        title_prefix = payload.title_prefix.strip() or "AI素材"
        merged_tags = self._normalize_tags(f"AI|{payload.tags}")
        uploaded = []
        duplicate_count = 0
        missing_count = 0

        for idx, temp_id in enumerate(temp_ids, start=1):
            metadata = generated_index.get(temp_id)
            if not isinstance(metadata, dict):
                missing_count += 1
                continue

            local_file_path = str(metadata.get("local_file_path") or "").strip()
            if not local_file_path:
                missing_count += 1
                continue

            absolute_path = self._resolve_data_path(local_file_path)
            if not absolute_path.exists() or not absolute_path.is_file():
                missing_count += 1
                continue

            raw_bytes = absolute_path.read_bytes()
            image_hash = hashlib.sha256(raw_bytes).hexdigest()
            exists = self.material_repository.get_by_hash(image_hash)
            if exists:
                duplicate_count += 1
                continue

            image = Image.open(BytesIO(raw_bytes)).convert("RGB")
            width, height = image.size

            thumb_path = THUMBNAIL_DIR / f"ai_{image_hash[:12]}.png"
            thumbnail = image.copy()
            thumbnail.thumbnail((360, 360))
            thumbnail.save(thumb_path, format="PNG")

            material = self.material_repository.create_material(
                {
                    "material_name": f"{title_prefix}-{idx}",
                    "search_keyword": payload.keywords.strip(),
                    "source_site_code": "ai_assist",
                    "source_type": "ai",
                    "source_page_url": "",
                    "source_image_url": str(metadata.get("preview_url") or f"ai://{temp_id}"),
                    "local_file_path": local_file_path,
                    "local_thumbnail_path": thumb_path.relative_to(DATA_DIR).as_posix(),
                    "image_hash": image_hash,
                    "image_width": width,
                    "image_height": height,
                    "material_status": "available",
                    "audit_status": "approved",
                    "used_count": 0,
                    "tag_codes": merged_tags,
                    "crawl_task_id": None,
                    "prompt_text": payload.remark.strip() or str(metadata.get("prompt") or ""),
                }
            )
            uploaded.append(material)

        return AiAssistAddToMaterialRead(
            uploaded=[self._serialize_material(material) for material in uploaded],
            duplicate_count=duplicate_count,
            missing_count=missing_count,
        )

    async def _call_image_api(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str,
        timeout_seconds: int,
        prompt: str,
        negative_prompt: str,
        count: int,
        size: str,
        quality: str,
        style: str,
        reference_image_bytes: bytes | None,
    ) -> list[bytes]:
        normalized_base_url = base_url.rstrip("/")
        if not normalized_base_url:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="AI 接口地址不能为空")
        if not model.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="AI 模型不能为空")

        final_prompt = prompt.strip()
        if negative_prompt:
            final_prompt = f"{final_prompt}\n\n负向要求：{negative_prompt.strip()}"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            if reference_image_bytes:
                form_data = {
                    "model": model,
                    "prompt": final_prompt,
                    "n": str(count),
                    "size": size,
                }
                if quality:
                    form_data["quality"] = quality
                if style:
                    form_data["style"] = style

                response = await client.post(
                    f"{normalized_base_url}/images/edits",
                    data=form_data,
                    files={"image": ("reference.png", reference_image_bytes, "image/png")},
                    headers=headers,
                )
            else:
                payload = {
                    "model": model,
                    "prompt": final_prompt,
                    "n": count,
                    "size": size,
                }
                if quality:
                    payload["quality"] = quality
                if style:
                    payload["style"] = style

                response = await client.post(
                    f"{normalized_base_url}/images/generations",
                    json=payload,
                    headers=headers,
                )

            try:
                body = response.json()
            except ValueError as exc:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI 接口返回非 JSON 数据") from exc

            if not response.is_success:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"AI 接口调用失败（HTTP {response.status_code}）：{body}",
                )

            rows = body.get("data")
            if not isinstance(rows, list) or not rows:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI 接口返回结果为空")

            output_images: list[bytes] = []
            for item in rows[:count]:
                if not isinstance(item, dict):
                    continue
                b64_json = item.get("b64_json")
                image_url = item.get("url")
                if isinstance(b64_json, str) and b64_json.strip():
                    try:
                        output_images.append(base64.b64decode(b64_json))
                    except Exception:
                        continue
                    continue
                if isinstance(image_url, str) and image_url.strip():
                    image_response = await client.get(image_url.strip())
                    if image_response.is_success and image_response.content:
                        output_images.append(image_response.content)

            if not output_images:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI 接口未返回可用图片数据")

            return output_images

    def _load_config_dict(self) -> dict[str, Any]:
        default_config = self._default_config_dict()
        raw = self.setting_repository.get_setting_value(AI_ASSIST_CONFIG_KEY, "")
        if not raw.strip():
            return default_config

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return default_config

        if not isinstance(payload, dict):
            return default_config

        merged = {**default_config, **payload}
        merged["base_url"] = str(merged.get("base_url") or "").strip().rstrip("/")
        merged["model"] = str(merged.get("model") or "").strip()
        merged["api_key"] = str(merged.get("api_key") or "").strip()
        return merged

    def _default_config_dict(self) -> dict[str, Any]:
        yaml_config = load_yaml_config()
        openai_config = yaml_config.get("openAi") if isinstance(yaml_config, dict) else {}
        openai_config = openai_config if isinstance(openai_config, dict) else {}

        return {
            "base_url": str(openai_config.get("url") or "https://www.qiuner.top/v1").strip().rstrip("/"),
            "model": str(openai_config.get("model") or "gpt-image-1").strip(),
            "default_size": "1024x1024",
            "default_quality": "standard",
            "default_style": "vivid",
            "default_count": 4,
            "timeout_seconds": 120,
            "default_negative_prompt": "",
            "api_key": str(
                openai_config.get("Key")
                or openai_config.get("key")
                or settings.api_key
                or ""
            ).strip(),
        }

    def _load_generated_index(self) -> dict[str, Any]:
        raw = self.setting_repository.get_setting_value(AI_ASSIST_GENERATED_INDEX_KEY, "")
        if not raw.strip():
            return {}
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        if not isinstance(payload, dict):
            return {}
        return payload

    def _persist_generated_index(self, payload: dict[str, Any]) -> None:
        try:
            self.setting_repository.upsert_setting_value(
                AI_ASSIST_GENERATED_INDEX_KEY,
                json.dumps(payload, ensure_ascii=False),
            )
            self.setting_repository.commit()
        except Exception:
            self.setting_repository.rollback()
            raise

    def _resolve_data_path(self, relative_path: str) -> Path:
        normalized = relative_path.strip().lstrip("/\\")
        target_path = (DATA_DIR / normalized).resolve()
        try:
            target_path.relative_to(DATA_DIR.resolve())
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"非法素材路径：{relative_path}") from exc
        return target_path

    def _normalize_tags(self, tags: str) -> str:
        return "|".join(dict.fromkeys(self._split_tags(tags)))

    def _split_tags(self, raw_tags: str) -> list[str]:
        normalized = raw_tags.replace("，", "|").replace(",", "|").replace(" ", "|")
        return [tag.strip() for tag in normalized.split("|") if tag.strip()]

    def _mask_key(self, api_key: str) -> str:
        if not api_key:
            return ""
        if len(api_key) <= 8:
            return "*" * len(api_key)
        return f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"

    def _serialize_material(self, material) -> dict[str, Any]:
        return {
            "id": material.id,
            "material_name": material.material_name,
            "search_keyword": material.search_keyword,
            "source_site_code": material.source_site_code,
            "source_type": material.source_type,
            "source_page_url": material.source_page_url,
            "source_image_url": material.source_image_url,
            "local_file_path": material.local_file_path,
            "local_thumbnail_path": material.local_thumbnail_path,
            "image_hash": material.image_hash,
            "image_width": material.image_width,
            "image_height": material.image_height,
            "material_status": material.material_status,
            "audit_status": material.audit_status,
            "used_count": material.used_count,
            "tag_codes": material.tag_codes,
            "crawl_task_id": material.crawl_task_id,
            "prompt_text": material.prompt_text,
            "created_at": material.created_at,
            "updated_at": material.updated_at,
        }
