import logging

import pytest
import src.v1.models.alerts as alerts_models
import src.v1.models.basins as basins_models
import src.v1.models.cap as cap_models

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def single_level_cap_comp(alert_level_data, basin_data):
    """
    returns a cap comparison object with a single alert level and a single basin

    :param alert_level_data: _description_
    :type alert_level_data: _type_
    :param basin_data: _description_
    :type basin_data: _type_
    :yield: _description_
    :rtype: _type_
    """
    LOGGER.debug(f"basin_data: {basin_data}")

    alert_level = alerts_models.Alert_Levels_Base(alert_level=alert_level_data[0]["alert_level"])
    basin = basins_models.BasinBase(basin_name=basin_data[0]["basin_name"])
    cap_comp = cap_models.Cap_Comparison(alert_level=alert_level, basins=[basin])
    yield cap_comp


@pytest.fixture(scope="function")
def all_alert_level_caps_comp(alert_level_data, basin_data):
    """
    returns a list of cap comparison objects for each possible defined alert level
    each cap comparion object will have 5 different basins associated with it.

    :param alert_level_data: _description_
    :type alert_level_data: _type_
    :param basin_data: _description_
    :type basin_data: _type_
    :yield: _description_
    :rtype: _type_
    """
    LOGGER.debug(f"basin_data: {basin_data}")

    chunk_size = 5
    basin_chunks_list = []
    basin_list = []
    # organized basin data into chunks defined by chunk_size, then apply different
    # chunks later on to different alert levels.
    basin_cnt = 0
    for basin in basin_data:
        basin_model = basins_models.BasinBase(basin_name=basin['basin_name'])
        basin_list.append(basin_model)
        if len(basin_list) >= chunk_size:
            basin_chunks_list.append(basin_list)
            basin_list = []

    all_caps = []
    for alert_level in alert_level_data:
        alert_level_str = alert_level["alert_level"]
        alert_level = alerts_models.Alert_Levels_Base(alert_level=alert_level_str)
        basins = basin_chunks_list.pop()
        cap_comp = cap_models.Cap_Comparison(alert_level=alert_level, basins=basins)
        all_caps.append(cap_comp)
    yield all_caps



