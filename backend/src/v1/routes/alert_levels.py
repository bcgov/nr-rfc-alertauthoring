import logging
from typing import Any, List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.db import session
from src.v1.crud import crud_alerts
from src.v1.models import alerts as alerts_models

router = APIRouter()
LOGGER = logging.getLogger(__name__)


@router.get("/", response_model=List[alerts_models.Alert_Levels_Read])
def read_alert_levels(
    db: Session = Depends(session.get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve existing alerts.
    """
    alerts = crud_alerts.get_alert_levels(db)
    LOGGER.info(f"alerts: {alerts}")
    return alerts

