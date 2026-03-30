from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SiteConfig(Base):
    __tablename__ = "site_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    search_rule: Mapped[str] = mapped_column(Text, default="", nullable=False)
    parse_rule: Mapped[str] = mapped_column(Text, default="", nullable=False)
    page_rule: Mapped[str] = mapped_column(Text, default="", nullable=False)
    remark: Mapped[str] = mapped_column(Text, default="", nullable=False)
    crawl_method: Mapped[str] = mapped_column(String(100), default="HTML解析", nullable=False)
    rule_config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    last_crawled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
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
