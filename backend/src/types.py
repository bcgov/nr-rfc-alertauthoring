import typing

from typing_extensions import TypedDict

# The data model used for RFC alerts
AlertAreaLevel = TypedDict("AlertAreaLevel", {"basin": str, "alert_level": int})

# the data model used to describe data used to create caps
AlertDataDict = typing.TypedDict(
    "AlertDataDict", {"alert_level": str, "basin_names": typing.List[str]}
)
