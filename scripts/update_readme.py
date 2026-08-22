from pathlib import Path
import re
from collections import Counter


ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"


# Map folder names to README topic names
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
}


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


# -----------------------------------
# Find all problems
# -----------------------------------

problems = []

for file_path in ROOT.rglob("*.py"):

    # Ignore automation scripts
    if "scripts" in file_path.parts:
        continue

    metadata = parse_problem(file_path)

    if "Problem" in metadata:
        metadata["folder"] = file_path.parent.name
        problems.append(metadata)


# -----------------------------------
# Overall statistics
# -----------------------------------

total = len(problems)

difficulty = Counter(
    problem.get("Difficulty", "Unknown")
    for problem in problems
)

status = Counter(
    problem.get("Status", "Unknown")
    for problem in problems
)


# -----------------------------------
# Topic statistics
# -----------------------------------

topic_counts = Counter()

for problem in problems:
    folder = problem.get("folder")

    if folder in TOPICS:
        topic_counts[TOPICS[folder]] += 1


def topic_status(count):
    if count == 0:
        return "🔴"
    elif count < 5:
        return "🟡"
    else:
        return "🟢"


# -----------------------------------
# Generate Progress section
# -----------------------------------

progress = f"""<!-- DSA-STATS:START -->

## 📊 Progress

| Metric | Progress |
|---|---:|
| Problems Solved | {total} |
| Easy | {difficulty.get("Easy", 0)} |
| Medium | {difficulty.get("Medium", 0)} |
| Hard | {difficulty.get("Hard", 0)} |
| Independent | {status.get("Independent", 0)} |
| Hint Needed | {status.get("Hint", 0)} |
| Solution Needed | {status.get("Solution", 0)} |

<!-- DSA-STATS:END -->"""


# -----------------------------------
# Generate Topics section
# -----------------------------------

topics = """<!-- DSA-TOPICS:START -->

## 🧠 Topics

| Topic | Problems | Status |
|---|---:|---|
"""

for folder, topic in TOPICS.items():
    count = topic_counts.get(topic, 0)
    topics += f"| {topic} | {count} | {topic_status(count)} |\n"

topics += """
<!-- DSA-TOPICS:END -->"""


# -----------------------------------
# Update README
# -----------------------------------

readme = README.read_text(encoding="utf-8")


def replace_section(text, start_marker, end_marker, replacement):

    pattern = re.compile(
        re.escape(start_marker)
        + r".*?"
        + re.escape(end_marker),
        re.DOTALL,
    )

    if pattern.search(text):
        return pattern.sub(replacement, text)

    return text + "\n\n" + replacement


readme = replace_section(
    readme,
    "<!-- DSA-STATS:START -->",
    "<!-- DSA-STATS:END -->",
    progress,
)

readme = replace_section(
    readme,
    "<!-- DSA-TOPICS:START -->",
    "<!-- DSA-TOPICS:END -->",
    topics,
)


README.write_text(readme, encoding="utf-8")

print(f"Found {total} problems.")
print("Updated progress statistics.")
print("Updated topic statistics.")