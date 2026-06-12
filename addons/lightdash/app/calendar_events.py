from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_CACHE_TTL = 300
_WINDOW_BACK = 2
_WINDOW_FWD = 9


class CalendarCache:
    def __init__(self) -> None:
        self._data: Dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any:
        entry = self._data.get(key)
        if entry is None:
            return None
        data, ts = entry
        if time.monotonic() - ts > _CACHE_TTL:
            del self._data[key]
            return None
        return data

    def set(self, key: str, data: Any) -> None:
        self._data[key] = (data, time.monotonic())

    def clear(self, key: str) -> None:
        self._data.pop(key, None)


def _parse_when(obj: Any) -> tuple[Optional[datetime], bool]:
    if not isinstance(obj, dict):
        return None, False
    if obj.get("dateTime"):
        raw = obj["dateTime"].replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(raw)
        except ValueError:
            return None, False
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(), False
    if obj.get("date"):
        try:
            d = datetime.strptime(obj["date"], "%Y-%m-%d")
        except ValueError:
            return None, False
        return d.astimezone(), True
    return None, False


def _normalise(raw_events: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not isinstance(raw_events, list):
        return out
    for ev in raw_events:
        if not isinstance(ev, dict):
            continue
        start, all_day = _parse_when(ev.get("start"))
        end, _ = _parse_when(ev.get("end"))
        if start is None:
            continue
        if end is None:
            end = start + timedelta(hours=1)
        out.append({
            "summary": ev.get("summary", "") or "",
            "start": start,
            "end": end,
            "all_day": all_day,
        })
    out.sort(key=lambda e: e["start"])
    return out


async def get_events(
    entity_id: str,
    ha_client: Any,
    cache: CalendarCache,
) -> List[Dict[str, Any]]:
    cached = cache.get(entity_id)
    if cached is not None:
        return cached

    now = datetime.now().astimezone()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start = (midnight - timedelta(days=_WINDOW_BACK)).isoformat()
    end = (midnight + timedelta(days=_WINDOW_FWD)).isoformat()

    raw = await ha_client.get_calendar_events(entity_id, start, end)
    events = _normalise(raw or [])
    cache.set(entity_id, events)
    return events


def get_dummy_events(target_date) -> List[Dict[str, Any]]:
    """Return synthetic events for the given date covering all visual states."""
    tz = datetime.now().astimezone().tzinfo
    noon = datetime(target_date.year, target_date.month, target_date.day, 12, 0, tzinfo=tz)
    now = datetime.now().astimezone()
    today = now.date()
    offset_days = (target_date - today).days

    def _dt(h, m=0):
        return datetime(target_date.year, target_date.month, target_date.day, h, m, tzinfo=tz)

    events = []

    # past event (1 hour ago if today, else first slot)
    events.append({
        "summary": "Morning standup",
        "start": _dt(8, 30),
        "end": _dt(8, 45),
        "all_day": False,
    })

    # current event (only if today, covers 09-17)
    if offset_days == 0:
        events.append({
            "summary": "Home-Office",
            "start": _dt(9, 0),
            "end": _dt(17, 0),
            "all_day": False,
        })
        events.append({
            "summary": "Dentist — Dr. Okafor",
            "start": _dt(13, 30),
            "end": _dt(14, 15),
            "all_day": False,
        })
        events.append({
            "summary": "1:1 with Priya",
            "start": _dt(16, 0),
            "end": _dt(16, 30),
            "all_day": False,
        })
    else:
        events.append({
            "summary": "Team sync",
            "start": _dt(10, 0),
            "end": _dt(11, 0),
            "all_day": False,
        })

    # all-day
    events.append({
        "summary": "Recycling collection",
        "start": datetime(target_date.year, target_date.month, target_date.day, tzinfo=tz),
        "end": datetime(target_date.year, target_date.month, target_date.day, tzinfo=tz) + timedelta(days=1),
        "all_day": True,
    })

    # multi-day (3-day span starting here)
    events.append({
        "summary": "Conf · Berlin",
        "start": datetime(target_date.year, target_date.month, target_date.day, tzinfo=tz),
        "end": datetime(target_date.year, target_date.month, target_date.day, tzinfo=tz) + timedelta(days=3),
        "all_day": True,
    })

    events.sort(key=lambda e: e["start"])
    return events
