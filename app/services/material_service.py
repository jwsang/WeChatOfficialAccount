from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from PIL import Image
from sqlalchemy.orm import Session

from app.core.config import DATA_DIR
from app.models.material_image import MaterialImage
from app.repositories.material_repository import MaterialRepository
from app.schemas.material import (
    MaterialActionRequest,
    MaterialListFilters,
    MaterialRead,
    MaterialTagSummaryRead,
    MaterialUploadRead,
)


UPLOAD_DIR = DATA_DIR / "uploads"
THUMBNAIL_DIR = DATA_DIR / "thumbnails"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)


class MaterialService:
    def __init__(self, db: Session):
        self.repository = MaterialRepository(db)

    def list_materials(self, filters: MaterialListFilters) -> list[MaterialRead]:
        materials = self.repository.list_materials()
        filtered = [item for item in materials if self._matches(item, filters)]
        return [self._serialize_material(item) for item in filtered]

    def get_material(self, material_id: int) -> MaterialRead:
        material = self.repository.get_material(material_id)
        if not material:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="素材不存在")
        return self._serialize_material(material)

    async def upload_materials(
        self,
        files: list[UploadFile],
        title: str | None,
        keywords: str,
        remark: str,
        tags: str,
    ) -> MaterialUploadRead:
        if not files:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请至少上传一个图片文件")

        uploaded: list[MaterialRead] = []
        duplicate_count = 0
        normalized_tags = self._normalize_tags(tags)

        for index, upload_file in enumerate(files, start=1):
            suffix = Path(upload_file.filename or f"upload_{index}.png").suffix.lower() or ".png"
            if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"不支持的图片格式：{suffix}")

            raw_bytes = await upload_file.read()
            if not raw_bytes:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="上传文件不能为空")

            image_hash = hashlib.sha256(raw_bytes).hexdigest()
            exists = self.repository.get_by_hash(image_hash)
            if exists:
                duplicate_count += 1
                continue

            image = Image.open(BytesIO(raw_bytes))
            width, height = image.size
            image = image.convert("RGB")

            material_name = self._resolve_material_name(upload_file, title, index)
            file_stem = f"manual_{image_hash[:12]}"
            image_path = UPLOAD_DIR / f"{file_stem}.png"
            thumbnail_path = THUMBNAIL_DIR / f"{file_stem}.png"
            image.save(image_path, format="PNG")

            thumbnail = image.copy()
            thumbnail.thumbnail((360, 360))
            thumbnail.save(thumbnail_path, format="PNG")

            material = self.repository.create_material(
                {
                    "material_name": material_name,
                    "search_keyword": keywords,
                    "source_site_code": "manual_upload",
                    "source_type": "manual",
                    "source_page_url": "",
                    "source_image_url": f"manual://{upload_file.filename or file_stem}",
                    "local_file_path": image_path.relative_to(DATA_DIR).as_posix(),
                    "local_thumbnail_path": thumbnail_path.relative_to(DATA_DIR).as_posix(),
                    "image_hash": image_hash,
                    "image_width": width,
                    "image_height": height,
                    "material_status": "available",
                    "audit_status": "pending",
                    "used_count": 0,
                    "tag_codes": normalized_tags,
                    "crawl_task_id": None,
                    "prompt_text": remark,
                }
            )
            uploaded.append(self._serialize_material(material))

        return MaterialUploadRead(uploaded=uploaded, duplicate_count=duplicate_count)

    def update_material_action(self, material_id: int, payload: MaterialActionRequest) -> MaterialRead:
        material = self.repository.get_material(material_id)
        if not material:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="素材不存在")

        if payload.action == "audit":
            material.audit_status = "approved"
            updated = self.repository.save_material(material)
            return self._serialize_material(updated)

        if payload.action == "delete":
            deleted_view = self._serialize_material(material)
            deleted_view.material_status = "deleted"
            local_paths = [material.local_file_path, material.local_thumbnail_path]
            self.repository.delete_material(material)
            for relative_path in local_paths:
                self._delete_local_asset(relative_path)
            return deleted_view

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的素材操作")

    def list_tag_summary(self) -> list[MaterialTagSummaryRead]:
        counter: dict[str, int] = {}
        for material in self.repository.list_materials():
            if material.material_status == "deleted":
                continue
            for tag in self._split_tags(material.tag_codes):
                counter[tag] = counter.get(tag, 0) + 1
        return [
            MaterialTagSummaryRead(tag=tag, count=count)
            for tag, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
        ]

    def _matches(self, material: MaterialImage, filters: MaterialListFilters) -> bool:
        if filters.query_text:
            query_text = filters.query_text.lower()
            id_match = query_text.isdigit() and int(query_text) == material.id
            name_match = query_text in material.material_name.lower()
            if not (id_match or name_match):
                return False
        if filters.keyword and filters.keyword.lower() not in material.search_keyword.lower():
            return False
        if filters.source_site_code and material.source_site_code != filters.source_site_code:
            return False
        if filters.source_type and material.source_type != filters.source_type:
            return False
        if filters.material_status and material.material_status != filters.material_status:
            return False
        if filters.audit_status and material.audit_status != filters.audit_status:
            return False
        if filters.tag and filters.tag not in self._split_tags(material.tag_codes):
            return False
        return True

    def _serialize_material(self, material: MaterialImage) -> MaterialRead:
        return MaterialRead(
            id=material.id,
            material_name=material.material_name,
            search_keyword=material.search_keyword,
            source_site_code=material.source_site_code,
            source_type=material.source_type,
            source_page_url=material.source_page_url,
            source_image_url=material.source_image_url,
            local_file_path=material.local_file_path,
            local_thumbnail_path=material.local_thumbnail_path,
            image_hash=material.image_hash,
            image_width=material.image_width,
            image_height=material.image_height,
            material_status=material.material_status,
            audit_status=material.audit_status,
            used_count=material.used_count,
            tag_codes=material.tag_codes,
            crawl_task_id=material.crawl_task_id,
            prompt_text=material.prompt_text,
            created_at=material.created_at,
            updated_at=material.updated_at,
        )

    def _normalize_tags(self, tags: str) -> str:
        return "|".join(dict.fromkeys(self._split_tags(tags)))

    def _split_tags(self, raw_tags: str) -> list[str]:
        normalized = raw_tags.replace("，", "|").replace(",", "|").replace(" ", "|")
        return [tag.strip() for tag in normalized.split("|") if tag.strip()]

    def _delete_local_asset(self, relative_path: str) -> None:
        normalized = (relative_path or "").strip().lstrip("/\\")
        if not normalized:
            return

        target_path = (DATA_DIR / normalized).resolve()
        try:
            target_path.relative_to(DATA_DIR.resolve())
        except ValueError:
            return

        if target_path.exists() and target_path.is_file():
            target_path.unlink()

    def _resolve_material_name(self, upload_file: UploadFile, title: str | None, index: int) -> str:
        if title and len(title.strip()) > 0:
            if index == 1:
                return title.strip()
            return f"{title.strip()}-{index}"
        return Path(upload_file.filename or f"manual_{index}").stem
