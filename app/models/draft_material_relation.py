from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DraftMaterialRelation(Base):
    __tablename__ = "draft_material_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    draft_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    material_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    sort_index: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    caption_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
