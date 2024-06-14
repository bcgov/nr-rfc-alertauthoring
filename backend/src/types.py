import typing

from typing_extensions import TypedDict

AlertAreaLevel = TypedDict("AlertAreaLevel", {"basin": str, "alert_level": int})


AlertDataDict = typing.TypedDict(
    "AlertDataDict", {"alert_level": str, "basin_names": typing.List[str]}
)
