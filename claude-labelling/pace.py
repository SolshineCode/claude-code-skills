#!/usr/bin/env python3
"""Go/no-go pacing for Claude-Code-subscription labelling batches.

Reads the numbers from the Claude usage page (Settings -> Usage) and decides whether the NEXT
batch may start, so labelling never runs the account into a plan limit (where usage credits,
i.e. real money, may take over) and always leaves the user a reserve that scales with how far
off the weekly renewal is.

Rules (all must pass):
  S  session:  session_used + batch_session_cost <= SESSION_CEIL (default 80%)
               -> otherwise WAIT for the session reset, never push through it
  W  weekly:   week_used + batch_week_cost <= 100 - reserve
               reserve = max(RESERVE_MIN, RESERVE_PER_DAY * days_until_weekly_reset)
               (defaults 15 and 12: two days out keeps about 24 points for the user; near
                the renewal the reserve shrinks to 15, because unused capacity is lost at reset)
               FINAL WINDOW: in the last 2 hours before the weekly reset the weekly ceiling is 98%
               total (the user's rule), whatever the reserve formula says
  C  credits:  if usage credits are ON, both ceilings tighten by CREDIT_MARGIN (default 5)
               because hitting a limit spends real money instead of pausing

Batch costs should be MEASURED after the first batch (usage delta / batches run), not guessed.

Usage:
  python pace.py --session 19 --week 48 --week-reset "2026-09-25 19:00" \
                 --batch-session 18 --batch-week 1.5 [--credits-on] [--now "2026-09-23 11:30"]
Exit code 0 = GO, 1 = WAIT (session), 2 = STOP (weekly), 3 = bad input.
"""
import argparse, sys
from datetime import datetime

SESSION_CEIL, RESERVE_MIN, RESERVE_PER_DAY, CREDIT_MARGIN = 80.0, 15.0, 12.0, 5.0
# Final window before the weekly renewal: unused capacity is lost at reset, so labelling may use
# the week up to FINAL_CEIL total. The session ceiling still applies throughout.
FINAL_WINDOW_HOURS, FINAL_CEIL = 2.0, 98.0


def decide(session, week, week_reset, batch_session, batch_week, now, credits_on=False):
    days = max(0.0, (week_reset - now).total_seconds() / 86400)
    reserve = max(RESERVE_MIN, RESERVE_PER_DAY * days)
    s_ceil = SESSION_CEIL - (CREDIT_MARGIN if credits_on else 0)
    w_ceil = 100 - reserve - (CREDIT_MARGIN if credits_on else 0)
    final_window = days * 24 <= FINAL_WINDOW_HOURS
    if final_window:
        w_ceil = FINAL_CEIL
    info = {"days_to_weekly_reset": round(days, 2), "weekly_reserve_pts": round(reserve, 1),
            "session_ceiling": s_ceil, "weekly_ceiling": round(w_ceil, 1), "final_window": final_window,
            "session_after": session + batch_session, "week_after": round(week + batch_week, 1)}
    if week + batch_week > w_ceil:
        return "STOP", 2, info
    if session + batch_session > s_ceil:
        return "WAIT", 1, info
    info["batches_left_this_week"] = int((w_ceil - week) // batch_week) if batch_week > 0 else None
    return "GO", 0, info


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", type=float, required=True, help="current session %% used")
    ap.add_argument("--week", type=float, required=True, help="current week %% used")
    ap.add_argument("--week-reset", required=True, help='weekly reset, "YYYY-MM-DD HH:MM" local')
    ap.add_argument("--batch-session", type=float, required=True, help="measured session %% per batch")
    ap.add_argument("--batch-week", type=float, required=True, help="measured week %% per batch")
    ap.add_argument("--credits-on", action="store_true", help="usage credits toggle is ON")
    ap.add_argument("--now", default=None, help='override now, "YYYY-MM-DD HH:MM"')
    a = ap.parse_args()
    try:
        reset = datetime.strptime(a.week_reset, "%Y-%m-%d %H:%M")
        now = datetime.strptime(a.now, "%Y-%m-%d %H:%M") if a.now else datetime.now()
    except ValueError as e:
        print(f"bad time: {e}"); return 3
    verdict, code, info = decide(a.session, a.week, reset, a.batch_session, a.batch_week, now, a.credits_on)
    print(verdict, info)
    return code


if __name__ == "__main__":
    sys.exit(main())
