"""Copy the publishable part of this project into a git clone of the GitHub repo.

The project folder itself is never turned into a git repo (other tools work in it), so
publishing = run this into a separate clone, review `git status`, commit, push.

Usage:  python3 tools/export_github.py /path/to/MMM-ML-clone
Excluded on purpose: the professor's raw data, derived curve caches, the old submitted PDF
and the two AI-generated historical handoffs, the group-chat app, virtualenvs, caches.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (source in project, destination in repo)
COPY = [
    ("src", "src"), ("app", "app"), ("tests", "tests"), ("tools", "tools"), ("figures", "figures"),
    ("reports", "reports"), ("runs", "runs"), ("requirements.txt", "requirements.txt"),
    ("data/manifest.json", "data/manifest.json"), ("data/split.json", "data/split.json"),
    ("README.github.md", "README.md"), ("WORKLOG.md", "WORKLOG.md"),
    # project notes, kept together under docs/
    ("README.md", "docs/HANDOFF.md"), ("AGENTS.md", "docs/AGENTS.md"),
    ("ROOM_STATE.md", "docs/ROOM_STATE.md"),
    *[(f, f"docs/{f}") for f in ("context.md", "decisions.md", "research.md", "dataset.md",
                                 "methodology.md", "open-questions.md", "tasks.md", "logs.md",
                                 "project-questionnaire.md")],
    ("research_notes", "docs/research_notes"),
    ("project files", "project files"),
]
SKIP_PARTS = {"__pycache__", ".pytest_cache", ".ipynb_checkpoints"}
GITIGNORE = """# Python
.venv/
__pycache__/
*.pyc
# Professor-supplied raw data: place it here locally, do not commit (see README)
TEAM_8_extracted_results_set_1/
# Caches rebuilt by src/data.py from the raw data
data/curves_*.npz
"""


def copy(src, dst):
    if src.is_dir():
        for f in sorted(src.rglob("*")):
            if f.is_file() and not SKIP_PARTS & set(f.parts):
                copy(f, dst / f.relative_to(src))
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    repo = Path(sys.argv[1]).resolve()
    if not (repo / ".git").is_dir():
        sys.exit(f"{repo} is not a git clone")
    if repo == ROOT or ROOT in repo.parents:
        sys.exit("export target must be outside the project folder")
    for src, dst in COPY:
        s = ROOT / src
        if not s.exists():
            sys.exit(f"missing {src}")
        target = repo / dst
        if target.is_dir():
            shutil.rmtree(target)  # mirror: files deleted in the project disappear in the repo too
        copy(s, target)
    (repo / ".gitignore").write_text(GITIGNORE)
    print(f"exported {len(COPY)} items to {repo}")


if __name__ == "__main__":
    main()
