from pathlib import Path
import re
from collections import Counter


ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"


def parse_problem(file_path):
    text = file_path.read_text(encoding="utf-8")

    metadata = {}

    fields = [
        "Problem",
        "LeetCode",
        "Difficulty",
        "Pattern",
        "Status",
        "Date",
    ]

    for field in fields:
        match = re.search(
            rf"^\s*{field}\s*:\s*(.+?)\s*$",
            text,
            re.MULTILINE,
        )

        if match:
            metadata[field] = match.group(1).strip()

    return metadata


problems = []

for file_path in ROOT.rglob("*.py"):
    # Don't scan the automation script itself
    if "scripts" in file_path.parts:
        continue

    metadata = parse_problem(file_path)

    if "Problem" in metadata:
        problems.append(metadata)


# -----------------------------
# Statistics
# -----------------------------

total = len(problems)

difficulty = Counter(
    problem.get("Difficulty", "Unknown")
    for problem in problems
)

status = Counter(
    problem.get("Status", "Unknown")
    for problem in problems
)

patterns = Counter(
    problem.get("Pattern", "Unknown")
    for problem in problems
)


def progress_row(name, count):
    return f"| {name} | {count} |"


stats = f"""<!-- DSA-STATS:START -->

## 📊 DSA Progress

| Metric | Count |
|---|---:|
| 🧩 Total Problems | {total} |
| 🟢 Independent | {status.get("Independent", 0)} |
| 🟡 Hint Needed | {status.get("Hint", 0)} |
| 🔴 Solution Needed | {status.get("Solution", 0)} |
| 🟢 Easy | {difficulty.get("Easy", 0)} |
| 🟡 Medium | {difficulty.get("Medium", 0)} |
| 🔴 Hard | {difficulty.get("Hard", 0)} |

### 🧠 Patterns

| Pattern | Problems |
|---|---:|
"""

for pattern, count in patterns.most_common():
    stats += progress_row(pattern, count)

stats += """
<!-- DSA-STATS:END -->
"""


# -----------------------------
# Update README
# -----------------------------

readme = README.read_text(encoding="utf-8")

start_marker = "<!-- DSA-STATS:START -->"
end_marker = "<!-- DSA-STATS:END -->"

pattern = re.compile(
    re.escape(start_marker) + r".*?" + re.escape(end_marker),
    re.DOTALL,
)

if pattern.search(readme):
    readme = pattern.sub(stats.strip(), readme)
else:
    readme += "\n\n" + stats

README.write_text(readme, encoding="utf-8")

print(f"Updated README with {total} problems.")