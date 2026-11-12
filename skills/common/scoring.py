#!/usr/bin/env python3
"""
DeepGit Composite Scoring Formula
=================================
Signals:
- relevance (0.0 - 1.0): token overlap with queries/topics + match hits
- maintenance (0.0 - 1.0): freshness based on updated_at / pushed_at
- popularity (0.0 - 1.0): log-scaled star count
- health (0.0 - 1.0): license status, description, size
- composite_score (0.0 - 1.0): 0.45*rel + 0.25*pop + 0.20*maint + 0.10*health
"""

from __future__ import annotations

import datetime
import math
import re
from typing import Any, Dict, List, Set


def extract_intent_terms(queries: List[str], derived_topics: List[str]) -> Set[str]:
    terms: Set[str] = set()
    token_re = re.compile(r"[a-z0-9_-]+")
    for text in queries + derived_topics:
        for w in token_re.findall(text.lower()):
            if len(w) >= 3 and not w.isdigit():
                terms.add(w)
    return terms


def score_repository(repo: Dict[str, Any], intent_terms: Set[str]) -> None:
    # 1. Relevance calculation
    searchable_text = " ".join([
        repo.get("name", ""),
        repo.get("full_name", ""),
        repo.get("description", "") or "",
        " ".join(repo.get("topics", []) or []),
        repo.get("readme_digest", "") or "",
    ]).lower()

    if intent_terms:
        matches = sum(1 for t in intent_terms if t in searchable_text)
        term_ratio = matches / len(intent_terms)
    else:
        term_ratio = 0.5

    hit_count = repo.get("hit_count", 1)
    hit_bonus = min(0.3, (hit_count - 1) * 0.08)
    relevance = min(1.0, term_ratio * 0.7 + hit_bonus)

    # 2. Popularity (logarithmic scaling: 1000 stars -> ~0.75, 10000 -> 1.0)
    stars = max(0, int(repo.get("stars", 0)))
    if stars > 0:
        popularity = min(1.0, math.log10(stars + 1) / 4.0)
    else:
        popularity = 0.05

    # 3. Maintenance / Freshness
    pushed_at = repo.get("pushed_at") or repo.get("updated_at") or ""
    freshness = pushed_at[:10] if len(pushed_at) >= 10 else "Unknown"
    days_ago = 999
    if freshness != "Unknown":
        try:
            dt = datetime.datetime.strptime(freshness, "%Y-%m-%d").date()
            days_ago = max(0, (datetime.date.today() - dt).days)
        except Exception:
            pass

    if days_ago <= 30:
        maintenance = 1.0
    elif days_ago <= 90:
        maintenance = 0.85
    elif days_ago <= 180:
        maintenance = 0.70
    elif days_ago <= 365:
        maintenance = 0.50
    elif days_ago <= 730:
        maintenance = 0.30
    else:
        maintenance = 0.15

    # 4. Health & License
    lic = str(repo.get("license_verdict", ""))
    if "🟢" in lic:
        lic_score = 1.0
    elif "🟡" in lic:
        lic_score = 0.65
    else:
        lic_score = 0.30

    desc_score = 1.0 if (repo.get("description") and len(repo["description"]) > 15) else 0.4
    health = 0.6 * lic_score + 0.4 * desc_score

    # Composite Score
    composite = round(
        0.45 * relevance + 0.25 * popularity + 0.20 * maintenance + 0.10 * health,
        3,
    )

    repo["signals"] = {
        "composite_score": composite,
        "relevance": round(relevance, 2),
        "maintenance": round(maintenance, 2),
        "popularity": round(popularity, 2),
        "health": round(health, 2),
        "freshness": f"{days_ago}d ago" if days_ago < 999 else freshness,
    }
