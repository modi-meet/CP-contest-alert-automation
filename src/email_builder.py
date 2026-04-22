"""
HTML email template builder for contest alerts.

Design philosophy:
  - TIME is the hero — largest, boldest element in every card
  - Minimal noise — only what you need to know
  - Platform identity via colored left border accent
  - Gmail-optimized — all inline CSS, table layout, no external resources

Two email types:
  1. Daily Digest — clean morning overview of today's contests
  2. Pre-Contest Alert — focused 3-hour warning for a single contest
"""

from datetime import datetime


# ─── Helper Functions ────────────────────────────────────────────────────────

def _format_time_12h(dt: datetime) -> str:
    """
    Format datetime as '8:05 PM' (12-hour, no leading zero).

    Uses manual formatting instead of %-I for cross-platform safety
    (%-I is a GNU extension that may not work on all systems).
    """
    hour_24 = dt.hour
    minute = dt.minute
    period = "AM" if hour_24 < 12 else "PM"
    hour_12 = hour_24 % 12
    if hour_12 == 0:
        hour_12 = 12
    return f"{hour_12}:{minute:02d} {period}"


def _format_date(dt: datetime) -> str:
    """Format datetime as 'Friday, April 18, 2026'."""
    return f"{dt.strftime('%A')}, {dt.strftime('%B')} {dt.day}, {dt.year}"


def _get_countdown_style(minutes: int) -> tuple[str, str]:
    """
    Get countdown badge colors based on urgency.

    Returns:
        Tuple of (background_color, text_color).
    """
    if minutes <= 120:       # Less than 2 hours — RED (urgent)
        return ("#fef2f2", "#dc2626")
    elif minutes <= 360:     # 2-6 hours — AMBER (warning)
        return ("#fffbeb", "#d97706")
    else:                    # More than 6 hours — GREEN (relaxed)
        return ("#f0fdf4", "#16a34a")


# ─── Contest Card Component ─────────────────────────────────────────────────

def _build_contest_card(contest: dict, is_alert: bool = False) -> str:
    """
    Build a minimal contest card with time as the hero element.

    The card uses a colored left border for platform identity,
    and makes the start time the largest, most prominent element.
    """
    bg_color, text_color = _get_countdown_style(contest["total_minutes_until"])
    start_time = _format_time_12h(contest["start_ist"])
    end_time = _format_time_12h(contest["end_ist"])

    # Split time into parts for styling
    time_parts = start_time.split(" ")  # ["8:05", "PM"]
    time_value = time_parts[0]
    time_period = time_parts[1] if len(time_parts) > 1 else ""

    return f"""
    <tr>
      <td style="padding: {'0' if is_alert else '8px 0'};">
        <table width="100%" cellpadding="0" cellspacing="0"
               style="background: #ffffff; border-radius: 10px;
                      border-left: 5px solid {contest['platform_color']};
                      border: 1px solid #f0f0f0;
                      border-left: 5px solid {contest['platform_color']};">
          <tr>
            <td style="padding: 28px 28px 24px;">

              <!-- Platform Label -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td>
                    <span style="color: {contest['platform_color']}; font-size: 11px;
                                 font-weight: 700; text-transform: uppercase;
                                 letter-spacing: 1.5px;">
                      {contest['platform']}
                    </span>
                  </td>
                  <td align="right">
                    <span style="background: {bg_color}; color: {text_color};
                                 padding: 4px 12px; border-radius: 12px;
                                 font-size: 11px; font-weight: 700;
                                 display: inline-block;">
                      {contest['time_until']}
                    </span>
                  </td>
                </tr>
              </table>

              <!-- TIME — Hero Element -->
              <div style="margin: 16px 0 4px;">
                <span style="font-size: 40px; font-weight: 800; color: #111827;
                             letter-spacing: -1px; line-height: 1;">
                  {time_value}
                </span>
                <span style="font-size: 18px; font-weight: 600; color: #6b7280;
                             margin-left: 3px; vertical-align: top; line-height: 1;">
                  {time_period}
                </span>
                <span style="font-size: 14px; color: #9ca3af; font-weight: 500;
                             margin-left: 6px;">
                  IST
                </span>
              </div>

              <!-- Contest Name -->
              <p style="margin: 12px 0 0; font-size: 16px; color: #374151;
                        font-weight: 600; line-height: 1.5;">
                {contest['name']}
              </p>

              <!-- Metadata -->
              <p style="margin: 8px 0 0; color: #b0b0b0; font-size: 13px;">
                {contest['duration_hours']}h duration &middot; ends {end_time}
              </p>

              <!-- Open Link -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 20px;">
                <tr>
                  <td>
                    <a href="{contest['url']}"
                       style="display: inline-block; background: {contest['platform_color']};
                              color: #ffffff; padding: 10px 22px; border-radius: 6px;
                              text-decoration: none; font-size: 13px; font-weight: 600;">
                      Open Contest
                    </a>
                  </td>
                </tr>
              </table>

            </td>
          </tr>
        </table>
      </td>
    </tr>"""


# ─── Base Email Wrapper ─────────────────────────────────────────────────────

def _wrap_email(content_html: str) -> str:
    """Wrap content in the base email shell — clean, minimal container."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Contest Alert</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f9fafb;
             font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
             Roboto, 'Helvetica Neue', Arial, sans-serif;
             -webkit-font-smoothing: antialiased;
             -moz-osx-font-smoothing: grayscale;">

  <table width="100%" cellpadding="0" cellspacing="0"
         style="background-color: #f9fafb;">
    <tr>
      <td align="center" style="padding: 32px 16px 40px;">
        <table width="100%" cellpadding="0" cellspacing="0"
               style="max-width: 520px;">

          {content_html}

          <!-- Footer -->
          <tr>
            <td style="padding: 32px 4px 0; text-align: center;">
              <p style="margin: 0; color: #c0c0c0; font-size: 11px;">
                All times in IST (UTC+5:30)
              </p>
              <p style="margin: 6px 0 0; color: #d4d4d4; font-size: 11px;">
                via
                <a href="https://clist.by" style="color: #b0b0b0; text-decoration: none;">Clist.by</a>
                &middot;
                <a href="https://resend.com" style="color: #b0b0b0; text-decoration: none;">Resend</a>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


# ─── Daily Digest Builder ───────────────────────────────────────────────────

def build_daily_digest(contests: list[dict], date_str: str) -> tuple[str, str]:
    """
    Build the daily digest email.

    Args:
        contests: List of contest dicts from clist_client.fetch_contests().
        date_str: Formatted date string (e.g., "Friday, April 18, 2026").

    Returns:
        Tuple of (subject_line, html_body).
    """
    count = len(contests)

    # ── Header — Clean text, no gradient ─────────────────────────────────
    summary_text = f"{count} contest{'s' if count != 1 else ''} today" if contests else "No contests today"

    header = f"""
          <tr>
            <td style="padding: 0 4px 28px; text-align: left;">
              <h1 style="margin: 0; font-size: 24px; font-weight: 700;
                         color: #111827; letter-spacing: -0.3px;">
                Contest Digest
              </h1>
              <p style="margin: 6px 0 0; font-size: 14px; color: #9ca3af;">
                {date_str} &middot; {summary_text}
              </p>
            </td>
          </tr>

          <!-- Divider -->
          <tr>
            <td style="padding: 0 4px;">
              <div style="border-top: 1px solid #e5e7eb;"></div>
            </td>
          </tr>"""

    # ── Body ─────────────────────────────────────────────────────────────
    if contests:
        cards_html = "".join(_build_contest_card(c) for c in contests)

        body = f"""
          <tr>
            <td style="padding: 24px 4px 0;">
              <table width="100%" cellpadding="0" cellspacing="0">
                {cards_html}
              </table>
            </td>
          </tr>"""

        subject = f"{count} contest{'s' if count != 1 else ''} today — {date_str}"

    else:
        body = """
          <tr>
            <td style="padding: 48px 4px; text-align: center;">
              <p style="margin: 0; font-size: 15px; color: #9ca3af; line-height: 1.7;">
                No rated contests scheduled for today.<br/>
                We'll alert you when the next one comes up.
              </p>
            </td>
          </tr>"""

        subject = f"No contests today — {date_str}"

    html = _wrap_email(header + body)
    return subject, html


# ─── Pre-Contest Alert Builder ───────────────────────────────────────────────

def build_pre_contest_alert(contest: dict) -> tuple[str, str]:
    """
    Build a focused pre-contest alert email for a single contest.

    Args:
        contest: A single contest dict from clist_client.fetch_contests().

    Returns:
        Tuple of (subject_line, html_body).
    """
    start_time = _format_time_12h(contest["start_ist"])

    # ── Header — Urgent but clean ────────────────────────────────────────
    header = f"""
          <tr>
            <td style="padding: 0 4px 8px; text-align: left;">
              <span style="display: inline-block; background: #fef2f2; color: #dc2626;
                           padding: 5px 14px; border-radius: 6px; font-size: 11px;
                           font-weight: 700; text-transform: uppercase;
                           letter-spacing: 1px;">
                Starting soon
              </span>
              <h1 style="margin: 10px 0 0; font-size: 24px; font-weight: 700;
                         color: #111827; letter-spacing: -0.3px;">
                Contest in ~{contest['time_until']}
              </h1>
            </td>
          </tr>

          <!-- Divider -->
          <tr>
            <td style="padding: 0 4px;">
              <div style="border-top: 1px solid #e5e7eb;"></div>
            </td>
          </tr>"""

    # ── Body — Single contest card ───────────────────────────────────────
    card_html = _build_contest_card(contest, is_alert=True)

    body = f"""
          <tr>
            <td style="padding: 24px 4px 0;">
              <table width="100%" cellpadding="0" cellspacing="0">
                {card_html}
              </table>
            </td>
          </tr>"""

    subject = f"{contest['platform']}: {contest['name']} — {start_time} IST"
    html = _wrap_email(header + body)
    return subject, html
