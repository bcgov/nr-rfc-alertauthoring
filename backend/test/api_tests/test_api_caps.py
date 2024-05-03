import logging
import pprint

import fastapi.testclient
import src.v1.models.alerts as alert_models
from sqlmodel import Session, select
from src.core.config import Configuration

LOGGER = logging.getLogger(__name__)

def test_get_caps(db_with_alert: Session, test_client_with_alert_and_cap, alert_dict):
    client = test_client_with_alert_and_cap
    prefix = Configuration.API_V1_STR
    session = db_with_alert
    session.commit()

    response = client.get(f"{prefix}/cap/")

    assert response.status_code == 200
    LOGGER.debug(f"response: {response}")
    LOGGER.debug(f"responsedata : {response.json()}")

    cap_dict = response.json()
    data_formatted = pprint.pformat(cap_dict, indent=4)

    LOGGER.debug(f"data: \n{data_formatted}\n")

    # verify that the caps where created properly
    #  first get the alert for the cap
    alert_query = select(alert_models.Alerts).where(alert_models.Alerts.alert_description == alert_dict["alert_description"])
    alert_records = session.exec(alert_query).fetchall()
    alert_record = alert_records[-1] # get the last record
    alert_id_to_verify = alert_record.alert_id
    LOGGER.debug(f"verify the alert id: {alert_id_to_verify}")

    # now verify that the alert levels / basins in the alert record correspond 
    # to the cap records
    
    # verify the alert levels
    # go through the alert and organize the basins by alert levels
    alert_lvl_basins_dict = {}
    for alert_link in alert_record.alert_links:
        if alert_link.alert_level.alert_level not in alert_lvl_basins_dict:
            alert_lvl_basins_dict[alert_link.alert_level.alert_level] = []
        alert_lvl_basins_dict[alert_link.alert_level.alert_level].append(alert_link.basin.basin_name)

    # now iterate over the caps and verify the cap data is in the alert
    for cap in cap_dict:
        assert cap['alert_id'] == alert_id_to_verify
        # verify the alert level is in the alert
        assert cap['alert_level']['alert_level'] in alert_lvl_basins_dict
        # verify the basins
        for event_area in cap['event_areas']:
            assert event_area['cap_area_basin']['basin_name'] in alert_lvl_basins_dict[cap['alert_level']['alert_level']]
