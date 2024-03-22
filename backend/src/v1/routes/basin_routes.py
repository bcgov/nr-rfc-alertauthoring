import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from src.db import session
from src.v1.models import model

# from src.v1.repository.basin_repository import basinRepository

router = APIRouter()
LOGGER = logging.getLogger(__name__)


@router.get("/", response_model=List[model.Basins])
def read_basins(
    db: Session = Depends(session.get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve basins.
    """
    basins = db.exec(select(model.Basins)).all()
    return basins
