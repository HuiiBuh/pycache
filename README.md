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

### Cache

Use a cache which expires after a certain amount of time:

```python
from pycache import cache


# The format for schedule_type is <hh:mm:ss>
# This _cache would expire every 10 seconds
@cache(expires_at="*:*:10")
def please_cache():
    pass


# This _cache would expire every 5 minutes and 10 seconds
@cache(expires_every="*:5:10")
def please_cache():
    pass
```

Use a _cache which expires every time at a certain time (A bit like a cron job).

```python
from pycache import cache


# The format for _schedule_str is <hh:mm:ss>
# This _cache would expire every day at 15:10:05
@cache(expires_at="15:10:05")
def please_cache():
    pass


# This _cache would expire every hour 8 minutes after a full hour
@cache(expires_at="*:08:00")
def please_cache():
    pass
```

Limit the number of _cache entries

```python
from pycache import cache


# This would result in only one _cache entry
@cache(expires_every="*:*:10", max_cache_size=1)
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

### Schedule

```python3
from pycache import schedule, add_schedule, ScheduleSubscription


# Gets called every 10 seconds
@schedule(call_every="*:*:10")
def schedule_me():
    pass


# Gets called every at 10 am
@schedule(call_every="10:00:00")
def schedule_me():
    pass


# Gets called 3 times
@schedule(call_every="10:00:00", stop_after=3)
def schedule_me():
    pass


# Call with args and keyword args
@schedule(call_every="10:00:00", args=(3,), kwargs={"hello": "world"})
def schedule_me(three: int, hello: str):
    pass


def schedule_programmatically():
    pass


# Call this every five seconds
schedule_subscription: ScheduleSubscription = add_schedule(schedule_programmatically, call_every="*:*:5")

# Stop the schedule call
schedule_subscription.stop()

# Start the schedule again
schedule_subscription.stop()
```
