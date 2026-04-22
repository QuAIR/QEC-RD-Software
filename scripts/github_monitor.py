#!/usr/bin/env python3
"""
GitHub monitor for QuAIR/QEC-RD-Software.
Tracks PRs and issues for mentions/comments directed at LeiZhang-116-4.
"""
import json
import subprocess
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

REPO = "QuAIR/QEC-RD-Software"
MY_USERNAME = "LeiZhang-116-4"
TARGET_MENTION = "lei-zhang-116.4"
STATE_FILE = Path(__file__).parent / ".monitor_state.json"
CUTOFF_DATE = datetime(2026, 4, 26, 23, 59, 59, tzinfo=timezone.utc)


def run_gh(args: list[str]) -> dict | list:
    cmd = ["gh"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"gh error: {result.stderr}", file=sys.stderr)
        return {}
    return json.loads(result.stdout) if result.stdout.strip() else {}


def run_gh_api(endpoint: str) -> dict | list:
    return run_gh(["api", f"repos/{REPO}/{endpoint}"])


def load_state() -> dict:
    defaults = {"processed_comments": [], "processed_reviews": [], "processed_issue_bodies": [], "last_check": None}
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            state = json.load(f)
        for key, val in defaults.items():
            if key not in state:
                state[key] = val
        return state
    return defaults


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_my_open_prs() -> list[dict]:
    prs = run_gh([
        "pr", "list", "--repo", REPO,
        "--author", MY_USERNAME,
        "--state", "open",
        "--json", "number,title,url,createdAt,headRefName"
    ])
    return prs if isinstance(prs, list) else []


def get_open_issues() -> list[dict]:
    issues = run_gh([
        "issue", "list", "--repo", REPO,
        "--state", "open",
        "--json", "number,title,url,createdAt,author,body"
    ])
    return issues if isinstance(issues, list) else []


def get_pr_issue_comments(pr_number: int) -> list[dict]:
    """Get issue-like comments on a PR."""
    comments = run_gh([
        "pr", "view", str(pr_number), "--repo", REPO,
        "--json", "comments"
    ])
    if isinstance(comments, dict):
        return comments.get("comments", [])
    return []


def get_pr_review_comments(pr_number: int) -> list[dict]:
    """Get review comments (line-level) on a PR."""
    return run_gh_api(f"pulls/{pr_number}/comments") or []


def get_pr_reviews(pr_number: int) -> list[dict]:
    """Get PR reviews (APPROVE/REQUEST_CHANGES/COMMENT)."""
    return run_gh_api(f"pulls/{pr_number}/reviews") or []


def get_issue_comments(issue_number: int) -> list[dict]:
    comments = run_gh([
        "issue", "view", str(issue_number), "--repo", REPO,
        "--json", "comments"
    ])
    if isinstance(comments, dict):
        return comments.get("comments", [])
    return []


def check_mentions(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    return (f"@{TARGET_MENTION}" in text_lower or
            f"@{MY_USERNAME.lower()}" in text_lower)


def make_id(prefix: str, number: int, item: dict) -> str:
    """Create a unique ID for a comment/review item."""
    item_id = item.get("id") or item.get("node_id") or item.get("createdAt") or item.get("created_at") or "unknown"
    return f"{prefix}-{number}-{item_id}"


def format_notification(item: dict, comment: dict, item_type: str, subtype: str = "") -> str:
    author = "unknown"
    if "author" in comment:
        author = comment["author"].get("login", "unknown")
    elif "user" in comment:
        author = comment["user"].get("login", "unknown")

    created = comment.get("createdAt") or comment.get("created_at") or "unknown"
    body = comment.get("body", "")

    subtype_str = f" ({subtype})" if subtype else ""

    return f"""
{'='*70}
{item_type} #{item['number']}{subtype_str}: {item['title']}
Author: {author} | Created: {created}
URL: {item['url']}

{body}
{'='*70}
"""


def main():
    now_dt = datetime.now(timezone.utc)
    now = now_dt.isoformat()

    # Check if monitoring period has expired
    if now_dt > CUTOFF_DATE:
        print(f"[{now}] MONITORING PERIOD EXPIRED (cutoff: {CUTOFF_DATE.isoformat()})")
        print("Please delete the cron job to stop automatic checks.")
        return 2  # Exit code 2 = monitoring expired

    state = load_state()

    print(f"[{now}] GitHub Monitor Check")
    print(f"Repo: {REPO} | User: {MY_USERNAME}")
    print(f"Monitoring until: {CUTOFF_DATE.isoformat()}")
    print("-" * 50)

    new_notifications = []

    # === Check PRs ===
    my_prs = get_my_open_prs()
    print(f"Open PRs by {MY_USERNAME}: {len(my_prs)}")

    for pr in my_prs:
        pr_num = pr["number"]

        # 1. Issue-like comments on PR
        for comment in get_pr_issue_comments(pr_num):
            cid = make_id("pr-comment", pr_num, comment)
            if cid not in state["processed_comments"]:
                state["processed_comments"].append(cid)
                new_notifications.append(format_notification(pr, comment, "PR", "comment"))

        # 2. Review comments (line-level)
        for comment in get_pr_review_comments(pr_num):
            cid = make_id("pr-review-comment", pr_num, comment)
            if cid not in state["processed_reviews"]:
                state["processed_reviews"].append(cid)
                new_notifications.append(format_notification(pr, comment, "PR", "review comment"))

        # 3. PR reviews (body of the review)
        for review in get_pr_reviews(pr_num):
            rid = make_id("pr-review", pr_num, review)
            if rid not in state["processed_reviews"]:
                state["processed_reviews"].append(rid)
                body = review.get("body", "")
                if body and body.strip():
                    new_notifications.append(format_notification(pr, review, "PR", f"review ({review.get('state', 'unknown')})"))

    # === Check Issues for mentions ===
    open_issues = get_open_issues()
    print(f"Open issues: {len(open_issues)}")

    for issue in open_issues:
        issue_num = issue["number"]

        # Check issue body for mentions
        issue_body = issue.get("body", "")
        bid = f"issue-body-{issue_num}"
        if bid not in state["processed_issue_bodies"]:
            state["processed_issue_bodies"].append(bid)
            if check_mentions(issue_body):
                new_notifications.append(format_notification(issue, {"body": issue_body, "author": issue.get("author", {}), "createdAt": issue.get("createdAt")}, "Issue", "body mention"))

        for comment in get_issue_comments(issue_num):
            body = comment.get("body", "")
            cid = make_id("issue-comment", issue_num, comment)

            # Track all issue comments, but only flag mentions
            if cid not in state["processed_comments"]:
                state["processed_comments"].append(cid)
                if check_mentions(body):
                    new_notifications.append(format_notification(issue, comment, "Issue", "mention"))

    state["last_check"] = now
    save_state(state)

    if new_notifications:
        print(f"\n{'='*70}")
        print(f"ACTION REQUIRED: {len(new_notifications)} new notification(s)")
        print(f"{'='*70}")
        for i, notif in enumerate(new_notifications, 1):
            print(f"\n--- Notification {i}/{len(new_notifications)} ---")
            print(notif)
        return 1
    else:
        print(f"[{now}] All clear. No new notifications.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
