"""
Clist.by API client for fetching upcoming rated contests.

Fetches contests from Codeforces and CodeChef, filters out unrated ones,
and returns structured contest data with IST-converted timestamps.
"""

import requests
from datetime import datetime, timezone as tz

from src.config import (
    CLIST_API_BASE,
    CLIST_USERNAME,
    CLIST_API_KEY,
    RESOURCE_ID_FILTER,
    RESOURCE_IDS,
    IST,
)


def fetch_contests(start_gte: datetime, start_lte: datetime) -> list[dict]:
    """
    Fetch rated contests from Clist.by within a time window.

    Args:
        start_gte: Minimum start time (inclusive, timezone-aware).
        start_lte: Maximum start time (inclusive, timezone-aware).

    Returns:
        List of contest dicts sorted by start time, with IST timestamps.
        Unrated contests are excluded.

    Raises:
        requests.HTTPError: If the Clist.by API returns an error.
    """
    # Convert to UTC for the API query (Clist.by expects UTC)
    start_gte_utc = start_gte.astimezone(tz.utc)
    start_lte_utc = start_lte.astimezone(tz.utc)

    params = {
        "username": CLIST_USERNAME,
        "api_key": CLIST_API_KEY,
        "resource_id__in": RESOURCE_ID_FILTER,
        "start__gte": start_gte_utc.strftime("%Y-%m-%dT%H:%M:%S"),
        "start__lte": start_lte_utc.strftime("%Y-%m-%dT%H:%M:%S"),
        "order_by": "start",
    }

    print(f"   → Querying Clist.by API...")
    response = requests.get(CLIST_API_BASE, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    raw_contests = data.get("objects", [])
    print(f"   → API returned {len(raw_contests)} contest(s)")

    contests = []
    now_ist = datetime.now(IST)

    for obj in raw_contests:
        event_name = obj.get("event", "")

        # ── Filter out unrated contests ──────────────────────────────────
        # Codeforces labels unrated rounds explicitly in the event name.
        # CodeChef's short contests (Starters, Cook-Off, Lunchtime) are rated.
        if "unrated" in event_name.lower():
            print(f"   ⏩ Skipping unrated: {event_name}")
            continue

        # ── Parse timestamps ─────────────────────────────────────────────
        # Clist.by returns naive datetimes in UTC
        start_str = obj.get("start", "")
        end_str = obj.get("end", "")

        start_utc = datetime.fromisoformat(start_str).replace(tzinfo=tz.utc)
        end_utc = datetime.fromisoformat(end_str).replace(tzinfo=tz.utc)

        start_ist = start_utc.astimezone(IST)
        end_ist = end_utc.astimezone(IST)

        # ── Duration ─────────────────────────────────────────────────────
        duration_seconds = obj.get("duration", 0)
        duration_hours = round(duration_seconds / 3600, 1)

        # ── Countdown ────────────────────────────────────────────────────
        time_diff = start_ist - now_ist
        total_minutes = int(time_diff.total_seconds() // 60)

        if total_minutes > 0:
            hours = total_minutes // 60
            mins = total_minutes % 60
            time_until = f"{hours}h {mins}m"
        else:
            time_until = "Started"

        # ── Platform info ────────────────────────────────────────────────
        # Handle both flat `resource_id` and nested `resource.id` formats
        resource_id = obj.get("resource_id") or obj.get("resource", {}).get("id", 0)
        platform_info = RESOURCE_IDS.get(
            resource_id,
            {"name": "Unknown", "color": "#6b7280", "icon": "🏆"},
        )

        contests.append({
            "platform": platform_info["name"],
            "platform_color": platform_info["color"],
            "platform_icon": platform_info["icon"],
            "name": event_name,
            "start_ist": start_ist,
            "end_ist": end_ist,
            "duration_hours": duration_hours,
            "url": obj.get("href", "#"),
            "time_until": time_until,
            "total_minutes_until": total_minutes,
        })

    return contests
