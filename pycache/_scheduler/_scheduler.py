import asyncio
import threading
from asyncio import sleep
from datetime import datetime
from typing import Callable, Any, Tuple, Dict

from _shared._parser import parse_expires_at, get_schedule_type, ScheduleType, parse_expires_every


class ScheduleSubscription:
    def __init__(self, schedule_type: ScheduleType, schedule_str: str, func: Callable, stop_after: int, args, kwargs):
        self._stop_after = stop_after
        self._schedule_type = schedule_type
        self._schedule_str = schedule_str
        self._args = args
        self._kwargs = kwargs
        self._func = func
        self._running = True

        threading.Thread(target=self._start).start()

    def _start(self):
        loop = self._get_or_create_eventloop()
        loop.run_until_complete(self._schedule())

    def _get_or_create_eventloop(self):
        try:
            return asyncio.get_event_loop()
        except RuntimeError as ex:
            if "There is no current event loop in thread" in str(ex):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return asyncio.get_event_loop()

    async def _schedule(self):
        while self._running and self._continue_running():
            if asyncio.iscoroutinefunction(self._func):
                await self._func(*self._args, **self._kwargs)
            else:
                self._func(*self._args, **self._kwargs)
            await sleep(self._run_in())
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
        self._running = False

    def start(self):
        self._running = True


def schedule(
        expires_every: str = None,
        expires_at: str = None,
        stop_after: int = None,
        args: Tuple[Any] = (),
        kwargs: Dict[str, Any] = None
):
    def wrapper(func: Callable):
        add_schedule(func, expires_every, expires_at, stop_after, args, kwargs)

    return wrapper


def add_schedule(func: Callable,
                 expires_every: str = None,
                 expires_at: str = None,
                 stop_after: int = None,
                 args: Tuple[Any] = (),
                 kwargs: Dict[str, Any] = None
                 ) -> ScheduleSubscription:
    schedule_type, schedule_str = get_schedule_type(expires_every, expires_at)

    if kwargs is None:
        kwargs = {}

    return ScheduleSubscription(schedule_type, schedule_str, func, stop_after, args, kwargs)
