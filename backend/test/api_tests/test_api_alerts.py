import datetime
import json
import logging

from src.core.config import Configuration

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
    assert len(data) == 1

    LOGGER.debug(f'data: { data[0]["alert_created"]} {type( data[0]["alert_created"])}')

    # 2024-02-03T00:32:50.468722
    # data: 2024-02-03T00:32:50.468722 <class 'str'>

    # data_create_time = datetime.datetime.strptime(
    #     data[0]["alert_created"], "%Y-%m-%dT%H:%M:%S.%f"
    # )
    # LOGGER.debug(f"data_create_time: {data_create_time}")
    # assert alert_data_only.alert_created == data_create_time

    properties_to_check = [
        "alert_status",
        "author_name",
        "alert_description",
        "alert_hydro_conditions",
        "alert_meteorological_conditions",
    ]
    for current_property in properties_to_check:
        assert alert_dict[current_property] == data[0][current_property]
    # now verify the basin / alert levels are entered correctly

    assert len(alert_dict["alert_links"]) == len(data[0]["alert_links"])


# db_with_alert
def test_alert(test_client_fixture, db_with_alert, alert_dict):
    client = test_client_fixture

    prefix = Configuration.API_V1_STR
    # get all the alerts that were populated by the fixture
    alerts_response = client.get(f"{prefix}/alerts")
    alerts_data = alerts_response.json()

    # use the first record from all alerts to test the retrieval of a specific alert
    url = f"{prefix}/alerts/{alerts_data[0]['alert_id']}"
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


def test_alert_patch(test_client_fixture, alert_dict, db_with_alert):
    #TODO: code this up
    pass
