import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

import src.v1.models.alerts as alerts
from src.db import session

router = APIRouter()
LOGGER = logging.getLogger(__name__)


@router.get("/", response_model=List[alerts.Basins])
def read_basins(
    db: Session = Depends(session.get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve basins.
    """
    basins = db.exec(select(alerts.Basins)).all()
    return basins
