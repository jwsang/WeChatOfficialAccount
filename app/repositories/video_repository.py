from typing import Any

from sqlalchemy.orm import Session

from app.models.material_video import MaterialVideo


class VideoRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_videos(self, filters: dict[str, Any] | None = None) -> list[MaterialVideo]:
        query = self.db.query(MaterialVideo)
        if filters:
            if filters.get("query_text"):
                query = query.filter(
                    MaterialVideo.material_name.contains(filters["query_text"])
                )
            if filters.get("keyword"):
                query = query.filter(MaterialVideo.search_keyword == filters["keyword"])
            if filters.get("source_site_code"):
                query = query.filter(MaterialVideo.source_site_code == filters["source_site_code"])
            if filters.get("source_type"):
                query = query.filter(MaterialVideo.source_type == filters["source_type"])
            if filters.get("material_status"):
                query = query.filter(MaterialVideo.material_status == filters["material_status"])
            if filters.get("audit_status"):
                query = query.filter(MaterialVideo.audit_status == filters["audit_status"])
        return query.order_by(MaterialVideo.created_at.desc()).all()

    def get_video(self, video_id: int) -> MaterialVideo | None:
        return self.db.query(MaterialVideo).filter(MaterialVideo.id == video_id).first()

    def create_video(self, data: dict[str, Any]) -> MaterialVideo:
        video = MaterialVideo(**data)
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        return video

    def update_video(self, video_id: int, data: dict[str, Any]) -> MaterialVideo | None:
        video = self.get_video(video_id)
        if video:
            for key, value in data.items():
                if hasattr(video, key):
                    setattr(video, key, value)
            self.db.commit()
            self.db.refresh(video)
        return video

    def delete_video(self, video_id: int) -> bool:
        video = self.get_video(video_id)
        if video:
            self.db.delete(video)
            self.db.commit()
            return True
        return False

    def find_video_by_url_or_hash(self, video_url: str, video_hash: str) -> MaterialVideo | None:
        return self.db.query(MaterialVideo).filter(
            (MaterialVideo.source_video_url == video_url) |
            (MaterialVideo.video_hash == video_hash)
        ).first()
