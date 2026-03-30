from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.crawl_task import CrawlTask
from app.models.crawl_task_log import CrawlTaskLog
from app.models.material_image import MaterialImage
from app.models.site_config import SiteConfig


class CrawlTaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_tasks(self) -> list[CrawlTask]:
        statement = select(CrawlTask).order_by(CrawlTask.created_at.desc())
        return list(self.db.scalars(statement).all())

    def get_task(self, task_id: int) -> CrawlTask | None:
        return self.db.get(CrawlTask, task_id)

    def create_task(self, payload: dict) -> CrawlTask:
        task = CrawlTask(**payload)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def save_task(self, task: CrawlTask) -> CrawlTask:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def list_enabled_sites(self) -> list[SiteConfig]:
        statement = select(SiteConfig).where(SiteConfig.enabled.is_(True)).order_by(SiteConfig.name.asc())
        return list(self.db.scalars(statement).all())

    def list_enabled_sites_by_codes(self, codes: list[str]) -> list[SiteConfig]:
        if not codes:
            return []
        statement = (
            select(SiteConfig)
            .where(SiteConfig.enabled.is_(True), SiteConfig.code.in_(codes))
            .order_by(SiteConfig.name.asc())
        )
        return list(self.db.scalars(statement).all())

    def find_material_by_url_or_hash(self, source_image_url: str, image_hash: str) -> MaterialImage | None:
        statement = select(MaterialImage).where(
            or_(
                MaterialImage.source_image_url == source_image_url,
                MaterialImage.image_hash == image_hash,
            )
        )
        return self.db.scalar(statement)

    def create_material(self, payload: dict) -> MaterialImage:
        material = MaterialImage(**payload)
        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)
        return material

    def list_materials_by_task(self, task_id: int) -> list[MaterialImage]:
        statement = (
            select(MaterialImage)
            .where(MaterialImage.crawl_task_id == task_id)
            .order_by(MaterialImage.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def create_log(self, payload: dict) -> CrawlTaskLog:
        log = CrawlTaskLog(**payload)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_logs_by_task(self, task_id: int) -> list[CrawlTaskLog]:
        statement = (
            select(CrawlTaskLog)
            .where(CrawlTaskLog.crawl_task_id == task_id)
            .order_by(CrawlTaskLog.created_at.desc(), CrawlTaskLog.id.desc())
        )
        return list(self.db.scalars(statement).all())
