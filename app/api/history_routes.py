from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.history import HistoryOverviewRead
from app.services.history_service import HistoryService


router = APIRouter(prefix="/api/history", tags=["history"])


def get_history_service(db: Session = Depends(get_db)) -> HistoryService:
    return HistoryService(db)


@router.get("/overview", response_model=HistoryOverviewRead)
def get_history_overview(service: HistoryService = Depends(get_history_service)):
    return service.get_overview()
