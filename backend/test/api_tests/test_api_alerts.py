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
