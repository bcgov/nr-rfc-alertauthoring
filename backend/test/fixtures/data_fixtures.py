import json
import logging
import os
from typing import Generator

import pytest
from src.v1.models import alerts as alerts_model  # noqa: F403

LOGGER = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def alert_level_data() -> Generator[alerts_model.Alert_Levels_Read, None, None]:  # noqa: F405
    """
    reads the alert levels json file and loads to a List[Dict] structure.

    :yield: List
    :rtype: Generator[Alert_Levels_Read, None, None]
    """

    alert_level_data_file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "alembic",
        "data",
        "alert_levels.json",
    )

    with open(alert_level_data_file, "r") as json_file:
        alert_level_data = json.load(json_file)
    yield alert_level_data

@pytest.fixture(scope="session")
def basin_data():
    basin_file = os.path.join(
        os.path.dirname(__file__), "..", "..", "alembic", "data", "basins.json"
    )
    LOGGER.debug(f"src file for basin data: {basin_file}")
    with open(basin_file, "r") as json_file:
        basins_data = json.load(json_file)
    yield basins_data

    
