import logging
from typing import Any, List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.db import session
from src.oidc import oidcAuthorize
from src.v1.crud import crud_alerts
from src.v1.models import alerts as alerts_models
from src.v1.models import auth_model

# from src.v1.repository.basin_repository import basinRepository
router = APIRouter()
LOGGER = logging.getLogger(__name__)


@router.get("/", response_model=List[alerts_models.Alert_Basins])
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


@router.get("/{alert_id}", response_model=alerts_models.Alert_Basins)
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


#


@router.post(
    "/",
    status_code=201,
    response_model=alerts_models.Alert_Basins,
)
def create_alert(
    alert: alerts_models.Alert_Basins_Write,
    session: Session = Depends(session.get_db),
    is_authorized: bool = Depends(oidcAuthorize.authorize),
    token=Depends(oidcAuthorize.get_current_user),
):
    LOGGER.debug(f"token: {token}")
    written_alert = crud_alerts.create_alert(session=session, alert=alert)
    return written_alert


@router.patch(
    "/{alert_id}",
    response_model=alerts_models.Alert_Basins,
)
def update_alert(
    alert_id: int,
    alert: alerts_models.Alert_Basins_Write,
    session: Session = Depends(session.get_db),
    is_authorized: bool = Depends(oidcAuthorize.authorize),
    token: auth_model.User = Depends(oidcAuthorize.get_current_user),
) -> alerts_models.Alerts:
    """
    Performs an update of the alert, needs to also cache the changes to the previous
    alert.

    :param alert_id: the id for the alert that is being updated
    :type alert_id: int
    :param alert: the input data model that should be used to update the alert
    :type alert: model.Alert_Basins_Write
    :param session: database session for the transaction, defaults to Depends(session.get_db)
    :type session: Session, optional
    :param is_authorized: determines if the token has been sent and if it includes the required roles, defaults to Depends(oidcAuthorize.authorize)
    :type is_authorized: bool, optional
    :param token: access token, defaults to Depends(oidcAuthorize.get_current_user)
    :type token: _type_, optional
    :return: the updated alert object
    :rtype: auth_model.Alert
    """
    LOGGER.debug(f"token: {token}")
    LOGGER.debug(f"alertid: {alert_id}")
    current_status_alert = crud_alerts.get_alert(session, alert_id=alert_id)
    LOGGER.debug(f"current description: {current_status_alert}")
    LOGGER.debug(f"incomming description: {alert.alert_description}")
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

    # TODO: get the author name from the oidc access token and update before
    #       sending to the database.

    updated_alert = crud_alerts.update_alert(
        session=session, alert_id=alert_id, updated_alert=alert
    )
    LOGGER.debug(f"updated_alert: {updated_alert}")
    session.commit()
    return updated_alert
