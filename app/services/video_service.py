from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import DATA_DIR
from app.repositories.video_repository import VideoRepository
from app.schemas.video import MaterialVideoCreate, MaterialVideoRead


UPLOAD_DIR = DATA_DIR / "uploads" / "videos"
THUMBNAIL_DIR = DATA_DIR / "thumbnails" / "videos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)


class VideoService:
    def __init__(self, db: Session):
        self.repository = VideoRepository(db)

    def list_videos(self, filters: dict | None = None) -> list[MaterialVideoRead]:
        videos = self.repository.list_videos(filters)
        return [self._serialize_video(video) for video in videos]

    def get_video(self, video_id: int) -> MaterialVideoRead:
        video = self.repository.get_video(video_id)
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="视频素材不存在")
        return self._serialize_video(video)

    def upload_video(self, file: UploadFile, material_name: str | None = None) -> MaterialVideoRead:
        if not file.content_type or not file.content_type.startswith("video/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只能上传视频文件")

        content = file.file.read()
        video_hash = hashlib.sha256(content).hexdigest()

        exists = self.repository.find_video_by_url_or_hash("", video_hash)
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="视频已存在")

        ext = Path(file.filename).suffix if file.filename else ".mp4"
        filename = f"{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{video_hash[:8]}{ext}"
        local_path = UPLOAD_DIR / filename
        local_path.write_bytes(content)

        thumbnail_path = THUMBNAIL_DIR / f"{filename}.jpg"
        thumbnail_path.touch()

        video = self.repository.create_video({
            "material_name": material_name or file.filename or "未命名视频",
            "search_keyword": "",
            "source_site_code": "manual",
            "source_type": "upload",
            "source_page_url": "",
            "source_video_url": "",
            "local_file_path": str(local_path),
            "local_thumbnail_path": str(thumbnail_path),
            "video_hash": video_hash,
            "video_width": 0,
            "video_height": 0,
            "video_duration": 0.0,
            "file_size": len(content),
            "video_format": ext.lstrip(".").lower() or "mp4",
            "material_status": "available",
            "audit_status": "pending",
            "used_count": 0,
            "tag_codes": "",
            "crawl_task_id": None,
        })
        return self._serialize_video(video)

    def delete_video(self, video_id: int) -> bool:
        video = self.repository.get_video(video_id)
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="视频素材不存在")

        local_path = Path(video.local_file_path)
        if local_path.exists():
            local_path.unlink()

        thumbnail_path = Path(video.local_thumbnail_path)
        if thumbnail_path.exists():
            thumbnail_path.unlink()

        return self.repository.delete_video(video_id)

    def _serialize_video(self, video) -> MaterialVideoRead:
        return MaterialVideoRead(
            id=video.id,
            material_name=video.material_name,
            search_keyword=video.search_keyword,
            source_site_code=video.source_site_code,
            source_type=video.source_type,
            source_page_url=video.source_page_url,
            source_video_url=video.source_video_url,
            local_file_path=video.local_file_path,
            local_thumbnail_path=video.local_thumbnail_path,
            video_hash=video.video_hash,
            video_width=video.video_width,
            video_height=video.video_height,
            video_duration=video.video_duration,
            file_size=video.file_size,
            video_format=video.video_format,
            material_status=video.material_status,
            audit_status=video.audit_status,
            used_count=video.used_count,
            tag_codes=video.tag_codes,
            crawl_task_id=video.crawl_task_id,
            created_at=video.created_at,
            updated_at=video.updated_at,
        )
