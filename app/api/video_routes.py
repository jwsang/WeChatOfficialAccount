from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.video import MaterialVideoRead
from app.services.video_service import VideoService


router = APIRouter(prefix="/api/videos", tags=["videos"])


def get_video_service(db: Session = Depends(get_db)) -> VideoService:
    return VideoService(db)


@router.get("", response_model=list[MaterialVideoRead])
def list_videos(service: VideoService = Depends(get_video_service)):
    return service.list_videos()


@router.post("", response_model=MaterialVideoRead, status_code=status.HTTP_201_CREATED)
def upload_video(
    file: UploadFile = File(...),
    material_name: str | None = Form(None),
    service: VideoService = Depends(get_video_service),
):
    return service.upload_video(file, material_name)


@router.delete("/{video_id}")
def delete_video(video_id: int, service: VideoService = Depends(get_video_service)):
    return {"deleted": service.delete_video(video_id)}


@router.get("/{video_id}", response_model=MaterialVideoRead)
def get_video(video_id: int, service: VideoService = Depends(get_video_service)):
    return service.get_video(video_id)
