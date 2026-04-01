from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.model_config import ModelConfigCreate, ModelConfigRead, ModelConfigUpdate
from app.services.model_service import ModelConfigService

router = APIRouter(prefix="/api/model-configs", tags=["model-configs"])


@router.post("/", response_model=ModelConfigRead, status_code=status.HTTP_201_CREATED)
def create_model_config(
    model_config: ModelConfigCreate,
    db: Session = Depends(get_db)
):
    """
    创建模型配置
    """
    # 检查模型名称是否已存在
    existing_model = ModelConfigService.get_model_config_by_name(db, model_config.name)
    if existing_model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="模型名称已存在"
        )
    
    return ModelConfigService.create_model_config(db, model_config)


@router.get("/{model_id}", response_model=ModelConfigRead)
def get_model_config(
    model_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取模型配置
    """
    model_config = ModelConfigService.get_model_config_by_id(db, model_id)
    if not model_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型配置未找到"
        )
    
    return model_config


@router.put("/{model_id}", response_model=ModelConfigRead)
def update_model_config(
    model_id: int,
    model_config: ModelConfigUpdate,
    db: Session = Depends(get_db)
):
    """
    更新模型配置
    """
    updated_model = ModelConfigService.update_model_config(db, model_id, model_config)
    if not updated_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型配置未找到"
        )
    
    return updated_model


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model_config(
    model_id: int,
    db: Session = Depends(get_db)
):
    """
    删除模型配置
    """
    success = ModelConfigService.delete_model_config(db, model_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型配置未找到"
        )
    
    return


@router.get("", response_model=list[ModelConfigRead])
@router.get("/", response_model=list[ModelConfigRead])
def list_model_configs(
    db: Session = Depends(get_db)
):
    """
    获取所有模型配置
    """
    return ModelConfigService.get_all_model_configs(db)


@router.get("/default/", response_model=ModelConfigRead)
def get_default_model_config(
    db: Session = Depends(get_db)
):
    """
    获取默认模型配置
    """
    default_model = ModelConfigService.get_default_model_config(db)
    if not default_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未设置默认模型"
        )
    
    return default_model


@router.post("/test-connection/{model_id}", response_model=dict)
def test_model_connection(
    model_id: int,
    db: Session = Depends(get_db)
):
    """
    测试模型连接
    """
    model_config = ModelConfigService.get_model_config_by_id(db, model_id)
    if not model_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型配置未找到"
        )
    
    success, message = ModelConfigService.test_model_connection(model_config)
    return {
        "success": success,
        "message": message,
        "model_name": model_config.name
    }