import logging
from typing import Any, List

import src.v1.models.alerts as alerts
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import src.v1.models.alerts as alerts

# from src.oidc.oidcAuthorize as oidcAuthorize
from src.db import session
from src.oidc import oidcAuthorize
from src.v1.crud import crud_alerts

# from src.v1.repository.basin_repository import basinRepository
router = APIRouter()
LOGGER = logging.getLogger(__name__)


@router.get("/", response_model=List[alerts.Alert_Basins])
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


@router.get("/{alert_id}", response_model=alerts.Alert_Basins)
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


@router.post(
    "/",
    response_model=alerts.Alert_Basins,
)
def create_alert(
    alert: alerts.Alert_Basins_Write,
    session: Session = Depends(session.get_db),
    is_authorized: bool = Depends(oidcAuthorize.authorize),
    token=Depends(oidcAuthorize.get_current_user),
):
    LOGGER.debug(f"token: {token}")
    written_alert = crud_alerts.create_alert(session=session, alert=alert)
    return written_alert


@router.patch(
    "/{alert_id}",
    response_model=alerts.Alert_Basins,
)
def update_alert(
    alert_id: int,
    alert: alerts.Alert_Basins_Write,
    session: Session = Depends(session.get_db),
    is_authorized: bool = Depends(oidcAuthorize.authorize),
    token=Depends(oidcAuthorize.get_current_user),
):
    """
    Performs an update of the alert, needs to also cache the changes to the previous
    alert.

    :param alert_id: _description_
    :type alert_id: int
    :param alert: _description_
    :type alert: model.Alert_Basins_Write
    :param session: _description_, defaults to Depends(session.get_db)
    :type session: Session, optional
    :param is_authorized: _description_, defaults to Depends(oidcAuthorize.authorize)
    :type is_authorized: bool, optional
    :param token: _description_, defaults to Depends(oidcAuthorize.get_current_user)
    :type token: _type_, optional
    :return: _description_
    :rtype: _type_
    """
    LOGGER.debug(f"token: {token}")
    current_status_alert = crud_alerts.get_alert(session, alert_id=alert_id)

    # get incomming related (basin and alert_level) data
    # get existing related (basin and alert_level ) data
    # compare incomming and existing data
    # separate changes into:
    #   - net new area / alert level added
    #   - existing area / alert level removed
    #   - existing area / alert level updated
    #
    # record changes in the alert history table

    # has the alert record changed / yes
    #    - record the previous alert status in history
    #    - update the alert record with incomming changes

    #

    return current_status_alert
    # written_alert = crud_alerts.create_alert(session=session, alert=alert)
    # return written_alert
