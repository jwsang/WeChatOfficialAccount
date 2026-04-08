from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MaterialVideo(Base):
    __tablename__ = "material_videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    material_name: Mapped[str] = mapped_column(String(200), nullable=False)
    search_keyword: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    source_site_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(20), default="crawl", nullable=False)
    source_page_url: Mapped[str] = mapped_column(Text, default="", nullable=False)
    source_video_url: Mapped[str] = mapped_column(Text, default="", nullable=False)
    local_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    local_thumbnail_path: Mapped[str] = mapped_column(String(500), nullable=False)
    video_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    video_width: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    video_height: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    video_duration: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    video_format: Mapped[str] = mapped_column(String(20), default="mp4", nullable=False)
    material_status: Mapped[str] = mapped_column(String(30), default="available", nullable=False)
    audit_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tag_codes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    crawl_task_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
