from pathlib import Path
from textwrap import dedent

BASE = Path(__file__).resolve().parent
FILES: dict[str, str] = {
    "app/schemas/material.py": dedent(
        '''
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
        '''
    ).strip() + "\n",
    "app/repositories/material_repository.py": dedent(
        '''
        from sqlalchemy import select
        from sqlalchemy.orm import Session

        from app.models.material_image import MaterialImage


        class MaterialRepository:
            def __init__(self, db: Session):
                self.db = db

            def list_materials(self) -> list[MaterialImage]:
                statement = select(MaterialImage).order_by(MaterialImage.created_at.desc(), MaterialImage.id.desc())
                return list(self.db.scalars(statement).all())

            def get_material(self, material_id: int) -> MaterialImage | None:
                return self.db.get(MaterialImage, material_id)

            def get_by_hash(self, image_hash: str) -> MaterialImage | None:
                statement = select(MaterialImage).where(MaterialImage.image_hash == image_hash)
                return self.db.scalar(statement)

            def create_material(self, payload: dict) -> MaterialImage:
                material = MaterialImage(**payload)
                self.db.add(material)
                self.db.commit()
                self.db.refresh(material)
                return material

            def save_material(self, material: MaterialImage) -> MaterialImage:
                self.db.add(material)
                self.db.commit()
                self.db.refresh(material)
                return material
        '''
    ).strip() + "\n",
    "app/services/material_service.py": dedent(
        '''
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

                tags = self._split_tags(material.tag_codes)
                if payload.action == "favorite":
                    if "favorite" not in tags:
                        tags.append("favorite")
                elif payload.action == "unfavorite":
                    tags = [tag for tag in tags if tag != "favorite"]
                elif payload.action == "not_recommended":
                    material.material_status = "not_recommended"
                elif payload.action == "restore":
                    material.material_status = "available"
                elif payload.action == "audit":
                    material.audit_status = "approved"
                elif payload.action == "delete":
                    material.material_status = "deleted"

                material.tag_codes = "|".join(dict.fromkeys(tags))
                updated = self.repository.save_material(material)
                return self._serialize_material(updated)

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

            def _resolve_material_name(self, upload_file: UploadFile, title: str | None, index: int) -> str:
                if title and len(title.strip()) > 0:
                    if index == 1:
                        return title.strip()
                    return f"{title.strip()}-{index}"
                return Path(upload_file.filename or f"manual_{index}").stem
        '''
    ).strip() + "\n",
    "app/api/material_routes.py": dedent(
        '''
        from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
        from sqlalchemy.orm import Session

        from app.db.session import get_db
        from app.schemas.material import (
            MaterialActionRequest,
            MaterialListFilters,
            MaterialRead,
            MaterialTagSummaryRead,
            MaterialUploadRead,
        )
        from app.services.material_service import MaterialService


        router = APIRouter(prefix="/api/materials", tags=["materials"])


        def get_material_service(db: Session = Depends(get_db)) -> MaterialService:
            return MaterialService(db)


        @router.get("/tags/summary", response_model=list[MaterialTagSummaryRead])
        def list_tag_summary(service: MaterialService = Depends(get_material_service)):
            return service.list_tag_summary()


        @router.get("", response_model=list[MaterialRead])
        def list_materials(
            query_text: str = Query(default=""),
            keyword: str = Query(default=""),
            source_site_code: str = Query(default=""),
            source_type: str = Query(default=""),
            material_status: str = Query(default=""),
            audit_status: str = Query(default=""),
            tag: str = Query(default=""),
            service: MaterialService = Depends(get_material_service),
        ):
            filters = MaterialListFilters(
                query_text=query_text,
                keyword=keyword,
                source_site_code=source_site_code,
                source_type=source_type,
                material_status=material_status,
                audit_status=audit_status,
                tag=tag,
            )
            return service.list_materials(filters)


        @router.post("/upload", response_model=MaterialUploadRead)
        async def upload_materials(
            files: list[UploadFile] = File(...),
            title: str | None = Form(default=None),
            keywords: str = Form(default=""),
            remark: str = Form(default=""),
            tags: str = Form(default=""),
            service: MaterialService = Depends(get_material_service),
        ):
            return await service.upload_materials(files, title, keywords, remark, tags)


        @router.get("/{material_id}", response_model=MaterialRead)
        def get_material(material_id: int, service: MaterialService = Depends(get_material_service)):
            return service.get_material(material_id)


        @router.post("/{material_id}/actions", response_model=MaterialRead)
        def update_material_action(
            material_id: int,
            payload: MaterialActionRequest,
            service: MaterialService = Depends(get_material_service),
        ):
            return service.update_material_action(material_id, payload)
        '''
    ).strip() + "\n",
    "tests/test_materials.py": dedent(
        '''
        import io

        from fastapi.testclient import TestClient
        from PIL import Image

        from app.main import app


        client = TestClient(app)


        def build_image_bytes(color: tuple[int, int, int]) -> bytes:
            image = Image.new("RGB", (640, 480), color=color)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            return buffer.getvalue()


        def ensure_material_seed() -> None:
            site_response = client.post(
                "/api/sites",
                json={
                    "name": "MaterialSeedSite",
                    "code": "material_seed_site",
                    "domain": "seed.example.com",
                    "enabled": True,
                    "search_rule": "/search?q={keyword}",
                    "parse_rule": "results[].url",
                    "page_rule": "page={page}",
                    "remark": "素材库测试站点",
                    "crawl_method": "API接口",
                },
            )
            assert site_response.status_code in (201, 400)

            task_response = client.post(
                "/api/crawl-tasks",
                json={
                    "keyword": "春日花海",
                    "target_scope": "selected",
                    "target_site_codes": ["material_seed_site"],
                    "per_site_limit": 2,
                    "max_pages": 1,
                    "created_by": "pytest-material",
                },
            )
            assert task_response.status_code == 201


        def test_material_library_flow():
            ensure_material_seed()

            list_response = client.get("/api/materials")
            assert list_response.status_code == 200
            assert len(list_response.json()) >= 1

            search_response = client.get("/api/materials", params={"query_text": "春日花海"})
            assert search_response.status_code == 200
            assert len(search_response.json()) >= 1

            upload_response = client.post(
                "/api/materials/upload",
                data={
                    "title": "手动素材",
                    "keywords": "本地上传 测试",
                    "remark": "手动上传备注",
                    "tags": "手动 测试 上传",
                },
                files=[
                    ("files", ("manual-1.png", build_image_bytes((255, 0, 0)), "image/png")),
                    ("files", ("manual-2.png", build_image_bytes((0, 255, 0)), "image/png")),
                ],
            )
            assert upload_response.status_code == 200
            upload_body = upload_response.json()
            assert len(upload_body["uploaded"]) == 2
            assert upload_body["duplicate_count"] == 0

            first_material_id = upload_body["uploaded"][0]["id"]
            detail_response = client.get(f"/api/materials/{first_material_id}")
            assert detail_response.status_code == 200
            assert detail_response.json()["source_type"] == "manual"

            action_response = client.post(
                f"/api/materials/{first_material_id}/actions",
                json={"action": "audit"},
            )
            assert action_response.status_code == 200
            assert action_response.json()["audit_status"] == "approved"

            tag_response = client.get("/api/materials/tags/summary")
            assert tag_response.status_code == 200
            assert any(tag["tag"] == "手动" for tag in tag_response.json())
        '''
    ).strip() + "\n",
}

for relative_path, content in FILES.items():
    target = BASE / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

print(f"generated {len(FILES)} files for material module")
