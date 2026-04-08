from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class WechatMenu(Base):
    __tablename__ = "wechat_menus"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    menu_name: Mapped[str] = mapped_column(String(100), nullable=False)
    menu_type: Mapped[str] = mapped_column(String(50), default="click", nullable=False)
    menu_key: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    menu_url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    menu_appid: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    menu_pagepath: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    menu_status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
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
