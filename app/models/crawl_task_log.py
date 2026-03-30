from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CrawlTaskLog(Base):
    __tablename__ = "crawl_task_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    crawl_task_id: Mapped[int] = mapped_column(ForeignKey("crawl_tasks.id"), nullable=False, index=True)
    site_code: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    message: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
