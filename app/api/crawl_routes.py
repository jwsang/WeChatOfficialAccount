from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.crawl_task import CrawlTaskCreate, CrawlTaskDetailRead, CrawlTaskRead, CrawlTaskRetryRequest
from app.services.crawl_service import CrawlService


router = APIRouter(prefix="/api/crawl-tasks", tags=["crawl-tasks"])


def get_crawl_service(db: Session = Depends(get_db)) -> CrawlService:
    return CrawlService(db)


@router.get("", response_model=list[CrawlTaskRead])
def list_tasks(service: CrawlService = Depends(get_crawl_service)):
    return service.list_tasks()


@router.post("", response_model=CrawlTaskDetailRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: CrawlTaskCreate, service: CrawlService = Depends(get_crawl_service)):
    return service.create_task(payload)


@router.get("/{task_id}", response_model=CrawlTaskDetailRead)
def get_task(task_id: int, service: CrawlService = Depends(get_crawl_service)):
    return service.get_task_detail(task_id)


@router.post("/{task_id}/retry", response_model=CrawlTaskDetailRead)
def retry_task(task_id: int, payload: CrawlTaskRetryRequest, service: CrawlService = Depends(get_crawl_service)):
    return service.retry_task(task_id, payload)
