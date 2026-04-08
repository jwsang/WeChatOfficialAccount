from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.wechat_client import WechatApiClient


router = APIRouter(prefix="/api/wechat", tags=["wechat"])


def get_wechat_config(db: Session = Depends(get_db)) -> dict:
    from app.models.app_setting import AppSetting
    setting = db.query(AppSetting).filter(
        AppSetting.setting_key.in_(["wechat_app_id", "wechat_app_secret"])
    ).all()
    config = {s.setting_key: s.setting_value for s in setting}
    return config


@router.get("/config-status")
def get_config_status(db: Session = Depends(get_db)):
    config = get_wechat_config(db)
    has_app_id = bool(config.get("wechat_app_id"))
    has_secret = bool(config.get("wechat_app_secret"))
    return {
        "configured": has_app_id and has_secret,
        "has_app_id": has_app_id,
        "has_app_secret": has_secret,
    }


@router.put("/config")
def update_config(app_id: str, app_secret: str, db: Session = Depends(get_db)):
    from app.models.app_setting import AppSetting
    for key, value in [("wechat_app_id", app_id), ("wechat_app_secret", app_secret)]:
        setting = db.query(AppSetting).filter(AppSetting.setting_key == key).first()
        if setting:
            setting.setting_value = value
        else:
            setting = AppSetting(setting_key=key, setting_value=value)
            db.add(setting)
    db.commit()
    return {"status": "success"}


@router.get("/menu")
def get_menu(db: Session = Depends(get_db)):
    from app.models.wechat_menu import WechatMenu
    menus = db.query(WechatMenu).filter(WechatMenu.parent_id.is_(None)).order_by(WechatMenu.sort_order).all()
    result = []
    for menu in menus:
        item = {
            "id": menu.id,
            "name": menu.menu_name,
            "type": menu.menu_type,
            "key": menu.menu_key,
            "url": menu.menu_url,
            "children": [],
        }
        children = db.query(WechatMenu).filter(WechatMenu.parent_id == menu.id).order_by(WechatMenu.sort_order).all()
        for child in children:
            item["children"].append({
                "id": child.id,
                "name": child.menu_name,
                "type": child.menu_type,
                "key": child.menu_key,
                "url": child.menu_url,
            })
        result.append(item)
    return {"menu": result}


@router.post("/menu")
def save_menu(menu_data: list[dict], db: Session = Depends(get_db)):
    from app.models.wechat_menu import WechatMenu
    db.query(WechatMenu).delete()
    for idx, item in enumerate(menu_data):
        parent = WechatMenu(
            menu_name=item.get("name", ""),
            menu_type=item.get("type", "click"),
            menu_key=item.get("key", ""),
            menu_url=item.get("url", ""),
            sort_order=idx,
            menu_status="draft",
        )
        db.add(parent)
        db.flush()
        for cidx, child in enumerate(item.get("children", [])):
            sub = WechatMenu(
                menu_name=child.get("name", ""),
                menu_type=child.get("type", "click"),
                menu_key=child.get("key", ""),
                menu_url=child.get("url", ""),
                parent_id=parent.id,
                sort_order=cidx,
                menu_status="draft",
            )
            db.add(sub)
    db.commit()
    return {"status": "success"}


@router.post("/menu/publish")
def publish_menu(db: Session = Depends(get_db)):
    config = get_wechat_config(db)
    if not config.get("wechat_app_id") or not config.get("wechat_app_secret"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="微信配置不完整")
    
    client = WechatApiClient(config["wechat_app_id"], config["wechat_app_secret"])
    access_token = client.get_access_token()
    
    from app.models.wechat_menu import WechatMenu
    menus = db.query(WechatMenu).filter(WechatMenu.parent_id.is_(None)).order_by(WechatMenu.sort_order).all()
    menu_json = {"button": []}
    for menu in menus:
        button = {"name": menu.menu_name, "sub_button": []}
        children = db.query(WechatMenu).filter(WechatMenu.parent_id == menu.id).order_by(WechatMenu.sort_order).all()
        if children:
            for child in children:
                sub_btn = {"type": child.menu_type, "name": child.menu_name}
                if child.menu_type == "view":
                    sub_btn["url"] = child.menu_url
                elif child.menu_type == "click":
                    sub_btn["key"] = child.menu_key
                button["sub_button"].append(sub_btn)
        else:
            if menu.menu_type == "view":
                button["type"] = "view"
                button["url"] = menu.menu_url
            else:
                button["type"] = "click"
                button["key"] = menu.menu_key
        menu_json["button"].append(button)
    
    import httpx
    url = f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={access_token}"
    with httpx.Client() as client_http:
        resp = client_http.post(url, json=menu_json)
        result = resp.json()
        if result.get("errcode", 0) != 0:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"发布失败：{result.get('errmsg')}")
    
    db.query(WechatMenu).update({"menu_status": "published"})
    db.commit()
    return {"status": "success"}


@router.get("/reply")
def list_replies(db: Session = Depends(get_db)):
    from app.models.auto_reply import AutoReply
    replies = db.query(AutoReply).order_by(AutoReply.created_at.desc()).all()
    return [{"id": r.id, "name": r.reply_name, "keyword": r.keyword, "type": r.reply_type, "enabled": r.is_enabled} for r in replies]


@router.post("/reply")
def create_reply(reply_data: dict, db: Session = Depends(get_db)):
    from app.models.auto_reply import AutoReply
    reply = AutoReply(
        reply_name=reply_data.get("name", ""),
        reply_type=reply_data.get("type", "text"),
        keyword=reply_data.get("keyword", ""),
        keyword_type=reply_data.get("keyword_type", "exact"),
        reply_content=reply_data.get("content", ""),
        is_enabled=reply_data.get("enabled", True),
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return {"id": reply.id, "status": "success"}


@router.delete("/reply/{reply_id}")
def delete_reply(reply_id: int, db: Session = Depends(get_db)):
    from app.models.auto_reply import AutoReply
    reply = db.query(AutoReply).filter(AutoReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="回复规则不存在")
    db.delete(reply)
    db.commit()
    return {"status": "success"}
