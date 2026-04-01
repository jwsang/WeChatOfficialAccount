from typing import List, Optional
import json
from sqlalchemy.orm import Session
from app.models.model_config import ModelConfig
from app.schemas.model_config import ModelConfigCreate, ModelConfigUpdate, ModelProvider


class ModelConfigService:
    """
    模型配置服务类
    提供对模型配置的增删改查操作
    """
    
    @staticmethod
    def create_model_config(db: Session, model_config: ModelConfigCreate) -> ModelConfig:
        """
        创建模型配置
        
        Args:
            db: 数据库会话
            model_config: 模型配置创建对象
            
        Returns:
            ModelConfig: 创建的模型配置对象
        """
        # 验证额外配置是否为有效的JSON
        if model_config.extra_config and model_config.extra_config != "{}":
            try:
                parsed_extra_config = json.loads(model_config.extra_config)
                if not isinstance(parsed_extra_config, dict):
                    raise ValueError("额外配置必须是JSON对象")
            except json.JSONDecodeError:
                raise ValueError("额外配置不是有效的JSON格式")
        else:
            model_config.extra_config = "{}"
        
        # 如果设置为默认模型，则先取消其他模型的默认状态
        if model_config.is_default:
            ModelConfigService._unset_default_models(db)
        
        db_model = ModelConfig(
            name=model_config.name,
            provider=model_config.provider.value if hasattr(model_config.provider, 'value') else model_config.provider,
            model_identifier=model_config.model_identifier,
            api_key=model_config.api_key,
            api_base=model_config.api_base,
            is_default=model_config.is_default,
            description=model_config.description,
            extra_config=model_config.extra_config
        )
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model
    
    @staticmethod
    def get_model_config_by_id(db: Session, model_id: int) -> Optional[ModelConfig]:
        """
        根据ID获取模型配置
        
        Args:
            db: 数据库会话
            model_id: 模型配置ID
            
        Returns:
            ModelConfig: 模型配置对象，如果不存在则返回None
        """
        return db.query(ModelConfig).filter(ModelConfig.id == model_id).first()
    
    @staticmethod
    def get_model_config_by_name(db: Session, name: str) -> Optional[ModelConfig]:
        """
        根据名称获取模型配置
        
        Args:
            db: 数据库会话
            name: 模型名称
            
        Returns:
            ModelConfig: 模型配置对象，如果不存在则返回None
        """
        return db.query(ModelConfig).filter(ModelConfig.name == name).first()
    
    @staticmethod
    def get_all_model_configs(db: Session) -> List[ModelConfig]:
        """
        获取所有模型配置
        
        Args:
            db: 数据库会话
            
        Returns:
            List[ModelConfig]: 所有模型配置列表
        """
        return db.query(ModelConfig).order_by(ModelConfig.created_at.desc()).all()
    
    @staticmethod
    def update_model_config(db: Session, model_id: int, model_config: ModelConfigUpdate) -> Optional[ModelConfig]:
        """
        更新模型配置
        
        Args:
            db: 数据库会话
            model_id: 模型配置ID
            model_config: 模型配置更新对象
            
        Returns:
            ModelConfig: 更新后的模型配置对象，如果不存在则返回None
        """
        db_model = ModelConfigService.get_model_config_by_id(db, model_id)
        if not db_model:
            return None
        
        # 验证额外配置是否为有效的JSON（如果提供了的话）
        update_data = model_config.dict(exclude_unset=True)
        if 'extra_config' in update_data and update_data['extra_config'] and update_data['extra_config'] != "{}":
            try:
                parsed_extra_config = json.loads(update_data['extra_config'])
                if not isinstance(parsed_extra_config, dict):
                    raise ValueError("额外配置必须是JSON对象")
            except json.JSONDecodeError:
                raise ValueError("额外配置不是有效的JSON格式")
        elif 'extra_config' in update_data and not update_data['extra_config']:
            # 如果提供了空的extra_config，将其设置为默认值
            update_data['extra_config'] = "{}"
        
        # 如果更新为默认模型，则先取消其他模型的默认状态
        if model_config.is_default:
            ModelConfigService._unset_default_models(db)
        
        for field, value in update_data.items():
            if field == 'provider' and hasattr(value, 'value'):
                # 处理枚举值
                setattr(db_model, field, value.value)
            else:
                setattr(db_model, field, value)
        
        db.commit()
        db.refresh(db_model)
        return db_model
    
    @staticmethod
    def delete_model_config(db: Session, model_id: int) -> bool:
        """
        删除模型配置
        
        Args:
            db: 数据库会话
            model_id: 模型配置ID
            
        Returns:
            bool: 删除成功返回True，否则返回False
        """
        db_model = ModelConfigService.get_model_config_by_id(db, model_id)
        if not db_model:
            return False
        
        db.delete(db_model)
        db.commit()
        return True
    
    @staticmethod
    def get_default_model_config(db: Session) -> Optional[ModelConfig]:
        """
        获取默认模型配置
        
        Args:
            db: 数据库会话
            
        Returns:
            ModelConfig: 默认模型配置对象，如果不存在则返回None
        """
        return db.query(ModelConfig).filter(ModelConfig.is_default == True).first()
    
    @staticmethod
    def _unset_default_models(db: Session) -> None:
        """
        取消所有模型的默认状态
        内部方法，用于确保只有一个默认模型
        
        Args:
            db: 数据库会话
        """
        db.query(ModelConfig).filter(ModelConfig.is_default == True).update({ModelConfig.is_default: False})
        db.commit()
    
    @staticmethod
    def get_default_api_base(provider: str) -> str:
        """
        根据提供商获取默认的 API 基础 URL
        """
        provider_map = {
            'openai': 'https://api.openai.com/v1',
            'anthropic': 'https://api.anthropic.com/v1',
            'aliyun': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
            'zhipu': 'https://open.bigmodel.cn/api/paas/v4',
            'baidu': 'https://aip.baidubce.com/rpc/2.0/ernie_bot',
            'tencent': 'https://hunyuan.tencentcloudapi.com',
            'moonshot': 'https://api.moonshot.cn/v1',
            'deepseek': 'https://api.deepseek.com/v1',
            'minimax': 'https://api.minimaxi.com/v1',
            'stepfun': 'https://api.stepfun.com/v1'
        }
        return provider_map.get(provider.lower(), 'https://api.openai.com/v1')

    @staticmethod
    def test_model_connection(model_config: ModelConfig) -> tuple[bool, str]:
        """
        测试模型连接是否有效
        
        Args:
            model_config: 模型配置对象
            
        Returns:
            tuple[bool, str]: (是否成功, 错误信息或成功信息)
        """
        import httpx
        try:
            # 动态获取 API 基础 URL，不再硬编码 OpenAI 地址
            api_base = model_config.api_base or ModelConfigService.get_default_api_base(model_config.provider)
            headers = {
                "Authorization": f"Bearer {model_config.api_key}",
                "Content-Type": "application/json"
            }
            
            # 使用一个非常简单的 chat completion 请求来测试
            payload = {
                "model": model_config.model_identifier,
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 5
            }
            
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    f"{api_base.rstrip('/')}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    return True, f"{model_config.provider} 模型连接测试成功"
                else:
                    error_msg = response.text
                    try:
                        error_json = response.json()
                        if "error" in error_json:
                            error_msg = error_json["error"].get("message", error_msg)
                    except:
                        pass
                    return False, f"连接测试失败 ({response.status_code}): {error_msg}"
                
        except Exception as e:
            return False, f"模型连接测试过程中发生异常: {str(e)}"