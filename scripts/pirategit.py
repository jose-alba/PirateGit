#!/usr/bin/env python3
"""
GitHub Repo Scout — Multi-Channel Open-Source Intelligence & Repo Scavenger CLI
===============================================================================
Zero-dependency (100% Python stdlib) CLI toolkit for AI coding agents to discover,
score, triage by README, anatomically X-ray, inspect, and harvest open-source
repositories from GitHub, Hacker News (Algolia), and Reddit (Public JSON + PullPush).

Incorporates techniques adapted from:
  - `zamalali/DeepGit` (MIT): Multi-signal scoring (`relevance_score`, `maintenance_score`,
    `popularity_score`, `health_score`), discriminative intent tokenization, and `topic:` search.
  - `AlekseiUL/hermes-researcher-agent` (MIT): Public-only Reddit + PullPush archive fallback
    search and repository traction/hygiene verification.

Commands:
  1. explore / search : Multi-query parallel search across GitHub API + GitHub Topics +
                        Hacker News (Algolia) + Reddit (JSON + PullPush archive), automatic
                        parallel README.md fetching & cleaning, and DeepGit composite scoring.
                        Default scope: 50 repositories (configurable via `--100repos` or `--max-total`).
  2. xray             : Deep anatomical inspection of 1..N repositories WITHOUT cloning.
                        Categorizes the full file tree into 4 loot buckets:
                        - Data & Knowledge Bases (.json, .sqlite, .csv, .db, .yaml...)
                        - Core Engines & Algorithms (largest non-test code files)
                        - Prompts, Skills, Agents & MCP definitions
                        - Manifests & Dependencies (pyproject.toml, requirements.txt, package.json...)
                        Plus hygiene signals (tests, CI, license, health score).
  3. files            : Instant keyword filter over a repository's entire file tree.
  4. peek             : Zero-API-quota file reader via `raw.githubusercontent.com`.
  5. harvest          : Selective file/path downloader or full repository archive extractor into `others/`.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import io
import json
import math
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CACHE_DIR = Path(tempfile.gettempdir()) / "agy_github_scout_cache"
CACHE_TTL_SECONDS = 3600 * 12  # 12-hour cache to preserve rate limits

PERMISSIVE_LICENSES = {
    "MIT",
    "APACHE-2.0",
    "BSD-2-CLAUSE",
    "BSD-3-CLAUSE",
    "ISC",
    "UNLICENSE",
    "0BSD",
    "CC0-1.0",
    "ZLIB",
    "BSL-1.0",
}

COPYLEFT_LICENSES = {
    "GPL-2.0",
    "GPL-3.0",
    "AGPL-3.0",
    "LGPL-2.1",
    "LGPL-3.0",
    "MPL-2.0",
    "EPL-2.0",
    "EUPL-1.2",
}

DATA_EXTENSIONS = {
    ".json",
    ".jsonl",
    ".sqlite",
    ".sqlite3",
    ".db",
    ".csv",
    ".tsv",
    ".parquet",
    ".yaml",
    ".yml",
    ".kicad_sym",
    ".kicad_mod",
    ".kicad_sch",
    ".kicad_pcb",
}

CODE_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".rs",
    ".go",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".java",
    ".cs",
    ".rb",
    ".lua",
}

MANIFEST_FILENAMES = {
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "plugin.json",
    "mcp_config.json",
}

IGNORE_DIRS = {
    "node_modules",
    "vendor",
    "dist",
    "build",
    ".git",
    ".github",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "site-packages",
    "target",
    ".next",
    "coverage",
}

# Discriminative tokenization stopwords (adapted from DeepGit signals.py)
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "for", "to", "in", "on", "with", "that",
    "is", "it", "as", "at", "by", "be", "this", "i", "need", "want", "looking",
    "library", "tool", "package", "framework", "not", "must", "should", "repo",
    "repository", "repositories", "github", "actively", "maintained", "lightweight",
    "simple", "easy", "best", "good", "open", "source", "project", "projects",
}

# Pre-filter fusion weights (adapted from DeepGit signals.py)
W_RELEVANCE = 0.40
W_MAINTENANCE = 0.20
W_HEALTH = 0.15
W_POPULARITY = 0.25


def _get_headers(is_github_api: bool = True) -> Dict[str, str]:
    headers = {
        "User-Agent": "Antigravity-GitHub-Scout/3.0 (+public-source-research; no-cookies)",
    }
    if is_github_api:
        headers["Accept"] = "application/vnd.github+json"
        headers["X-GitHub-Api-Version"] = "2022-11-28"
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token.strip()}"
    else:
        headers["Accept"] = "application/json,text/plain;q=0.9,*/*;q=0.8"
    return headers


def _cache_get(key: str) -> Optional[Any]:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
        p = CACHE_DIR / f"{digest}.json"
        if p.exists() and (time.time() - p.stat().st_mtime) < CACHE_TTL_SECONDS:
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


def _cache_set(key: str, data: Any) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
        p = CACHE_DIR / f"{digest}.json"
        p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _http_get_json(
    url: str, is_github_api: bool = True, use_cache: bool = True, timeout: int = 15
) -> Tuple[Optional[Any], Optional[str]]:
    if use_cache:
        cached = _cache_get(url)
        if cached is not None:
            return cached, None

    req = urllib.request.Request(url, headers=_get_headers(is_github_api=is_github_api))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
            if use_cache:
                _cache_set(url, data)
            return data, None
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:300]
        except Exception:
            pass
        return None, f"HTTP {e.code}: {e.reason} ({body})"
    except Exception as e:
        return None, str(e)


def _http_get_text(url: str, timeout: int = 12, use_cache: bool = True) -> Tuple[Optional[str], Optional[str]]:
    if use_cache:
        cached = _cache_get(f"TEXT::{url}")
        if cached is not None:
            return cached.get("text"), None

    req = urllib.request.Request(url, headers=_get_headers(is_github_api=False))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            txt = resp.read().decode("utf-8", errors="replace")
            if use_cache:
                _cache_set(f"TEXT::{url}", {"text": txt})
            return txt, None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return None, str(e)


def classify_license(spdx_id: Optional[str]) -> str:
    if not spdx_id or spdx_id.upper() in ("NOASSERTION", "NONE", "OTHER"):
        return "🔴 UNKNOWN/NO-LICENSE (Check before commercial use)"
    up = spdx_id.upper()
    if up in PERMISSIVE_LICENSES:
        return f"🟢 {spdx_id} (Commercial-friendly / Permissive)"
    if up in COPYLEFT_LICENSES or "GPL" in up:
        return f"🟡 {spdx_id} (Copyleft - Caution for closed-source embedding)"
    return f"🟡 {spdx_id} (Verify terms)"


def is_permissive_license(spdx_id: Optional[str]) -> bool:
    return bool(spdx_id and spdx_id.upper() in PERMISSIVE_LICENSES)


def parse_repo_slug(repo_input: str) -> str:
    """Normalizes a GitHub URL or 'owner/repo' string into clean 'owner/repo'."""
    s = repo_input.strip().rstrip("/")
    s = re.sub(r"^https?://(www\.)?github\.com/", "", s, flags=re.IGNORECASE)
    parts = [p for p in s.split("/") if p]
    if len(parts) >= 2:
        repo_name = re.sub(r"\.(git|zip|tar\.gz)$", "", parts[1], flags=re.IGNORECASE)
        return f"{parts[0]}/{repo_name}"
    return s


# =====================================================================
# SIGNAL SCORING ENGINE (Adapted from zamalali/DeepGit `signals.py`)
# =====================================================================

def _tokens(text: str) -> Set[str]:
    return set(_TOKEN_RE.findall((text or "").lower()))


def extract_intent_terms(queries: List[str], topics: Optional[List[str]] = None) -> Set[str]:
    """Discriminative terms from all search queries and topics, stopwords removed."""
    combined = " ".join(queries + (topics or []))
    return {t for t in _tokens(combined) if t not in _STOPWORDS and len(t) > 1}


def days_since_iso(iso_str: str) -> int:
    if not iso_str:
        return 9999
    try:
        dt_val = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        if dt_val.tzinfo is None:
            dt_val = dt_val.replace(tzinfo=timezone.utc)
        return max(0, (datetime.now(timezone.utc) - dt_val).days)
    except Exception:
        return 9999


def calc_maintenance_score(pushed_at: str, is_archived: bool = False) -> float:
    """1.0 = pushed today, decaying logarithmically to ~0.0 at 3 years stale."""
    if is_archived:
        return 0.0
    d = days_since_iso(pushed_at)
    return round(max(0.0, min(1.0, 1.0 - math.log1p(d) / math.log1p(1095))), 3)


def calc_popularity_score(stars: int) -> float:
    """Log-scaled stars; ~10k stars saturates to 1.0 so niche gems still compete."""
    return round(max(0.0, min(1.0, math.log1p(max(0, stars)) / math.log1p(10000))), 3)


def calc_metadata_health_score(repo: Dict[str, Any]) -> float:
    """Fast metadata hygiene score during discovery (before full tree X-ray)."""
    s = 0.0
    lic = repo.get("license_spdx")
    if is_permissive_license(lic):
        s += 0.45
    elif lic and lic.upper() not in ("NOASSERTION", "NONE"):
        s += 0.25
    if (repo.get("size_kb") or 0) >= 50:
        s += 0.20
    if repo.get("description"):
        s += 0.15
    if repo.get("topics"):
        s += 0.20
    return round(min(1.0, s), 3)


def calc_tree_health_score(
    has_tests: bool, has_ci: bool, lic_spdx: Optional[str], has_manifests: bool
) -> float:
    """Full file-tree hygiene score (used in `xray`, directly from DeepGit)."""
    s = 0.0
    if has_tests:
        s += 0.40
    if has_ci:
        s += 0.25
    if lic_spdx and lic_spdx.upper() not in ("NOASSERTION", "NONE"):
        s += 0.20
    if has_manifests:
        s += 0.15
    return round(min(1.0, s), 3)


def calc_relevance_score(terms: Set[str], repo: Dict[str, Any]) -> float:
    """Fraction of discriminative intent terms found across repo name, desc, topics, and README."""
    if not terms:
        return 0.5
    hay = (
        _tokens(repo.get("full_name", ""))
        | _tokens(repo.get("description", ""))
        | _tokens(" ".join(repo.get("topics") or []))
        | _tokens(repo.get("readme_digest", ""))
    )
    return round(min(1.0, len(terms & hay) / len(terms)), 3)


def score_repository(repo: Dict[str, Any], terms: Set[str]) -> None:
    """Computes and attaches DeepGit signal scores & composite score to a repo dict."""
    rel = calc_relevance_score(terms, repo)
    maint = calc_maintenance_score(repo.get("pushed_at") or repo.get("updated_at") or "")
    pop = calc_popularity_score(repo.get("stars", 0))
    hlth = calc_metadata_health_score(repo)

    # Multi-query / multi-channel convergence bonus (up to +0.10)
    hit_bonus = min(0.10, max(0, repo.get("hit_count", 1) - 1) * 0.035)

    comp = (
        W_RELEVANCE * rel
        + W_MAINTENANCE * maint
        + W_HEALTH * hlth
        + W_POPULARITY * pop
        + hit_bonus
    )
    days = days_since_iso(repo.get("pushed_at") or repo.get("updated_at") or "")
    freshness = f"pushed {days}d ago" if days < 9999 else "unknown activity"

    repo["signals"] = {
        "composite_score": round(min(1.0, comp), 3),
        "relevance": rel,
        "maintenance": maint,
        "popularity": pop,
        "health": hlth,
        "freshness": freshness,
    }


def clean_readme_digest(raw_md: str, max_lines: int = 20, max_chars: int = 1000) -> str:
    """Strips badge clutter, HTML tags, and code blocks to preserve high-signal README prose."""
    if not raw_md:
        return "(No README.md available)"

    cleaned_lines: List[str] = []
    in_code_block = False
    for line in raw_md.splitlines():
        s = line.strip()
        if s.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not s:
            continue
        if s.startswith(("<div", "</div", "<p", "</p", "<img", "<a ", "</a", "[![", "![", "<table", "</table", "<tr", "</tr", "<td", "</td")):
            continue
        if "img.shields.io" in s or "badge.svg" in s:
            continue
        s = re.sub(r"<[^>]+>", "", s).strip()
        if not s or len(s) < 3:
            continue
        cleaned_lines.append(s)
        if len(cleaned_lines) >= max_lines:
            break

    digest = "\n       ".join(cleaned_lines)
    if len(digest) > max_chars:
        digest = digest[:max_chars] + "..."
    return digest or "(README contains only images/badges)"


def _fetch_repo_readme_digest(slug: str, branch: str, max_lines: int = 20, max_chars: int = 1000) -> str:
    for b in (branch, "main", "master"):
        for rname in ("README.md", "readme.md", "README.rst", "Readme.md"):
            url = f"https://raw.githubusercontent.com/{slug}/{b}/{rname}"
            txt, _ = _http_get_text(url, timeout=8)
            if txt:
                return clean_readme_digest(txt, max_lines=max_lines, max_chars=max_chars)
    return "(No README.md)"


# =====================================================================
# 1. MULTI-CHANNEL DISCOVERY: GitHub + Topics + HN Algolia + Reddit/PullPush
# =====================================================================

_GH_SLUG_EXCLUDE = (
    "orgs/", "topics/", "search/", "features/", "settings/", "sponsors/",
    "about/", "pricing/", "login/", "join/", "explore/", "marketplace/",
    "apps/", "notifications/", "issues/", "pulls/", "blog/", "security/",
)

_GH_URL_PATTERN = re.compile(r"https?://(?:www\.)?github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)")


def _extract_github_slugs_from_text(text: str) -> Set[str]:
    slugs: Set[str] = set()
    if not text:
        return slugs
    for match in _GH_URL_PATTERN.findall(text):
        slug = parse_repo_slug(match)
        if "/" in slug and not any(slug.lower().startswith(b) for b in _GH_SLUG_EXCLUDE):
            slugs.add(slug)
    return slugs


def _search_github_api(query: str, per_page: int = 20, sort: str = "", source_prefix: str = "gh") -> List[Dict[str, Any]]:
    params = {"q": query, "per_page": str(min(per_page, 100))}
    if sort in ("stars", "updated"):
        params["sort"] = sort
    url = f"https://api.github.com/search/repositories?{urllib.parse.urlencode(params)}"
    data, _ = _http_get_json(url, is_github_api=True)
    if not data or "items" not in data:
        return []
    results = []
    for item in data.get("items", []):
        if item.get("fork") or item.get("archived"):
            continue
        lic = (item.get("license") or {}).get("spdx_id")
        results.append({
            "full_name": item.get("full_name"),
            "html_url": item.get("html_url"),
            "description": item.get("description") or "",
            "stars": item.get("stargazers_count", 0),
            "forks": item.get("forks_count", 0),
            "language": item.get("language") or "Unknown",
            "license_spdx": lic,
            "license_verdict": classify_license(lic),
            "topics": item.get("topics") or [],
            "updated_at": (item.get("updated_at") or "")[:10],
            "pushed_at": item.get("pushed_at") or item.get("updated_at") or "",
            "default_branch": item.get("default_branch") or "main",
            "size_kb": item.get("size", 0),
            "source": f"{source_prefix}({query})",
        })
    return results


def _search_hn_algolia(query: str) -> List[str]:
    """Discovers GitHub repository URLs cited in Hacker News stories and comments."""
    q = f"github.com {query}"
    url = f"https://hn.algolia.com/api/v1/search?{urllib.parse.urlencode({'query': q, 'hitsPerPage': 25})}"
    data, _ = _http_get_json(url, is_github_api=False, timeout=10)
    if not data:
        return []

    slugs: Set[str] = set()
    for hit in data.get("hits", []):
        for field in ("url", "story_text", "comment_text", "title"):
            slugs.update(_extract_github_slugs_from_text(hit.get(field) or ""))
    return list(slugs)[:12]


def _search_reddit_public_fallback(query: str, limit: int = 12) -> List[str]:
    """
    Public-only Reddit + PullPush archive fallback search (adapted from
    AlekseiUL/hermes-researcher-agent `helpers/public_reddit_fallback_search.py`).
    Extracts GitHub repo slugs recommended in Reddit posts and comments without API keys.
    """
    q_str = f"github.com {query}"
    q_enc = urllib.parse.quote(q_str)
    slugs: Set[str] = set()

    # 1. Probe live public Reddit JSON first
    for base in ("https://www.reddit.com", "https://old.reddit.com"):
        probe_url = f"{base}/search.json?q={q_enc}&limit={limit}&sort=relevance"
        data, _ = _http_get_json(probe_url, is_github_api=False, timeout=8)
        if data and isinstance(data, dict):
            children = (data.get("data") or {}).get("children") or []
            for child in children:
                post = child.get("data") or {}
                for field in ("url", "selftext", "title"):
                    slugs.update(_extract_github_slugs_from_text(str(post.get(field) or "")))
            if slugs:
                break

    # 2. PullPush public Reddit archive fallback (submissions & comments)
    for kind in ("submission", "comment"):
        pp_url = f"https://api.pullpush.io/reddit/search/{kind}/?q={q_enc}&size={limit}&sort=desc&sort_type=score"
        pp_data, _ = _http_get_json(pp_url, is_github_api=False, timeout=10)
        if pp_data and isinstance(pp_data, dict):
            for item in (pp_data.get("data") or [])[:limit]:
                for field in ("url", "selftext", "body", "title"):
                    slugs.update(_extract_github_slugs_from_text(str(item.get(field) or "")))

    return list(slugs)[:12]


def _fetch_repo_metadata(slug: str, source_tag: str = "discovery") -> Optional[Dict[str, Any]]:
    url = f"https://api.github.com/repos/{slug}"
    item, _ = _http_get_json(url, is_github_api=True)
    if not item or "full_name" not in item:
        return None
    if item.get("archived"):
        return None
    lic = (item.get("license") or {}).get("spdx_id")
    return {
        "full_name": item.get("full_name"),
        "html_url": item.get("html_url"),
        "description": item.get("description") or "",
        "stars": item.get("stargazers_count", 0),
        "forks": item.get("forks_count", 0),
        "language": item.get("language") or "Unknown",
        "license_spdx": lic,
        "license_verdict": classify_license(lic),
        "topics": item.get("topics") or [],
        "updated_at": (item.get("updated_at") or "")[:10],
        "pushed_at": item.get("pushed_at") or item.get("updated_at") or "",
        "default_branch": item.get("default_branch") or "main",
        "size_kb": item.get("size", 0),
        "source": source_tag,
    }


def _auto_derive_topics(queries: List[str], explicit_topics: Optional[List[str]]) -> List[str]:
    """
    Derives 2-4 canonical hyphenated GitHub topic slugs if not explicitly provided
    (adapted from DeepGit's `topic:<slug> sort:stars` strategy).
    """
    if explicit_topics:
        return [t.strip().lower().replace(" ", "-") for t in explicit_topics if t.strip()]
    derived: List[str] = []
    for q in queries:
        words = [w.lower() for w in _TOKEN_RE.findall(q) if w.lower() not in _STOPWORDS]
        if 1 <= len(words) <= 2:
            slug = "-".join(words)
            if slug not in derived and len(slug) >= 3:
                derived.append(slug)
    return derived[:3]


def cmd_search(args: argparse.Namespace) -> None:
    queries: List[str] = args.queries
    max_total: int = args.max_total
    topics: List[str] = _auto_derive_topics(queries, getattr(args, "topics", None))
    per_query = max(args.limit, min(100, int((max_total * 1.4) / max(1, len(queries) + len(topics))) + 5))

    repos_by_name: Dict[str, Dict[str, Any]] = {}
    matched_queries: Dict[str, Set[str]] = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        # 1. Standard GitHub keyword queries
        gh_futures = {ex.submit(_search_github_api, q, per_query, args.sort, "gh"): q for q in queries}
        # 2. DeepGit-style GitHub Topic queries (`topic:<slug> sort:stars`)
        topic_futures = {
            ex.submit(_search_github_api, f"topic:{t}", max(10, per_query // 2), "stars", "topic"): f"topic:{t}"
            for t in topics
        }
        # 3. Hacker News Algolia discovery
        hn_futures = {ex.submit(_search_hn_algolia, q): q for q in queries[:5]} if not args.no_hn else {}
        # 4. Public Reddit + PullPush fallback discovery
        reddit_futures = (
            {ex.submit(_search_reddit_public_fallback, q, 10): q for q in queries[:4]}
            if not getattr(args, "no_reddit", False)
            else {}
        )

        for fut_map in (gh_futures, topic_futures):
            for fut, q_label in fut_map.items():
                for r in fut.result():
                    fn = r["full_name"]
                    matched_queries.setdefault(fn, set()).add(q_label)
                    if fn not in repos_by_name:
                        repos_by_name[fn] = r

        external_slugs_to_fetch: Dict[str, Set[str]] = {}
        for fut, q in hn_futures.items():
            for slug in fut.result():
                if slug in repos_by_name:
                    matched_queries.setdefault(slug, set()).add(f"HN:{q}")
                else:
                    external_slugs_to_fetch.setdefault(slug, set()).add(f"HN:{q}")

        for fut, q in reddit_futures.items():
            for slug in fut.result():
                if slug in repos_by_name:
                    matched_queries.setdefault(slug, set()).add(f"Reddit:{q}")
                else:
                    external_slugs_to_fetch.setdefault(slug, set()).add(f"Reddit:{q}")

        if external_slugs_to_fetch:
            # Prioritize slugs mentioned multiple times across HN/Reddit
            sorted_ext = sorted(external_slugs_to_fetch.items(), key=lambda x: len(x[1]), reverse=True)[:16]
            meta_futs = {
                ex.submit(_fetch_repo_metadata, slug, ", ".join(tags)): (slug, tags)
                for slug, tags in sorted_ext
            }
            for fut, (slug, tags) in meta_futs.items():
                r = fut.result()
                if r:
                    fn = r["full_name"]
                    repos_by_name[fn] = r
                    matched_queries.setdefault(fn, set()).update(tags)

    all_candidates = list(repos_by_name.values())
    intent_terms = extract_intent_terms(queries, topics)

    for r in all_candidates:
        fn = r["full_name"]
        hits = sorted(matched_queries.get(fn, set()))
        r["matched_queries"] = hits
        r["hit_count"] = len(hits)
        score_repository(r, intent_terms)

    # Initial pre-sort before README enrichment
    all_candidates.sort(
        key=lambda x: (x["signals"]["composite_score"], x.get("hit_count", 1), x.get("stars", 0)),
        reverse=True,
    )
    results = all_candidates[:max_total]

    # Parallel README.md fetching via raw.githubusercontent.com (0 GitHub API quota)
    fetch_readmes = getattr(args, "readmes", False) or getattr(args, "cmd", "") == "explore"
    if fetch_readmes and results:
        max_lines = 8 if len(results) > 15 else 16
        max_chars = 420 if len(results) > 15 else 800
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
            readme_futs = {
                ex.submit(
                    _fetch_repo_readme_digest,
                    r["full_name"],
                    r.get("default_branch", "main"),
                    max_lines,
                    max_chars,
                ): r
                for r in results
            }
            for fut, r in readme_futs.items():
                r["readme_digest"] = fut.result()
                # Re-score with full README text surface included!
                score_repository(r, intent_terms)

        # Final sort using README-enriched DeepGit composite score
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
                {"count": len(results), "queries": queries, "topics": topics, "repositories": results},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    except Exception:
        pass

    if args.json:
        print(json.dumps({"count": len(results), "repositories": results}, indent=2, ensure_ascii=False))
        return

    out_lines: List[str] = [
        f"=== GITHUB REPO SCOUT: {len(results)} repositories ranked (Max scope: {max_total}) ===",
        f"🔍 Queries: {queries} | 🏷️ Topics: {topics} | 🌐 Channels: GitHub + Topics + HN + Reddit/PullPush",
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


# =====================================================================
# 2. XRAY & FILES: Anatomical Repository Inspection Without Cloning
# =====================================================================

def _get_repo_tree(slug: str, branch: str) -> Tuple[List[Dict[str, Any]], str]:
    """
    Fetches the full recursive file tree of a repository:
    1) Tries GitHub REST API `/git/trees/{branch}?recursive=1` (12h cached)
    2) Falls back automatically to `codeload.github.com` ZIP central directory header
       inspection (zero REST API quota usage).
    """
    tree_url = f"https://api.github.com/repos/{slug}/git/trees/{branch}?recursive=1"
    data, err = _http_get_json(tree_url, is_github_api=True)
    if data and "tree" in data:
        files = [
            {"path": item["path"], "size": item.get("size", 0)}
            for item in data["tree"]
            if item.get("type") == "blob"
        ]
        return files, "github_api_tree"

    for b in (branch, "main", "master"):
        zip_url = f"https://codeload.github.com/{slug}/zip/refs/heads/{b}"
        req = urllib.request.Request(zip_url, headers=_get_headers(is_github_api=False))
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                raw_bytes = resp.read()
                with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
                    files = []
                    for info in zf.infolist():
                        if info.is_dir():
                            continue
                        parts = info.filename.split("/", 1)
                        rel_path = parts[1] if len(parts) > 1 else info.filename
                        files.append({"path": rel_path, "size": info.file_size})
                    _cache_set(tree_url, {"tree": [{"path": f["path"], "size": f["size"], "type": "blob"} for f in files]})
                    return files, f"codeload_zip({b})"
        except Exception:
            continue

    return [], f"error({err})"


def _is_ignored_path(path_str: str) -> bool:
    parts = path_str.split("/")
    return any(
        p in IGNORE_DIRS or (p.startswith(".") and p not in (".claude-plugin", ".agents", ".claude"))
        for p in parts[:-1]
    )


def _extract_dependencies_preview(slug: str, branch: str, manifest_paths: List[str]) -> Dict[str, List[str]]:
    sorted_manifests = sorted(manifest_paths, key=lambda p: (p.count("/"), len(p)))
    deps: Dict[str, List[str]] = {}
    for mp in sorted_manifests[:4]:
        raw_url = f"https://raw.githubusercontent.com/{slug}/{branch}/{mp}"
        txt, _ = _http_get_text(raw_url, timeout=10)
        if not txt:
            continue
        lines = [ln.strip() for ln in txt.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        deps[mp] = lines[:35]
    return deps


def _xray_single_repo(repo_input: str) -> Dict[str, Any]:
    slug = parse_repo_slug(repo_input)
    meta = _fetch_repo_metadata(slug, source_tag="xray")
    branch = (meta or {}).get("default_branch") or "main"

    files, method = _get_repo_tree(slug, branch)

    data_loot: List[Dict[str, Any]] = []
    engine_loot: List[Dict[str, Any]] = []
    agent_loot: List[Dict[str, Any]] = []
    manifests: List[str] = []
    top_dirs: Dict[str, int] = {}
    has_tests = False
    has_ci = False

    for f in files:
        p = f["path"]
        sz = f.get("size", 0)
        top = p.split("/")[0] if "/" in p else "(root)"
        top_dirs[top] = top_dirs.get(top, 0) + 1

        lower_p = p.lower()
        if ".github/workflows/" in lower_p or lower_p.startswith(".circleci") or ".gitlab-ci" in lower_p:
            has_ci = True
        if any(t in lower_p for t in ("test_", "_test.", "/tests/", "/test/", "conftest.py", "spec.")):
            has_tests = True

        if _is_ignored_path(p):
            continue

        fname = p.split("/")[-1]
        ext = os.path.splitext(fname)[1].lower()
        is_test = any(t in lower_p for t in ("test_", "_test.", "/tests/", "/test/", "conftest.py", "fixtures/"))

        if fname in MANIFEST_FILENAMES:
            manifests.append(p)

        # 1. Prompts, Skills, Agents & MCP definitions
        if not is_test and (
            fname.upper() in ("SKILL.MD", "AGENTS.MD", "CLAUDE.MD")
            or any(k in lower_p for k in ("skills/", "agents/", "prompts/", "prompt", "agent", "skill", "guidance"))
            and ext in (".md", ".py", ".ts", ".js", ".json", ".yaml", ".yml")
        ):
            agent_loot.append({"path": p, "size_kb": round(sz / 1024, 1)})

        # 2. Curated Data & Knowledge Bases (excluding tests, i18n translations, and lockfiles)
        if (
            not is_test
            and "/i18n/" not in lower_p
            and ext in DATA_EXTENSIONS
            and fname not in ("package.json", "package-lock.json", "pnpm-lock.yaml", "tsconfig.json")
        ):
            if sz >= 1024 or any(
                k in lower_p for k in ("data", "kb", "knowledge", "parts", "blocks", "rules", "catalog", "fab", "stackup")
            ):
                data_loot.append({"path": p, "size_kb": round(sz / 1024, 1)})

        # 3. Core Engines & Algorithms (excluding tests)
        if not is_test and ext in CODE_EXTENSIONS:
            engine_loot.append({"path": p, "size_kb": round(sz / 1024, 1)})

    data_loot.sort(key=lambda x: x["size_kb"], reverse=True)
    engine_loot.sort(key=lambda x: x["size_kb"], reverse=True)
    agent_loot.sort(key=lambda x: x["size_kb"], reverse=True)

    lic_spdx = (meta or {}).get("license_spdx")
    tree_health = calc_tree_health_score(has_tests, has_ci, lic_spdx, bool(manifests))
    maint_score = calc_maintenance_score((meta or {}).get("pushed_at") or (meta or {}).get("updated_at") or "")
    days = days_since_iso((meta or {}).get("pushed_at") or (meta or {}).get("updated_at") or "")

    readme_excerpt = _fetch_repo_readme_digest(slug, branch, max_lines=30, max_chars=1500)
    deps_preview = _extract_dependencies_preview(slug, branch, manifests)

    return {
        "repo": slug,
        "url": f"https://github.com/{slug}",
        "metadata": meta or {"full_name": slug, "default_branch": branch, "license_verdict": classify_license(None)},
        "hygiene": {
            "tree_health_score": tree_health,
            "maintenance_score": maint_score,
            "days_since_last_push": days,
            "has_tests": has_tests,
            "has_ci": has_ci,
            "has_manifests": bool(manifests),
        },
        "tree_source": method,
        "total_files": len(files),
        "top_level_structure": dict(sorted(top_dirs.items(), key=lambda x: x[1], reverse=True)[:15]),
        "loot": {
            "data_and_kb_files": data_loot[:20],
            "core_engine_files": engine_loot[:25],
            "prompts_skills_agents": agent_loot[:20],
            "manifests": manifests,
        },
        "dependencies_preview": deps_preview,
        "readme_head": readme_excerpt,
    }


def cmd_xray(args: argparse.Namespace) -> None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        reports = list(ex.map(_xray_single_repo, args.repos))

    if args.json:
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


def cmd_files(args: argparse.Namespace) -> None:
    slug = parse_repo_slug(args.repo)
    meta = _fetch_repo_metadata(slug)
    branch = (meta or {}).get("default_branch") or "main"
    files, _ = _get_repo_tree(slug, branch)

    keywords = [k.lower() for k in args.keywords]
    matches = []
    for f in files:
        p_low = f["path"].lower()
        if not keywords or any(k in p_low for k in keywords):
            matches.append(f)

    matches.sort(key=lambda x: x.get("size", 0), reverse=True)
    print(f"=== {len(matches)} matching files in {slug} (filter: {keywords}) ===")
    for m in matches[: args.limit]:
        kb = round(m.get("size", 0) / 1024, 1)
        print(f"  {m['path']}  ({kb} KB)")


# =====================================================================
# 3. PEEK: Zero-Quota File Inspection via raw.githubusercontent.com
# =====================================================================

def _peek_file(slug: str, branch: str, file_path: str, max_lines: int) -> Tuple[str, str]:
    clean_p = file_path.lstrip("/")
    for b in (branch, "main", "master"):
        url = f"https://raw.githubusercontent.com/{slug}/{b}/{clean_p}"
        txt, _ = _http_get_text(url, timeout=15)
        if txt is not None:
            lines = txt.splitlines()
            if max_lines > 0 and len(lines) > max_lines:
                snippet = "\n".join(lines[:max_lines]) + f"\n\n... [TRUNCATED: showing {max_lines} of {len(lines)} lines] ..."
            else:
                snippet = txt
            return clean_p, snippet
    return clean_p, f"[ERROR: Could not fetch {clean_p} from {slug}]"


def cmd_peek(args: argparse.Namespace) -> None:
    slug = parse_repo_slug(args.repo)
    meta = _fetch_repo_metadata(slug)
    branch = (meta or {}).get("default_branch") or args.branch or "main"

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(_peek_file, slug, branch, p, args.max_lines) for p in args.paths]
        for fut in futs:
            p, content = fut.result()
            print("=" * 78)
            print(f"📄 {slug} :: {p}")
            print("=" * 78)
            print(content)
            print()


# =====================================================================
# 4. HARVEST: Selective File or Full Repo Extraction to others/<repo>
# =====================================================================

def cmd_harvest(args: argparse.Namespace) -> None:
    slug = parse_repo_slug(args.repo)
    repo_short = slug.split("/")[-1]
    dest_root = Path(args.dest) / repo_short
    dest_root.mkdir(parents=True, exist_ok=True)

    meta = _fetch_repo_metadata(slug)
    branch = (meta or {}).get("default_branch") or "main"

    if args.paths:
        print(f"📥 Downloading {len(args.paths)} file(s) from {slug} ({branch}) into {dest_root}...")
        for p in args.paths:
            clean_p = p.lstrip("/")
            url = f"https://raw.githubusercontent.com/{slug}/{branch}/{clean_p}"
            txt, err = _http_get_text(url, timeout=25)
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
    req = urllib.request.Request(zip_url, headers=_get_headers(is_github_api=False))
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw_bytes = resp.read()
        with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
            zf.extractall(dest_root)
    print(f"✅ Repository extracted to: {dest_root.resolve()}")


def _preprocess_argv(argv: List[str]) -> List[str]:
    """Converts shorthand flags like `--100repos`, `--50repos`, `--20repo` into `--max-total N`."""
    out: List[str] = []
    for arg in argv:
        m = re.match(r"^--(\d+)repos?$", arg.strip(), flags=re.IGNORECASE)
        if m:
            out.extend(["--max-total", m.group(1)])
        else:
            out.append(arg)
    return out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="GitHub Repo Scout - Multi-channel discovery, DeepGit signal scoring, README triage, and anatomical X-ray."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    for sub_name, default_readmes, help_txt in (
        ("explore", True, "Search repos (default 50) across GitHub + Topics + HN + Reddit/PullPush, fetch READMEs, and score with DeepGit signals"),
        ("search", False, "Search repos in parallel (pass --readmes to also fetch and score READMEs)"),
    ):
        p_s = sub.add_parser(sub_name, help=help_txt)
        p_s.add_argument("queries", nargs="+", help="Search keyword queries (1-3 core words per query recommended)")
        p_s.add_argument("--topics", nargs="*", help="Optional GitHub topic slugs to search via `topic:<slug> sort:stars`")
        p_s.add_argument("--limit", type=int, default=15, help="Minimum results per query (default: 15)")
        p_s.add_argument("--max-total", type=int, default=50, help="Max total repositories to return (default: 50, or use --100repos)")
        p_s.add_argument("--readmes", action="store_true", default=default_readmes, help="Fetch cleaned README.md digest for every repo")
        p_s.add_argument("--sort", choices=["", "stars", "updated"], default="", help="GitHub API sort order (default: best match)")
        p_s.add_argument("--no-hn", action="store_true", help="Disable Hacker News Algolia discovery")
        p_s.add_argument("--no-reddit", action="store_true", help="Disable Reddit / PullPush public archive discovery")
        p_s.add_argument("--json", action="store_true", help="Output raw JSON")
        p_s.set_defaults(func=cmd_search)

    p_xray = sub.add_parser("xray", help="Anatomically inspect 1..N repositories without cloning")
    p_xray.add_argument("repos", nargs="+", help="Repositories to X-ray ('owner/repo' or GitHub URL)")
    p_xray.add_argument("--json", action="store_true", help="Output raw JSON")
    p_xray.set_defaults(func=cmd_xray)

    p_files = sub.add_parser("files", help="Filter a repository's file tree by keywords")
    p_files.add_argument("repo", help="Repository ('owner/repo' or URL)")
    p_files.add_argument("keywords", nargs="*", help="Keywords to match against file paths")
    p_files.add_argument("--limit", type=int, default=50, help="Max matching paths to display")
    p_files.set_defaults(func=cmd_files)

    p_peek = sub.add_parser("peek", help="Read specific files from a repo without spending GitHub API quota")
    p_peek.add_argument("repo", help="Repository ('owner/repo' or URL)")
    p_peek.add_argument("paths", nargs="+", help="File paths inside the repository")
    p_peek.add_argument("--branch", default="", help="Optional branch override")
    p_peek.add_argument("--max-lines", type=int, default=160, help="Max lines per file (0 = unlimited)")
    p_peek.set_defaults(func=cmd_peek)

    p_harvest = sub.add_parser("harvest", help="Download specific files or full repository ZIP into others/<repo>")
    p_harvest.add_argument("repo", help="Repository ('owner/repo' or URL)")
    p_harvest.add_argument("--dest", default="others", help="Destination directory (default: others)")
    p_harvest.add_argument("--paths", nargs="*", help="Specific file paths to download instead of full repo")
    p_harvest.set_defaults(func=cmd_harvest)

    return parser


if __name__ == "__main__":
    ap = build_parser()
    clean_args = _preprocess_argv(sys.argv[1:])
    parsed = ap.parse_args(clean_args)
    parsed.func(parsed)
