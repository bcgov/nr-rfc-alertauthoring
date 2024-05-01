import logging
from typing import Any, List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.db import session
from src.v1.crud import crud_cap
from src.v1.models import cap as cap_models

router = APIRouter()
LOGGER = logging.getLogger(__name__)

@router.get("/", response_model=List[cap_models.Cap_Event_Read])
def get_caps(
    alert_id: int,
    db: Session = Depends(session.get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve existing alert levels used to define individual alerts.
    """
    caps = crud_cap.get_cap_event(db, alert_id=alert_id)
    LOGGER.info(f"caps: {caps}")
    return caps
