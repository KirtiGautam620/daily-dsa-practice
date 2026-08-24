"""Spaced-repetition scheduling for the DSA repo.

The whole revision system lives here so that `update_readme.py` (which only
reads) and `revise.py` (which records completions) agree on the maths.

Data model
----------
Solution files stay the source of truth for *what* was solved and *when*.
Revision progress lives in a machine-managed JSON file:

    00-progress/revision-state.json

    {
      "version": 1,
      "problems": {
        "concatenation-of-array": {
          "title":  "Concatenation of Array",
          "path":   "01-arrays/concatenation-of-array.py",
          "solved": "2026-08-23",
          "rung":   1,                 # index of the NEXT revision in GAPS
          "anchor": "2026-08-24",      # date the next gap is measured from
          "history": [
            {"date": "2026-08-24", "scheduled": "2026-08-24",
             "result": "remembered", "rung_from": 0, "rung_to": 1,
             "anchor_from": "2026-08-23"}
          ]
        }
      }
    }

    next due = anchor + GAPS[rung]        (rung == len(GAPS) -> graduated)

Never hand-edit that file — `revise.py` owns it.

The ladder
----------
The schedule people quote is *cumulative* days after the solve:

    1 -> 3 -> 7 -> 15 -> 30 -> 60

Internally we store the same ladder as the *gaps between* consecutive
revisions (1, 2, 4, 8, 15, 30) and measure each gap from the date the
previous revision was actually completed. Stay on schedule and you land
exactly on the classic dates; fall behind and the ladder simply shifts
forward instead of piling up in the past.
"""

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "00-progress" / "revision-state.json"
STATE_VERSION = 1

# The classic spaced-repetition schedule, as days after the first solve.
CUMULATIVE_OFFSETS = (1, 3, 7, 15, 30, 60)

# The same ladder expressed as gaps between consecutive revisions.
GAPS = tuple(
    later - earlier
    for earlier, later in zip((0,) + CUMULATIVE_OFFSETS[:-1], CUMULATIVE_OFFSETS)
)
ROUNDS = len(GAPS)

RESULTS = ("remembered", "partial", "forgot")
DEFAULT_RESULT = "remembered"

RESULT_ICONS = {"remembered": "✅", "partial": "🟡", "forgot": "🔴"}

DATE_FMT = "%Y-%m-%d"
HUMAN_FMT = "%d %b %Y"

INDIA = timezone(timedelta(hours=5, minutes=30), "IST")


# -----------------------------------
# Dates
# -----------------------------------

def today_india():
    """Today in Asia/Kolkata, wherever the script happens to run."""
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo("Asia/Kolkata")).date()
    except Exception:  # no tzdata on this machine — fall back to a fixed offset
        return datetime.now(INDIA).date()


def parse_iso(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, DATE_FMT).date()
    except (TypeError, ValueError):
        return None


def iso(day):
    return day.strftime(DATE_FMT) if day else None


def human(day):
    return day.strftime(HUMAN_FMT) if day else "—"


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")


# -----------------------------------
# State file
# -----------------------------------

def load_state():
    if not STATE_PATH.exists():
        return {"version": STATE_VERSION, "problems": {}}

    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print(f"warning: could not read {STATE_PATH.name} — starting fresh")
        return {"version": STATE_VERSION, "problems": {}}

    state.setdefault("version", STATE_VERSION)
    state.setdefault("problems", {})
    return state


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ordered = {
        "version": STATE_VERSION,
        "problems": {key: state["problems"][key] for key in sorted(state["problems"])},
    }
    STATE_PATH.write_text(
        json.dumps(ordered, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def problem_key(metadata, taken=None):
    """Stable key for a problem: the slug of its title, folder-qualified on clash."""
    key = slugify(metadata.get("Problem")) or slugify(Path(metadata["path"]).stem)
    if taken and key in taken and taken[key] != metadata["path"]:
        key = f"{key}--{metadata.get('folder', 'x')}"
    return key


def sync_state(state, problems):
    """Seed entries for new problems and refresh titles/paths/solve dates.

    Returns True when anything changed. Entries whose solution file has gone
    away are kept (their history is worth keeping) but simply stop being shown.
    """
    changed = False
    problems_by_key = state["problems"]
    taken = {key: entry.get("path") for key, entry in problems_by_key.items()}

    for metadata in problems:
        solved = metadata.get("parsed_date")
        if not solved:
            continue

        key = problem_key(metadata, taken)
        taken[key] = metadata["path"]
        entry = problems_by_key.get(key)

        if entry is None:
            problems_by_key[key] = {
                "title": metadata.get("Problem", key),
                "path": metadata["path"],
                "solved": iso(solved),
                "rung": 0,
                "anchor": iso(solved),
                "history": [],
            }
            changed = True
            continue

        for field, value in (
            ("title", metadata.get("Problem", key)),
            ("path", metadata["path"]),
            ("solved", iso(solved)),
        ):
            if entry.get(field) != value:
                entry[field] = value
                changed = True

        # A corrected Date: in the header should move an untouched schedule too.
        if not entry.get("history") and entry.get("anchor") != iso(solved):
            entry["anchor"] = iso(solved)
            entry["rung"] = 0
            changed = True

    return changed


# -----------------------------------
# Schedule maths
# -----------------------------------

def rung_of(entry):
    try:
        return max(0, min(ROUNDS, int(entry.get("rung", 0))))
    except (TypeError, ValueError):
        return 0


def anchor_of(entry):
    return parse_iso(entry.get("anchor")) or parse_iso(entry.get("solved"))


def is_graduated(entry):
    return rung_of(entry) >= ROUNDS


def next_due(entry):
    """The date of the next uncompleted revision, or None once graduated."""
    if is_graduated(entry):
        return None
    anchor = anchor_of(entry)
    if not anchor:
        return None
    return anchor + timedelta(days=GAPS[rung_of(entry)])


def projected_dates(entry):
    """{rung: date} for every revision still ahead, projected from the anchor."""
    anchor = anchor_of(entry)
    if not anchor or is_graduated(entry):
        return {}

    cursor = anchor
    ahead = {}
    for index in range(rung_of(entry), ROUNDS):
        cursor = cursor + timedelta(days=GAPS[index])
        ahead[index] = cursor
    return ahead


def completed_dates(entry):
    """{rung: date} of revisions already done, keyed by the rung they cleared.

    A lapse (`forgot`) sends the problem back down the ladder, so a rung can be
    cleared more than once — the most recent attempt wins.
    """
    done = {}
    for record in entry.get("history", []):
        when = parse_iso(record.get("date"))
        rung_from = record.get("rung_from")
        if when is None or rung_from is None:
            continue
        done[int(rung_from)] = when
    return done


def lapses(entry):
    return sum(1 for r in entry.get("history", []) if r.get("result") == "forgot")


def record_revision(entry, on, result=DEFAULT_RESULT):
    """Mark the next scheduled revision of `entry` complete on `on`.

    The next gap is always measured from `on` — the date recall actually
    happened — because that is the moment the memory was refreshed.

        remembered -> climb one rung, next gap is the longer one
        partial    -> hold this rung, repeat the same gap
        forgot     -> back to the bottom rung, see it again tomorrow

    Returns the new due date (None once graduated).
    """
    if result not in RESULTS:
        raise ValueError(f"result must be one of {', '.join(RESULTS)}")
    if is_graduated(entry):
        raise ValueError("this problem has already finished its revision cycle")

    rung = rung_of(entry)
    scheduled = next_due(entry)

    if result == "remembered":
        new_rung = rung + 1
    elif result == "partial":
        new_rung = rung
    else:
        new_rung = 0

    entry.setdefault("history", []).append(
        {
            "date": iso(on),
            "scheduled": iso(scheduled),
            "result": result,
            "rung_from": rung,
            "rung_to": new_rung,
            "anchor_from": entry.get("anchor"),
        }
    )
    entry["rung"] = new_rung
    entry["anchor"] = iso(on)

    return next_due(entry)


def undo_revision(entry):
    """Roll back the most recent completion. Returns the record, or None."""
    history = entry.get("history") or []
    if not history:
        return None

    record = history.pop()
    entry["rung"] = int(record.get("rung_from", 0))
    entry["anchor"] = record.get("anchor_from") or entry.get("solved")
    return record


# -----------------------------------
# Views used by the README / tracker
# -----------------------------------

def schedule_rows(state, problems, today):
    """One row per live problem, sorted by urgency then title.

    Returns dicts: key, entry, metadata, due (date|None), overdue_days.
    """
    problems_by_key = state["problems"]
    taken = {key: entry.get("path") for key, entry in problems_by_key.items()}

    rows = []
    for metadata in problems:
        if not metadata.get("parsed_date"):
            continue

        key = problem_key(metadata, taken)
        entry = problems_by_key.get(key)
        if entry is None:
            continue

        due = next_due(entry)
        rows.append(
            {
                "key": key,
                "entry": entry,
                "metadata": metadata,
                "due": due,
                "overdue_days": (today - due).days if due and due < today else 0,
            }
        )

    rows.sort(key=lambda row: (row["due"] or date.max, row["metadata"].get("Problem", "")))
    return rows


def find_rows(rows, query):
    """Match a user-typed problem name against the schedule. Exact wins."""
    wanted = slugify(query)
    if not wanted:
        return []

    def slug_of(row):
        return slugify(row["entry"].get("title") or row["key"])

    for test in (
        lambda s: s == wanted,
        lambda s: s.startswith(wanted),
        lambda s: wanted in s,
    ):
        hits = [row for row in rows if test(slug_of(row))]
        if hits:
            return hits
    return []
