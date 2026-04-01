from __future__ import annotations

from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, validator

from app.schemas.ai_assist import AiAssistConfigRead


class ModelProvider(str, Enum):
    """模型提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    ALIYUN = "aliyun"
    ZHIPU = "zhipu"
    BAIDU = "baidu"
    TENCENT = "tencent"
    MOONSHOT = "moonshot"
    DEEPSEEK = "deepseek"
    MINIMAX = "minimax"
    STEPFUN = "stepfun"
    OTHER = "other"


class ModelConfigBase(BaseModel):
    """模型配置基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="模型名称")
    provider: ModelProvider = Field(..., description="模型提供商")
    model_identifier: str = Field(..., min_length=1, max_length=100, description="模型标识符")
    api_key: str = Field(..., min_length=1, max_length=500, description="API密钥")
    api_base: Optional[str] = Field(None, max_length=500, description="API基础URL")
    is_default: bool = Field(default=False, description="是否为默认模型")
    description: Optional[str] = Field("", max_length=1000, description="模型描述")
    extra_config: Optional[str] = Field(default="{}", max_length=2000, description="额外配置参数")

    @validator('api_base')
    def validate_api_base(cls, v, values):
        """验证API基础URL格式"""
        if v:
            # 简单验证URL格式
            if not v.startswith(('http://', 'https://')):
                raise ValueError('API基础URL必须以http://或https://开头')
        return v


class ModelConfigCreate(ModelConfigBase):
    """模型配置创建模型"""
    pass


class ModelConfigUpdate(BaseModel):
    """模型配置更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="模型名称")
    provider: Optional[str] = Field(None, min_length=1, max_length=50, description="模型提供商")
    model_identifier: Optional[str] = Field(None, min_length=1, max_length=100, description="模型标识符")
    api_key: Optional[str] = Field(None, min_length=1, max_length=500, description="API密钥")
    api_base: Optional[str] = Field(None, max_length=500, description="API基础URL")
    is_default: Optional[bool] = Field(None, description="是否为默认模型")
    description: Optional[str] = Field(None, max_length=1000, description="模型描述")
    extra_config: Optional[str] = Field(None, max_length=2000, description="额外配置参数")


class ModelConfigRead(ModelConfigBase):
    """模型配置读取模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True