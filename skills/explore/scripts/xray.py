#!/usr/bin/env python3
"""
PirateGit X-Ray CLI Entrypoint
==============================
Performs deep anatomical file-tree inspection of 1..N repositories without cloning,
classifying assets into 4 loot buckets and evaluating hygiene signals.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
from pathlib import Path

# Support installed skill (common inside scripts/) and local repo development (skills/common)
_SCRIPT_DIR = Path(__file__).resolve().parent
for _candidate in [_SCRIPT_DIR, _SCRIPT_DIR.parents[1]]:
    if (_candidate / "common").exists() and str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))
        break

from common.tree import xray_single_repo


def run_xray(repos: list[str], as_json: bool = False) -> None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        reports = list(ex.map(xray_single_repo, repos))

    if as_json:
        print(json.dumps(reports, indent=2, ensure_ascii=False))
        return

    for rep in reports:
        meta = rep["metadata"]
        hyg = rep["hygiene"]
        print("=" * 78)
        print(f"🔬 ANATOMICAL X-RAY: {rep['repo']}  ({rep['url']})")
        print(
            f"   Stars: ⭐ {meta.get('stars', '?')} | License: {meta.get('license_verdict', '?')}"
        )
        print(
            f"   Hygiene: 🏥 Health={hyg['tree_health_score']:.2f} | 🛠️ Maint={hyg['maintenance_score']:.2f} "
            f"(pushed {hyg['days_since_last_push']}d ago) | Tests={'✅' if hyg['has_tests'] else '❌'} | CI={'✅' if hyg['has_ci'] else '❌'}"
        )
        print(f"   Total files: {rep['total_files']} (via {rep['tree_source']})")
        if meta.get("description"):
            print(f"   Description: {meta['description']}")
        print("-" * 78)

        print("📁 Root directory distribution:")
        for folder, count in rep["top_level_structure"].items():
            print(f"   - {folder}: {count} files")

        loot = rep["loot"]
        print("\n💎 1. DATA & KNOWLEDGE BASE LOOT (Top curated data files):")
        if loot["data_and_kb_files"]:
            for item in loot["data_and_kb_files"][:12]:
                print(f"   - {item['path']} ({item['size_kb']} KB)")
        else:
            print("   (No large datasets or curated knowledge files detected)")

        print("\n⚙️ 2. CORE ENGINE & ALGORITHM LOOT (Densest source code files):")
        if loot["core_engine_files"]:
            for item in loot["core_engine_files"][:15]:
                print(f"   - {item['path']} ({item['size_kb']} KB)")
        else:
            print("   (No primary source code files detected)")

        print("\n🧠 3. AGENT, PROMPT, SKILL & MCP LOOT:")
        if loot["prompts_skills_agents"]:
            for item in loot["prompts_skills_agents"][:12]:
                print(f"   - {item['path']} ({item['size_kb']} KB)")
        else:
            print("   (No agent/skill/prompt files detected)")

        if rep["dependencies_preview"]:
            print("\n📦 4. MANIFESTS & ECOSYSTEM DEPENDENCIES:")
            for mf, lines in rep["dependencies_preview"].items():
                print(f"   [{mf}]: {' | '.join(lines[:12])}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="PirateGit Zero-Clone Anatomical X-Ray")
    parser.add_argument("repos", nargs="+", help="Repositories to X-ray ('owner/repo' or GitHub URL)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()
    run_xray(args.repos, as_json=args.json)


if __name__ == "__main__":
    main()

