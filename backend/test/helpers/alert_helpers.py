import datetime
import logging
import typing

import faker
from src.types import AlertDataDict
from src.v1.models import alerts as alerts_models
from src.v1.models import basins as basin_models

LOGGER = logging.getLogger(__name__)


def create_alertlvl_basin_dict(
    input_alert_data_dict_list: AlertDataDict,
) -> typing.Dict[str, typing.List[str]]:
    """
    creates a dictionary that contains the alert level as the key, and the
    basin names as the values.  This is used to simulate the data that would
    be returned from the database when querying for alerts and the associated
    basins.
    """
    alert_lvl_basin_dict = {}
    for input_alert_data_dict in input_alert_data_dict_list:
        for basin_name in input_alert_data_dict["basin_names"]:
            if input_alert_data_dict["alert_level"] in alert_lvl_basin_dict:
                alert_lvl_basin_dict[input_alert_data_dict["alert_level"]].append(
                    basin_name
                )
            else:
                alert_lvl_basin_dict[input_alert_data_dict["alert_level"]] = [
                    basin_name
                ]
    return alert_lvl_basin_dict


def create_alert_area_list(
    alert_list: AlertDataDict,
) -> typing.List[alerts_models.Alert_Areas_Write]:
    LOGGER.debug(f"alert_dict: {alert_list}")
    alert_area_list = []
    for alert_dict in alert_list:
        for basin_name in alert_dict["basin_names"]:
            LOGGER.debug(f"basin_name: {basin_name}")
            alert_area = alerts_models.Alert_Areas_Write(
                alert_level=alerts_models.Alert_Levels_Base(
                    alert_level=alert_dict["alert_level"]
                ),
                basin=basin_models.BasinBase(basin_name=basin_name),
            )
            alert_area_list.append(alert_area)
    return alert_area_list


def create_fake_alert(alert_list: AlertDataDict) -> alerts_models.Alert_Basins_Write:
    """
    creates a fake alert object from a dictionary.  The dictionary is expected
    to contain the following keys:
    - alert_level: the alert level string value
    - basin_names: a list of basin names that are associated with the alert level

    :param alert_dict: a dictionary containing the alert level and basin names
    :type alert_dict: typing.Dict
    """
    alert_area_list = create_alert_area_list(alert_list)
    fakeInst = faker.Faker("en_US")

    desc = fakeInst.text()
    met_cond = fakeInst.text()
    hydro_cond = fakeInst.text()
    auth = fakeInst.name()

    alert = alerts_models.Alert_Basins_Write(
        alert_description=desc,
        alert_hydro_conditions=hydro_cond,
        alert_meteorological_conditions=met_cond,
        author_name=auth,
        alert_status=alerts_models.AlertStatus.active.value,
        alert_created=datetime.datetime.now(datetime.timezone.utc),
        alert_updated=datetime.datetime.now(datetime.timezone.utc),
        alert_links=alert_area_list,
    )
    LOGGER.debug(f"fake alert: {alert}")
    return alert


def update_fake_alert(
    existing_alert: alerts_models.Alerts, alert_list: AlertDataDict
) -> alerts_models.Alert_Basins_Write:
    """
    used to simulate the condition where an alert has been updated and now the
    caps associated with that alert need to be updated.  Makes the necessary
    changes to the alert object, but doesn't update caps.
    """
    # create the alert area / alert level list to be added to the alert object
    # further down in the function
    alert_area_list = create_alert_area_list(alert_list)

    fakeInst = faker.Faker("en_US")
    auth = fakeInst.name()

    # mostly copy the attributes from the incomming alert, with the exception of
    # author, update time, and alert area / alert levels
    updated_alert = alerts_models.Alert_Basins_Write(
        alert_description=existing_alert.alert_description,
        alert_hydro_conditions=existing_alert.alert_hydro_conditions,
        alert_meteorological_conditions=existing_alert.alert_meteorological_conditions,
        author_name=auth,
        alert_status=existing_alert.alert_status,
        alert_created=existing_alert.alert_created,
        alert_updated=datetime.datetime.now(datetime.timezone.utc),
        alert_links=alert_area_list,
    )
    return updated_alert


def create_update_model(alert_list: AlertDataDict) -> alerts_models.Alert_Basins_Write:
    alert_area_list = create_alert_area_list(alert_list)

    fakeInst = faker.Faker("en_US")

    # generate new basin / alert levels object
    out_data = alerts_models.Alert_Basins_Write(
        alert_description=fakeInst.text(),
        alert_hydro_conditions=fakeInst.text(),
        alert_meteorological_conditions=fakeInst.text(),
        author_name=fakeInst.name(),
        alert_status="active",
        alert_links=alert_area_list,
    )
    return out_data
