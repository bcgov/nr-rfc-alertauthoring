import logging
from typing import Dict, List, TypedDict

import pytest
from sqlmodel import Session, select
from src.v1.crud import crud_cap
from src.v1.models import alerts as alerts_models
from src.v1.models import basins as basins_models
from src.v1.models import cap as caps_models

LOGGER = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "cap_comp_1_dict,cap_comp_2_dict,expected_result",
    [
        [{"Level1": ["basin1"]}, {"Level1": ["basin1", "basin2"]}, False],
        [
            {"Level1": ["basin2", "basin3", "basin4"]},
            {"Level1": ["basin3", "basin2", "basin4"]},
            True,
        ],
        [
            {"Level1": ["basin3", "basin4"]},
            {"Level1": ["basin3", "basin2", "basin4"]},
            False,
        ],
        [
            {"Level1": ["basin2", "basin3", "basin4"]},
            {"Level2": ["basin3", "basin2", "basin4"]},
            False,
        ],
        [{"Level1": ["basin4"]}, {"Level1": ["basin4"]}, True],
        [{"Level1": []}, {"Level1": ["basin4"]}, False],
    ],
)
def test_is_cap_comp_equal(cap_comp_1_dict, cap_comp_2_dict, expected_result):
    """
    tests two cap comparison objects to see if they are equal

    :param cap_comp_1: _description_
    :type cap_comp_1: _type_
    :param cap_comp_2: _description_
    :type cap_comp_2: _type_
    :return: _description_
    :rtype: _type_
    """
    cap_comp_1 = cap_comp_from_dict(cap_comp_1_dict)
    cap_comp_2 = cap_comp_from_dict(cap_comp_2_dict)
    delta_obj = crud_cap.CapDelta(
        existing_cap_struct=cap_comp_1,
        new_cap_struct=cap_comp_2,
        incomming_alert_status=alerts_models.AlertStatus.active,
    )
    actual_result = delta_obj.is_cap_comp_equal(cap_comp_1, cap_comp_2)
    assert actual_result == expected_result


@pytest.mark.parametrize(
    "existing_cap_dict,new_caps_dict,cancel_list",
    [
        [{"Level1": ["basin1"]}, {"Level1": ["basin1", "basin2"]}, []],
        [{"Level1": ["basin1"]}, {"Level1": ["basin1"], "Level2": ["basin2"]}, []],
        [{"Level1": ["basin1"]}, {"Level2": ["basin2"]}, [{"Level1": ["basin1"]}]],
        [
            {"Level2": ["basin2"], "Level3": ["basin3"]},
            {"Level1": ["basin1"]},
            [{"Level2": ["basin2"]}, {"Level3": ["basin3"]}],
        ],
        [
            {"Level2": ["basin2", "basin4", "basin3"], "Level3": ["basin7", "basin9"]},
            {"Level1": ["basin1"]},
            [
                {"Level2": ["basin2", "basin4", "basin3"]},
                {"Level3": ["basin7", "basin9"]},
            ],
        ],
        [
            {"Level2": ["basin2", "basin4", "basin3"], "Level3": ["basin7", "basin9"]},
            {},
            [
                {"Level2": ["basin2", "basin4", "basin3"]},
                {"Level3": ["basin7", "basin9"]},
            ],
        ],
        [
            {"Level2": ["basin2", "basin4"]},
            {"Level2": ["basin2", "basin4", "basin3"]},
            {},
        ],
        [
            {"Level1": ["basin2", "basin4"]},
            {"Level2": ["basin2", "basin4", "basin3"]},
            [{"Level1": ["basin2", "basin4"]}],
        ],
    ],
)
def test_cap_delta_cancels(existing_cap_dict, new_caps_dict, cancel_list):
    """
    Tests the cancel method of the cap delta object.  This method is used to
    determine if a cap event should be cancelled.  This is determined by
    comparing the existing cap alert levels to the new cap alert levels.  If
    the new cap alert levels are empty then the cap event should be cancelled.

    :return: None
    :rtype: None
    """
    existing_cap_comp = cap_comp_from_dict(existing_cap_dict)
    new_cap_comp = cap_comp_from_dict(new_caps_dict)

    expected_cap_comp = []
    for cancel_dict in cancel_list:
        expected_cap_comp.extend(cap_comp_from_dict(cancel_dict))

    delta_obj = crud_cap.CapDelta(
        existing_cap_struct=existing_cap_comp,
        new_cap_struct=new_cap_comp,
        incomming_alert_status=alerts_models.AlertStatus.active,
    )

    actual_cancels = delta_obj.getCancels()
    LOGGER.debug(f"actual_cancels: {actual_cancels}")
    LOGGER.debug(f"expected cancels: {expected_cap_comp}")
    equal = delta_obj.is_cap_comp_equal(expected_cap_comp, actual_cancels)
    LOGGER.debug(f"are objects equal: {equal}")
    assert equal


@pytest.mark.parametrize(
    "existing_cap_dict,new_caps_dict,update_list",
    [
        [
            {"Level1": ["basin1"]},
            {"Level1": ["basin1", "basin2"]},
            [{"Level1": ["basin1", "basin2"]}],
        ],
        [{"Level1": ["basin1"]}, {"Level1": ["basin1"]}, []],
        [
            {"Level1": ["basin1", "basin2"]},
            {"Level1": ["basin1"]},
            [{"Level1": ["basin1"]}],
        ],
        [{}, {"Level1": ["basin1"]}, []],
        [
            {"Level1": ["basin1", "basin2", "basin55"], "Level2": {"basin3", "basin4"}},
            {"Level1": ["basin1", "basin2"], "Level2": {"basin3", "basin4", "basin5"}},
            [
                {"Level1": ["basin1", "basin2"]},
                {"Level2": {"basin3", "basin4", "basin5"}},
            ],
        ],
    ],
)
def test_cap_delta_updates(existing_cap_dict, new_caps_dict, update_list):
    """
    Updates are defined by a change to the area affected in an existing alert level.

    Example the area expands or contracts for an existing cap alert level.

    Scenarios to test:
    - basin added
    - basin removed
    - new alert level and basin - this is a create, and should not emit an update
    - alert level removed and all basins - this is a delete, and should not emit an update

    :param existing_cap_dict: input cap comparison dictionary representing an existing
        state of cap alert levels in the database.

    :type existing_cap_dict: dict
    :param new_caps_dict: same as existing_cap_dict, except this represents the new state
        as a result of edits to the related alert
    :type new_caps_dict: dict
    :param create_list: a list of dictionaries describing the updates that should be
        issued.
    :type create_list: list
    """
    existing_cap_comp = cap_comp_from_dict(existing_cap_dict)
    new_cap_comp = cap_comp_from_dict(new_caps_dict)

    delta_obj = crud_cap.CapDelta(
        existing_cap_struct=existing_cap_comp,
        new_cap_struct=new_cap_comp,
        incomming_alert_status=alerts_models.AlertStatus.active,
    )
    actual_updates = delta_obj.getUpdates()
    LOGGER.debug(f"actual_updates: {actual_updates}")

    actual_updates_list = cap_comp_to_dict(actual_updates)
    LOGGER.debug(f"actual_updates_list: {actual_updates_list}")
    LOGGER.debug(f"expected updates: {update_list}")

    expected_cap_comp = []
    for update_dict in update_list:
        expected_cap_comp.extend(cap_comp_from_dict(update_dict))
    LOGGER.debug(f"expected_cap_comp: {expected_cap_comp}")

    # LOGGER.debug("creates: " + str(creates))
    # expected_updates_list = cap_comp_to_dict(update_list)
    # LOGGER.debug(f"updates: {expected_updates_list}")

    equal = delta_obj.is_cap_comp_equal(expected_cap_comp, actual_updates)
    LOGGER.debug(f"are objects equal: {equal}")
    assert equal


@pytest.mark.parametrize(
    "existing_cap_dict,new_caps_dict,create_list",
    [
        [{"Level1": ["basin1"]}, {"Level1": ["basin1", "basin2"]}, []],
        [
            {"Level1": ["basin1"]},
            {"Level1": ["basin1"], "Level2": ["basin2"]},
            [{"Level2": ["basin2"]}],
        ],
        [{"Level1": ["basin1"]}, {"Level2": ["basin2"]}, [{"Level2": ["basin2"]}]],
        [
            {"Level1": ["basin1"]},
            {"Level2": ["basin2"], "Level3": ["basin3"]},
            [{"Level2": ["basin2"]}, {"Level3": ["basin3"]}],
        ],
        [
            {"Level1": ["basin1"]},
            {"Level2": ["basin2", "basin4", "basin3"], "Level3": ["basin7", "basin9"]},
            [
                {"Level2": ["basin2", "basin4", "basin3"]},
                {"Level3": ["basin7", "basin9"]},
            ],
        ],
        [
            {},
            {"Level2": ["basin2", "basin4", "basin3"], "Level3": ["basin7", "basin9"]},
            [
                {"Level2": ["basin2", "basin4", "basin3"]},
                {"Level3": ["basin7", "basin9"]},
            ],
        ],
        [
            {"Level2": ["basin2", "basin4", "basin3"]},
            {"Level2": ["basin2", "basin4"]},
            {},
        ],
    ],
)
def test_cap_delta_adds(existing_cap_dict, new_caps_dict, create_list):
    """
    existing_cap_dict
        key: alert level, example 'Level1'
        value: list of basins, example ['basin1', 'basin2']

    new_caps_dict
        same struct as the existing_cap_dict

    create_list
        list of dictionaries that describes the differences between the existing_cap_dict
        and the new_caps_dict.

    * note the levels are not enforced, that will take place higher up in the code
      at the database (crud) level.  the cap_delta is only responsible for identifying
      how caps have changed and what actions need to take place as a result of those
      changes.

    [level, [basin list]]

    fixture provides detail about the

    # things to test
    - basin added
    - basin removed
    - new alert level
    - new alert level and basin
    - alert level removed and all basins
    """
    LOGGER.debug(f"existing_cap_dict: {existing_cap_dict}")

    existing_cap_comp = cap_comp_from_dict(existing_cap_dict)
    new_cap_comp = cap_comp_from_dict(new_caps_dict)

    expected_cap_comp = []
    for create_dict in create_list:
        expected_cap_comp.extend(cap_comp_from_dict(create_dict))
    # expected_cap_comp = cap_comp_from_dict(create_list)

    delta_obj = crud_cap.CapDelta(
        existing_cap_struct=existing_cap_comp,
        new_cap_struct=new_cap_comp,
        incomming_alert_status=alerts_models.AlertStatus.active,
    )
    actual_creates = delta_obj.getCreates()
    LOGGER.debug(f"expected_creates: {actual_creates}")
    # LOGGER.debug("creates: " + str(creates))
    # actual_creates_list = cap_comp_to_dict(creates)
    # LOGGER.debug(f"creates: {creates}")
    # LOGGER.debug(f"actual_creates_list: {actual_creates_list}")
    equal = delta_obj.is_cap_comp_equal(expected_cap_comp, actual_creates)
    LOGGER.debug(f"are objects equal: {equal}")
    assert equal


def cap_comp_from_dict(cap_comp_dict) -> List[caps_models.Cap_Comparison]:
    """
    create a cap comparison object from a dictionary

    :param cap_comp_dict: dictionary containing the alert level and basin data
    :type cap_comp_dict: dict
    :return: cap comparison object
    :rtype: cap_models.Cap_Comparison
    """
    cap_comps = []
    for alert_level in cap_comp_dict.keys():
        alert_lvl_model = alerts_models.Alert_Levels_Base(alert_level=alert_level)
        basins = []
        for basin in cap_comp_dict[alert_level]:
            basin_model = basins_models.BasinBase(basin_name=basin)
            basins.append(basin_model)
        cap_comp = caps_models.Cap_Comparison(
            alert_level=alert_lvl_model, basins=basins
        )
        cap_comps.append(cap_comp)
    return cap_comps


def cap_comp_to_dict(
    cap_comp: List[caps_models.Cap_Comparison],
) -> List[Dict[str, List[str]]]:
    """
    create a cap comparison object from a dictionary

    :param cap_comp: dictionary containing the alert level and basin data
    :type cap_comp: dict
    :return: cap comparison object
    :rtype: cap_models.Cap_Comparison
    """
    LOGGER.debug(f"input cap comp: {cap_comp}")
    cap_comps = []
    for cap in cap_comp:
        alert_level = cap.alert_level.alert_level
        LOGGER.debug(f"comp, alert_level: {alert_level}")
        basins = []
        for basin in cap.basins:
            basins.append(basin.basin_name)
        basins.sort()
        cap_comps.append({alert_level: basins})
    # cap_comps.sort()
    return cap_comps
