"""Rebuild the progress section of README.md from the solution files.

A solution file lives in a topic folder and is named like `0001-two-sum.py`.
Optional header lines inside the file (any comment style) are picked up:
    Difficulty: Easy | Medium | Hard
    Link: https://leetcode.com/problems/two-sum/
Run from the repo root:  python scripts/update_readme.py
"""

from __future__ import annotations

import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
START, END = "<!-- PROGRESS:START -->", "<!-- PROGRESS:END -->"
NAME = re.compile(r"^(\d+)-([a-z0-9-]+)\.(py|cpp|java|js|ts|go|c)$")
LANGS = {"py": "Python", "cpp": "C++", "java": "Java", "js": "JavaScript",
         "ts": "TypeScript", "go": "Go", "c": "C"}
SKIP = {"scripts", ".github", ".git", ".claude"}


def header(text: str, key: str) -> str:
    m = re.search(rf"{key}\s*:\s*(\S.*)", text, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def first_commit_date(path: Path) -> str:
    """Date the file was first committed (YYYY-MM-DD), or '' if not committed yet."""
    out = subprocess.run(
        ["git", "log", "--diff-filter=A", "--follow", "--format=%as", "--", str(path)],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.split()
    return out[-1] if out else ""


def collect() -> list[dict]:
    rows = []
    for topic in sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name not in SKIP):
        for f in sorted(topic.iterdir()):
            m = NAME.match(f.name)
            if not m:
                continue
            num, slug, ext = m.groups()
            text = f.read_text(encoding="utf-8", errors="ignore")
            difficulty = header(text, "Difficulty").split()[0].capitalize() if header(text, "Difficulty") else ""
            rows.append({
                "num": int(num),
                "title": slug.replace("-", " ").title(),
                "link": header(text, "Link") or f"https://leetcode.com/problems/{slug}/",
                "topic": topic.name,
                "difficulty": difficulty if difficulty in {"Easy", "Medium", "Hard"} else "-",
                "lang": LANGS[ext],
                "path": f.relative_to(ROOT).as_posix(),
                "date": first_commit_date(f),
            })
    return rows


def render(rows: list[dict]) -> str:
    diff = Counter(r["difficulty"] for r in rows)
    topics = Counter(r["topic"] for r in rows)
    lines = [
        f"**Solved: {len(rows)}** · Easy {diff['Easy']} · Medium {diff['Medium']} · Hard {diff['Hard']}",
        "",
    ]
    if not rows:
        lines.append("_Nothing here yet. The first problem is on its way._")
        return "\n".join(lines)
    lines += ["| Topic | Solved |", "|---|---:|"]
    lines += [f"| [{t}]({t}/) | {n} |" for t, n in sorted(topics.items())]
    lines += ["", "| # | Problem | Difficulty | Topic | Solution | Date |",
              "|---:|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["date"] or "9999", r["num"]), reverse=True):
        lines.append(
            f"| {r['num']} | [{r['title']}]({r['link']}) | {r['difficulty']} | "
            f"{r['topic']} | [{r['lang']}]({r['path']}) | {r['date']} |"
        )
    return "\n".join(lines)


def main() -> None:
    text = README.read_text(encoding="utf-8")
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    README.write_text(f"{before}{START}\n{render(collect())}\n{END}{after}", encoding="utf-8")


if __name__ == "__main__":
    main()
