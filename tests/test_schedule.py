from datetime import datetime

from time import sleep

from pycache import add_schedule, schedule


def test_interval():
    counter = {"hello": 1}

    def internal():
        counter["hello"] += 1

    schedule = add_schedule(internal, "0:0:1")
    sleep(2)
    schedule.stop()
    assert counter["hello"] == 3 or counter["hello"] == 4 or counter["hello"] == 2


def test_pass_args():
    counter = {"hello": 1}

    @schedule(expires_every="0:0:1", args=(counter,), kwargs={"b": 1}, stop_after=3)
    def internal(a, b):
        a["hello"] += b

    sleep(2)
    assert counter["hello"] == 3


def test_start():
    counter = {"hello": 1}

    def internal():
        print("called")
        counter["hello"] += 1

    schedule = add_schedule(internal, "0:0:1")
    sleep(2)
    schedule.stop()
    print("stop")
    schedule.start()
    sleep(2)
    schedule.stop()

    assert counter["hello"] == 5


def test_count():
    counter = {"hello": 1}

    async def internal():
        print("called")
        counter["hello"] += 1

    schedule = add_schedule(internal, "0:0:1", stop_after=3)
    sleep(5)
    schedule.stop()

    assert counter["hello"] == 4


def test_expire_at():
    counter = {"hello": 1}

    async def internal():
        print("called")
        counter["hello"] += 1

    current = datetime.now()
    schedule_subscription = add_schedule(internal, expires_at=f"{current.hour}:{current.minute}:{current.minute + 2}")
    sleep(1)
    schedule_subscription.stop()

    assert counter["hello"] == 2
