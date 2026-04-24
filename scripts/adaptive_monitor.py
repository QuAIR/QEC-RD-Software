#!/usr/bin/env python3
"""
Adaptive GitHub monitor with dynamic frequency adjustment.
Runs on a fixed cron, but only performs actual check when interval expires.
Interval range: 30 seconds (high activity) ~ 2 hours (idle).
"""
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO = "QuAIR/QEC-RD-Software"
STATE_FILE = Path(__file__).parent / ".monitor_state.json"
LOG_DIR = Path(__file__).parent / "logs"
LOG_FILE = LOG_DIR / "monitor.log"
MIN_INTERVAL = 0.5    # 30 seconds
MAX_INTERVAL = 120    # 2 hours
GROWTH_FACTOR = 1.12  # exponential growth per idle check
CUTOFF_DATE = datetime(2026, 4, 26, 23, 59, 59, tzinfo=timezone.utc)

# Setup logging: file gets everything, console only gets actual checks (not skips)
LOG_DIR.mkdir(exist_ok=True)
logger = logging.getLogger("adaptive_monitor")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Separate file-only logger for skip messages (no console output)
skip_logger = logging.getLogger("adaptive_monitor.skip")
skip_logger.setLevel(logging.INFO)
skip_logger.propagate = False  # Don't inherit parent handlers
skip_file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
skip_file_handler.setFormatter(formatter)
skip_logger.addHandler(skip_file_handler)
# No console handler for skip_logger

# Console handler for main logger (actual checks)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


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
        "idle_streak": 0,
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
        # Look for the exact github_monitor pattern (after log timestamp)
        if "ACTION REQUIRED:" in line and "new notification" in line:
            # Line format: "2026-04-22 14:57:38 [WARNING] ACTION REQUIRED: 1 new notification(s)"
            # Find the part after "ACTION REQUIRED:"
            idx = line.find("ACTION REQUIRED:")
            if idx != -1:
                after = line[idx + len("ACTION REQUIRED:"):].strip()
                try:
                    count = int(after.split()[0])
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


def compute_new_interval(state: dict, new_notifications: int, recent_events: list[dict]) -> float:
    """Calculate next check interval based on activity metrics.

    Exponential growth from MIN_INTERVAL when idle, capped at MAX_INTERVAL.
    Growth rate is slow at the beginning (gentle decay from frequent checks).
    Only resets to MIN when there are actual notifications (not just repo events).
    """
    event_count = len(recent_events)

    # Track idle streak: increments when no actionable notifications
    idle_streak = state.get("idle_streak", 0)
    if new_notifications > 0:
        # Actionable activity - reset to fastest
        idle_streak = 0
    else:
        # No notifications - grow streak (repo events don't reset)
        idle_streak += 1
    state["idle_streak"] = idle_streak

    # Exponential growth: interval = MIN * GROWTH_FACTOR ^ idle_streak
    interval = MIN_INTERVAL * (GROWTH_FACTOR ** idle_streak)
    interval = min(interval, MAX_INTERVAL)

    return max(MIN_INTERVAL, interval)


def is_beijing_night_hours(dt: datetime) -> bool:
    """Return True if Beijing time is between 22:00 and 08:00 (night pause)."""
    beijing = dt.astimezone(timezone(timedelta(hours=8)))
    hour = beijing.hour
    return hour >= 22 or hour < 8


def next_beijing_morning_8am(dt: datetime) -> datetime:
    """Return the next 08:00 Beijing time as UTC datetime."""
    beijing = dt.astimezone(timezone(timedelta(hours=8)))
    if beijing.hour >= 22:
        # After 22:00, next morning is tomorrow
        next_day = beijing.date() + timedelta(days=1)
    else:
        # Before 08:00, next morning is today
        next_day = beijing.date()
    morning_beijing = datetime(next_day.year, next_day.month, next_day.day, 8, 0, 0, tzinfo=timezone(timedelta(hours=8)))
    return morning_beijing.astimezone(timezone.utc)


def main():
    now = now_utc()

    if now > CUTOFF_DATE:
        print(f"[{now.isoformat()}] MONITORING PERIOD EXPIRED")
        return 2

    state = load_state()

    # Night pause: Beijing 22:00 - 08:00
    if is_beijing_night_hours(now):
        next_morning = next_beijing_morning_8am(now)
        state["next_check_time"] = next_morning.isoformat()
        save_state(state)
        logger.info(f"Night pause (Beijing {now.astimezone(timezone(timedelta(hours=8))).strftime('%H:%M')}), next check at {next_morning.isoformat()}")
        return 0

    if not should_check(state):
        next_str = state.get("next_check_time", "unknown")
        interval = state.get("current_interval", 20)
        if interval < 1:
            iv_str = f"{interval * 60:.0f}s"
        else:
            iv_str = f"{interval:.1f}m"
        skip_logger.info(f"Skip (interval={iv_str}, next={next_str})")
        return 0

    # Time to check
    prev = state.get('current_interval', 20)
    if prev < 1:
        prev_str = f"{prev * 60:.0f}s"
    else:
        prev_str = f"{prev:.1f}m"
    logger.info(f"Running check (interval was {prev_str})")

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

    if new_interval < 1:
        iv_str = f"{new_interval * 60:.0f}s"
    else:
        iv_str = f"{new_interval:.1f}m"
    logger.info(f"Activity: {new_notifications} notifications, {len(recent_events)} events -> next interval={iv_str}")

    # Log structured action summary
    next_check = state.get("next_check_time", "unknown")
    if new_notifications > 0:
        logger.warning(f"ACTION REQUIRED: {new_notifications} new notification(s) detected")
        logger.info(
            f"SUMMARY | check_time={now.isoformat()} | "
            f"result=ACTION_REQUIRED | notifications={new_notifications} | "
            f"events={len(recent_events)} | next_check={next_check} | interval={iv_str}"
        )
    else:
        logger.info("No actionable notifications")
        logger.info(
            f"SUMMARY | check_time={now.isoformat()} | "
            f"result=NO_ACTION | notifications=0 | events={len(recent_events)} | "
            f"next_check={next_check} | interval={iv_str}"
        )

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
