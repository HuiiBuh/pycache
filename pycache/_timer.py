import re
from datetime import datetime, timedelta
from typing import Optional


class Timer:

    def __init__(self, start_time: datetime):
        self._start_time: datetime = start_time

        self._expiry_str: Optional[str] = None
        self._schedule_str: Optional[str] = None
        self._expiry_date: Optional[datetime] = None

    def set_expiry(self, expires_every: str, schedule: str):
        self._expiry_str = expires_every
        self._schedule_str = schedule
        if self._expiry_str:
            self._expiry_date = self._parse_expiry()
        else:
            self._expiry_date = self._parse_schedule()

    def _parse_expiry(self) -> datetime:
        split_str = self._expiry_str.split(":")
        h = split_str[0]
        m = split_str[1]
        s = split_str[2]

        seconds = 0
        if not re.search("^\\*+$", h):
            seconds += int(h) * 60 * 60

        if not re.search("^\\*+$", m):
            seconds += int(m) * 60

        if not re.search("^\\*+$", s):
            seconds += int(s)

        return self._start_time + timedelta(0, seconds)

    def _parse_schedule(self) -> datetime:
        split_str = self._schedule_str.split(":")
        h = split_str[0]
        m = split_str[1]
        s = split_str[2]

        current = datetime.now()
        days = current.day

        if not re.search("^\\*+$", s):
            seconds = int(s)
        else:
            seconds = current.second

        if not re.search("^\\*+$", m):
            minutes = int(m)
        else:
            minutes = current.minute

        if not re.search("^\\*+$", h):
            hours = int(h)
        else:
            hours = current.hour

        if re.search("^\\*+$", h) and re.search("^\\*+$", m):
            minutes += 1
        elif re.search("^\\*+$", h):
            hours += 1
        else:
            days += 1

        return datetime(current.year, current.month, days, hours, minutes, seconds)

    def has_expired(self) -> bool:
        return self._expiry_date < datetime.now()

    def reset(self):
        self._start_time = datetime.now()
        if self._expiry_str:
            self._expiry_date = self._parse_expiry()
        else:
            self._expiry_date = self._parse_schedule()
