"""
Pre-Contest Alert — Sends an urgent email ~3 hours before each rated contest.

Scheduled to run every 30 minutes via GitHub Actions.
Checks for contests starting in the [now + 2h45m, now + 3h15m] window.
If found, sends individual alert emails. If the window is empty, exits silently.

Usage:
    python pre_contest_alert.py
    python pre_contest_alert.py --test   # Force-send a sample alert for testing
"""

import sys
from datetime import datetime, timedelta

from src.config import IST, ALERT_WINDOW_MIN, ALERT_WINDOW_MAX
from src.clist_client import fetch_contests
from src.email_builder import build_pre_contest_alert, _format_time_12h
from src.email_sender import send_email


def _send_test_alert():
    """Send a test alert email with mock contest data."""
    print("🧪 TEST MODE — Sending a sample pre-contest alert...\n")

    mock_contest = {
        "platform": "Codeforces",
        "platform_color": "#1a73e8",
        "platform_icon": "📊",
        "name": "Codeforces Round 999 (Div. 2) [TEST]",
        "start_ist": datetime.now(IST) + timedelta(hours=3),
        "end_ist": datetime.now(IST) + timedelta(hours=5),
        "duration_hours": 2.0,
        "url": "https://codeforces.com/contests",
        "time_until": "3h 0m",
        "total_minutes_until": 180,
    }

    subject, html_body = build_pre_contest_alert(mock_contest)

    try:
        send_email(subject, html_body)
        print("\n✅ Test alert sent! Check your inbox.")
    except Exception as e:
        print(f"\n❌ Failed to send test alert: {e}")
        sys.exit(1)


def main():
    # ── Handle test mode ─────────────────────────────────────────────────
    if "--test" in sys.argv:
        _send_test_alert()
        return

    now = datetime.now(IST)
    print(f"🏆 Contest Alert System — Pre-Contest Check")
    print(f"   🕐 Current time: {now.strftime('%H:%M:%S')} IST")

    # ── Define the 30-minute alert window ────────────────────────────────
    window_start = now + timedelta(minutes=ALERT_WINDOW_MIN)  # +2h 45m
    window_end = now + timedelta(minutes=ALERT_WINDOW_MAX)    # +3h 15m

    start_str = _format_time_12h(window_start)
    end_str = _format_time_12h(window_end)
    print(f"   🔍 Alert window: {start_str} – {end_str} IST")
    print()

    # ── Fetch contests in the alert window ───────────────────────────────
    try:
        contests = fetch_contests(start_gte=window_start, start_lte=window_end)
    except Exception as e:
        print(f"   ❌ Failed to fetch contests: {e}")
        sys.exit(1)

    # ── No contests? Exit silently ───────────────────────────────────────
    if not contests:
        print("😴 No contests in the alert window. Exiting quietly.")
        return

    # ── Send individual alert for each contest ───────────────────────────
    print(f"🔔 Found {len(contests)} contest(s) to alert about!\n")

    for contest in contests:
        start_time = _format_time_12h(contest["start_ist"])
        print(f"   📧 Alerting: [{contest['platform']}] {contest['name']} at {start_time} IST")

        subject, html_body = build_pre_contest_alert(contest)

        try:
            send_email(subject, html_body)
        except Exception as e:
            print(f"   ❌ Failed to send alert for {contest['name']}: {e}")
            # Continue sending alerts for other contests
            continue

    print(f"\n✅ All alerts processed!")


if __name__ == "__main__":
    main()
