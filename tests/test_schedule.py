import asyncio
from datetime import datetime

from time import sleep

from _scheduler._scheduler import ScheduleSubscription
from pycache import add_schedule, schedule


def test_interval():
    counter = {"hello": 0}

    def internal():
        counter["hello"] += 1

    schedule = add_schedule(internal, "0:0:1", stop_after=2)
    sleep(3)
    schedule.stop()
    assert counter["hello"] == 2


def test_pass_args():
    counter = {"hello": 0}

    @schedule(call_every="0:0:1", args=(counter,), kwargs={"b": 1}, stop_after=2)
    def internal(a, b):
        a["hello"] += b

    sleep(3)
    assert counter["hello"] == 2


def test_start():
    counter = {"hello": 0}

    def internal():
        counter["hello"] += 1

    schedule_subscription = add_schedule(internal, "0:0:1")
    sleep(1.5)
    schedule_subscription.stop()
    sleep(10)
    schedule_subscription.start()
    sleep(1.5)
    schedule_subscription.stop()

    assert counter["hello"] == 4


def test_count():
    counter = {"hello": 0}

    async def internal():
        counter["hello"] += 1

    schedule = add_schedule(internal, "0:0:1", stop_after=3)
    sleep(4)
    schedule.stop()

    assert counter["hello"] == 3


def test_multiple_scheduler():
    counter = {"hello": 0}

    async def internal1():
        counter["hello"] += 1

    async def internal2():
        counter["hello"] += 1

    schedule1 = add_schedule(internal1, "0:0:1")
    schedule2 = add_schedule(internal2, "0:0:1")
    sleep(2.5)
    schedule1.stop()
    schedule2.stop()

    assert counter["hello"] == 6


def test_expire_at():
    counter = {"hello": 0}

    async def internal():
        counter["hello"] += 1

    current = datetime.now()
    schedule_subscription = add_schedule(internal, call_at=f"{current.hour}:{current.minute}:{current.second + 2}")
    sleep(1)
    schedule_subscription.stop()

    assert counter["hello"] == 1


def test_call_from_async():
    counter = {"hello": 0}

    async def internal():
        counter["hello"] += 1

    async def call():
        current = datetime.now()
        schedule_subscription = add_schedule(internal, call_at=f"{current.hour}:{current.minute}:{current.second + 2}")
        await asyncio.sleep(1)
        schedule_subscription.stop()

    loop = ScheduleSubscription._get_or_create_event_loop()
    loop.run_until_complete(call())

    assert counter["hello"] == 1
