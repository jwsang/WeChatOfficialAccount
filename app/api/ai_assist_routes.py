from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ai_assist import (
    AiAssistAddToMaterialRead,
    AiAssistAddToMaterialRequest,
    AiAssistConfigRead,
    AiAssistConfigUpdateRequest,
    AiAssistGenerateRead,
)
from app.services.ai_assist_service import AiAssistService


router = APIRouter(prefix="/api/ai-assist", tags=["ai-assist"])


def get_ai_assist_service(db: Session = Depends(get_db)) -> AiAssistService:
    return AiAssistService(db)


@router.get("/config", response_model=AiAssistConfigRead)
def get_ai_assist_config(service: AiAssistService = Depends(get_ai_assist_service)):
    return service.get_config()


@router.put("/config", response_model=AiAssistConfigRead)
def update_ai_assist_config(
    payload: AiAssistConfigUpdateRequest,
    service: AiAssistService = Depends(get_ai_assist_service),
):
    return service.update_config(payload)


@router.put("/config-with-model/{model_config_id}", response_model=AiAssistConfigRead)
def update_ai_assist_config_with_model(
    model_config_id: int,
    service: AiAssistService = Depends(get_ai_assist_service),
):
    """
    使用模型管理中的配置更新AI助手配置
    """
    return service.update_config_with_model(model_config_id)


@router.post("/generate", response_model=AiAssistGenerateRead)
async def generate_ai_images(
    prompt: str = Form(...),
    model_id: int | None = Form(default=None),
    negative_prompt: str = Form(default=""),
    count: int = Form(default=4),
    size: str = Form(default="1024x1024"),
    quality: str = Form(default="standard"),
    style: str = Form(default="vivid"),
    reference_image: UploadFile | None = File(default=None),
    service: AiAssistService = Depends(get_ai_assist_service),
):
    return await service.generate_images(
        prompt=prompt,
        model_id=model_id,
        negative_prompt=negative_prompt,
        count=count,
        size=size,
        quality=quality,
        style=style,
        reference_image=reference_image,
    )


@router.post("/materials", response_model=AiAssistAddToMaterialRead)
def add_generated_images_to_materials(
    payload: AiAssistAddToMaterialRequest,
    service: AiAssistService = Depends(get_ai_assist_service),
):
    return service.add_generated_to_materials(payload)
