import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from src.db import session
from src.v1.crud import crud_alerts
from src.v1.models import model

# from src.v1.repository.basin_repository import basinRepository

router = APIRouter()
LOGGER = logging.getLogger(__name__)


@router.get("/", response_model=List[model.Alert_Basins])
def read_alerts(
    db: Session = Depends(session.get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve existing alerts.
    """
    alerts = crud_alerts.get_alerts(db)
    for alert in alerts:
        LOGGER.info(f"alerts: {alert}")
        LOGGER.info(f"alerts: {alert.alert_links}")
        for alert_link in alert.alert_links:
            LOGGER.debug(f"alerts: {alert_link.alert_level}")
            LOGGER.debug(f"basin: {alert_link.basin}")
    return alerts


@router.get("/{alert_id}", response_model=model.Alert_Basins)
def read_alert(
    alert_id: int,
    session: Session = Depends(session.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve a specific alert
    """
    LOGGER.debug(f"alert_id: {alert_id}")
    LOGGER.debug(f"session is type: {type(session)}")
    alert = crud_alerts.get_alert(session, alert_id=alert_id)
    LOGGER.debug(f"alert from DB: {alert}")
    return alert


@router.post("/", response_model=model.Alert_Basins)
def create_alert(
    alert: model.Alert_Basins_Write, session: Session = Depends(session.get_db)
):
    written_alert = crud_alerts.create_alert(session=session, alert=alert)
    return written_alert
