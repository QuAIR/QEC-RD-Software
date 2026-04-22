# Agentic GitHub Monitor for QEC-RD-Software

> **For autonomous agents** (Claude Code, Codex, etc.) acting on behalf of a human developer.

This directory contains a lightweight, adaptive monitoring system that lets an agent continuously watch the `QuAIR/QEC-RD-Software` repository for activity directed at the developer it represents — without the developer keeping a live terminal.

## What it does

- **Tracks PRs** opened by the developer for new comments, review comments, and reviews.
- **Tracks open issues** for `@mention` directed at the developer.
- **Filters duplicates** via a local state file so the same comment is never reported twice.
- **Adapts check frequency** based on recent activity: checks as often as every 30 s during busy periods, backs off to 2 h when idle via exponential growth with slow initial decay.
- **Expires automatically** after a configurable cutoff date (default: 2026-04-26 23:59 UTC).

## Files

| File | Purpose |
|------|---------|
| `github_monitor.py` | Core monitor. Queries GitHub (via `gh` CLI), detects new notifications, prints them to stdout. Exit codes: `0` = all clear, `1` = new notifications, `2` = monitoring expired. |
| `adaptive_monitor.py` | Frequency governor. Wraps `github_monitor.py`, adjusts check interval dynamically (30 s – 2 h) via exponential growth, manages `next_check_time` to avoid unnecessary API calls. |
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
[...] Skip (interval=30s, next=2026-04-22T06:12:00+00:00)

# Time to check — nothing new
[...] Activity: 0 notifications, 2 events -> next interval=34s

# Time to check — new notification(s)
[...] Activity: 1 notifications, 5 events -> next interval=30s
# (The wrapped github_monitor.py output follows, with full comment/review text)
```

### 3. Continuous monitoring via Claude Code cron

The simplest hands-off setup is a recurring Claude Code cron job that calls `adaptive_monitor.py`. The script itself decides whether to run or skip based on its internal clock.

```bash
# From Claude Code, create a durable recurring job
cron "* * * * *" true \
  "Run python3 /path/to/scripts/adaptive_monitor.py. \
   If exit code 1, read stdout to get new notifications, \
   then act on them (reply, code changes, etc.)."
```

**Why a fixed cron + adaptive skip instead of a dynamic cron?**
- Claude Code cron does not support dynamic intervals.
- Running `adaptive_monitor.py` every minute and letting it skip is cheap — the script exits in <50 ms when nothing to do.
- When activity spikes, the script resets its internal interval to 30 s, so consecutive cron triggers will actually perform checks and report quickly.
- As idle time accumulates, the interval grows exponentially (slowly at first, then faster), and the script starts skipping cron triggers until it reaches the 2 h maximum.

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
| `MIN_INTERVAL` / `MAX_INTERVAL` | `adaptive_monitor.py` | Bounds for adaptive check frequency (default: 30 s / 2 h). |
| `GROWTH_FACTOR` | `adaptive_monitor.py` | Exponential growth per idle check (default: 1.12). Increase for faster decay; decrease for slower decay. |

## How the adaptive interval works

The monitor uses an **idle streak** counter with **exponential growth**:

1. After each check, determine if there were **actionable notifications** (new PR comments, reviews, or issue mentions directed at the developer).
2. Update the idle streak:
   - **Notifications found** → reset `idle_streak = 0` → interval = `MIN_INTERVAL` (30 s)
   - **No notifications** → increment `idle_streak += 1`
3. Compute interval:
   - `interval = MIN_INTERVAL × GROWTH_FACTOR ^ idle_streak`
   - Capped at `MAX_INTERVAL` (2 h)
4. Write `next_check_time = now + interval` to state file.

**Growth progression** (with defaults `MIN=30 s`, `GROWTH_FACTOR=1.12`):

| Idle streak | Interval | Increase from previous |
|-------------|----------|------------------------|
| 0 | 30 s | — |
| 5 | 53 s | +4.6 s/check |
| 10 | 1.6 min | +6.4 s/check |
| 20 | 4.8 min | +17 s/check |
| 30 | 15 min | +45 s/check |
| 40 | 47 min | +2.3 min/check |
| 50 | 2 h (capped) | — |

The decay is intentionally **slow at the beginning** (only ~4.6 s per check for the first 5 checks) and **accelerates** as idle time accumulates. This avoids over-reacting to brief lulls while still backing off efficiently during true idle periods.

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

Use a **low-frequency durable cron** (e.g., every 5–10 min) as a heartbeat. When it fires, run `adaptive_monitor.py` unconditionally. Between cron fires, the developer can manually enter the tmux session and ask for an immediate check.

```bash
# Heartbeat cron (durable, survives reboots if desired)
*/5 * * * *
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
