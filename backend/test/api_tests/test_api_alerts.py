import datetime
import logging

from src.core.config import Configuration

LOGGER = logging.getLogger(__name__)


def test_alerts(db_with_alert, test_client_fixture, alert_data, alert_data_test_levels):
    client = test_client_fixture
    prefix = Configuration.API_V1_STR
    response = client.get(f"{prefix}/alerts")

    assert response.status_code == 200
    LOGGER.debug(f"response: {response}")
    LOGGER.debug(f"responsedata : {response.json()}")

    data = response.json()

    # verify that the correct data is returned
    assert len(data) == 1

    LOGGER.debug(f'data: { data[0]["alert_created"]} {type( data[0]["alert_created"])}')

    # 2024-02-03T00:32:50.468722
    # data: 2024-02-03T00:32:50.468722 <class 'str'>

    data_create_time = datetime.datetime.strptime(
        data[0]["alert_created"], "%Y-%m-%dT%H:%M:%S.%f"
    )
    LOGGER.debug(f"data_create_time: {data_create_time}")
    assert alert_data.alert_created == data_create_time

    # now verify the basin / alert levels are entered correctly
    assert len(alert_data.alert_links) == len(data[0]["alert_links"])


# db_with_alert
def test_alert(test_client_fixture, db_with_alert, alert_data):
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
    assert alert_data["alert_id"] == alerts_data[0]["alert_id"]
