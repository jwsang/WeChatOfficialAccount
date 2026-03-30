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
