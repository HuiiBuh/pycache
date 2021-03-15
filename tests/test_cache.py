import asyncio
from datetime import datetime, timedelta

import pytest
import toml
from time import sleep

from _cache._memmory_db import DataCache, FunctionCache
from _shared._singleton import Singleton
from pycache import __version__, cache
from pycache._cache._memmory_db import DataCache as CDataCache


class ThirdSingleton(metaclass=Singleton):
    pass


def test_singleton():
    c1 = CDataCache()
    c1.cache["hello"] = "world"
    c2 = DataCache()

    assert c2.cache["hello"] == "world"
    assert c1 is c2

    c3 = ThirdSingleton()
    c4 = ThirdSingleton()
    assert c3 is c4
    assert c2 is not c3 and c1 is not c3


def test_version():
    try:
        parsed_toml = toml.load("../pyproject.toml")
    except FileNotFoundError:
        parsed_toml = toml.load("pyproject.toml")

    version = parsed_toml \
        .get("tool") \
        .get("poetry") \
        .get("version")
    assert __version__ == version


def test_simple_cache():
    @cache("*:*:1")
    def cached_method(c):
        c["value"] += 1
        return "hello"

    counter = {"value": 0}
    for _ in range(100):
        return_value = cached_method(counter)
        assert return_value is "hello"

    assert counter["value"] is 1


def test_cache_and_expire():
    @cache("*:*:1")
    def cache_method(c):
        c["value"] += 1

    counter = {"value": 0}

    cache_method(counter)
    sleep(1)
    cache_method(counter)

    assert counter["value"] is 2


def test_expiry_date():
    def internal(cache_str: str, seconds: int):
        data_cache = DataCache()

        def cache_method():
            pass

        wrapped_cache_method = cache(cache_str)(cache_method)

        wrapped_cache_method()

        key = DataCache.hash_args(tuple(), dict())
        expiry_date = data_cache.cache[cache_method].cache[key]._timer._expiry_date
        calc_exp_date = datetime.now() + timedelta(0, seconds)

        assert expiry_date.year == calc_exp_date.year
        assert expiry_date.month == calc_exp_date.month
        assert expiry_date.day == calc_exp_date.day
        assert expiry_date.hour == calc_exp_date.hour
        assert expiry_date.minute == calc_exp_date.minute
        try:
            assert expiry_date.second == calc_exp_date.second
        except AssertionError:
            assert expiry_date.second == calc_exp_date.second - 1

    internal("1:0:0", 60 * 60)
    internal("*:45:0", 45 * 60)
    internal("1:45:10", 60 * 60 + 45 * 60 + 10)
    internal("*:*:*", 0)


def test_schedule_time():
    def internal(cache_str: str, expected_date: datetime):
        data_cache = DataCache()

        def cache_method():
            pass

        wrapped_cache_method = cache(expires_at=cache_str)(cache_method)

        wrapped_cache_method()

        key = DataCache.hash_args(tuple(), dict())
        expiry_date = data_cache.cache[cache_method].cache[key]._timer._expiry_date

        assert expiry_date.year == expected_date.year
        assert expiry_date.month == expected_date.month
        assert expiry_date.day == expected_date.day
        assert expiry_date.hour == expected_date.hour
        assert expiry_date.minute == expected_date.minute
        try:
            assert expiry_date.second == expected_date.second
        except AssertionError:
            assert expiry_date.second == expected_date.second - 1

    current = datetime.now()
    internal("17:00:15", datetime(current.year, current.month, current.day + 1, 17, 0, 15))
    internal("*:10:00", datetime(current.year, current.month, current.day, current.hour + 1, 10, 00))
    internal("*:*:12", datetime(current.year, current.month, current.day, current.hour, current.minute + 1, 12))


def test_invalid_cache_size():
    with pytest.raises(Exception):
        @cache(expires_every="*:*:1", max_cache_size=-1)
        def cache_method():
            pass


def test_async():
    @cache(expires_every="*:*:1")
    async def cache_method(c):
        c["value"] += 1

    counter = {"value": 0}

    loop = asyncio.get_event_loop()
    loop.run_until_complete(cache_method(counter))
    loop.run_until_complete(cache_method(counter))

    assert counter["value"] == 1


def test_to_many_args():
    with pytest.raises(Exception):
        @cache(expires_every="*:*:1", expires_at="*:*:1")
        def cache_method(_):
            pass


def test_get_invalid_value():
    function = FunctionCache(10)
    data = DataCache()

    with pytest.raises(Exception):
        function.get_value_from_cache(123)
    with pytest.raises(Exception):
        data.get_value_from_cache(234, lambda e: e)


def test_add_same_funciton():
    def empty():
        pass

    f_cache = FunctionCache(10)

    data = DataCache()
    data.add_function_cache(empty, f_cache)

    with pytest.raises(Exception):
        data.add_function_cache(empty, f_cache)


def test_hash_kwargs():
    @cache("*:*:1")
    def method(integer: int, hello="test", c=None):
        c["value"] += 1

    counter = {"value": 0}

    method(1, hello="world", c=counter)
    method(1, hello="world", c=counter)

    assert counter["value"] is 1


def test_large_cache_size():
    @cache("*:*:1", max_cache_size=1)
    def method(c):
        c["value"] += 1

    counter1 = {"value": 0}
    counter2 = {"value": 0}

    method(counter1)
    method(counter2)
    method(counter1)

    assert counter1["value"] is 2


def test_schedule_and_expire():
    def internal(schedule: str, expected: int, s=0):
        @cache(expires_at=schedule)
        def cache_method(c):
            c["value"] += 1

        counter = {"value": 0}

        cache_method(counter)
        cache_method(counter)
        sleep(s)
        cache_method(counter)
        cache_method(counter)

        assert counter["value"] is expected

    now = datetime.now()
    internal(f"{now.hour}:{now.minute}:{now.second + 1}", 1)
    now = datetime.now()
    internal(f"*:*:{now.second}", 2, 61)
    now = datetime.now()
    internal(f"*:1:{now.second}", 1, 0)
    internal(f"*:1:*", 1, 0)
