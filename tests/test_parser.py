from calendar import monthrange
from datetime import datetime, timedelta
from random import randrange

import pytest

from pycache._shared._parser import parse_expires_at, parse_expires_every, get_schedule_type


def time_equals(t1: datetime, t2: datetime):
    assert t1.year == t2.year
    assert t1.month == t2.month
    assert t1.day == t2.day
    assert t1.hour == t2.hour
    assert t1.minute == t2.minute


def test_expire_at():
    # Seconds
    current = datetime.now()
    for i in range(5000):
        second = randrange(0, 59)
        time_equals(
            parse_expires_at(f"00:00:{second}"),
            datetime(current.year, current.month, current.day + 1, 0, 0, second)
        )
    for i in range(5000):
        second = randrange(0, 59)
        time_equals(
            parse_expires_at(f"*:00:{second}"),
            datetime(current.year, current.month, current.day, current.hour + 1, 0, second)
        )
    for i in range(5000):
        second = randrange(1, 58)
        current_plus = datetime(current.year, current.month, current.day, current.hour, current.minute, 0)
        time_equals(
            parse_expires_at(f"*:*:{second}", current_plus),
            datetime(current.year, current.month, current.day, current.hour, current.minute, second)
        )

    # Minutes
    for i in range(5000):
        minute = randrange(0, 58)
        time_equals(
            parse_expires_at(f"00:{minute}:00"),
            datetime(current.year, current.month, current.day + 1, 0, minute, 0)
        )

    for i in range(5000):
        minute = randrange(0, 58)
        current_plus = datetime(current.year, current.month, current.day, current.hour, 59, 13)
        time_equals(
            parse_expires_at(f"*:{minute}:13", current_plus),
            datetime(current.year, current.month, current.day, current.hour + 1, minute, 13)
        )

    # Hour
    for i in range(5000):
        hour = randrange(0, 22)
        current_plus = datetime(current.year, current.month, current.day, 23, 55, 13)
        time_equals(
            parse_expires_at(f"{hour}:55:13", current_plus),
            datetime(current.year, current.month, current.day + 1, hour, 55, 13)
        )


def test_expires_every():
    for i in range(2000):
        hour = randrange(0, 23)
        minute = randrange(0, 59)
        second = randrange(0, 59)

        assert parse_expires_every(f"{hour}:{minute}:{second}") \
               == timedelta(hours=hour, minutes=minute, seconds=second).total_seconds()


def test_no_params():
    with pytest.raises(Exception):
        get_schedule_type()


def test_invalid_strings():
    with pytest.raises(Exception):
        parse_expires_at("00:00:60")
    with pytest.raises(Exception):
        parse_expires_at("00:60:00")
    with pytest.raises(Exception):
        parse_expires_at("24:00:00")


def test_edge_cases():
    current = datetime.now()
    overflow_minute = datetime(current.year, current.month, current.day, current.hour, 59, 59)
    time_equals(
        parse_expires_at("*:*:59", overflow_minute),
        datetime(current.year, current.month, current.day, current.hour + 1, 0, current.second)
    )

    current = datetime.now()
    overflow_hour = datetime(current.year, current.month, current.day, 23, 59, 59)
    time_equals(
        parse_expires_at("*:59:59", overflow_hour),
        datetime(current.year, current.month, current.day + 1, 0, 59, 59)
    )

    current = datetime.now()
    overflow_day = datetime(current.year, current.month, monthrange(current.year, current.month)[1], 23,
                            59, 59)
    time_equals(
        parse_expires_at("23:59:59", overflow_day),
        datetime(current.year, current.month + 1, 1, 23, 59, 59)
    )

    current = datetime.now()
    overflow_month = datetime(current.year, 12, monthrange(current.year, current.month)[1], 23, 59, 59)
    time_equals(
        parse_expires_at("23:59:59", overflow_month),
        datetime(current.year + 1, 1, 1, 23, 59, 59)
    )
