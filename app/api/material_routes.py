from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.material import (
    MaterialActionRequest,
    MaterialListFilters,
    MaterialRead,
    MaterialTagSummaryRead,
    MaterialUploadRead,
)
from app.services.material_service import MaterialService


router = APIRouter(prefix="/api/materials", tags=["materials"])


def get_material_service(db: Session = Depends(get_db)) -> MaterialService:
    return MaterialService(db)


@router.get("/tags/summary", response_model=list[MaterialTagSummaryRead])
def list_tag_summary(service: MaterialService = Depends(get_material_service)):
    return service.list_tag_summary()


@router.get("", response_model=list[MaterialRead])
def list_materials(
    query_text: str = Query(default=""),
    keyword: str = Query(default=""),
    source_site_code: str = Query(default=""),
    source_type: str = Query(default=""),
    material_status: str = Query(default=""),
    audit_status: str = Query(default=""),
    tag: str = Query(default=""),
    service: MaterialService = Depends(get_material_service),
):
    filters = MaterialListFilters(
        query_text=query_text,
        keyword=keyword,
        source_site_code=source_site_code,
        source_type=source_type,
        material_status=material_status,
        audit_status=audit_status,
        tag=tag,
    )
    return service.list_materials(filters)


@router.post("/upload", response_model=MaterialUploadRead)
async def upload_materials(
    files: list[UploadFile] = File(...),
    title: str | None = Form(default=None),
    keywords: str = Form(default=""),
    remark: str = Form(default=""),
    tags: str = Form(default=""),
    service: MaterialService = Depends(get_material_service),
):
    return await service.upload_materials(files, title, keywords, remark, tags)


@router.get("/{material_id}", response_model=MaterialRead)
def get_material(material_id: int, service: MaterialService = Depends(get_material_service)):
    return service.get_material(material_id)


@router.post("/{material_id}/actions", response_model=MaterialRead)
def update_material_action(
    material_id: int,
    payload: MaterialActionRequest,
    service: MaterialService = Depends(get_material_service),
):
    return service.update_material_action(material_id, payload)
