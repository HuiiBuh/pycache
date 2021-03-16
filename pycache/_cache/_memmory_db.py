from typing import Optional, Any, Dict, Callable, Hashable

from pycache._cache._timer import Timer
from pycache._shared._parser import ScheduleType
from pycache._shared._singleton import Singleton


class CacheEntry:
    def __init__(self):
        self._value: Optional[Any] = None
        self._timer = Timer()
        self._was_set = False

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value):
        self._was_set = True
        self._value = value
        self._timer.reset()

    def is_valid(self) -> bool:
        return self._was_set and not self._timer.has_expired()

    def set_expiry(self, schedule_type: ScheduleType, schedule_str: str) -> None:
        self._timer.set_schedule(schedule_type, schedule_str)


class FunctionCache:
    def __init__(self, max_cache_entries: int):
        self.max_cache_entries = max_cache_entries
        self.cache: Dict[int, CacheEntry] = {}

    def is_in_cache(self, key: int) -> bool:
        return key in self.cache and self.cache[key].is_valid()

    def get_value_from_cache(self, key: int) -> Any:
        if self.is_in_cache(key):
            return self.cache[key].value
        raise Exception("Value could not be found")

    def add_cache_entry(self, key: int, value: Any, schedule_type: ScheduleType, schedule_str: str) -> None:
        if key not in self.cache:

            # Check if to many cache entries
            key_list = list(self.cache.keys())
            if len(key_list) >= self.max_cache_entries:
                del self.cache[key_list[0]]

            self.cache[key] = CacheEntry()
            self.cache[key].set_expiry(schedule_type, schedule_str)
        self.cache[key].value = value


class DataCache(metaclass=Singleton):

    def __init__(self):
        self.cache: Dict[Callable, FunctionCache] = {}

    @staticmethod
    def hash_args(args: tuple, kwargs: Dict[str, Any]) -> int:
        hash_key = ()
        for value in args:
            if isinstance(value, Hashable):
                hash_key += (value,)
            else:
                hash_key += (id(value),)

        for key in (sorted(kwargs.keys())):
            value = kwargs[key]

            if isinstance(value, Hashable):
                hash_key += (key, value,)
            else:
                hash_key += (key, id(value),)

        return hash(hash_key)

    def is_in_cache(self, key: int, func: Callable) -> bool:
        return func in self.cache and \
               self.cache[func].is_in_cache(key)

    def get_value_from_cache(self, key: int, func: Callable) -> Any:
        if self.is_in_cache(key, func):
            return self.cache[func].get_value_from_cache(key)
        raise Exception("Value could not be found")

    def add_function_cache(self, func: Callable, function_cache: FunctionCache) -> None:
        if func not in self.cache:
            self.cache[func] = function_cache
        else:
            raise Exception("Function is already in cache")
