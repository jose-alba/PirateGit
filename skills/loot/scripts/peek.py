#!/usr/bin/env python3
"""
PirateGit File Peeker Entrypoint
================================
Zero-quota file reader via raw.githubusercontent.com.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import sys
from pathlib import Path
from typing import Tuple

# Support installed skill (common inside scripts/) and local repo development (skills/common)
_SCRIPT_DIR = Path(__file__).resolve().parent
for _candidate in [_SCRIPT_DIR, _SCRIPT_DIR.parents[1]]:
    if (_candidate / "common").exists() and str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))
        break

from common.utils import http_get_text, parse_repo_slug
from common.channels import fetch_repo_metadata


def peek_file(slug: str, branch: str, file_path: str, max_lines: int) -> Tuple[str, str]:
    clean_p = file_path.lstrip("/")
    for b in (branch, "main", "master"):
        url = f"https://raw.githubusercontent.com/{slug}/{b}/{clean_p}"
        txt, _ = http_get_text(url, timeout=15)
        if txt is not None:
            lines = txt.splitlines()
            if max_lines > 0 and len(lines) > max_lines:
                snippet = "\n".join(lines[:max_lines]) + f"\n\n... [TRUNCATED: showing {max_lines} of {len(lines)} lines] ..."
            else:
                snippet = txt
            return clean_p, snippet
    return clean_p, f"[ERROR: Could not fetch {clean_p} from {slug}]"


def run_peek(repo: str, paths: list[str], branch: str = "", max_lines: int = 160) -> None:
    slug = parse_repo_slug(repo)
    meta = fetch_repo_metadata(slug)
    target_branch = (meta or {}).get("default_branch") or branch or "main"

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(peek_file, slug, target_branch, p, max_lines) for p in paths]
        for fut in futs:
            p, content = fut.result()
            print("=" * 78)
            print(f"📄 {slug} :: {p}")
            print("=" * 78)
            print(content)
            print()


def main() -> None:
    parser = argparse.ArgumentParser(description="PirateGit Zero-Quota File Peeker")
    parser.add_argument("repo", help="Repository ('owner/repo' or URL)")
    parser.add_argument("paths", nargs="+", help="File paths inside the repository")
    parser.add_argument("--branch", default="", help="Optional branch override")
    parser.add_argument("--max-lines", type=int, default=160, help="Max lines per file (0 = unlimited)")
    args = parser.parse_args()
    run_peek(args.repo, args.paths, branch=args.branch, max_lines=args.max_lines)


if __name__ == "__main__":
    main()
