import datetime
import json
import logging
import os
import random
import typing

import faker
from src.types import AlertAreaLevel, AlertDataDict
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
    alert_list: typing.List[AlertDataDict],
) -> typing.List[alerts_models.Alert_Areas_Write]:
    LOGGER.debug(f"alert_dict: {alert_list}")
    alert_area_list = []
    for alert_dict in alert_list:
        # it is possible to remove all areas associated with an alert
        # which will ultimately cancel the alert
        if alert_dict["basin_names"]:
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


def create_fake_alert(
    alert_list: typing.List[AlertDataDict],
) -> alerts_models.Alert_Basins_Write:
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


def AlertAreaLevel_to_AlertDataDict(
    input_alert_area_levels: typing.List[AlertAreaLevel],
) -> typing.List[AlertDataDict]:
    """
    in order to accomodate older tests that used the AlertAreaLevel data model to
    define the alert areas, and alert levels for test conditions, this function
    will convert from the AlertAreaLevel data model to the Alert_Areas_Write data
    to allow other methods in this library to be used to parameterize testing.

    :param input_alert_area_levels: a list of AlertAreaLevel data models to be converted
        to Alert_Areas_Write models
    :type input_alert_area_levels: typing.List[AlertAreaLevel]
    :return: _description_
    :rtype: typing.List[alerts_models.Alert_Areas_Write]
    """
    tmp_dict = {}
    for alert_area_level in input_alert_area_levels:
        if alert_area_level["alert_level"] not in tmp_dict:
            tmp_dict[alert_area_level["alert_level"]] = {
                "alert_level": alert_area_level["alert_level"],
                "basin_names": [alert_area_level["basin"]],
            }
        else:
            tmp_dict[alert_area_level["alert_level"]]["basin_names"].append(
                alert_area_level["basin"]
            )
    return list(tmp_dict.values())


def update_random_alert_data_dict(
    alert_list: typing.List[AlertDataDict], update=False
) -> typing.List[AlertDataDict]:
    """
    randomly updates the alert_list

    :param alert_list: _description_
    :type alert_list: _type_
    """
    all_basins = get_basin_data(just_basins=True)
    alert_lvls = get_alert_level_data(just_alerts=True)

    alert_data_list = []
    num_alerts = random.randint(1, len(alert_lvls))

    used_alert_lvls = []
    used_basins = []

    for alert_index in range(num_alerts):
        if alert_index < len(alert_list):
            # the alert exists
            alert_lvl = alert_list[alert_index]["alert_level"]
            used_alert_lvls.append(alert_lvl)
            num_basins = random.randint(1, 5)

            if num_basins > len(alert_list[alert_index]["basin_names"]):
                # we need to add __ number of basins
                avail_basins_set = (
                    set(all_basins)
                    - set(alert_list[alert_index]["basin_names"])
                    - set(used_basins)
                )

                avail_basins = list(avail_basins_set)

                new_basins = random.choices(
                    avail_basins,
                    k=num_basins - len(alert_list[alert_index]["basin_names"]),
                )
                basins = alert_list[alert_index]["basin_names"][0:]
                basins = basins.extend(new_basins)
                used_basins.extend(new_basins)

            elif num_basins < len(alert_list[alert_index]["basin_names"]):
                # need to randomly remove basins
                basins = random.choices(
                    alert_list[alert_index]["basin_names"], k=num_basins
                )
            elif num_basins == len(alert_list[alert_index]["basin_names"]):
                basins = alert_list[alert_index]["basin_names"]
            if basins is None:
                basins = []
            alert_dict = {"alert_level": alert_lvl, "basin_names": basins}
            alert_data_list.append(alert_dict)
        else:
            # the alert level does not exist
            avail_alerts = list(set(alert_lvls) - set(used_alert_lvls))
            alert_lvl = random.choice(avail_alerts)
            used_alert_lvls.append(alert_lvl)
            num_basins = random.randint(1, 5)
            basins = random.choices(all_basins, k=num_basins)
            if basins is None:
                basins = []
            alert_dict = {"alert_level": alert_lvl, "basin_names": basins}
            alert_data_list.append(alert_dict)

    # if update is true then at least one of the existing alert levels must
    # be part of the updated alert list
    if update:
        # check to see if the alert level is included in the alert_data_list
        updated_alert_lvls = [alert["alert_level"] for alert in alert_data_list]
        original_alert_lvls = [
            alert["alert_level"]
            for alert in alert_list
            if alert["alert_level"] in updated_alert_lvls
        ]
        if not original_alert_lvls:
            # take the first alert level and make it the same as the first alert
            # level in original_alert_lvls
            alert_data_list[0]["alert_level"] = alert_list[0]["alert_level"]

    # There MUST be a difference so if none is detected then run again
    if alert_data_list == alert_list:
        alert_data_list = update_random_alert_data_dict(alert_list, update=update)

    return alert_data_list


def get_random_alert_data_dict() -> typing.List[AlertDataDict]:

    basins = get_basin_data(just_basins=True)
    alert_lvls = get_alert_level_data(just_alerts=True)
    LOGGER.debug(f"alert_lvls: {alert_lvls}")

    alert_data_list = []
    # determines how many alert_level / basin dicts to generate
    num_alerts = random.randint(1, len(alert_lvls))

    for _ in range(num_alerts):
        alert_lvl = random.choice(alert_lvls)
        num_basins = random.randint(1, 5)
        basins = random.choices(basins, k=num_basins)
        alert_dict = {"alert_level": alert_lvl, "basin_names": basins}
        alert_data_list.append(alert_dict)
    return alert_data_list


def update_fake_alert(
    existing_alert: alerts_models.Alerts, alert_list: typing.List[AlertDataDict]
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
        # alert_created=existing_alert.alert_created,
        # alert_updated=datetime.datetime.now(datetime.timezone.utc),
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


def get_basin_data(just_basins: bool = False):
    basin_data_file_path = os.path.realpath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "alembic",
            "data",
            "basins.json",
        )
    )
    LOGGER.debug(f"basin data path: {basin_data_file_path}")
    with open(basin_data_file_path, "r") as basin_data_file:
        basin_data = json.load(basin_data_file)
    LOGGER.debug(f"number of basins: {len(basin_data)}")
    if just_basins:
        basin_list = [basin_record["basin_name"] for basin_record in basin_data]

        LOGGER.debug(f"basin_list length: {len(basin_list)}")
        return basin_list
    return basin_data


def get_alert_level_data(just_alerts: bool = False):
    alert_lvl_file_path = os.path.realpath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "alembic",
            "data",
            "alert_levels.json",
        )
    )
    LOGGER.debug(f"alert_lvl_file_path: {alert_lvl_file_path}")

    with open(alert_lvl_file_path, "r") as alert_lvl_file:
        alert_lvl_data = json.load(alert_lvl_file)

    if just_alerts:
        alert_list = [alert_record["alert_level"] for alert_record in alert_lvl_data]
        return alert_list
    return alert_lvl_data
