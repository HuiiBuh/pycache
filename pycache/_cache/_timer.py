from datetime import datetime, timedelta
from typing import Optional

from pycache._shared._parser import parse_expires_every, parse_expires_at, ScheduleType


class Timer:

    def __init__(self):
        self._schedule_type: Optional[ScheduleType] = None
        self._schedule_str: Optional[str] = None

        self._expiry_date: Optional[datetime] = None

    def set_schedule(self, schedule_type: ScheduleType, schedule_str: str):
        self._schedule_type = schedule_type
        self._schedule_str = schedule_str
        self.reset()

    def has_expired(self) -> bool:
        return self._expiry_date < datetime.now()

    def reset(self):
        start_time = datetime.now()
        if self._schedule_type == ScheduleType.EVERY:
            self._expiry_date = start_time + timedelta(seconds=parse_expires_every(self._schedule_str))
        elif self._schedule_type == ScheduleType.AT:
            self._expiry_date = parse_expires_at(self._schedule_str)
