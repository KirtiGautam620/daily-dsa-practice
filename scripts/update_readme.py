"""Generate the progress, topics and recent-activity sections of README.md.

Every solution file carries a small metadata header, e.g.

    '''
    Problem: Concatenation of Array
    LeetCode: #1929
    Difficulty: Easy
    Pattern: Array
    Status: Independent
    Date: 2026-08-23
    '''

This script reads those headers and rewrites the marked blocks in README.md.

Usage:
    python scripts/update_readme.py            # rewrite README.md
    python scripts/update_readme.py --check     # exit 1 if README is stale
"""

from pathlib import Path
from collections import Counter, defaultdict
from datetime import date, datetime
import re
import sys

import revision as rev


ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
TRACKER = ROOT / "00-progress" / "revision-tracker.md"

# Only Python solutions are picked up.
SOURCE_SUFFIX = ".py"

# Directories that never contain solutions.
SKIP_DIRS = {"scripts", "00-progress", ".git", ".github", "__pycache__", ".venv"}

# Folder name -> README topic name. Order defines the table order.
TOPICS = {
    "01-arrays": "Arrays",
    "02-strings": "Strings",
    "03-hashing": "Hashing",
    "04-two-pointers": "Two Pointers",
    "05-sliding-window": "Sliding Window",
    "06-stack": "Stack",
    "07-binary-search": "Binary Search",
    "08-linked-list": "Linked List",
    "09-trees": "Trees",
    "10-heap": "Heap",
    "11-recursion-backtracking": "Recursion / Backtracking",
    "12-trie": "Trie",
    "13-graphs": "Graphs",
    "14-greedy": "Greedy",
    "15-dynamic-programming": "Dynamic Programming",
    "contests": "Contests",
}

FIELDS = ("Problem", "LeetCode", "Link", "Difficulty", "Pattern", "Status", "Date")

STATUS_ICONS = {
    "Independent": "🟢",
    "Hint": "🟡",
    "Solution": "🔴",
}

DIFFICULTY_ICONS = {
    "Easy": "🟩",
    "Medium": "🟨",
    "Hard": "🟥",
}

RECENT_LIMIT = 10

# The README revision block is a dashboard, not a database: it must stay a
# constant size whether 4 or 500+ problems are logged. Per-problem schedules
# and full history live in 00-progress/revision-tracker.md instead.
DUE_LIMIT = 15        # rows in "Due Today" before spilling to the tracker
OVERDUE_LIMIT = 15    # rows in "Overdue" before spilling to the tracker
UPCOMING_DAYS = 8     # calendar days listed in "Upcoming"

# Short dates keep the dashboard narrow; the tracker carries full dates.
DASH_DATE = "%d %b"


# -----------------------------------
# Parsing
# -----------------------------------

def parse_problem(file_path):
    """Extract the metadata header from a solution file."""
    try:
        text = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return {}

    # Only the top of the file is a header; stop before the code starts.
    head = "\n".join(text.splitlines()[:40])

    metadata = {}
    for field in FIELDS:
        match = re.search(rf"^\W*{field}\s*:\s*(.+?)\s*$", head, re.MULTILINE)
        if match:
            metadata[field] = match.group(1).strip()

    return metadata


def parse_date(value):
    """Accept 2026-08-23, 23-08-2026 or 23 Aug 2026; return a date or None."""
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def problem_link(metadata):
    """Prefer an explicit Link:, otherwise build a LeetCode URL from the title."""
    if metadata.get("Link"):
        return metadata["Link"]

    title = metadata.get("Problem", "")
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not slug:
        return ""
    return f"https://leetcode.com/problems/{slug}/"


def collect_problems():
    problems = []

    for file_path in sorted(ROOT.rglob(f"*{SOURCE_SUFFIX}")):
        if not file_path.is_file():
            continue
        if SKIP_DIRS & set(file_path.parts):
            continue

        metadata = parse_problem(file_path)
        if "Problem" not in metadata:
            continue

        metadata["folder"] = file_path.parent.name
        metadata["path"] = file_path.relative_to(ROOT).as_posix()
        metadata["parsed_date"] = parse_date(metadata.get("Date"))
        problems.append(metadata)

    return problems


# -----------------------------------
# Small helpers
# -----------------------------------

def percent(part, whole):
    return f"{(100 * part / whole):.0f}%" if whole else "0%"


def bar(part, whole, width=10):
    filled = round(width * part / whole) if whole else 0
    return "█" * filled + "░" * (width - filled)


def topic_health(count):
    if count == 0:
        return "🔴 Not started"
    if count < 5:
        return "🟡 In progress"
    if count < 15:
        return "🟢 Comfortable"
    return "💪 Strong"


def solved_dates(problems):
    return sorted({p["parsed_date"] for p in problems if p["parsed_date"]})


def current_streak(dates, today):
    """Consecutive days of practice ending today or yesterday."""
    if not dates:
        return 0

    day_set = set(dates)
    cursor = today
    if cursor not in day_set:
        cursor = today.fromordinal(today.toordinal() - 1)
        if cursor not in day_set:
            return 0

    streak = 0
    while cursor in day_set:
        streak += 1
        cursor = cursor.fromordinal(cursor.toordinal() - 1)
    return streak


def longest_streak(dates):
    best = run = 0
    previous = None
    for day in dates:
        run = run + 1 if previous and (day - previous).days == 1 else 1
        best = max(best, run)
        previous = day
    return best


# -----------------------------------
# Section builders
# -----------------------------------

def build_progress(problems, today):
    total = len(problems)
    difficulty = Counter(p.get("Difficulty", "Unknown") for p in problems)
    status = Counter(p.get("Status", "Unknown") for p in problems)

    dates = solved_dates(problems)
    active_days = len(dates)
    started = dates[0].strftime("%d %b %Y") if dates else "—"

    lines = [
        "<!-- DSA-STATS:START -->",
        "",
        f"**{total}** {'problem' if total == 1 else 'problems'} solved across "
        f"**{active_days}** active {'day' if active_days == 1 else 'days'} "
        f"· 🔥 **{current_streak(dates, today)}-day streak** "
        f"(best: {longest_streak(dates)}) · started {started}",
        "",
        "| Difficulty | Solved | Share | |",
        "|---|---:|---:|---|",
    ]

    for level in ("Easy", "Medium", "Hard"):
        count = difficulty.get(level, 0)
        lines.append(
            f"| {DIFFICULTY_ICONS[level]} {level} | {count} | "
            f"{percent(count, total)} | `{bar(count, total)}` |"
        )
    lines.append(f"| **Total** | **{total}** | | |")

    lines += [
        "",
        "| How it was solved | Count | Share |",
        "|---|---:|---:|",
    ]
    for label in ("Independent", "Hint", "Solution"):
        count = status.get(label, 0)
        lines.append(
            f"| {STATUS_ICONS[label]} {label} | {count} | {percent(count, total)} |"
        )

    lines += [
        "",
        f"_Last updated: {today.strftime('%d %b %Y')}_",
        "",
        "<!-- DSA-STATS:END -->",
    ]
    return "\n".join(lines)


def build_topics(problems):
    by_topic = defaultdict(list)
    for problem in problems:
        folder = problem.get("folder")
        if folder in TOPICS:
            by_topic[folder].append(problem)

    lines = [
        "<!-- DSA-TOPICS:START -->",
        "",
        "| Topic | Solved | Easy | Med | Hard | Last solved | Status |",
        "|---|---:|---:|---:|---:|---|---|",
    ]

    for folder, topic in TOPICS.items():
        items = by_topic.get(folder, [])
        count = len(items)
        difficulty = Counter(p.get("Difficulty") for p in items)

        dates = [p["parsed_date"] for p in items if p["parsed_date"]]
        last = max(dates).strftime("%d %b") if dates else "—"

        # Link only once a folder holds something: empty directories aren't
        # tracked by git, so linking on existence alone makes the table flip
        # back and forth between local runs and the Actions runner.
        name = f"[{topic}]({folder}/)" if count else topic

        lines.append(
            f"| {name} | {count} | {difficulty.get('Easy', 0)} | "
            f"{difficulty.get('Medium', 0)} | {difficulty.get('Hard', 0)} | "
            f"{last} | {topic_health(count)} |"
        )

    lines += ["", "<!-- DSA-TOPICS:END -->"]
    return "\n".join(lines)


def build_recent(problems):
    ordered = sorted(
        problems,
        key=lambda p: (p["parsed_date"] or date.min, p.get("Problem", "")),
        reverse=True,
    )[:RECENT_LIMIT]

    lines = [
        "<!-- DSA-RECENT:START -->",
        "",
    ]

    if not ordered:
        lines += ["_No problems logged yet._", "", "<!-- DSA-RECENT:END -->"]
        return "\n".join(lines)

    lines += [
        "| Date | Problem | Difficulty | Pattern | Result | Solution |",
        "|---|---|---|---|:---:|---|",
    ]

    for problem in ordered:
        when = problem["parsed_date"].strftime("%d %b") if problem["parsed_date"] else "—"
        title = problem.get("Problem", "Untitled")
        link = problem_link(problem)
        titled = f"[{title}]({link})" if link else title
        status = problem.get("Status", "")

        lines.append(
            f"| {when} | {titled} | {problem.get('Difficulty', '—')} | "
            f"{problem.get('Pattern', '—')} | {STATUS_ICONS.get(status, '⚪')} | "
            f"[code]({problem['path']}) |"
        )

    lines += ["", "<!-- DSA-RECENT:END -->"]
    return "\n".join(lines)


def topic_of(metadata):
    return metadata.get("Pattern") or TOPICS.get(metadata.get("folder"), "—")


def days_label(count):
    return "1 day" if count == 1 else f"{count} days"


def build_revision(rows, today):
    """A fixed-size dashboard: what to revise today, what slipped, what's next.

    Deliberately shallow — no per-problem ladders, no history, capped row
    counts. Everything deeper belongs in 00-progress/revision-tracker.md.
    """
    overdue = [row for row in rows if row["overdue_days"] > 0]
    due_today = [row for row in rows if row["due"] == today]
    upcoming = [row for row in rows if row["due"] and row["due"] > today]

    lines = ["<!-- DSA-REVISION:START -->", ""]

    if not rows:
        lines += ["_Nothing logged yet._", "", "<!-- DSA-REVISION:END -->"]
        return "\n".join(lines)

    if due_today:
        lines += [
            f"### 🔴 Due Today · {len(due_today)}",
            "",
            "| Problem | Topic | Revision |",
            "|---|---|---|",
        ]
        for row in due_today[:DUE_LIMIT]:
            lines.append(
                f"| {row['entry']['title']} | {topic_of(row['metadata'])} | "
                f"{row['due'].strftime(DASH_DATE)} |"
            )
        hidden = len(due_today) - DUE_LIMIT
        if hidden > 0:
            lines.append(f"| _+{hidden} more — `python scripts/revise.py`_ | | |")
        lines.append("")

    if overdue:
        lines += [
            f"### ⚠️ Overdue · {len(overdue)}",
            "",
            "| Problem | Due | Overdue |",
            "|---|---|---:|",
        ]
        # Most overdue first — those are the ones actually at risk.
        for row in sorted(overdue, key=lambda r: -r["overdue_days"])[:OVERDUE_LIMIT]:
            lines.append(
                f"| {row['entry']['title']} | {row['due'].strftime(DASH_DATE)} | "
                f"{days_label(row['overdue_days'])} |"
            )
        hidden = len(overdue) - OVERDUE_LIMIT
        if hidden > 0:
            lines.append(f"| _+{hidden} more — `python scripts/revise.py`_ | | |")
        lines.append("")

    if not overdue and not due_today:
        lines += ["### ✅ Nothing due today", "", "All caught up.", ""]

    if upcoming:
        by_day = Counter(row["due"] for row in upcoming)
        days = sorted(by_day)

        lines += ["### ⏳ Upcoming", "", "| Date | Problems |", "|---|---:|"]
        for day in days[:UPCOMING_DAYS]:
            lines.append(f"| {day.strftime(DASH_DATE)} | {by_day[day]} |")

        later = days[UPCOMING_DAYS:]
        if later:
            beyond = sum(by_day[day] for day in later)
            lines.append(f"| _later_ | {beyond} |")
        lines.append("")

    lines += [
        f"_{rev.human(today)} (IST) · "
        "mark done: `python scripts/revise.py \"<problem>\"` · "
        "full schedule: [revision-tracker.md](00-progress/revision-tracker.md)_",
        "",
        "<!-- DSA-REVISION:END -->",
    ]
    return "\n".join(lines)


def build_tracker(rows, today):
    """The per-problem ✅/⬜ ladder written to 00-progress/revision-tracker.md."""
    header = " | ".join(f"R{i + 1}" for i in range(rev.ROUNDS))

    lines = [
        "<!-- DSA-TRACKER:START -->",
        "",
        f"_Generated by [`scripts/update_readme.py`](../scripts/update_readme.py) · "
        f"{rev.human(today)} (IST). Do not hand-edit — "
        f"use `python scripts/revise.py \"<problem>\"`._",
        "",
        "Ladder: **"
        + " → ".join(str(o) for o in rev.CUMULATIVE_OFFSETS)
        + " days** after the solve, each gap measured from the revision you "
        "actually completed. ✅ done · ⬜ next up · ⚠️ next up but overdue · "
        "· not yet scheduled.",
        "",
        f"| Problem | Solved | Done | {header} | Next due |",
        "|---|---|:---:|" + "---|" * rev.ROUNDS + "---|",
    ]

    if not rows:
        lines = lines[:-2] + ["_No problems logged yet._", ""]
    else:
        for row in rows:
            entry = row["entry"]
            rung = rev.rung_of(entry)
            done = rev.completed_dates(entry)
            ahead = rev.projected_dates(entry)

            cells = []
            for index in range(rev.ROUNDS):
                if index < rung and index in done:
                    cells.append(f"✅ {done[index].strftime('%d %b')}")
                elif index == rung:
                    icon = "⚠️" if row["overdue_days"] else "⬜"
                    cells.append(f"{icon} {ahead[index].strftime('%d %b')}")
                elif index in ahead:
                    cells.append(f"· {ahead[index].strftime('%d %b')}")
                else:
                    cells.append("✅")

            if row["due"] is None:
                next_cell = "🎓 graduated"
            elif row["overdue_days"]:
                next_cell = f"⚠️ {rev.human(row['due'])} ({row['overdue_days']}d late)"
            elif row["due"] == today:
                next_cell = f"🔴 {rev.human(row['due'])} (today)"
            else:
                next_cell = rev.human(row["due"])

            lines.append(
                f"| [{entry['title']}](../{row['metadata']['path']}) | "
                f"{rev.human(rev.parse_iso(entry.get('solved')))} | "
                f"{min(rung, rev.ROUNDS)}/{rev.ROUNDS} | "
                + " | ".join(cells)
                + f" | {next_cell} |"
            )
        lines.append("")

    log = []
    for row in rows:
        for record in row["entry"].get("history", []):
            when = rev.parse_iso(record.get("date"))
            if when:
                log.append((when, row["entry"]["title"], record))
    log.sort(key=lambda item: (item[0], item[1]), reverse=True)

    if log:
        lines += [
            "### 📝 Revision log",
            "",
            "| Revised on | Problem | Was scheduled | Result | Round |",
            "|---|---|---|:---:|:---:|",
        ]
        for when, title, record in log[:40]:
            result = record.get("result", "—")
            icon = rev.RESULT_ICONS.get(result, "⚪")
            scheduled = rev.human(rev.parse_iso(record.get("scheduled")))
            rung_from = record.get("rung_from", 0)
            lines.append(
                f"| {rev.human(when)} | {title} | {scheduled} | "
                f"{icon} {result} | R{int(rung_from) + 1} |"
            )
        lines.append("")

    lines.append("<!-- DSA-TRACKER:END -->")
    return "\n".join(lines)


# -----------------------------------
# README rewriting
# -----------------------------------

def replace_section(text, name, replacement):
    start = f"<!-- DSA-{name}:START -->"
    end = f"<!-- DSA-{name}:END -->"

    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)

    if pattern.search(text):
        return pattern.sub(lambda _: replacement, text)

    print(f"warning: markers for {name} not found in README.md — skipped")
    return text


TRACKER_HEADER = "# 🔁 Revision Tracker\n\n<!-- DSA-TRACKER:START -->\n<!-- DSA-TRACKER:END -->\n"


def main():
    check_only = "--check" in sys.argv
    today = rev.today_india()

    problems = collect_problems()

    # Seed schedules for anything newly logged, then read them back.
    state = rev.load_state()
    state_changed = rev.sync_state(state, problems)
    rows = rev.schedule_rows(state, problems, today)

    sections = {
        "STATS": build_progress(problems, today),
        "TOPICS": build_topics(problems),
        "RECENT": build_recent(problems),
        "REVISION": build_revision(rows, today),
    }

    original = README.read_text(encoding="utf-8")
    updated = original
    for name, block in sections.items():
        updated = replace_section(updated, name, block)

    tracker_original = (
        TRACKER.read_text(encoding="utf-8") if TRACKER.exists() else TRACKER_HEADER
    )
    if "<!-- DSA-TRACKER:START -->" not in tracker_original:
        tracker_original = TRACKER_HEADER
    tracker_updated = replace_section(tracker_original, "TRACKER", build_tracker(rows, today))

    stale = updated != original or tracker_updated != tracker_original or state_changed

    if not stale:
        print(f"Found {len(problems)} problems. Everything already up to date.")
        return 0

    if check_only:
        print("Generated files are out of date — run: python scripts/update_readme.py")
        return 1

    if state_changed:
        rev.save_state(state)
    if updated != original:
        README.write_text(updated, encoding="utf-8")
    if tracker_updated != tracker_original:
        TRACKER.write_text(tracker_updated, encoding="utf-8")

    print(f"Found {len(problems)} problems. Updated README.md and revision-tracker.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
