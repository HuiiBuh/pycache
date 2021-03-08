# Method cache

If you want to cache the calls to a specific method or function you could use the python `functools.cache` decorator. If
this has not enough configuration options for your taste, or you work with arguments which are not hashable this cache
decorator could be useful.

## Advantages

+ Works with non hashable objects
+ Set expiry after time
+ Set expiry after a schedule
+ Set maximal cache size per method
+ Works with sync and async functions
+ Properly tested

## Usage

Use a cache which expires after a certain amount of time:

```python
from pycache import cache


# The format for expires_every is <hh:mm:ss>
# This cache would expire every 10 seconds
@cache(expires_every="*:*:10")
def please_cache():
    pass


# This cache would expire every 5 minutes and 10 seconds
@cache(expires_every="*:5:10")
def please_cache():
    pass
```

Use a cache which expires every time at a certain time (A bit like a cron job).

```python
from pycache import cache


# The format for schedule is <hh:mm:ss>
# This cache would expire every day at 15:10:05
@cache(schedule="15:10:05")
def please_cache():
    pass


# This cache would expire every hour 8 minutes after a full hour
@cache(schedule="*:08:00")
def please_cache():
    pass
```

Limit the number of cache entries

```python
from pycache import cache


# This would result in only one cache entry
@cache(expires_every="*:*:10", max_cache_size=1)
def please_cache(data: str):
    pass


# Gets placed in cache
please_cache("hello")
# Gets called from cache
please_cache("hello")

# Gets placed in cache and "hello" gets removed
please_cache("world")

# Is not found in cache, because "world" is the only cache entry, 
# because the cache size is one
please_cache("hello")
```
