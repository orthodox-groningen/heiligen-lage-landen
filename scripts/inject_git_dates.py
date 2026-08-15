"""Zet git_date (YYYY-MM-DD) in gegenereerde Hugo-frontmatter vanuit data-YAML."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = REPO_ROOT / "site" / "content"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inject git_date in Hugo-content op basis van source_path.",
    )
    parser.add_argument(
        "--content-root",
        type=Path,
        default=CONTENT_ROOT,
    )
    return parser.parse_args()


def git_last_commit_date(path: Path) -> str | None:
    if not path.is_file():
        return None
    result = subprocess.run(
        ["git", "log", "-1", "--format=%as", "--", str(path)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    date_iso = result.stdout.strip()
    return date_iso or None


def set_frontmatter_field(content: str, key: str, value: str) -> str:
    if content.startswith("---\n"):
        end = content.find("\n---\n", 4)
        if end == -1:
            return content
        fm_lines = content[4:end].splitlines()
        body = content[end + 5 :]
        fm_lines = [line for line in fm_lines if not line.startswith(f"{key}:")]
        fm_lines.append(f"{key}: {value}")
        return "---\n" + "\n".join(fm_lines) + "\n---\n" + body
    return f"---\n{key}: {value}\n---\n\n" + content


def extract_source_path(content: str) -> str | None:
    match = re.search(r"^source_path:\s*\"?([^\n\"]+)\"?\s*$", content, re.M)
    return match.group(1).strip() if match else None


def main() -> int:
    args = parse_args()
    count = 0
    for md_file in sorted(args.content_root.rglob("*.md")):
        original = md_file.read_text(encoding="utf-8")
        source_rel = extract_source_path(original)
        if source_rel:
            date_iso = git_last_commit_date(REPO_ROOT / source_rel)
        else:
            date_iso = git_last_commit_date(md_file)
        if not date_iso:
            # Eerste commit / untracked: gebruik vandaag niet; laat leeg tot git history bestaat.
            continue
        updated = set_frontmatter_field(original, "git_date", date_iso)
        if updated != original:
            md_file.write_text(updated, encoding="utf-8", newline="\n")
            count += 1
    print(f"git_date gezet op {count} pagina(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
