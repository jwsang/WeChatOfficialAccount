from datetime import UTC, datetime
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ModelConfig(Base):
    """
    大模型配置表
    用于统一管理项目中使用的所有大模型配置
    """
    __tablename__ = "model_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # 模型名称，如 "GPT-4", "Claude-3", "阿里云百炼" 等
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    # 模型类型，如 "openai", "anthropic", "aliyun", "zhipu" 等
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    # 模型标识符，如 "gpt-4-turbo", "claude-3-opus", "qwen-max" 等
    model_identifier: Mapped[str] = mapped_column(String(100), nullable=False)
    # API密钥
    api_key: Mapped[str] = mapped_column(Text, nullable=False)
    # API基础URL，不同服务商可能不同
    api_base: Mapped[str] = mapped_column(Text, nullable=True)
    # 是否为默认模型
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # 模型描述
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    # 额外配置参数，JSON格式存储
    extra_config: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    # 更新时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )