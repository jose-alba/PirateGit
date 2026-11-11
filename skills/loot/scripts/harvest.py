#!/usr/bin/env python3
"""
PirateGit Harvester CLI Entrypoint
==================================
Selectively downloads files or full repository archives into local quarantine (`others/<repo>`).
"""

from __future__ import annotations

import argparse
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from lib.common import get_headers, http_get_text, parse_repo_slug
from lib.channels import fetch_repo_metadata


def run_harvest(repo: str, dest: str = "others", paths: list[str] | None = None) -> None:
    slug = parse_repo_slug(repo)
    repo_short = slug.split("/")[-1]
    dest_root = Path(dest) / repo_short
    dest_root.mkdir(parents=True, exist_ok=True)

    meta = fetch_repo_metadata(slug)
    branch = (meta or {}).get("default_branch") or "main"

    if paths:
        print(f"📥 Downloading {len(paths)} file(s) from {slug} ({branch}) into {dest_root}...")
        for p in paths:
            clean_p = p.lstrip("/")
            url = f"https://raw.githubusercontent.com/{slug}/{branch}/{clean_p}"
            txt, err = http_get_text(url, timeout=25)
            if txt is None:
                print(f"  ❌ Failed {clean_p}: {err}")
                continue
            target = dest_root / clean_p
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(txt, encoding="utf-8")
            print(f"  ✅ Saved: {target}")
        return

    zip_url = f"https://codeload.github.com/{slug}/zip/refs/heads/{branch}"
    print(f"📦 Downloading full repository archive {slug} ({branch}) from {zip_url}...")
    req = urllib.request.Request(zip_url, headers=get_headers(is_github_api=False))
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw_bytes = resp.read()
        with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
            zf.extractall(dest_root)
    print(f"✅ Repository extracted to: {dest_root.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="PirateGit Code & Data Harvester")
    parser.add_argument("repo", help="Repository ('owner/repo' or URL)")
    parser.add_argument("--dest", default="others", help="Destination folder (default: others)")
    parser.add_argument("--paths", nargs="*", help="Specific paths to download instead of full zip")
    args = parser.parse_args()
    run_harvest(args.repo, dest=args.dest, paths=args.paths)


if __name__ == "__main__":
    main()

