"""
Configuration constants for the Contest Alert System.

All settings are loaded from environment variables for security.
Secrets should be stored in GitHub Actions secrets (production)
or a local .env file (development).
"""

import os
from datetime import timezone, timedelta


# ─── Timezone ────────────────────────────────────────────────────────────────
# Indian Standard Time: UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30), name="IST")


# ─── Clist.by API ────────────────────────────────────────────────────────────
CLIST_API_BASE = "https://clist.by/api/v4/json/contest/"
CLIST_USERNAME = os.environ.get("CLIST_USERNAME", "")
CLIST_API_KEY = os.environ.get("CLIST_API_KEY", "")

# Platform resource IDs on Clist.by
# Verify yours at: https://clist.by/api/v4/json/resource/?username=YOUR_USER&api_key=YOUR_KEY
RESOURCE_IDS = {
    1: {"name": "Codeforces", "color": "#1a73e8", "icon": "⚡"},
    2: {"name": "CodeChef",   "color": "#c4721a", "icon": "👨‍🍳"},
}
RESOURCE_ID_FILTER = ",".join(str(rid) for rid in RESOURCE_IDS)


# ─── Resend Email ────────────────────────────────────────────────────────────
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = "Contest Alerts <onboarding@resend.dev>"
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "")


# ─── Pre-Contest Alert Window ────────────────────────────────────────────────
# The pre-contest cron runs every 30 minutes.
# We check for contests starting in a 30-minute window centered at 3 hours:
#   - Window: [now + 2h45m, now + 3h15m]
#   - This ensures no missed alerts and no duplicates across cron runs.
ALERT_WINDOW_CENTER = 180   # 3 hours = 180 minutes
ALERT_WINDOW_TOLERANCE = 15 # ±15 minutes
ALERT_WINDOW_MIN = ALERT_WINDOW_CENTER - ALERT_WINDOW_TOLERANCE  # 165 min
ALERT_WINDOW_MAX = ALERT_WINDOW_CENTER + ALERT_WINDOW_TOLERANCE  # 195 min
