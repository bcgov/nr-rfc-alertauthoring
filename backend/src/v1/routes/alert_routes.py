import logging
from typing import Any, List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.db import session
from src.oidc import oidcAuthorize
from src.v1.crud import crud_alerts, crud_cap
from src.v1.models import alerts as alerts_models
from src.v1.models import auth_model
from src.v1.models import cap as cap_models

# from src.v1.repository.basin_repository import basinRepository
router = APIRouter()
LOGGER = logging.getLogger(__name__)


# get all the alerts
@router.get("/", response_model=List[alerts_models.Alert_Basins])
def read_alerts(
    db: Session = Depends(session.get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve existing alerts.
    """
    LOGGER.debug("incomming alert list request")
    alerts = crud_alerts.get_alerts(db)
    LOGGER.debug(f"alerts: {alerts}")
    for alert in alerts:
        LOGGER.info(f"alerts: {alert}")
        LOGGER.info(f"alerts: {alert.alert_links}")
        for alert_link in alert.alert_links:
            LOGGER.debug(f"alerts: {alert_link.alert_level}")
            LOGGER.debug(f"basin: {alert_link.basin}")
    return alerts


# get a specific alert
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


# create an alert
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
    caps = crud_cap.create_cap_event(session=session, alert=written_alert)
    # not doing anything with the caps at this point
    LOGGER.debug(f"cap created from the alert: {caps}")
    # session.commit()
    return written_alert


# update an alert
@router.patch(
    "/{alert_id}" + "/",
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

    # get the alert from the database that is going to be updated
    current_status_alert = crud_alerts.get_alert(session, alert_id=alert_id)
    LOGGER.debug(f"current description: {current_status_alert}")
    LOGGER.debug(f"incomming description: {alert.alert_description}")

    # record the current state of the alert as a history record
    crud_alerts.create_history_record(session, current_status_alert)

    # update the alert with the new data
    updated_alert = crud_alerts.update_alert(
        session=session, alert_id=alert_id, updated_alert=alert
    )
    LOGGER.debug(f"updated_alert: {updated_alert}")

    # now update the author from the access token
    LOGGER.debug(f"token: {token}")
    updated_alert.author_name = token["display_name"]
    session.add(updated_alert)
    session.flush()

    # record the current state of the cap events that are relted to the alert that
    # is being updated.
    crud_cap.record_history(session, updated_alert)

    # update cap events.  This operation will break the caps into three categories
    #  - new caps (for the addition of a new alert level associated with the alert)
    #  - updated caps (existing alert levels with areas added or removed)
    #  - cancels (for alert levels that no longer have areas associated with them,
    #             OR if the alert itself has been set to 'CANCEL')
    crud_cap.update_cap_event(session, updated_alert)
    return updated_alert


@router.get("/{alert_id}/caps", response_model=List[cap_models.Cap_Event_And_Areas])
def get_caps_for_alert(
    alert_id: int,
    session: Session = Depends(session.get_db),
    skip: int = 0,
    limit: int = 100,
):
    LOGGER.debug(f"alert_id: {alert_id}")
    caps = crud_cap.get_cap_events_for_alert(session=session, alert_id=alert_id)
    return caps
