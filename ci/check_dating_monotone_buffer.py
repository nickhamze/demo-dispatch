#!/usr/bin/env python3
"""
Date-buffer monotonicity guard.

Asserts that the gap between the newest Sandbox post and the oldest non-Sandbox
post is at least 30 days. This is the safety margin so that a single
date-correction does not collapse the buffer that keeps Sandbox below page 2.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_sandbox_below_fold import parse_posts  # noqa: E402

MIN_GAP_DAYS = 30


def parse_date(s: str) -> datetime:
    return datetime.fromisoformat(s.split(".")[0].replace(" ", "T"))


def main() -> int:
    posts = parse_posts()
    visible = [p for p in posts if p.get("status") not in ("draft", "future")]

    sandbox = [p for p in visible if p.get("category") == "sandbox"]
    others = [p for p in visible if p.get("category") != "sandbox"]
    if not sandbox or not others:
        print("  WARN  not enough posts to compute buffer")
        return 0

    newest_sandbox = max(sandbox, key=lambda p: parse_date(p["date"]))
    oldest_other = min(others, key=lambda p: parse_date(p["date"]))

    gap_days = (parse_date(oldest_other["date"]) - parse_date(newest_sandbox["date"])).days
    print(
        f"newest sandbox: {newest_sandbox['slug']} ({newest_sandbox['date']}); "
        f"oldest non-sandbox: {oldest_other['slug']} ({oldest_other['date']}); "
        f"gap: {gap_days} days"
    )
    if gap_days < MIN_GAP_DAYS:
        print(f"  FAIL  buffer is {gap_days} days, need >= {MIN_GAP_DAYS}")
        return 1
    print("  OK    dating buffer monotone")
    return 0


if __name__ == "__main__":
    sys.exit(main())
