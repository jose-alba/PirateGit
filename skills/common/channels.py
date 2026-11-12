#!/usr/bin/env python3
"""
Multi-Channel Repository Search & Discovery
===========================================
Channels:
1. GitHub Search API (repos + topics)
2. Hacker News via Algolia API
3. Reddit Search via Public JSON
4. GitHub Repo Metadata Hydration
"""

from __future__ import annotations

import json
import re
import urllib.parse
from typing import Any, Dict, List, Optional, Set

from .utils import (
    PERMISSIVE_LICENSES,
    COPYLEFT_LICENSES,
    get_headers,
    http_get_text,
    parse_repo_slug,
)


def format_license_verdict(license_info: Optional[Dict[str, Any]]) -> str:
    if not license_info or not isinstance(license_info, dict):
        return "🔴 Sin licencia"
    spdx = (license_info.get("spdx_id") or license_info.get("key") or "").lower()
    name = license_info.get("name") or spdx or "Unknown"

    if spdx in PERMISSIVE_LICENSES:
        return f"🟢 Permisiva ({license_info.get('spdx_id') or name})"
    if spdx in COPYLEFT_LICENSES or "gpl" in spdx or "mpl" in spdx or "lgpl" in spdx:
        return f"🟡 Copyleft ({license_info.get('spdx_id') or name})"
    if spdx in ("other", "none", ""):
        return "🔴 Sin licencia / Desconocida"
    return f"🟡 {name}"


def normalize_gh_repo(raw: Dict[str, Any]) -> Dict[str, Any]:
    full_name = raw.get("full_name") or f"{raw.get('owner', {}).get('login', '')}/{raw.get('name', '')}"
    return {
        "full_name": full_name,
        "name": raw.get("name", full_name.split("/")[-1]),
        "html_url": raw.get("html_url") or f"https://github.com/{full_name}",
        "description": raw.get("description") or "",
        "stars": raw.get("stargazers_count", 0),
        "forks": raw.get("forks_count", 0),
        "open_issues": raw.get("open_issues_count", 0),
        "language": raw.get("language") or "Other",
        "size_kb": raw.get("size", 0),
        "updated_at": raw.get("updated_at", ""),
        "pushed_at": raw.get("pushed_at", ""),
        "default_branch": raw.get("default_branch", "main"),
        "topics": raw.get("topics", []) or [],
        "license_verdict": format_license_verdict(raw.get("license")),
    }


def search_github_api(
    query: str,
    limit: int = 15,
    sort: str = "",
    source_prefix: str = "gh",
) -> List[Dict[str, Any]]:
    params = {"q": query, "per_page": str(min(limit, 100))}
    if sort in ("stars", "updated"):
        params["sort"] = sort
        params["order"] = "desc"
    encoded = urllib.parse.urlencode(params)
    url = f"https://api.github.com/search/repositories?{encoded}"
    txt, err = http_get_text(url, timeout=15)
    if not txt or err:
        return []
    try:
        data = json.loads(txt)
        return [normalize_gh_repo(it) for it in data.get("items", []) if not it.get("fork")]
    except Exception:
        return []


def search_hn_algolia(query: str, limit: int = 15) -> List[str]:
    # Returns GitHub repo slugs discovered in Hacker News comments and stories
    encoded = urllib.parse.quote_plus(query)
    url = f"https://hn.algolia.com/api/v1/search?query={encoded}&tags=(story,comment)&hitsPerPage={limit}"
    txt, err = http_get_text(url, timeout=12)
    if not txt or err:
        return []
    try:
        data = json.loads(txt)
        gh_slugs: Set[str] = set()
        slug_regex = re.compile(r"github\.com/([a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+)", re.IGNORECASE)

        for hit in data.get("hits", []):
            blob = json.dumps(hit)
            for m in slug_regex.findall(blob):
                clean = parse_repo_slug(m)
                if "/" in clean and not clean.startswith("topics/") and not clean.endswith(".png"):
                    gh_slugs.add(clean)

        return list(gh_slugs)
    except Exception:
        return []


def search_reddit_public_fallback(query: str, limit: int = 15) -> List[str]:
    # Zero-API Reddit search using public JSON endpoint
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.reddit.com/search.json?q={encoded}&limit={limit}&sort=relevance"
    txt, err = http_get_text(url, timeout=12)
    if not txt or err:
        return []
    try:
        data = json.loads(txt)
        gh_slugs: Set[str] = set()
        slug_regex = re.compile(r"github\.com/([a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+)", re.IGNORECASE)

        children = data.get("data", {}).get("children", [])
        for c in children:
            item = c.get("data", {})
            blob = (item.get("title", "") + " " + item.get("selftext", "") + " " + item.get("url", ""))
            for m in slug_regex.findall(blob):
                clean = parse_repo_slug(m)
                if "/" in clean and not clean.startswith("topics/") and not clean.endswith(".png"):
                    gh_slugs.add(clean)

        return list(gh_slugs)
    except Exception:
        return []


def fetch_repo_metadata(slug: str, source_tag: str = "discovery") -> Optional[Dict[str, Any]]:
    clean_slug = parse_repo_slug(slug)
    url = f"https://api.github.com/repos/{clean_slug}"
    txt, err = http_get_text(url, timeout=12)
    if not txt or err:
        return None
    try:
        raw = json.loads(txt)
        if "id" in raw:
            return normalize_gh_repo(raw)
        return None
    except Exception:
        return None

