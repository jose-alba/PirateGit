#!/usr/bin/env python3
"""
PirateGit Staging Queue & Surgical Transfusion Minitool
======================================================
Manages the temporary staging queue (`staging/`) between raw quarantine (`others/`)
and clean production layout (`src/`, `assets/`, `tests/`).

Commands:
  - add <path> --repo <repo> [--license <lic>] : Stage a file from others/ into staging/
  - status                                     : Show current burn-down checklist of staging queue
  - complete <staging_path> --dest <dest_path> : Stamp provenance, log to projects.md, and remove from staging
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Support installed skill (common inside scripts/) and local repo development (skills/common)
_SCRIPT_DIR = Path(__file__).resolve().parent
for _candidate in [_SCRIPT_DIR, _SCRIPT_DIR.parents[1]]:
    if (_candidate / "common").exists() and str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))
        break

from common.utils import parse_repo_slug

STAGING_DIR = Path("staging")
MANIFEST_FILE = STAGING_DIR / "MANIFEST.json"
PROJECTS_MD = Path("projects.md")


def load_manifest() -> Dict[str, Dict[str, Any]]:
    if not MANIFEST_FILE.exists():
        return {}
    try:
        return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_manifest(manifest: Dict[str, Dict[str, Any]]) -> None:
    if not manifest:
        if MANIFEST_FILE.exists():
            MANIFEST_FILE.unlink()
        return
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def cmd_add(src_path: str, repo: str, license_name: str = "Unknown") -> None:
    src = Path(src_path)
    if not src.exists():
        print(f"❌ Source file not found: {src}")
        sys.exit(1)

    slug = parse_repo_slug(repo)
    repo_short = slug.split("/")[-1]

    # Target path inside staging/
    # If src is inside others/<repo>/path/to/file, preserve relative path under staging/<repo>/
    try:
        rel_parts = src.parts
        if "others" in rel_parts:
            idx = rel_parts.index("others")
            # Skip 'others' and repo folder
            sub_parts = rel_parts[idx + 2 :] if len(rel_parts) > idx + 2 else rel_parts[idx + 1 :]
            target = STAGING_DIR / repo_short / Path(*sub_parts)
        else:
            target = STAGING_DIR / repo_short / src.name
    except Exception:
        target = STAGING_DIR / repo_short / src.name

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(src.read_bytes())

    manifest = load_manifest()
    norm_key = str(target.as_posix())
    manifest[norm_key] = {
        "repo": slug,
        "original_file": str(src.as_posix()),
        "license": license_name,
        "staged_at": datetime.now().isoformat()[:19],
        "size_kb": round(target.stat().st_size / 1024, 1),
    }
    save_manifest(manifest)
    print(f"📥 Staged: {target} ({manifest[norm_key]['size_kb']} KB) [Repo: {slug} | Lic: {license_name}]")


def cmd_status() -> None:
    manifest = load_manifest()
    # Also discover any unindexed files inside staging/
    existing_files = [p for p in STAGING_DIR.rglob("*") if p.is_file() and p.name != "MANIFEST.json"]

    if not existing_files:
        print("🎉 Staging queue is 100% empty! All looted items have been transfused and verified.")
        return

    print(f"🏴‍☠️ PirateGit Staging Queue: {len(existing_files)} item(s) pending burn-down:\n")
    for f in existing_files:
        key = str(f.as_posix())
        meta = manifest.get(key, {})
        repo = meta.get("repo", "Unknown repo")
        lic = meta.get("license", "Unknown")
        size = round(f.stat().st_size / 1024, 1)
        print(f"  [ ] {key} ({size} KB)  --> Origin: {repo} ({lic})")
    print("\n💡 Use 'python skills/loot/scripts/stage.py complete <staged_path> --dest <dest_path>' to burn down.")


def inject_provenance_header(dest_path: Path, repo: str, license_name: str, original_path: str = "") -> None:
    if not dest_path.exists():
        return

    content = dest_path.read_text(encoding="utf-8", errors="replace")
    if "[PIRATEGIT LOOT PROVENANCE]" in content:
        return  # Already tagged

    provenance_doc = f'''"""
[PIRATEGIT LOOT PROVENANCE]
- Origin: https://github.com/{repo} (path: {original_path or dest_path.name})
- Original License: {license_name}
- Usage Status: ⚠️ PoC / Prototipo Experimental
- Production Note: Si este proyecto pasa a producción comercial, revisar la licencia.
                   (Permisiva = uso directo | Copyleft/Privativa = reescribir con Clean-Room).
"""
'''
    if dest_path.suffix.lower() == ".py":
        new_content = provenance_doc + "\n" + content
    elif dest_path.suffix.lower() in (".json", ".yaml", ".yml"):
        # For JSON/YAML, don't corrupt syntax; add comment if yaml, or top-level field if json
        if dest_path.suffix.lower() == ".json":
            try:
                data = json.loads(content)
                if isinstance(data, dict) and "_provenance" not in data:
                    new_data = {
                        "_provenance": {
                            "origin": f"https://github.com/{repo}",
                            "license": license_name,
                            "usage_status": "PoC / Prototipo Experimental",
                        },
                        **data,
                    }
                    new_content = json.dumps(new_data, indent=2, ensure_ascii=False)
                else:
                    new_content = content
            except Exception:
                new_content = content
        else:
            comment_block = f"# [PIRATEGIT LOOT PROVENANCE] Origin: https://github.com/{repo} | License: {license_name}\n"
            new_content = comment_block + content
    else:
        new_content = f"// [PIRATEGIT LOOT PROVENANCE] Origin: https://github.com/{repo} | License: {license_name}\n" + content

    dest_path.write_text(new_content, encoding="utf-8")


def append_to_projects_md(repo: str, dest_path: str, license_name: str, component_name: str) -> None:
    if not PROJECTS_MD.exists():
        PROJECTS_MD.write_text(
            "# 🏴‍☠️ PirateGit: Provenance & Scavenged Assets Log (`projects.md`)\n\n"
            "This file records every external algorithm, dataset, schema, or utility scavenged into the codebase.\n\n"
            "| Component / Function | Destination File | Origin Repository | Original License | Usage Status | Production Notes |\n"
            "|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )

    content = PROJECTS_MD.read_text(encoding="utf-8")
    table_line = (
        f"| `{component_name}` | `{dest_path}` | [{repo}](https://github.com/{repo}) | "
        f"{license_name} | ⚠️ PoC / Prototipo Experimental | Transplantado desde staging/ |\n"
    )

    if dest_path not in content:
        # Append before footnotes or at end of table
        PROJECTS_MD.write_text(content.rstrip() + "\n" + table_line, encoding="utf-8")


def cmd_complete(staged_file: str, dest_file: str, repo: str | None = None, license_name: str | None = None) -> None:
    staged = Path(staged_file)
    dest = Path(dest_file)

    manifest = load_manifest()
    norm_key = str(staged.as_posix())
    meta = manifest.get(norm_key, {})

    final_repo = repo or meta.get("repo") or "Unknown"
    final_lic = license_name or meta.get("license") or "Unknown"
    orig_path = meta.get("original_file", staged.name)

    if not dest.exists():
        print(f"⚠️ Warning: Destination file '{dest}' does not exist yet. Please write/port code to destination first.")
        sys.exit(1)

    # 1. Inject provenance tag into destination
    inject_provenance_header(dest, final_repo, final_lic, original_path=orig_path)
    print(f"🏷️  Injected [PIRATEGIT LOOT PROVENANCE] tag into: {dest}")

    # 2. Append to projects.md
    append_to_projects_md(final_repo, str(dest.as_posix()), final_lic, dest.name)
    print(f"📝 Logged provenance to: {PROJECTS_MD}")

    # 3. Remove staged file
    if staged.exists():
        staged.unlink()
        print(f"🔥 Burned down from staging: {staged}")

    # 4. Update manifest
    if norm_key in manifest:
        del manifest[norm_key]
        save_manifest(manifest)

    # 5. Check if staging is empty
    remaining = [p for p in STAGING_DIR.rglob("*") if p.is_file() and p.name != "MANIFEST.json"]
    if not remaining:
        # Clean empty dirs
        try:
            for p in sorted(STAGING_DIR.rglob("*"), reverse=True):
                if p.is_dir() and not list(p.iterdir()):
                    p.rmdir()
            if STAGING_DIR.exists() and not list(STAGING_DIR.iterdir()):
                STAGING_DIR.rmdir()
        except Exception:
            pass
        print("\n🎉 STAGING 100% VACÍA: ¡Todo el botín ha sido integrado, etiquetado y probado!")
    else:
        print(f"⏳ Quedan {len(remaining)} archivo(s) pendientes en staging/.")


def main() -> None:
    parser = argparse.ArgumentParser(description="PirateGit Staging Queue & Transfusion Minitool")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # add
    p_add = subparsers.add_parser("add", help="Add file to staging queue")
    p_add.add_argument("path", help="Path to file (e.g. inside others/)")
    p_add.add_argument("--repo", required=True, help="Origin repository slug (owner/repo)")
    p_add.add_argument("--license", default="Unknown", help="License name")

    # status
    subparsers.add_parser("status", help="Check burn-down status of staging queue")

    # complete
    p_comp = subparsers.add_parser("complete", help="Complete transfusion, inject tag, log & burn down")
    p_comp.add_argument("staged_path", help="Path of the file inside staging/")
    p_comp.add_argument("--dest", required=True, help="Destination file in src/ or assets/")
    p_comp.add_argument("--repo", help="Optional override for origin repo")
    p_comp.add_argument("--license", help="Optional override for license")

    args = parser.parse_args()

    if args.cmd == "add":
        cmd_add(args.path, repo=args.repo, license_name=args.license)
    elif args.cmd == "status":
        cmd_status()
    elif args.cmd == "complete":
        cmd_complete(args.staged_path, dest_file=args.dest, repo=args.repo, license_name=args.license)


if __name__ == "__main__":
    main()
