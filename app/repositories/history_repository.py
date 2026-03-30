from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.article_draft import ArticleDraft
from app.models.crawl_task import CrawlTask
from app.models.crawl_task_log import CrawlTaskLog
from app.models.material_image import MaterialImage
from app.models.publish_record import PublishRecord


class HistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_drafts(self) -> list[ArticleDraft]:
        statement = select(ArticleDraft).order_by(ArticleDraft.updated_at.desc(), ArticleDraft.id.desc())
        return list(self.db.scalars(statement).all())

    def list_materials(self) -> list[MaterialImage]:
        statement = select(MaterialImage).order_by(MaterialImage.created_at.desc(), MaterialImage.id.desc())
        return list(self.db.scalars(statement).all())

    def list_crawl_tasks(self, limit: int = 20) -> list[CrawlTask]:
        statement = select(CrawlTask).order_by(CrawlTask.created_at.desc(), CrawlTask.id.desc()).limit(limit)
        return list(self.db.scalars(statement).all())

    def list_crawl_logs(self, limit: int = 20) -> list[CrawlTaskLog]:
        statement = select(CrawlTaskLog).order_by(CrawlTaskLog.created_at.desc(), CrawlTaskLog.id.desc()).limit(limit)
        return list(self.db.scalars(statement).all())

    def list_publish_records(self, limit: int = 20) -> list[PublishRecord]:
        statement = select(PublishRecord).order_by(PublishRecord.created_at.desc(), PublishRecord.id.desc()).limit(limit)
        return list(self.db.scalars(statement).all())
