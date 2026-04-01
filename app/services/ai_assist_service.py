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
from openai import AsyncOpenAI

from app.core.config import DATA_DIR, load_yaml_config, settings
from app.models.model_config import ModelConfig
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
from app.services.model_service import ModelConfigService


AI_ASSIST_CONFIG_KEY = "ai_assist.config"
AI_ASSIST_GENERATED_INDEX_KEY = "ai_assist.generated.index"
AI_GENERATED_DIR = DATA_DIR / "ai_generated"
THUMBNAIL_DIR = DATA_DIR / "thumbnails"
AI_GENERATED_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)


class AiAssistService:
    def __init__(self, db: Session):
        self.db = db
        self.setting_repository = ArticleRepository(db)
        self.material_repository = MaterialRepository(db)

    def get_config(self) -> AiAssistConfigRead:
        # 首先加载存储在 settings 中的 AI 助手基础配置
        config = self._load_config_dict()
        
        # 获取最终使用的模型配置
        target_model = self._resolve_effective_model_config(config.get("model_id"))
            
        if target_model:
            # 使用模型管理中的配置
            return AiAssistConfigRead(
                model_id=target_model.id,
                base_url=target_model.api_base or ModelConfigService.get_default_api_base(target_model.provider),
                model=target_model.model_identifier,
                provider=target_model.provider,  # 添加提供商信息
                default_size=str(config.get("default_size") or "1024x1024").strip() or "1024x1024",
                default_quality=str(config.get("default_quality") or "standard").strip() or "standard",
                default_style=str(config.get("default_style") or "vivid").strip() or "vivid",
                default_count=int(config.get("default_count") or 4),
                timeout_seconds=int(config.get("timeout_seconds") or 120),
                default_negative_prompt=str(config.get("default_negative_prompt") or "").strip(),
                has_api_key=True,
                api_key_masked=self._mask_key(target_model.api_key),
            )
        else:
            # 如果没有配置模型，则回退到旧的配置方式（为了兼容性）
            api_key = str(config.get("api_key") or "").strip()
            return AiAssistConfigRead(
                model_id=None,
                base_url=str(config.get("base_url") or "").strip(),
                model=str(config.get("model") or "").strip(),
                default_size=str(config.get("default_size") or "1024x1024").strip() or "1024x1024",
                default_quality=str(config.get("default_quality") or "standard").strip() or "standard",
                default_style=str(config.get("default_style") or "vivid").strip() or "vivid",
                default_count=int(config.get("default_count") or 4),
                timeout_seconds=int(config.get("timeout_seconds") or 120),
                default_negative_prompt=str(config.get("default_negative_prompt") or "").strip(),
                has_api_key=bool(api_key),
                api_key_masked=self._mask_key(api_key),
            )

    def _resolve_effective_model_config(self, model_id: Any = None) -> ModelConfig | None:
        """
        统一解析最终使用的模型配置对象
        """
        # 如果指定了 model_id，优先使用
        if model_id:
            try:
                target_model = ModelConfigService.get_model_config_by_id(self.db, int(model_id))
                if target_model:
                    return target_model
            except (ValueError, TypeError):
                pass
        
        # 否则尝试获取全局默认模型
        return ModelConfigService.get_default_model_config(self.db)

    def update_config(self, payload: AiAssistConfigUpdateRequest) -> AiAssistConfigRead:
        config = self._load_config_dict()
        config["model_id"] = payload.model_id
        
        # 只有在没有选择 model_id 的情况下，才允许手动设置 base_url, model 和 api_key
        if not payload.model_id:
            if payload.base_url.strip():
                config["base_url"] = payload.base_url.strip().rstrip("/")
            if payload.model.strip():
                config["model"] = payload.model.strip()
            
            next_api_key = payload.api_key.strip()
            if next_api_key:
                config["api_key"] = next_api_key
        
        config["default_size"] = payload.default_size.strip()
        config["default_quality"] = payload.default_quality.strip()
        config["default_style"] = payload.default_style.strip()
        config["default_count"] = payload.default_count
        config["timeout_seconds"] = payload.timeout_seconds
        config["default_negative_prompt"] = payload.default_negative_prompt.strip()

        try:
            self.setting_repository.upsert_setting_value(AI_ASSIST_CONFIG_KEY, json.dumps(config, ensure_ascii=False))
            self.setting_repository.commit()
        except Exception:
            self.setting_repository.rollback()
            raise
        return self.get_config()

    def update_config_with_model(self, model_config_id: int) -> AiAssistConfigRead:
        """
        使用模型管理中的配置更新AI助手配置
        """
        # 获取指定的模型配置
        model_config = ModelConfigService.get_model_config_by_id(self.db, model_config_id)
        if not model_config:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="指定的模型配置不存在")
        
        # 仅更新 model_id，不再复制 api_base, model, api_key 等字段，实现真正的动态关联
        config = self._load_config_dict()
        config["model_id"] = model_config.id

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
        model_id: int | None = None,
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

        # 统一解析配置：
        # 1. 如果传入了 model_id，优先使用
        # 2. 否则使用 AI 助手页面保存的 model_id
        # 3. 最后回退到全局默认模型
        config = self._load_config_dict()
        effective_model_id = model_id or config.get("model_id")
        target_model = self._resolve_effective_model_config(effective_model_id)
        
        if target_model:
            # 使用模型管理中的配置
            base_url = target_model.api_base or ModelConfigService.get_default_api_base(target_model.provider)
            model = target_model.model_identifier
            api_key = target_model.api_key
            provider = target_model.provider
            timeout_seconds = int(config.get("timeout_seconds") or 120)
        else:
            # 如果没有配置任何模型（包括全局默认），则回退到旧的独立配置方式
            api_key = str(config.get("api_key") or "").strip()
            if not api_key:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请先在 AI 辅助页面选择模型或配置 API Key")
            
            base_url = str(config.get("base_url") or "").strip() or "https://api.openai.com/v1"
            model = str(config.get("model") or "").strip()
            provider = "openai" # 默认假设是 OpenAI
            timeout_seconds = int(config.get("timeout_seconds") or 120)

        reference_bytes: bytes | None = None
        if reference_image is not None:
            reference_bytes = await reference_image.read()
            if not reference_bytes:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="参考图文件不能为空")

        image_bytes_list = await self._call_image_api(
            base_url=base_url,
            model=model,
            api_key=api_key,
            provider=provider,
            timeout_seconds=timeout_seconds,
            prompt=normalized_prompt,
            negative_prompt=negative_prompt.strip(),
            count=max(1, min(count, 6)),
            size=size.strip() or "1024x1024",  # 使用默认尺寸
            quality=quality.strip() or "standard",  # 使用默认质量
            style=style.strip() or "vivid",  # 使用默认风格
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
        provider: str = "openai",
        timeout_seconds: int,
        prompt: str,
        negative_prompt: str,
        count: int,
        size: str,
        quality: str,
        style: str,
        reference_image_bytes: bytes | None,
    ) -> list[bytes]:
        normalized_base_url = base_url.strip().rstrip("/")
        if not normalized_base_url:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="AI 接口地址不能为空")
        
        # 兼容性处理：如果用户提供了包含 /chat/completions 等后缀的 URL，自动剥离
        suffixes_to_strip = ["/chat/completions", "/completions", "/chat", "/images/generations", "/images/edits"]
        for suffix in suffixes_to_strip:
            if normalized_base_url.endswith(suffix):
                normalized_base_url = normalized_base_url[: -len(suffix)].rstrip("/")
                break

        if not model.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="AI 模型不能为空")

        final_prompt = prompt.strip()
        if negative_prompt:
            final_prompt = f"{final_prompt}\n\n负向要求：{negative_prompt.strip()}"

        try:
            async with AsyncOpenAI(api_key=api_key, base_url=normalized_base_url, timeout=timeout_seconds) as client:
                if reference_image_bytes:
                    response = await client.images.edit(
                        model=model,
                        prompt=final_prompt,
                        n=count,
                        size=size,
                        image=("reference.png", reference_image_bytes),
                        response_format="b64_json"
                    )
                else:
                    kwargs = {
                        "model": model,
                        "prompt": final_prompt,
                        "n": count,
                        "size": size,
                        "response_format": "b64_json"
                    }
                    if quality: kwargs["quality"] = quality
                    if style: kwargs["style"] = style
                    response = await client.images.generate(**kwargs)
                
                output_images = []
                for item in response.data:
                    if item.b64_json:
                        output_images.append(base64.b64decode(item.b64_json))
                    elif item.url:
                        async with httpx.AsyncClient() as http_client:
                            img_resp = await http_client.get(item.url)
                            if img_resp.is_success:
                                output_images.append(img_resp.content)
                
                if not output_images:
                    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI 接口未返回可用图片数据")
                return output_images
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI 接口请求失败：{str(e)}"
            )

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
