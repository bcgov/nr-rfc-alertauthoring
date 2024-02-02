import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from src.db import session
from src.v1.models import model

# from src.v1.repository.basin_repository import basinRepository

router = APIRouter()
LOGGER = logging.getLogger(__name__)


@router.get("/", response_model=List[model.Alert_Basins])
def read_basins(
    db: Session = Depends(session.get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve basins.
    """
    alerts = db.exec(select(model.Alerts)).all()

    for alert in alerts:
        LOGGER.info(f"alerts: {alert}")
        LOGGER.info(f"alerts: {alert.alert_links}")
        for alert_link in alert.alert_links:
            LOGGER.debug(f"alerts: {alert_link.alert_level}")
            LOGGER.debug(f"basin: {alert_link.basin}")

    return alerts
