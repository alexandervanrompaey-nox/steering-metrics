from typing import Optional
import arrow
from arrow import Arrow


def floor_to_15_minutes(timestamp: Arrow) -> Arrow:
    _timestamp = timestamp.floor("minute")
    extra_minutes = timestamp.minute % 15
    return _timestamp.shift(minutes=-extra_minutes)


def floor_to_5_minutes(timestamp: Arrow) -> Arrow:
    _timestamp = timestamp.floor("minute")
    extra_minutes = timestamp.minute % 5
    return _timestamp.shift(minutes=-extra_minutes)


def parse_arrow(value: Optional[str]) -> Optional[Arrow]:
    if value in (None, ""):
        return None
    try:
        return Arrow.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return arrow.get(value)
