#!/usr/bin/env python3
"""
Adaptive GitHub monitor with dynamic frequency adjustment.
Runs on a fixed 5-minute cron, but only performs actual check when interval expires.
Interval range: 5 minutes (high activity) ~ 120 minutes (idle).
"""
import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO = "QuAIR/QEC-RD-Software"
STATE_FILE = Path(__file__).parent / ".monitor_state.json"
MIN_INTERVAL = 5      # minutes
MAX_INTERVAL = 120    # minutes
CUTOFF_DATE = datetime(2026, 4, 26, 23, 59, 59, tzinfo=timezone.utc)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "next_check_time": None,
        "current_interval": 20,
        "activity_scores": [],
        "processed_comments": [],
        "processed_reviews": [],
        "last_check": None,
    }


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def should_check(state: dict) -> bool:
    """Return True if enough time has passed since last check."""
    next_time_str = state.get("next_check_time")
    if not next_time_str:
        return True
    next_time = datetime.fromisoformat(next_time_str)
    return now_utc() >= next_time


def run_monitor_script() -> tuple[int, int]:
    """Run the actual monitor script. Return (exit_code, new_notification_count)."""
    script_path = Path(__file__).parent / "github_monitor.py"
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
    )
    # Count new notifications from stdout
    output = result.stdout + result.stderr
    count = 0
    for line in output.splitlines():
        if "new notification" in line.lower() and "action required" in line.lower():
            # Parse "ACTION REQUIRED: N new notification(s)"
            try:
                parts = line.split(":")
                if len(parts) >= 2:
                    num_str = parts[1].strip().split()[0]
                    count = int(num_str)
            except (ValueError, IndexError):
                pass
    return result.returncode, count


def get_recent_events(minutes: int) -> list[dict]:
    """Fetch recent GitHub events to estimate activity level."""
    since = now_utc() - timedelta(minutes=minutes)
    cmd = [
        "gh", "api",
        f"repos/{REPO}/events",
        "--paginate",
        "-q", ".[] | {type: .type, created_at: .created_at}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    events = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
            created = ev.get("created_at")
            if created:
                ev_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if ev_dt >= since:
                    events.append(ev)
        except (json.JSONDecodeError, ValueError):
            continue
    return events


def compute_new_interval(state: dict, new_notifications: int, recent_events: list[dict]) -> int:
    """Calculate next check interval based on activity metrics."""
    # Activity score = weighted sum of signals
    event_count = len(recent_events)
    score = new_notifications * 5 + event_count

    history = state.get("activity_scores", [])
    history.append(score)
    if len(history) > 5:
        history = history[-5:]
    state["activity_scores"] = history

    # Smooth: use max of recent scores to avoid over-reacting to single quiet check
    smoothed_score = max(history) if history else score

    if smoothed_score >= 8:
        interval = 5
    elif smoothed_score >= 4:
        interval = 10
    elif smoothed_score >= 1:
        interval = 20
    else:
        # Idle: back off gradually, cap at MAX_INTERVAL
        current = state.get("current_interval", 20)
        interval = min(int(current * 1.5 + 10), MAX_INTERVAL)

    return max(MIN_INTERVAL, interval)


def main():
    now = now_utc()

    if now > CUTOFF_DATE:
        print(f"[{now.isoformat()}] MONITORING PERIOD EXPIRED")
        return 2

    state = load_state()

    if not should_check(state):
        next_str = state.get("next_check_time", "unknown")
        interval = state.get("current_interval", 20)
        print(f"[{now.isoformat()}] Skip (interval={interval}m, next={next_str})")
        return 0

    # Time to check
    print(f"[{now.isoformat()}] Running check (interval was {state.get('current_interval', 20)}m)")

    exit_code, new_notifications = run_monitor_script()

    # Gather activity metrics
    lookback = max(state.get("current_interval", 20), 30)
    recent_events = get_recent_events(lookback)

    # Compute next interval
    new_interval = compute_new_interval(state, new_notifications, recent_events)
    state["current_interval"] = new_interval
    state["next_check_time"] = (now + timedelta(minutes=new_interval)).isoformat()
    state["last_check"] = now.isoformat()
    save_state(state)

    print(f"[{now.isoformat()}] Activity: {new_notifications} notifications, {len(recent_events)} events -> next interval={new_interval}m")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
