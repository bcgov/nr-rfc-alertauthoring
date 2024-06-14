import logging
import pprint

import src.v1.models.alerts as alert_models
from sqlmodel import Session, select
from src.core.config import Configuration

LOGGER = logging.getLogger(__name__)


def test_get_caps(db_with_alert: Session, test_client_with_alert_and_cap, alert_dict):
    client = test_client_with_alert_and_cap[0]
    session = test_client_with_alert_and_cap[1]
    prefix = Configuration.API_V1_STR
    # session = db_with_alert
    # session.flush()

    response = client.get(f"{prefix}/cap/")

    assert response.status_code == 200
    LOGGER.debug(f"response: {response}")
    LOGGER.debug(f"responsedata : {response.json()}")

    cap_dict = response.json()
    data_formatted = pprint.pformat(cap_dict, indent=4)

    LOGGER.debug(f"data: \n{data_formatted}\n")

    # verify that the caps where created properly
    #  first get the alert for the cap
    alert_query = select(alert_models.Alerts).where(
        alert_models.Alerts.alert_description == alert_dict["alert_description"]
    )
    LOGGER.debug(f"alert_query: {alert_query}")
    alert_records = session.exec(alert_query).all()

    # identify the alert with with the largest id to indicate the last one
    # created
    alert_record = None
    for cur_alert in alert_records:
        if alert_record is None:
            alert_record = cur_alert
        elif cur_alert.alert_id > alert_record.alert_id:
            alert_record = cur_alert
    LOGGER.debug(f"alert_record: {alert_record}")
    alert_id_to_verify = alert_record.alert_id
    LOGGER.debug(f"verify the alert id: {alert_id_to_verify}")

    for cap in cap_dict:
        LOGGER.debug(f"cap alert id: {cap['alert_id']}")

    # now iterate over the caps and verify the cap data is in the alert
    for cap in cap_dict:
        # if the alert_id isn't the one that has been created for this test don't
        # skip over those caps
        if cap["alert_id"] == alert_id_to_verify:
            # get the alert that corresponds with the cap
            alert_query = select(alert_models.Alerts).where(
                alert_models.Alerts.alert_id == cap["alert_id"]
            )
            alert_record = session.exec(alert_query).all()[-1]
            assert cap["alert_id"] == alert_record.alert_id
            LOGGER.debug(f"cap alert area id: {cap['alert_id']}")

            # now extract the alert levels / alert basins from the alert to verify against
            # alert levels and basins in the cap
            alert_lvl_basins_dict = {}
            for alert_link in alert_record.alert_links:
                if alert_link.alert_level.alert_level not in alert_lvl_basins_dict:
                    alert_lvl_basins_dict[alert_link.alert_level.alert_level] = []
                alert_lvl_basins_dict[alert_link.alert_level.alert_level].append(
                    alert_link.basin.basin_name
                )
            LOGGER.debug(f"alert_lvl_basins_dict: {alert_lvl_basins_dict}")

            # verify the alert level is in the alert
            assert cap["alert_level"]["alert_level"] in alert_lvl_basins_dict
            # verify the basins
            for event_area in cap["event_areas"]:
                LOGGER.debug(f"current event_area: {event_area}")
                assert (
                    event_area["cap_area_basin"]["basin_name"]
                    in alert_lvl_basins_dict[cap["alert_level"]["alert_level"]]
                )


