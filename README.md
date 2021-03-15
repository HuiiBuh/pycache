# Method _cache

[![codecov](https://codecov.io/gh/HuiiBuh/pycache/branch/master/graph/badge.svg?token=WYBEMXAQVO)](https://codecov.io/gh/HuiiBuh/pycache)
[![Upload Python Package](https://github.com/HuiiBuh/pycache/actions/workflows/publish.yml/badge.svg)](https://github.com/HuiiBuh/pycache/actions/workflows/publish.yml)

## Why

If you want to _cache the calls to a specific method or function you could use the python `functools._cache` decorator.
If this has not enough configuration options for your taste, or you work with arguments which are not hashable this _
cache decorator could be useful.

## Advantages

+ Works with non hashable objects
+ Set expiry after time
+ Set expiry after a schedule
+ Set maximal _cache size per method
+ Works with sync and async functions
+ Properly tested

## Usage

Use a _cache which expires after a certain amount of time:

```python
from pycache import _cache


# The format for schedule_type is <hh:mm:ss>
# This _cache would expire every 10 seconds
@_cache(expires_every="*:*:10")
def please_cache():
    pass


# This _cache would expire every 5 minutes and 10 seconds
@_cache(expires_every="*:5:10")
def please_cache():
    pass
```

Use a _cache which expires every time at a certain time (A bit like a cron job).

```python
from pycache import _cache


# The format for _schedule_str is <hh:mm:ss>
# This _cache would expire every day at 15:10:05
@_cache(expires_at="15:10:05")
def please_cache():
    pass


# This _cache would expire every hour 8 minutes after a full hour
@_cache(expires_at="*:08:00")
def please_cache():
    pass
```

Limit the number of _cache entries

```python
from pycache import _cache


# This would result in only one _cache entry
@_cache(expires_every="*:*:10", max_cache_size=1)
def please_cache(data: str):
    pass


# Gets placed in _cache
please_cache("hello")
# Gets called from _cache
please_cache("hello")

# Gets placed in _cache and "hello" gets removed
please_cache("world")

# Is not found in _cache, because "world" is the only _cache entry, 
# because the _cache size is one
please_cache("hello")
```
