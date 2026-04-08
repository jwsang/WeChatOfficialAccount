from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AutoReply(Base):
    __tablename__ = "auto_replies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reply_name: Mapped[str] = mapped_column(String(100), nullable=False)
    reply_type: Mapped[str] = mapped_column(String(50), default="text", nullable=False)
    keyword: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    keyword_type: Mapped[str] = mapped_column(String(30), default="exact", nullable=False)
    reply_content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    media_id: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    media_url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    match_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
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
