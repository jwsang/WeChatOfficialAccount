from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ArticleDraft(Base):
    __tablename__ = "article_drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    article_title: Mapped[str] = mapped_column(String(200), nullable=False)
    cover_material_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    article_summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    author_name: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    source_url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    content_html: Mapped[str] = mapped_column(Text, default="", nullable=False)
    publish_payload: Mapped[str] = mapped_column(Text, default="", nullable=False)
    template_code: Mapped[str] = mapped_column(String(50), default="image_gallery", nullable=False)
    draft_status: Mapped[str] = mapped_column(String(30), default="editing", nullable=False)
    wx_draft_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    wx_publish_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
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
