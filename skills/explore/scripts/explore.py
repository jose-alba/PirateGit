#!/usr/bin/env python3
"""
PirateGit /explore CLI Entrypoint
=================================
Executes 4-channel search (GitHub, Topics, HN, Reddit), fetches cleaned READMEs,
and ranks repositories using DeepGit composite scoring.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Ensure lib package can be imported regardless of execution working directory
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from lib.common import CACHE_DIR, fetch_repo_readme_digest
from lib.scoring import extract_intent_terms, score_repository
from lib.channels import (
    search_github_api,
    search_hn_algolia,
    search_reddit_public_fallback,
    fetch_repo_metadata,
)


def auto_derive_topics(queries: List[str], explicit_topics: Optional[List[str]]) -> List[str]:
    if explicit_topics:
        return [t.strip().lower().replace(" ", "-") for t in explicit_topics if t.strip()]
    derived: List[str] = []
    _token_re = re.compile(r"[a-z0-9]+")
    for q in queries:
        words = [w.lower() for w in _token_re.findall(q)]
        if 1 <= len(words) <= 2:
            slug = "-".join(words)
            if slug not in derived and len(slug) >= 3:
                derived.append(slug)
    return derived[:3]


def run_explore(
    queries: List[str],
    topics: Optional[List[str]] = None,
    max_total: int = 50,
    sort: str = "",
    no_hn: bool = False,
    no_reddit: bool = False,
    as_json: bool = False,
) -> List[Dict[str, Any]]:
    derived_topics = auto_derive_topics(queries, topics)
    per_query = max(15, min(100, int((max_total * 1.4) / max(1, len(queries) + len(derived_topics))) + 5))

    repos_by_name: Dict[str, Dict[str, Any]] = {}
    matched_queries: Dict[str, Set[str]] = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        gh_futures = {ex.submit(search_github_api, q, per_query, sort, "gh"): q for q in queries}
        topic_futures = {
            ex.submit(search_github_api, f"topic:{t}", max(10, per_query // 2), "stars", "topic"): f"topic:{t}"
            for t in derived_topics
        }
        hn_futures = {ex.submit(search_hn_algolia, q): q for q in queries[:5]} if not no_hn else {}
        reddit_futures = {ex.submit(search_reddit_public_fallback, q, 10): q for q in queries[:4]} if not no_reddit else {}

        for fut_map in (gh_futures, topic_futures):
            for fut, q_label in fut_map.items():
                for r in fut.result():
                    fn = r["full_name"]
                    matched_queries.setdefault(fn, set()).add(q_label)
                    if fn not in repos_by_name:
                        repos_by_name[fn] = r

        external_slugs: Dict[str, Set[str]] = {}
        for fut, q in hn_futures.items():
            for slug in fut.result():
                if slug in repos_by_name:
                    matched_queries.setdefault(slug, set()).add(f"HN:{q}")
                else:
                    external_slugs.setdefault(slug, set()).add(f"HN:{q}")

        for fut, q in reddit_futures.items():
            for slug in fut.result():
                if slug in repos_by_name:
                    matched_queries.setdefault(slug, set()).add(f"Reddit:{q}")
                else:
                    external_slugs.setdefault(slug, set()).add(f"Reddit:{q}")

        if external_slugs:
            sorted_ext = sorted(external_slugs.items(), key=lambda x: len(x[1]), reverse=True)[:16]
            meta_futs = {
                ex.submit(fetch_repo_metadata, slug, ", ".join(tags)): (slug, tags)
                for slug, tags in sorted_ext
            }
            for fut, (slug, tags) in meta_futs.items():
                r = fut.result()
                if r:
                    fn = r["full_name"]
                    repos_by_name[fn] = r
                    matched_queries.setdefault(fn, set()).update(tags)

    all_candidates = list(repos_by_name.values())
    intent_terms = extract_intent_terms(queries, derived_topics)

    for r in all_candidates:
        fn = r["full_name"]
        hits = sorted(matched_queries.get(fn, set()))
        r["matched_queries"] = hits
        r["hit_count"] = len(hits)
        score_repository(r, intent_terms)

    all_candidates.sort(
        key=lambda x: (x["signals"]["composite_score"], x.get("hit_count", 1), x.get("stars", 0)),
        reverse=True,
    )
    results = all_candidates[:max_total]

    # Parallel README ingestion (0 API quota)
    if results:
        max_lines = 8 if len(results) > 15 else 16
        max_chars = 420 if len(results) > 15 else 800
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
            readme_futs = {
                ex.submit(
                    fetch_repo_readme_digest,
                    r["full_name"],
                    r.get("default_branch", "main"),
                    max_lines,
                    max_chars,
                ): r
                for r in results
            }
            for fut, r in readme_futs.items():
                r["readme_digest"] = fut.result()
                score_repository(r, intent_terms)

        results.sort(
            key=lambda x: (x["signals"]["composite_score"], x.get("hit_count", 1), x.get("stars", 0)),
            reverse=True,
        )

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    digest_md_path = CACHE_DIR / "last_explore_digest.md"
    json_cache_path = CACHE_DIR / "last_explore_results.json"

    try:
        json_cache_path.write_text(
            json.dumps(
                {"count": len(results), "queries": queries, "topics": derived_topics, "repositories": results},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    except Exception:
        pass

    if as_json:
        print(json.dumps({"count": len(results), "repositories": results}, indent=2, ensure_ascii=False))
        return results

    out_lines: List[str] = [
        f"=== GITHUB REPO SCOUT: {len(results)} repositories ranked (Max scope: {max_total}) ===",
        f"🔍 Queries: {queries} | 🏷️ Topics: {derived_topics} | 🌐 Channels: GitHub + Topics + HN + Reddit/PullPush",
        f"📄 Full untruncated digest saved to: {digest_md_path}\n",
    ]
    for idx, r in enumerate(results, 1):
        sig = r.get("signals") or {}
        out_lines.append(
            f"[{idx}/{len(results)}] {r['full_name']}  "
            f"(🎯 Score: {sig.get('composite_score', 0):.2f} [Rel:{sig.get('relevance', 0):.2f} Maint:{sig.get('maintenance', 0):.2f} Pop:{sig.get('popularity', 0):.2f}] "
            f"| ⭐ {r['stars']} | 💻 {r['language']} | 📦 {r['size_kb']} KB | 🕒 {sig.get('freshness', r['updated_at'])})"
        )
        out_lines.append(f"    URL      : {r['html_url']}")
        out_lines.append(f"    License  : {r['license_verdict']}")
        if r["description"]:
            out_lines.append(f"    Desc     : {r['description']}")
        if r["topics"]:
            out_lines.append(f"    Topics   : {', '.join(r['topics'][:8])}")
        out_lines.append(f"    Matched  : {', '.join(r['matched_queries'])}")
        if "readme_digest" in r:
            out_lines.append(f"    README   :\n       {r['readme_digest']}")
        out_lines.append("-" * 78)

    full_report_text = "\n".join(out_lines)
    try:
        digest_md_path.write_text(full_report_text, encoding="utf-8")
    except Exception:
        pass

    print(full_report_text)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="PirateGit Multi-Channel Open-Source Intelligence Explorer")
    parser.add_argument("queries", nargs="+", help="Search keyword queries (1-3 core words per query)")
    parser.add_argument("--topics", nargs="*", help="Optional canonical topic slugs")
    parser.add_argument("--limit", type=int, default=15, help="Min results per query")
    parser.add_argument("--max-total", type=int, default=50, help="Max total repos to return")
    parser.add_argument("--sort", choices=["", "stars", "updated"], default="", help="GitHub sort order")
    parser.add_argument("--no-hn", action="store_true", help="Disable Hacker News Algolia discovery")
    parser.add_argument("--no-reddit", action="store_true", help="Disable Reddit / PullPush discovery")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    # Support shorthand flags like --100repos, --20repos
    clean_argv: List[str] = []
    for arg in sys.argv[1:]:
        m = re.match(r"^--(\d+)repos?$", arg.strip(), flags=re.IGNORECASE)
        if m:
            clean_argv.extend(["--max-total", m.group(1)])
        else:
            clean_argv.append(arg)

    args = parser.parse_args(clean_argv)
    run_explore(
        queries=args.queries,
        topics=args.topics,
        max_total=args.max_total,
        sort=args.sort,
        no_hn=args.no_hn,
        no_reddit=args.no_reddit,
        as_json=args.json,
    )


if __name__ == "__main__":
    main()

