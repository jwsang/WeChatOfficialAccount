from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.site import (
    SiteConfigCreate,
    SiteConfigRead,
    SiteConfigUpdate,
    SiteTestRequest,
    SiteTestResponse,
)
from app.services.site_service import SiteService


router = APIRouter(prefix="/api/sites", tags=["sites"])


def get_site_service(db: Session = Depends(get_db)) -> SiteService:
    return SiteService(db)


@router.get("", response_model=list[SiteConfigRead])
def list_sites(service: SiteService = Depends(get_site_service)):
    return service.list_sites()


@router.post("", response_model=SiteConfigRead, status_code=status.HTTP_201_CREATED)
def create_site(payload: SiteConfigCreate, service: SiteService = Depends(get_site_service)):
    return service.create_site(payload)


@router.put("/{site_id}", response_model=SiteConfigRead)
def update_site(site_id: int, payload: SiteConfigUpdate, service: SiteService = Depends(get_site_service)):
    return service.update_site(site_id, payload)


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_site(site_id: int, service: SiteService = Depends(get_site_service)):
    service.delete_site(site_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{site_id}/test", response_model=SiteTestResponse)
def test_site(site_id: int, payload: SiteTestRequest, service: SiteService = Depends(get_site_service)):
    return service.test_site(site_id, payload.keyword)
