import asyncio
import functools
from typing import Callable

from pycache._memmory_db import DataCache, FunctionCache


def cache(expires_every: str = None, schedule: str = None, max_cache_size=50) -> Callable:
    """
    Cache the results of a method or function with the arguments of the function
    :param expires_every: A string which specifies every how many hours/minutes/seconds the cache expires
                          Format: hh:mm:ss | h:mm:s | ...
                          Use * if you dont want to specify.
    :param schedule: A string which describes a schedule
                     Format: hh:mm:ss
                     For example a string like this `**:30:00` will cause the cache to expire every hour at 30 past.
                     For example a string like this `18:30:00` will cause the cache to expire every day at 18:30:00
    :param max_cache_size: The maximal amount of cache results per method which should be cached
    """
    data_cache = DataCache()

    if max_cache_size < 1:
        raise Exception("Max cache size cannot be smaller than 1")

    def function_wrapper(func: Callable):
        func_cache = FunctionCache(max_cache_size)
        data_cache.add_function_cache(func, func_cache)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = DataCache.hash_args(args, kwargs)
            if data_cache.is_in_cache(key, func):
                value = data_cache.get_value_from_cache(key, func)
            else:
                value = func(*args, **kwargs)
                func_cache.add_cache_entry(key, value, expires_every, schedule)
            return value

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            key = DataCache.hash_args(args, kwargs)
            if data_cache.is_in_cache(key, func):
                value = data_cache.get_value_from_cache(key, func)
            else:
                value = await func(*args, **kwargs)
                func_cache.add_cache_entry(key, value, expires_every, schedule)
            return value

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return function_wrapper
