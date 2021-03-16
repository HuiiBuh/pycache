import asyncio
import threading
from datetime import datetime
from typing import Callable, Any, Tuple, Dict

from pycache._shared._parser import parse_expires_at, get_schedule_type, ScheduleType, parse_expires_every


class ScheduleSubscription:
    def __init__(self, schedule_type: ScheduleType, schedule_str: str, func: Callable, stop_after: int, args, kwargs):
        self._stop_after = stop_after
        self._schedule_type = schedule_type
        self._schedule_str = schedule_str
        self._args = args
        self._kwargs = kwargs
        self._func = func

        self._thread = threading.Thread(target=self._schedule)
        self._kill = threading.Event()
        self._thread.start()

    @staticmethod
    def _get_or_create_event_loop():
        try:
            return asyncio.get_event_loop()
        except RuntimeError as ex:
            if "There is no current event loop in thread" in str(ex):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return asyncio.get_event_loop()

    def _schedule(self):
        while self._continue_running():
            if asyncio.iscoroutinefunction(self._func):
                loop = ScheduleSubscription._get_or_create_event_loop()
                loop.run_until_complete(self._func(*self._args, **self._kwargs))
            else:
                self._func(*self._args, **self._kwargs)

            is_killed = self._kill.wait(self._run_in())
            if is_killed:
                break

            if self._stop_after is not None:
                self._stop_after -= 1

    def _continue_running(self):
        if self._stop_after is None:
            return True
        else:
            return self._stop_after > 0

    def _run_in(self) -> float:
        if self._schedule_type == ScheduleType.EVERY:
            return parse_expires_every(self._schedule_str)
        elif self._schedule_type == ScheduleType.AT:
            return (parse_expires_at(self._schedule_str) - datetime.now()).total_seconds()

    def stop(self):
        self._kill.set()
        self._thread.join(2)
        self._kill.clear()

    def start(self):
        self._thread = threading.Thread(target=self._schedule)
        self._thread.start()


def schedule(
        call_every: str = None,
        call_at: str = None,
        stop_after: int = None,
        args: Tuple[Any] = (),
        kwargs: Dict[str, Any] = None
):
    def wrapper(func: Callable):
        add_schedule(func, call_every, call_at, stop_after, args, kwargs)

    return wrapper


def add_schedule(func: Callable,
                 call_every: str = None,
                 call_at: str = None,
                 stop_after: int = None,
                 args: Tuple[Any] = (),
                 kwargs: Dict[str, Any] = None
                 ) -> ScheduleSubscription:
    schedule_type, schedule_str = get_schedule_type(call_every, call_at)

    if kwargs is None:
        kwargs = {}

    return ScheduleSubscription(schedule_type, schedule_str, func, stop_after, args, kwargs)
