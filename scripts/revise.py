"""Mark a revision complete. The schedule takes care of itself.

    python scripts/revise.py                          # what's due right now
    python scripts/revise.py "Two Sum"                # revised it, remembered it
    python scripts/revise.py two-sum                  # partial names are fine
    python scripts/revise.py "Two Sum" -r partial     # shaky — repeat this gap
    python scripts/revise.py "Two Sum" -r forgot      # blanked — back to +1 day
    python scripts/revise.py --all                    # everything overdue + due today
    python scripts/revise.py "Two Sum" --on 2026-08-23  # backfill a past revision
    python scripts/revise.py "Two Sum" --undo         # take back the last entry

Every run rewrites README.md and 00-progress/revision-tracker.md, so a single
command is all that is needed before committing.
"""

import argparse
import sys

import revision as rev
import update_readme


RESULT_BLURB = {
    "remembered": "next gap is the longer one",
    "partial": "same gap again",
    "forgot": "back to the bottom of the ladder",
}


def status_of(row, today):
    if row["due"] is None:
        return "🎓 graduated"
    if row["overdue_days"]:
        return f"⚠️ {rev.human(row['due'])} ({row['overdue_days']}d overdue)"
    if row["due"] == today:
        return f"🔴 {rev.human(row['due'])} (today)"
    return f"⏳ {rev.human(row['due'])}"


def show_due(rows, today):
    pending = [r for r in rows if r["due"] and r["due"] <= today]
    if not pending:
        upcoming = [r for r in rows if r["due"] and r["due"] > today]
        print("Nothing due today. 🎉")
        if upcoming:
            nxt = min(r["due"] for r in upcoming)
            count = sum(1 for r in upcoming if r["due"] == nxt)
            print(f"Next up: {rev.human(nxt)} ({count} problem(s)).")
        return

    print(f"Due as of {rev.human(today)} (IST):\n")
    width = max(len(r["entry"]["title"]) for r in pending)
    for row in pending:
        rung = rev.rung_of(row["entry"])
        print(
            f"  {row['entry']['title']:<{width}}  "
            f"R{rung + 1}/{rev.ROUNDS}  {status_of(row, today)}"
        )
    print('\nMark one done:  python scripts/revise.py "<problem>"')
    print("Mark all done:  python scripts/revise.py --all")


def regenerate():
    update_readme.main()


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="revise.py",
        description="Mark spaced-repetition revisions complete.",
    )
    parser.add_argument("problem", nargs="*", help="problem name (partial is fine)")
    parser.add_argument(
        "-r",
        "--result",
        choices=rev.RESULTS,
        default=rev.DEFAULT_RESULT,
        help="how it went (default: remembered)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="mark_all",
        help="mark every overdue and due-today revision complete",
    )
    parser.add_argument(
        "--on",
        metavar="YYYY-MM-DD",
        help="date the revision happened (default: today, IST)",
    )
    parser.add_argument("--undo", action="store_true", help="undo the last revision")
    parser.add_argument("--list", action="store_true", help="show every problem")
    args = parser.parse_args(argv)

    today = rev.today_india()
    on = rev.parse_iso(args.on) if args.on else today
    if args.on and on is None:
        parser.error(f"--on must look like YYYY-MM-DD, got {args.on!r}")

    problems = update_readme.collect_problems()
    state = rev.load_state()
    rev.sync_state(state, problems)
    rows = rev.schedule_rows(state, problems, today)

    if args.list:
        for row in rows:
            print(f"  {row['entry']['title']}  —  {status_of(row, today)}")
        return 0

    query = " ".join(args.problem).strip()

    if not query and not args.mark_all:
        show_due(rows, today)
        return 0

    if args.mark_all:
        targets = [r for r in rows if r["due"] and r["due"] <= today]
        if not targets:
            print("Nothing due today. 🎉")
            return 0
    else:
        targets = rev.find_rows(rows, query)
        if not targets:
            print(f"No problem matching {query!r}.")
            print("Try:  python scripts/revise.py --list")
            return 1
        if len(targets) > 1:
            print(f"{query!r} matches {len(targets)} problems — be more specific:")
            for row in targets:
                print(f"  {row['entry']['title']}")
            return 1

    for row in targets:
        entry = row["entry"]
        title = entry["title"]

        if args.undo:
            record = rev.undo_revision(entry)
            if record is None:
                print(f"{title}: no revision to undo.")
                continue
            print(
                f"↩️  {title}: undid the {rev.human(rev.parse_iso(record['date']))} "
                f"revision. Next due {rev.human(rev.next_due(entry))}."
            )
            continue

        if rev.is_graduated(entry):
            print(f"🎓 {title} has already finished its revision cycle — skipped.")
            continue

        scheduled = row["due"]
        following = rev.record_revision(entry, on, args.result)
        rung = rev.rung_of(entry)

        note = ""
        if scheduled and on > scheduled:
            note = f" (was due {rev.human(scheduled)} — rescheduled from today)"
        elif scheduled and on < scheduled:
            note = f" (early — was due {rev.human(scheduled)})"

        icon = rev.RESULT_ICONS[args.result]
        if following is None:
            print(f"{icon} {title}: revision {rung}/{rev.ROUNDS} done — graduated 🎓{note}")
        else:
            print(
                f"{icon} {title}: {args.result} "
                f"({RESULT_BLURB[args.result]}) → next revision "
                f"{rev.human(following)} · round {rung + 1}/{rev.ROUNDS}{note}"
            )

    rev.save_state(state)
    regenerate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
