#!/usr/bin/env python3
"""Quick status check for the adaptive GitHub monitor."""
import json
from datetime import datetime, timezone
from pathlib import Path

STATE_FILE = Path(__file__).parent / ".monitor_state.json"


def main():
    if not STATE_FILE.exists():
        print("No state file found. Monitor has not run yet.")
        return

    with open(STATE_FILE) as f:
        state = json.load(f)

    iv = state.get('current_interval', 'N/A')
    if isinstance(iv, (int, float)) and iv < 1:
        iv_str = f"{iv * 60:.0f}s"
    elif isinstance(iv, (int, float)):
        iv_str = f"{iv:.1f}m"
    else:
        iv_str = str(iv)
    print("GitHub Monitor Status")
    print("=" * 40)
    print(f"Last check:       {state.get('last_check', 'Never')}")
    print(f"Next check:       {state.get('next_check_time', 'N/A')}")
    print(f"Current interval: {iv_str}")
    print(f"Idle streak:      {state.get('idle_streak', 0)}")
    print(f"Processed comments: {len(state.get('processed_comments', []))}")
    print(f"Processed reviews:  {len(state.get('processed_reviews', []))}")
    print("=" * 40)

    next_str = state.get("next_check_time")
    if next_str:
        next_dt = datetime.fromisoformat(next_str)
        now = datetime.now(timezone.utc)
        remaining = next_dt - now
        if remaining.total_seconds() > 0:
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            print(f"Time until next check: {mins}m {secs}s")
        else:
            print("Next check is overdue (will run on next trigger)")

    print("\nTo manually check now, run:")
    print("  python3 /home/leizhang/QEC-RD-Software/scripts/adaptive_monitor.py")


if __name__ == "__main__":
    main()
