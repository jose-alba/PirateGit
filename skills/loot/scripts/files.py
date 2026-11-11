#!/usr/bin/env python3
"""
PirateGit File Tree Path Filter CLI
===================================
Filters a repository's full file tree by keywords to instantly locate specific files.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from lib.common import parse_repo_slug
from lib.channels import fetch_repo_metadata
from lib.tree import get_repo_tree


def run_files(repo: str, keywords: list[str], limit: int = 50) -> None:
    slug = parse_repo_slug(repo)
    meta = fetch_repo_metadata(slug)
    branch = (meta or {}).get("default_branch") or "main"
    files, _ = get_repo_tree(slug, branch)

    kw_lower = [k.lower() for k in keywords]
    matches = []
    for f in files:
        p_low = f["path"].lower()
        if not kw_lower or any(k in p_low for k in kw_lower):
            matches.append(f)

    matches.sort(key=lambda x: x.get("size", 0), reverse=True)
    print(f"=== {len(matches)} matching files in {slug} (filter: {keywords}) ===")
    for m in matches[:limit]:
        kb = round(m.get("size", 0) / 1024, 1)
        print(f"  {m['path']}  ({kb} KB)")


def main() -> None:
    parser = argparse.ArgumentParser(description="PirateGit File Tree Path Filter")
    parser.add_argument("repo", help="Repository ('owner/repo' or URL)")
    parser.add_argument("keywords", nargs="*", help="Keywords to match against file paths")
    parser.add_argument("--limit", type=int, default=50, help="Max matching paths to display")
    args = parser.parse_args()
    run_files(args.repo, args.keywords, limit=args.limit)


if __name__ == "__main__":
    main()

