import os
import shutil
from pathlib import Path

ARTIFACTS = [
    ".pytest_cache",
    ".coverage",
    "coverage.xml",
    "htmlcov",
    "ruff_report.json",
]

HISTORY_FILES = [
    Path.home() / ".lambdora_history",
    Path(".lambdora_history"),
]


def rm_path(p: Path) -> None:
    """Remove a file or directory if it exists (silently)."""
    if p.is_dir():
        shutil.rmtree(p, ignore_errors=True)
    elif p.exists():
        try:
            p.unlink()
        except OSError:
            # Might be a symlink to a missing target or similar
            pass


def main() -> None:
    for name in ARTIFACTS:
        rm_path(Path(name))

    # Remove all __pycache__ directories recursively
    for cache_dir in Path(".").rglob("__pycache__"):
        rm_path(cache_dir)

    # Remove REPL history files
    for hist in HISTORY_FILES:
        rm_path(Path(hist))

    print("Workspace cleaned.")


if __name__ == "__main__":
    main()
