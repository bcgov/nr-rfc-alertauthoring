import datetime
import json
import logging
import os.path

import fastapi.testclient
from sqlmodel import select
from src.core.config import Configuration
from src.v1.models import alerts as alert_model

LOGGER = logging.getLogger(__name__)


def test_get_alerts(db_with_alert, test_client_fixture, alert_dict):
    
    
    client = test_client_fixture
    prefix = Configuration.API_V1_STR
    response = client.get(f"{prefix}/alerts/")

    assert response.status_code == 200
    LOGGER.debug(f"response: {response}")
    LOGGER.debug(f"responsedata : {response.json()}")

    data = response.json()

    # verify that the correct data is returned
    assert len(data) >= 1

    # find the alert with the alert description the same as the submitted data
    alert_record = None
    for alert in data:
        if alert['alert_description'] == alert_dict['alert_description']:
            alert_record = alert
            break

    LOGGER.debug(f'data: { alert_record["alert_created"]} {type( alert_record["alert_created"])}')

    properties_to_check = [
        "alert_status",
        "author_name",
        "alert_description",
        "alert_hydro_conditions",
        "alert_meteorological_conditions",
    ]
    for current_property in properties_to_check:
        assert alert_dict[current_property] == alert_record[current_property]
    # now verify the basin / alert levels are entered correctly

    assert len(alert_dict["alert_links"]) == len(alert_record["alert_links"])


# db_with_alert
def test_alert(test_client_fixture, db_with_alert, alert_dict):
    client = test_client_fixture

    prefix = Configuration.API_V1_STR
    # get all the alerts that were populated by the fixture
    alerts_response = client.get(f"{prefix}/alerts")
    alerts_data = alerts_response.json()

    # get the alert record that was created by the fixture
    cnt = 0
    for cnt in range(0, len(alerts_data)):
        if alerts_data[cnt]["alert_description"] == alert_dict["alert_description"]:
            break
        cnt += 1



    # use the first record from all alerts to test the retrieval of a specific alert
    url = f"{prefix}/alerts/{alerts_data[cnt]['alert_id']}"
    alert_response = client.get(url)
    LOGGER.debug(f"alert_response: {alert_response}")
    alert_data = alert_response.json()
    LOGGER.debug(f"alert_data: {alert_data}")
    assert alert_response.status_code == 200
    assert alert_data["alert_description"] == alert_dict["alert_description"]


def test_alert_post(test_client_fixture, alert_dict):
    """
    tests creating a new record through the api

    :param test_client_fixture: _description_
    :type test_client_fixture: _type_
    :param alert_basin_write: _description_
    :type alert_basin_write: _type_
    """
    client = test_client_fixture
    prefix = Configuration.API_V1_STR

    alert_dict_json = json.dumps(alert_dict)
    LOGGER.debug(f"alert_dict_json: {alert_dict_json}")
    response = client.post(f"{prefix}/alerts/", json=alert_dict)
    resp_data = response.json()
    LOGGER.debug(f"resp_data: {resp_data}")
    LOGGER.debug(f"response: {response}")
    assert response.status_code == 201
    data = response.json()
    LOGGER.debug(f"data: {data}")
    # assert data["alert_description"] == alert_basin_write["alert_description"]
    # TODO: assert the data created is the same as the data sent


def test_alert_patch(test_client_fixture, alert_dict, db_with_alert, mock_access_token):
    """
    The fixture db_with_alert ensure that the database includes the alert that
    is also described in alert_basin_write as an alert_model.Alert_Basins_Write
    and alert_dict which contains a dict with the same data.

    the test will call the update end point, and then verify that the returned
    data contains the changes that were requested.

    The method that the end point calls has other tests associated with it that
    do in depth verification that the correct history records etc are created.

    :param test_client_fixture: a startlette test client that is configured to
        test the application
    :type test_client_fixture: fastapi.testclient.TestClient
    :param alert_dict: a dictionary that contains the alert record that has been
        inserted into the database
    :type alert_dict: dict
    :param db_with_alert: a database session object with the data in the database
    :type db_with_alert: sqlmodel.Session
    :param alert_basin_write: same as the dict but in the format of a alert_model.Alert_Basins_Write
    :type alert_basin_write: alert_model.Alert_Basins_Write
    """
    client = test_client_fixture
    prefix = Configuration.API_V1_STR
    db_with_alert.commit()

    # get the alert id
    # cur_alert = select(alert_model.Alerts).where(alert_model.Alerts.alert_description == alert_dict["alert_description"])
    # alert_id = cur_alert.alert_id
    # LOGGER.debug(f"alert_id: {alert_id}")

    response = client.get(f"{prefix}/alerts/")
    resp_json = response.json()
    LOGGER.debug(f"resp_json: {resp_json}")
    alert_id = resp_json[0]['alert_id']

    # modify the dict
    #  - change the alert_description
    alert_dict["alert_description"] = (
        f"testing the patch method {datetime.datetime.now()}"
    )
    # update the dict author to the authorname from the simulated access token
    alert_dict["author_name"] = mock_access_token["display_name"]

    # add a basin / alert level
    alert_dict["alert_links"].append(
        {
            "basin": {"basin_name": "Liard"},
            "alert_level": {"alert_level": "High Streamflow Advisory"},
        }
    )
    endpoint_path = os.path.join(prefix, 'alerts', str(alert_id)) + '/'
    response = client.patch(endpoint_path, json=alert_dict)
    response_data = response.json()
    LOGGER.debug(f"response_data: {response_data}")

    assert response_data["alert_description"] == alert_dict["alert_description"]

    new_link_added = False
    liard_basin_cnt = 0
    for link in response_data['alert_links']:
        if link['basin']['basin_name'] == 'Liard':
            new_link_added = True
            break
        liard_basin_cnt += 1
    assert new_link_added

    # now modify the alert level for the record we just added
    alert_dict['alert_links'][liard_basin_cnt]['alert_level']['alert_level'] = 'Flood Watch'
    response = client.patch(endpoint_path, json=alert_dict)
    resp_data = response.json()

    liard_basin_cnt = 0
    for link in alert_dict['alert_links']:
        if link['basin']['basin_name'] == 'Liard':
            break
        liard_basin_cnt += 1
    LOGGER.debug(f'resp_data: {resp_data}')
    assert resp_data['alert_links'][liard_basin_cnt]['alert_level']['alert_level'] == 'Flood Watch'

    # test delete of alert link
    del alert_dict['alert_links'][liard_basin_cnt]
    response = client.patch(endpoint_path, json=alert_dict)
    resp_data = response.json()

    assert len(resp_data['alert_links']) == len(alert_dict['alert_links'])

    # make sure the same links are in the response as the sent data
    for link in resp_data['alert_links']:
        link_basin = {
            "basin": {"basin_name": link['basin']['basin_name']},
            "alert_level": {"alert_level": link['alert_level']['alert_level']}
        }
        assert link_basin in alert_dict['alert_links']

    for property in alert_dict.keys():
        if not isinstance(resp_data[property], list):
            assert resp_data[property] == alert_dict[property]


def test_get_alert_levels(test_client_fixture: fastapi.testclient, alert_level_data: list[alert_model.Alert_Levels_Read]):
    """
    verifies that the alert level end point is returning the expected data

    :param test_client_fixture: input test fixture
    :type test_client_fixture: fastapi.testclient
    :param alert_level_data: dictionary loaded from the alert_levels.json file
    :type alert_level_data: dict
    """
    client = test_client_fixture
    prefix = Configuration.API_V1_STR
    response = client.get(f"{prefix}/alert_levels/")
    alert_levels = response.json()
    LOGGER.debug(f"alert_levels: {alert_levels}")
    alert_level_strs = [level['alert_level'] for level in alert_level_data]

    assert len(alert_level_data) == len(alert_levels)
    for alert_level in alert_level_data:
        LOGGER.debug(f"alert_level: {alert_level['alert_level']}")
        assert alert_level['alert_level'] in alert_level_strs
