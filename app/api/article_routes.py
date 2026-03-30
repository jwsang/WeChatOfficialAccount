from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.article import (
    ArticleDraftListItemRead,
    ArticleDraftRead,
    ArticleDraftUpdateRequest,
    ArticleGenerateRequest,
    WechatConfigStatusRead,
    WechatPublishActionRead,
)
from app.services.article_service import ArticleService


router = APIRouter(prefix="/api/articles", tags=["articles"])


def get_article_service(db: Session = Depends(get_db)) -> ArticleService:
    return ArticleService(db)


@router.post("/preview", response_model=ArticleDraftRead)
def generate_article_preview(
    payload: ArticleGenerateRequest,
    service: ArticleService = Depends(get_article_service),
):
    return service.generate_preview(payload)


@router.post("/drafts", response_model=ArticleDraftRead, status_code=status.HTTP_201_CREATED)
def save_article_draft(
    payload: ArticleGenerateRequest,
    service: ArticleService = Depends(get_article_service),
):
    return service.save_draft(payload)


@router.get("/drafts", response_model=list[ArticleDraftListItemRead])
def list_article_drafts(
    service: ArticleService = Depends(get_article_service),
):
    return service.list_drafts()


@router.get("/drafts/{draft_id}", response_model=ArticleDraftRead)
def get_article_draft(
    draft_id: int,
    service: ArticleService = Depends(get_article_service),
):
    return service.get_draft(draft_id)


@router.put("/drafts/{draft_id}", response_model=ArticleDraftRead)
def update_article_draft(
    draft_id: int,
    payload: ArticleDraftUpdateRequest,
    service: ArticleService = Depends(get_article_service),
):
    return service.update_draft(draft_id, payload)


@router.post("/drafts/{draft_id}/duplicate", response_model=ArticleDraftRead, status_code=status.HTTP_201_CREATED)
def duplicate_article_draft(
    draft_id: int,
    service: ArticleService = Depends(get_article_service),
):
    return service.duplicate_draft(draft_id)


@router.get("/wechat/config-status", response_model=WechatConfigStatusRead)
def get_wechat_config_status(
    service: ArticleService = Depends(get_article_service),
):
    return service.get_wechat_config_status()


@router.post("/drafts/{draft_id}/sync", response_model=WechatPublishActionRead)
def sync_article_draft_to_wechat(
    draft_id: int,
    service: ArticleService = Depends(get_article_service),
):
    return service.sync_draft_to_wechat(draft_id)


@router.post("/drafts/{draft_id}/publish", response_model=WechatPublishActionRead)
def publish_article_draft(
    draft_id: int,
    service: ArticleService = Depends(get_article_service),
):
    return service.publish_draft_to_wechat(draft_id)


@router.delete("/drafts/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article_draft(
    draft_id: int,
    service: ArticleService = Depends(get_article_service),
):
    service.delete_draft(draft_id)
