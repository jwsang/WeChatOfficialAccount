from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.site_config import SiteConfig
from app.schemas.site import SiteConfigCreate, SiteConfigUpdate


class SiteRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_sites(self) -> list[SiteConfig]:
        statement = select(SiteConfig).order_by(SiteConfig.created_at.desc())
        return list(self.db.scalars(statement).all())

    def get_by_id(self, site_id: int) -> SiteConfig | None:
        return self.db.get(SiteConfig, site_id)

    def get_by_code(self, code: str) -> SiteConfig | None:
        statement = select(SiteConfig).where(SiteConfig.code == code)
        return self.db.scalar(statement)

    def create(self, payload: SiteConfigCreate) -> SiteConfig:
        site = SiteConfig(**payload.model_dump())
        self.db.add(site)
        self.db.commit()
        self.db.refresh(site)
        return site

    def update(self, site: SiteConfig, payload: SiteConfigUpdate) -> SiteConfig:
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(site, key, value)
        self.db.add(site)
        self.db.commit()
        self.db.refresh(site)
        return site

    def delete(self, site: SiteConfig) -> None:
        self.db.delete(site)
        self.db.commit()
