import logging
import pprint

import fastapi.testclient
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

    data = response.json()
    data_formatted = pprint.pformat(data, indent=4)

    LOGGER.debug(f"data: \n{data_formatted}\n")


