"""
Daily Digest — Morning email with today's rated contests.

Scheduled to run daily at 8:00 AM IST via GitHub Actions.
Fetches all rated Codeforces and CodeChef contests starting today,
builds a styled HTML digest, and sends it via Resend.

On days with no contests, sends a "no contests today" notification
to confirm the system is alive and working.

Usage:
    python daily_digest.py
"""

import sys
from datetime import datetime, timedelta

from src.config import IST
from src.clist_client import fetch_contests
from src.email_builder import build_daily_digest, _format_date
from src.email_sender import send_email


def main():
    now = datetime.now(IST)
    print(f"🏆 Contest Alert System — Daily Digest")
    print(f"   📅 {_format_date(now)}")
    print(f"   🕐 Current time: {now.strftime('%H:%M:%S')} IST")
    print()

    # ── Define today's boundaries in IST ─────────────────────────────────
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)

    # ── Fetch today's contests ───────────────────────────────────────────
    print(f"🔍 Fetching contests for today...")
    try:
        contests = fetch_contests(start_gte=start_of_day, start_lte=end_of_day)
    except Exception as e:
        print(f"   ❌ Failed to fetch contests: {e}")
        sys.exit(1)

    # ── Log results ──────────────────────────────────────────────────────
    print(f"\n📋 Found {len(contests)} rated contest(s) today:")
    if contests:
        for c in contests:
            start_time = c["start_ist"].strftime("%I:%M %p").lstrip("0")
            print(f"   • [{c['platform']}] {c['name']} at {start_time} IST ({c['time_until']})")
    else:
        print(f"   (none)")

    # ── Build and send email ─────────────────────────────────────────────
    date_str = _format_date(now)
    subject, html_body = build_daily_digest(contests, date_str)

    print(f"\n📧 Sending daily digest email...")
    try:
        send_email(subject, html_body)
    except Exception as e:
        print(f"   ❌ Failed to send email: {e}")
        sys.exit(1)

    print(f"\n✅ Daily digest complete!")


if __name__ == "__main__":
    main()
