import re
from calendar import monthrange
from datetime import datetime
from enum import IntEnum


def _test_valid_string(seconds, minutes, hours):
    # Check the range or hours, seconds, ...
    if seconds > 59 or seconds < 0:
        raise Exception("An second has to be between 0, ... 59")

    if minutes > 59 or minutes < 0:
        raise Exception("A minute has to be between 0, ... 59")

    if hours > 23 or hours < 0:
        raise Exception("An hour has to be between 0, ... 23")


def parse_expires_at(schedule_str: str, current: datetime = None) -> datetime:
    if not current:
        current = datetime.now()

    split_str = schedule_str.split(":")
    h = split_str[0]
    m = split_str[1]
    s = split_str[2]

    years = current.year
    months = current.month
    days = current.day

    # Check for wildcards and otherwise use the value in the string
    if not re.search("^\\*+$", s):
        seconds = int(s)
    else:
        seconds = current.second

    if not re.search("^\\*+$", m):
        minutes = int(m)
    else:
        minutes = current.minute

    if not re.search("^\\*+$", h):
        hours = int(h)
    else:
        hours = current.hour

    # Check if the template syntax has the right ranges
    _test_valid_string(seconds, minutes, hours)

    # If Minutes is the smallest wildcard
    if re.search("^\\*+$", h) and re.search("^\\*+$", m):
        minutes += 1
    # If Hours is the smallest wildcard
    elif re.search("^\\*+$", h):
        hours += 1
    # If There is no wildcard
    else:
        days += 1

    # Verify that the data is valid and if not handle the overflow
    if minutes == 60:
        hours += 1
        minutes = 0

    if hours == 24:
        days += 1
        hours = 0

    if days == monthrange(current.year, current.month)[1] + 1:
        months += 1
        days = 1

    if months > 12:
        years += 1
        months = 1

    return datetime(years, months, days, hours, minutes, seconds)


def parse_expires_every(expiry_str: str) -> int:
    split_str = expiry_str.split(":")
    h = split_str[0]
    m = split_str[1]
    s = split_str[2]

    seconds = 0
    if not re.search("^\\*+$", h):
        seconds += int(h) * 60 * 60

    if not re.search("^\\*+$", m):
        seconds += int(m) * 60

    if not re.search("^\\*+$", s):
        seconds += int(s)

    return seconds


class ScheduleType(IntEnum):
    EVERY = 0
    AT = 1


def get_schedule_type(expires_every: str = None, expires_at: str = None) -> (ScheduleType, str):
    if expires_every and expires_at:
        raise Exception("To many arguments")

    if expires_every:
        return ScheduleType.EVERY, expires_every
    if expires_at:
        return ScheduleType.AT, expires_at

    raise Exception("")
