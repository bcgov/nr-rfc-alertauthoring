import datetime
import json
import logging
import os.path
import typing

import fastapi.testclient
import helpers.alert_helpers as alert_helpers
import helpers.db_helpers as db_helpers
import pytest
import sqlmodel
import src.v1.crud.crud_alerts as crud_alerts
import src.v1.crud.crud_cap as crud_cap
from sqlmodel import Session
from src.core.config import Configuration
from src.types import AlertDataDict
from src.v1.models import alerts as alert_model
from src.v1.models import cap as cap_models

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
        if alert["alert_description"] == alert_dict["alert_description"]:
            alert_record = alert
            break

    LOGGER.debug(
        f'data: { alert_record["alert_created"]} {type( alert_record["alert_created"])}'
    )

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
    db_with_alert.flush()

    # query for all alerts, and grab the first alert
    response = client.get(f"{prefix}/alerts/")
    resp_json = response.json()
    LOGGER.debug(f"resp_json: {resp_json}")
    alert_id = resp_json[0]["alert_id"]

    # modify the dict
    #  - change the alert_description
    alert_dict["alert_description"] = (
        f"testing the patch method {datetime.datetime.now()}"
    )
    # update the dict author to the authorname from the simulated access token
    alert_dict["author_name"] = mock_access_token["display_name"]

    # add a basin / alert level and send to api
    alert_dict["alert_links"].append(
        {
            "basin": {"basin_name": "Liard"},
            "alert_level": {"alert_level": "High Streamflow Advisory"},
        }
    )
    endpoint_path = os.path.join(prefix, "alerts", str(alert_id)) + "/"
    response = client.patch(endpoint_path, json=alert_dict)
    response_data = response.json()
    LOGGER.debug(f"response_data: {response_data}")

    assert response_data["alert_description"] == alert_dict["alert_description"]

    new_link_added = False
    liard_basin_cnt = 0
    for link in response_data["alert_links"]:
        if link["basin"]["basin_name"] == "Liard":
            new_link_added = True
            break
        liard_basin_cnt += 1
    assert new_link_added

    # now modify the alert level for the record we just added
    alert_dict["alert_links"][liard_basin_cnt]["alert_level"][
        "alert_level"
    ] = "Flood Watch"
    response = client.patch(endpoint_path, json=alert_dict)
    resp_data = response.json()

    liard_basin_cnt = 0
    for link in alert_dict["alert_links"]:
        if link["basin"]["basin_name"] == "Liard":
            break
        liard_basin_cnt += 1
    LOGGER.debug(f"resp_data: {resp_data}")
    assert (
        resp_data["alert_links"][liard_basin_cnt]["alert_level"]["alert_level"]
        == "Flood Watch"
    )

    # test delete of alert link
    del alert_dict["alert_links"][liard_basin_cnt]
    response = client.patch(endpoint_path, json=alert_dict)
    resp_data = response.json()

    assert len(resp_data["alert_links"]) == len(alert_dict["alert_links"])

    # make sure the same links are in the response as the sent data
    for link in resp_data["alert_links"]:
        link_basin = {
            "basin": {"basin_name": link["basin"]["basin_name"]},
            "alert_level": {"alert_level": link["alert_level"]["alert_level"]},
        }
        assert link_basin in alert_dict["alert_links"]

    for property in alert_dict.keys():
        if not isinstance(resp_data[property], list):
            assert resp_data[property] == alert_dict[property]


def test_get_alert_levels(
    test_client_fixture: fastapi.testclient,
    alert_level_data: list[alert_model.Alert_Levels_Read],
):
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
    alert_level_strs = [level["alert_level"] for level in alert_level_data]

    assert len(alert_level_data) == len(alert_levels)
    for alert_level in alert_level_data:
        LOGGER.debug(f"alert_level: {alert_level['alert_level']}")
        assert alert_level["alert_level"] in alert_level_strs


@pytest.mark.parametrize(
    "existing_alert_list",
    [
        [
            {
                "alert_level": "High Streamflow Advisory",
                "basin_names": ["Central Coast", "Eastern Vancouver Island"],
            },
        ],
        [
            {
                "alert_level": "High Streamflow Advisory",
                "basin_names": ["Central Coast", "Eastern Vancouver Island"],
            },
            {"alert_level": "Flood Watch", "basin_names": ["Skeena"]},
            {
                "alert_level": "Flood Warning",
                "basin_names": ["Northern Vancouver Island"],
            },
        ],
    ],
)
def test_create_alert_history(
    test_client_fixture: fastapi.testclient,
    db_test_connection: Session,
    existing_alert_list: typing.List[AlertDataDict],
):
    """
    Create a alert through the API, then verify that it exists in the database.

    :param test_client_fixture: input test fixture
    :type test_client_fixture: fastapi.testclient
    :param proposed_alert: input alert record
    :type proposed_alert: dict
    """
    session = db_test_connection
    client = test_client_fixture
    prefix = Configuration.API_V1_STR

    alert = alert_helpers.create_fake_alert(existing_alert_list)
    alert_dict = alert.model_dump()

    alert_dict_json = json.dumps(alert_dict)
    LOGGER.debug(f"alert_dict_json: {alert_dict_json}")
    response = client.post(f"{prefix}/alerts/", json=alert_dict)
    existing_alert = response.json()
    LOGGER.debug(f"resp_data: {existing_alert}")
    LOGGER.debug(f"response: {response}")
    assert response.status_code == 201

    # now verify that the alert exists in the database
    # get all the history records
    hist_rec = crud_alerts.get_latest_history(
        session=session, alert_id=existing_alert["alert_id"]
    )
    LOGGER.debug(f"crud_alerts: {hist_rec}")
    # the alert was just created so there shouldn't be any history yet
    assert not hist_rec

    # now update the alert through the api
    # patch the alert data

    # the input schema to patch: Alert_Basins_Write
    # all the below todo can be accomplished with parameters
    # TODO: Add a basin, remove a basin
    # TODO: Add and alert level, remove an alert level
    patch_alert = alert_helpers.create_update_model(alert_list=existing_alert_list)
    patch_alert_dict = patch_alert.model_dump()
    alert_id = existing_alert["alert_id"]
    response = client.patch(f"{prefix}/alerts/{alert_id}" + "/", json=patch_alert_dict)
    patched_data = response.json()
    assert response.status_code >= 200 and response.status_code < 300

    # now verify the data
    LOGGER.debug(f"patched data: {patched_data}")

    # need to verify that the history record was created
    hist_rec = crud_alerts.get_latest_history(
        session=session, alert_id=existing_alert["alert_id"]
    )
    LOGGER.debug(f"type: {type(hist_rec)}")

    hist_rec_dict = hist_rec.model_dump()
    fields_to_check = [
        "alert_description",
        "alert_hydro_conditions",
        "alert_meteorological_conditions",
        "alert_status",
        "author_name",
    ]

    for key in fields_to_check:
        LOGGER.debug(f"key: {key} value: {hist_rec_dict[key]} ")
        assert existing_alert[key] == hist_rec_dict[key]

    # now verify the history alert level and basin data...
    # extract alert levels / basin dict from the history record
    hist_alert_basin_links = {}
    for link in hist_rec.alert_history_links:
        if link.alert_levels.alert_level not in hist_alert_basin_links:
            hist_alert_basin_links[link.alert_levels.alert_level] = []
        hist_alert_basin_links[link.alert_levels.alert_level].append(
            link.basins.basin_name
        )

    # extract alert levels / basin dict from original alert record that was created
    existing_alert_basin_links = {}
    for link in existing_alert["alert_links"]:
        if link["alert_level"]["alert_level"] not in existing_alert_basin_links:
            existing_alert_basin_links[link["alert_level"]["alert_level"]] = []
        existing_alert_basin_links[link["alert_level"]["alert_level"]].append(
            link["basin"]["basin_name"]
        )

    # now do the assertions
    assert len(existing_alert_basin_links) == len(hist_alert_basin_links)

    for key in existing_alert_basin_links.keys():
        assert key in hist_alert_basin_links
        for basin in existing_alert_basin_links[key]:
            assert basin in hist_alert_basin_links[key]

    for key in hist_alert_basin_links.keys():
        assert key in existing_alert_basin_links
        for basin in hist_alert_basin_links[key]:
            assert basin in existing_alert_basin_links[key]

    # instead of mocking the database behind the api client, opting to just do
    # a database cleanup on the alert that was created.  Cleanup will delete any
    # records in the database that are related to the provided alert id
    cleanup = db_helpers.db_cleanup(session=session)
    cleanup.cleanup(alert_id=existing_alert["alert_id"])

    session.commit()


@pytest.mark.parametrize(
    "existing_alert_list",
    [
        [
            {
                "alert_level": "High Streamflow Advisory",
                "basin_names": ["Central Coast", "Eastern Vancouver Island"],
            },
        ],
        [
            {
                "alert_level": "High Streamflow Advisory",
                "basin_names": ["Central Coast", "Eastern Vancouver Island"],
            },
            {"alert_level": "Flood Watch", "basin_names": ["Skeena"]},
            {
                "alert_level": "Flood Warning",
                "basin_names": ["Northern Vancouver Island"],
            },
        ],
    ],
)
def test_alert_cancel(
    test_client_fixture: fastapi.testclient,
    db_test_connection: Session,
    existing_alert_list: typing.List[AlertDataDict],
):
    """
    Setup, will create a alert, and then update that alert through the api, setting
    its status to 'Cancelled'

    The following will then be verified:
        * caps exist prior to the update
        * after the alert update (set to cancel), all caps are cancelled
    """
    session = db_test_connection
    client = test_client_fixture
    prefix = Configuration.API_V1_STR

    # create a fake alert in the database
    alert = alert_helpers.create_fake_alert(existing_alert_list)
    alert_db = crud_alerts.create_alert(session=session, alert=alert)
    alert_dict = alert.model_dump()

    # create the associated caps for the alert in the database
    caps = crud_cap.create_cap_event(session=session, alert=alert_db)

    # commit the changes so they are visible to the database session that
    # will be created for the api
    session.commit()

    # verify that the caps were in fact created, caps are unique to alert levels
    # so the number of alert levels in the input should align with the number of
    # caps created
    distinct_alert_levels = set(
        [
            existing_alert_dict["alert_level"]
            for existing_alert_dict in existing_alert_list
        ]
    )
    assert len(caps) == len(distinct_alert_levels)

    # now update the alert through the api setting its status to cancel
    cancelled_alert_list = existing_alert_list[0:]  # create copy of list
    cancelled_alert = alert_helpers.create_fake_alert(cancelled_alert_list)
    cancelled_alert.alert_status = alert_model.AlertStatus("cancelled").value

    LOGGER.debug(
        f"alert_status {cancelled_alert.alert_status}: {type(cancelled_alert.alert_status)}"
    )
    cancelled_alert_dict = cancelled_alert.model_dump()

    # now send the updated cancelled_alert to the api
    # response = client.post(f"{prefix}/alerts/", json=alert_dict)

    alert_dict_json = json.dumps(alert_dict)
    LOGGER.debug(f"alert_dict_json: {alert_dict_json}")
    response = client.patch(
        f"{prefix}/alerts/{alert_db.alert_id}/", json=cancelled_alert_dict
    )

    assert response.status_code == 200

    response_data = response.json()
    LOGGER.debug(f"response_data: {response_data}")

    cap_query = sqlmodel.select(cap_models.Cap_Event).where(
        cap_models.Cap_Event.alert_id == response_data["alert_id"]
    )

    # query for the cancel record
    caps = session.exec(cap_query).all()
    for cap in caps:
        LOGGER.debug(f"cap: {cap}")
        assert cap.cap_event_status.cap_event_status == "CANCEL"

    # now cleanup the caps and the alert
    cleanup = db_helpers.db_cleanup(session=session)
    cleanup.cleanup(alert_id=response_data["alert_id"])

    session.commit()

    # [
    #     {
    #         "alert_level": "High Streamflow Advisory",
    #         "basin_names": ["Central Coast", "Eastern Vancouver Island"],
    #     },
    #     {"alert_level": "Flood Watch", "basin_names": ["Skeena", "South Thompson"]},
    #     {
    #         "alert_level": "Flood Warning",
    #         "basin_names": ["Northern Vancouver Island", "Liard"],
    #     },
    # ],


@pytest.mark.parametrize(
    "existing_alert_list,updated_alert_list",
    [
        [
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast", "Eastern Vancouver Island"],
                }
            ],
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": [
                        "Central Coast",
                        "Eastern Vancouver Island",
                        "Skagit",
                    ],
                }
            ],
        ],
        [
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast", "Eastern Vancouver Island"],
                }
            ],
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast", "Eastern Vancouver Island"],
                },
                {
                    "alert_level": "Flood Watch",
                    "basin_names": ["Skagit"],
                },
            ],
        ],
        [
            [
                {
                    "alert_level": "Flood Warning",
                    "basin_names": ["Central Coast", "Eastern Vancouver Island"],
                }
            ],
            [
                {
                    "alert_level": "Flood Watch",
                    "basin_names": [
                        "Central Coast",
                        "Eastern Vancouver Island",
                        "Skagit",
                    ],
                }
            ],
        ],
        [
            [
                {
                    "alert_level": "Flood Warning",
                    "basin_names": ["Peace", "Northwest"],
                }
            ],
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": [
                        "Central Coast",
                        "Eastern Vancouver Island",
                        "Skagit",
                    ],
                }
            ],
        ],
        [
            [
                {
                    "alert_level": "Flood Warning",
                    "basin_names": ["Peace", "Northwest"],
                }
            ],
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Peace"],
                }
            ],
        ],
        [
            [
                {
                    "alert_level": "Flood Warning",
                    "basin_names": ["Peace", "Northwest"],
                }
            ],
            [
                {
                    "alert_level": "Flood Warning",
                    "basin_names": [],
                }
            ],
        ],
        [
            [
                {
                    "alert_level": "Flood Warning",
                    "basin_names": ["Peace", "Northwest"],
                }
            ],
            [
                {
                    "alert_level": "Flood Warning",
                    "basin_names": [],
                },
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Peace"],
                },
            ],
        ],
        [
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Peace"],
                }
            ],
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": [],
                },
                {
                    "alert_level": "Flood Warning",
                    "basin_names": [
                        "Skeena",
                        "Northwest",
                        "Fraser River",
                        "South Thompson",
                    ],
                },
                {
                    "alert_level": "Flood Watch",
                    "basin_names": ["Peace", "North Coast"],
                },
            ],
        ],
    ],
)
def test_alert_update_cap_history(
    test_client_fixture: fastapi.testclient,
    db_test_connection: Session,
    existing_alert_list: typing.List[AlertDataDict],
    updated_alert_list: typing.List[AlertDataDict],
):
    try:
        written_original_alert = None
        session = db_test_connection
        client = test_client_fixture
        prefix = Configuration.API_V1_STR

        # using the data in existing_alert_list create an Alert_Basins_Write object
        # then send that to the api to create the alert
        original_alert = alert_helpers.create_fake_alert(existing_alert_list)
        original_alert_dict = original_alert.model_dump()
        LOGGER.debug(f"alert to create: {original_alert_dict}")
        response = client.post(f"{prefix}/alerts/", json=original_alert_dict)
        written_original_alert = response.json()
        LOGGER.debug(f"resp_data: {written_original_alert}")

        # update the alert with random data
        # commented out because it was hard to debug random data.  Could
        # be reimplemented
        # updated_alert_list = alert_helpers.update_random_alert_data_dict(
        #     alert_list=existing_alert_list, update=True
        # )
        LOGGER.debug(f"random data: {updated_alert_list}")
        LOGGER.debug(f"source data: {existing_alert_list}")

        # create new a Alert_Basins_Write object from the data.
        written_original_alert_model = alert_model.Alert_Basins_Write(
            **written_original_alert
        )
        updated_alert = alert_helpers.update_fake_alert(
            existing_alert=written_original_alert_model, alert_list=updated_alert_list
        )
        updated_alert_dict = updated_alert.model_dump()
        # do the actual update of the alert through the api
        response = client.patch(
            f"{prefix}/alerts/{written_original_alert['alert_id']}/",
            json=updated_alert_dict,
        )
        assert response.status_code in [201, 200]
        updated_alert = response.json()

        session.flush()
        # query database for the cap history records
        cap_history_query = (
            sqlmodel.select(cap_models.Cap_Event_History).where(
                cap_models.Cap_Event_History.alert_id == updated_alert["alert_id"]
            )
            # .order_by(cap_models.Cap_Event_History.cap_event_hist_created_date.desc())
        )
        LOGGER.debug(f"query: {cap_history_query}")
        cap_history_records = session.exec(cap_history_query).all()
        LOGGER.debug(f"cap_history_records: {cap_history_records}")
        LOGGER.debug(f"existing_alert_list: {existing_alert_list}")

        # verify we have a cap event history record
        assert cap_history_records

        # verify its the correct record, associated with the alert
        for cap_hist_rec in cap_history_records:
            assert cap_hist_rec.alert_id == updated_alert["alert_id"]
        # should have the same number of history records as there are alert levels
        # in the existing_alert_list
        LOGGER.debug(f"length of cap_history_records: {len(cap_history_records)}")
        assert len(cap_history_records) == len(existing_alert_list)

        # make sure all the alerts in existing_alert_list are in the cap history and
        # vise versa
        hist_alert_lvls = [
            hist.alert_levels.alert_level for hist in cap_history_records
        ]
        for alert in existing_alert_list:
            assert alert["alert_level"] in hist_alert_lvls

        existing_alert_lvls = [alert["alert_level"] for alert in existing_alert_list]
        for alert_lvl in hist_alert_lvls:
            assert alert_lvl in existing_alert_lvls

        # per alert level make sure the basins align with the basins from existing_alert_list
        for hist in cap_history_records:
            hist_basins = [
                basin.basins.basin_name for basin in hist.cap_event_areas_hist
            ]
            for alert in existing_alert_list:
                if alert["alert_level"] == hist.alert_levels.alert_level:
                    for basin in alert["basin_names"]:
                        LOGGER.debug(f"basin: {basin}")
                        assert basin in hist_basins
    finally:
        if written_original_alert:
            cleanup = db_helpers.db_cleanup(session=session)
            cleanup.cleanup(alert_id=written_original_alert["alert_id"])

            session.commit()
