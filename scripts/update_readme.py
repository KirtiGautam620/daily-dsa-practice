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


ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

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

# Spaced-repetition schedule, in days after the first solve.
REVISION_OFFSETS = (1, 3, 7, 15, 30, 60)

RECENT_LIMIT = 10


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

        name = f"[{topic}]({folder}/)" if (ROOT / folder).is_dir() else topic

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


def build_revision(problems, today):
    """Problems whose next spaced-repetition review is due."""
    due = []

    for problem in problems:
        solved = problem["parsed_date"]
        if not solved:
            continue

        elapsed = (today - solved).days
        next_offset = next((o for o in REVISION_OFFSETS if o >= elapsed), None)
        if next_offset is None:
            continue

        due_on = solved.fromordinal(solved.toordinal() + next_offset)
        due.append((due_on, next_offset, problem))

    due.sort(key=lambda item: (item[0], item[2].get("Problem", "")))

    lines = ["<!-- DSA-REVISION:START -->", ""]

    if not due:
        lines += [
            "_Nothing scheduled — every logged problem has finished its revision cycle._",
            "",
            "<!-- DSA-REVISION:END -->",
        ]
        return "\n".join(lines)

    lines += [
        "| Due | Problem | Round | Solution |",
        "|---|---|---|---|",
    ]

    for due_on, offset, problem in due[:RECENT_LIMIT]:
        overdue = due_on < today
        marker = "⚠️ today" if due_on == today else ("⚠️ overdue" if overdue else due_on.strftime("%d %b"))
        lines.append(
            f"| {marker} | {problem.get('Problem', 'Untitled')} | +{offset}d | "
            f"[code]({problem['path']}) |"
        )

    lines += ["", "<!-- DSA-REVISION:END -->"]
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


def main():
    check_only = "--check" in sys.argv
    today = date.today()

    problems = collect_problems()

    sections = {
        "STATS": build_progress(problems, today),
        "TOPICS": build_topics(problems),
        "RECENT": build_recent(problems),
        "REVISION": build_revision(problems, today),
    }

    original = README.read_text(encoding="utf-8")
    updated = original
    for name, block in sections.items():
        updated = replace_section(updated, name, block)

    if updated == original:
        print(f"Found {len(problems)} problems. README already up to date.")
        return 0

    if check_only:
        print("README.md is out of date — run: python scripts/update_readme.py")
        return 1

    README.write_text(updated, encoding="utf-8")
    print(f"Found {len(problems)} problems. Updated README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
