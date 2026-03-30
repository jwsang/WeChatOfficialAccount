from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.article_draft import ArticleDraft
from app.models.draft_material_relation import DraftMaterialRelation
from app.models.material_image import MaterialImage
from app.models.publish_record import PublishRecord


class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_materials_by_ids(self, material_ids: list[int]) -> list[MaterialImage]:
        statement = select(MaterialImage).where(MaterialImage.id.in_(material_ids))
        return list(self.db.scalars(statement).all())

    def create_draft(self, payload: dict) -> ArticleDraft:
        draft = ArticleDraft(**payload)
        self.db.add(draft)
        self.db.flush()
        return draft

    def create_relations(self, payloads: list[dict]) -> list[DraftMaterialRelation]:
        relations = [DraftMaterialRelation(**payload) for payload in payloads]
        self.db.add_all(relations)
        self.db.flush()
        return relations

    def increase_material_usage(self, material_ids: list[int]) -> None:
        materials = self.get_materials_by_ids(material_ids)
        material_map = {material.id: material for material in materials}
        for material_id in material_ids:
            material = material_map.get(material_id)
            if material:
                material.used_count += 1
                self.db.add(material)

    def list_drafts(self, exclude_deleted: bool = True) -> list[ArticleDraft]:
        statement = select(ArticleDraft)
        if exclude_deleted:
            statement = statement.where(ArticleDraft.draft_status != "deleted")
        statement = statement.order_by(ArticleDraft.updated_at.desc(), ArticleDraft.id.desc())
        return list(self.db.scalars(statement).all())

    def get_draft(self, draft_id: int) -> ArticleDraft | None:
        return self.db.get(ArticleDraft, draft_id)

    def save_draft(self, draft: ArticleDraft) -> ArticleDraft:
        self.db.add(draft)
        self.db.flush()
        return draft

    def create_publish_record(self, payload: dict) -> PublishRecord:
        record = PublishRecord(**payload)
        self.db.add(record)
        self.db.flush()
        return record

    def delete_relations(self, draft_id: int) -> None:
        statement = delete(DraftMaterialRelation).where(DraftMaterialRelation.draft_id == draft_id)
        self.db.execute(statement)

    def list_relations(self, draft_id: int) -> list[DraftMaterialRelation]:
        statement = (
            select(DraftMaterialRelation)
            .where(DraftMaterialRelation.draft_id == draft_id)
            .order_by(DraftMaterialRelation.sort_index.asc(), DraftMaterialRelation.id.asc())
        )
        return list(self.db.scalars(statement).all())

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, instance) -> None:
        self.db.refresh(instance)
