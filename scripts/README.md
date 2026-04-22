# Agentic GitHub Monitor for QEC-RD-Software

> **For autonomous agents** (Claude Code, Codex, etc.) acting on behalf of a human developer.

This directory contains a lightweight, adaptive monitoring system that lets an agent continuously watch the `QuAIR/QEC-RD-Software` repository for activity directed at the developer it represents — without the developer keeping a live terminal.

## What it does

- **Tracks PRs** opened by the developer for new comments, review comments, and reviews.
- **Tracks open issues** for `@mention` directed at the developer.
- **Filters duplicates** via a local state file so the same comment is never reported twice.
- **Adapts check frequency** based on recent activity: checks as often as every 5 min during busy periods, backs off to 120 min when idle.
- **Expires automatically** after a configurable cutoff date (default: 2026-04-26 23:59 UTC).

## Files

| File | Purpose |
|------|---------|
| `github_monitor.py` | Core monitor. Queries GitHub (via `gh` CLI), detects new notifications, prints them to stdout. Exit codes: `0` = all clear, `1` = new notifications, `2` = monitoring expired. |
| `adaptive_monitor.py` | Frequency governor. Wraps `github_monitor.py`, adjusts check interval dynamically (5–120 min), manages `next_check_time` to avoid unnecessary API calls. |
| `monitor_status.py` | Quick status viewer. Shows last check time, next scheduled check, current interval, and processed item counts. |
| `.monitor_state.json` | **Auto-generated.** Tracks processed comment IDs, last check timestamp, activity scores, and the next scheduled check. Safe to delete — it will be recreated, but duplicate notifications may reappear. |

## Quick start for an agent

### 1. Prerequisites

- `gh` CLI installed and authenticated (`gh auth status` must pass).
- Python 3.10+.

### 2. One-shot check (manual)

```bash
python3 /path/to/scripts/adaptive_monitor.py
```

Output samples:

```
# Too soon — interval not elapsed yet
[...] Skip (interval=20m, next=2026-04-22T06:12:00+00:00)

# Time to check — nothing new
[...] Activity: 0 notifications, 2 events -> next interval=20m

# Time to check — new notification(s)
[...] Activity: 1 notifications, 5 events -> next interval=5m
# (The wrapped github_monitor.py output follows, with full comment/review text)
```

### 3. Continuous monitoring via Claude Code cron

The simplest hands-off setup is a recurring Claude Code cron job that calls `adaptive_monitor.py`. The script itself decides whether to run or skip based on its internal clock.

```bash
# From Claude Code, create a durable recurring job
cron "7,17,27,37,47,57 * * * *" true \
  "Run python3 /path/to/scripts/adaptive_monitor.py. \
   If exit code 1, read stdout to get new notifications, \
   then act on them (reply, code changes, etc.)."
```

**Why a fixed cron + adaptive skip instead of a dynamic cron?**
- Claude Code cron does not support dynamic intervals.
- Running `adaptive_monitor.py` every 10 minutes and letting it skip is cheap — the script exits in <50 ms when nothing to do.
- When activity spikes, the script shortens its internal interval to 5 min, so consecutive cron triggers will actually perform checks and report quickly.

### 4. Status check without triggering a run

```bash
python3 /path/to/scripts/monitor_status.py
```

## Configuration

Edit the constants at the top of each script:

| Constant | File | Meaning |
|----------|------|---------|
| `REPO` | `github_monitor.py`, `adaptive_monitor.py` | `"Owner/Repo"` to watch. |
| `MY_USERNAME` | `github_monitor.py` | The GitHub username of the human developer. |
| `TARGET_MENTION` | `github_monitor.py` | Lower-case `@handle` used in issue mentions (may differ from `MY_USERNAME`). |
| `CUTOFF_DATE` | `github_monitor.py`, `adaptive_monitor.py` | When monitoring auto-expires. After this, scripts print `MONITORING PERIOD EXPIRED` and exit with code `2`. |
| `MIN_INTERVAL` / `MAX_INTERVAL` | `adaptive_monitor.py` | Bounds for adaptive check frequency. |

## How the adaptive interval works

1. After each check, compute an **activity score**:
   - `new_notifications * 5 + recent_events_count`
2. Keep a rolling window of the last 5 scores; use the **maximum** to avoid over-reacting to a single quiet check.
3. Map smoothed score to interval:
   - `>= 8` → 5 min (high activity)
   - `>= 4` → 10 min (moderate)
   - `>= 1` → 20 min (low)
   - `0` → back off by `current * 1.5 + 10`, capped at `MAX_INTERVAL`
4. Write `next_check_time = now + interval` to state file.

## Integration patterns for agents

### Pattern A: Pure cron loop

Use Claude Code `/loop` or `CronCreate` to run `adaptive_monitor.py` on a fixed schedule. Parse exit code and stdout inside the prompt.

**Pros:** Zero local infrastructure, survives screen/tmux detach.  
**Cons:** Fixed cron granularity; may wake up just to skip.

### Pattern B: Long-lived tmux + dynamic sleep

Keep a Claude Code session alive in `tmux` or `screen`. Inside the session, implement a custom loop that sleeps for the exact `next_check_time - now` duration.

**Pros:** No wasted wake-ups; perfectly aligned with adaptive interval.  
**Cons:** Requires persistent process; if the session dies, monitoring stops.

### Pattern C: Hybrid (recommended)

Use a **low-frequency durable cron** (e.g., every 30 min) as a heartbeat. When it fires, run `adaptive_monitor.py` unconditionally. Between cron fires, the developer can manually enter the tmux session and ask for an immediate check.

```bash
# Heartbeat cron (durable, survives reboots if desired)
0,30 * * * *
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `gh error: ...` | Run `gh auth login` or `gh auth status`. The monitor uses the same token as your `gh` CLI. |
| Duplicate notifications after restart | `.monitor_state.json` was lost or deleted. This is expected — just let the monitor re-process; it will re-mark them as processed. |
| Monitoring stopped after 7 days | Claude Code in-memory cron auto-expires after 7 days. Recreate it, or use a durable cron (`durable: true`). |
| "Skip" every time | This is correct — it means the adaptive interval hasn't elapsed yet. Use `monitor_status.py` to see when the next real check is. |

## License

Same as the parent repository (Apache-2.0).
