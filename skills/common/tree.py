#!/usr/bin/env python3
"""
PirateGit Anatomical Zero-Clone Tree Inspector
==============================================
Dissects repository trees via GitHub Git Data Trees API (or raw HTML/zip fallback).
Classifies files into 4 loot buckets and computes code hygiene signals.
"""

from __future__ import annotations

import datetime
import json
import re
from typing import Any, Dict, List, Optional, Tuple

from .utils import (
    MANIFEST_NAMES,
    DATA_EXTENSIONS,
    ENGINE_EXTENSIONS,
    PROMPT_EXTENSIONS,
    get_headers,
    http_get_text,
    parse_repo_slug,
)
from .channels import fetch_repo_metadata


def get_repo_tree(slug: str, branch: str = "main") -> Tuple[List[Dict[str, Any]], str]:
    clean_slug = parse_repo_slug(slug)
    branches_to_try = [branch, "main", "master"] if branch not in ("main", "master") else ["main", "master"]

    for b in branches_to_try:
        url = f"https://api.github.com/repos/{clean_slug}/git/trees/{b}?recursive=1"
        txt, err = http_get_text(url, timeout=18)
        if txt and not err:
            try:
                data = json.loads(txt)
                tree = data.get("tree", [])
                if tree:
                    files = [
                        {"path": item["path"], "size": item.get("size", 0), "type": item.get("type", "blob")}
                        for item in tree
                        if item.get("type") == "blob"
                    ]
                    return files, f"git_tree_api ({b})"
            except Exception:
                pass

    return [], "empty_or_unavailable"


def extract_manifest_deps(slug: str, branch: str, manifest_paths: List[str]) -> Dict[str, List[str]]:
    preview: Dict[str, List[str]] = {}
    for mf in manifest_paths[:4]:
        url = f"https://raw.githubusercontent.com/{slug}/{branch}/{mf}"
        txt, err = http_get_text(url, timeout=10)
        if not txt or err:
            continue
        lines: List[str] = []
        if mf.endswith("requirements.txt"):
            lines = [l.strip() for l in txt.splitlines() if l.strip() and not l.startswith("#")][:15]
        elif mf.endswith("package.json"):
            try:
                pj = json.loads(txt)
                deps = list(pj.get("dependencies", {}).keys()) + list(pj.get("devDependencies", {}).keys())
                lines = deps[:15]
            except Exception:
                pass
        elif mf.endswith("pyproject.toml") or mf.endswith("Cargo.toml"):
            for l in txt.splitlines():
                if "=" in l and not l.strip().startswith("#"):
                    k = l.split("=")[0].strip()
                    if k and k not in lines and len(k) < 30:
                        lines.append(k)
                if len(lines) >= 12:
                    break
        if lines:
            preview[mf] = lines
    return preview


def xray_single_repo(repo: str) -> Dict[str, Any]:
    slug = parse_repo_slug(repo)
    meta = fetch_repo_metadata(slug) or {
        "full_name": slug,
        "name": slug.split("/")[-1],
        "html_url": f"https://github.com/{slug}",
        "stars": 0,
        "license_verdict": "🔴 Sin licencia / Desconocida",
        "default_branch": "main",
        "description": "",
    }
    branch = meta.get("default_branch") or "main"

    files, tree_source = get_repo_tree(slug, branch)

    # 1. Root structure
    top_level: Dict[str, int] = {}
    for f in files:
        p = f["path"]
        parts = p.split("/")
        root_dir = parts[0] if len(parts) > 1 else "<root>"
        top_level[root_dir] = top_level.get(root_dir, 0) + 1

    # 2. Hygiene calculation
    has_tests = any(
        "test" in f["path"].lower() or "spec" in f["path"].lower()
        for f in files
    )
    has_ci = any(
        f["path"].startswith(".github/workflows") or f["path"].startswith(".circleci") or "travis.yml" in f["path"]
        for f in files
    )
    has_docs = any(
        f["path"].lower().startswith("doc") or f["path"].lower().endswith(".md")
        for f in files
    )

    days_since_push = 999
    pushed = meta.get("pushed_at") or meta.get("updated_at") or ""
    if len(pushed) >= 10:
        try:
            pdt = datetime.datetime.strptime(pushed[:10], "%Y-%m-%d").date()
            days_since_push = max(0, (datetime.date.today() - pdt).days)
        except Exception:
            pass

    maint_score = max(0.1, 1.0 - (days_since_push / 365.0)) if days_since_push < 365 else 0.15
    tree_health = round(
        (0.3 if has_tests else 0.0) + (0.3 if has_ci else 0.0) + (0.2 if has_docs else 0.0) + (0.2 * maint_score),
        2,
    )

    # 3. Classify Loot
    data_kb: List[Dict[str, Any]] = []
    core_engine: List[Dict[str, Any]] = []
    prompts_agents: List[Dict[str, Any]] = []
    manifests: List[str] = []

    prompt_kws = {"prompt", "agent", "skill", "mcp", "rule", "instruction"}

    for f in files:
        p = f["path"]
        low_p = p.lower()
        size_kb = round(f.get("size", 0) / 1024, 1)
        filename = p.split("/")[-1]

        if filename in MANIFEST_NAMES or any(low_p.endswith(m) for m in MANIFEST_NAMES):
            manifests.append(p)

        if any(kw in low_p for kw in prompt_kws) and any(low_p.endswith(ext) for ext in PROMPT_EXTENSIONS):
            prompts_agents.append({"path": p, "size_kb": size_kb})

        if any(low_p.endswith(ext) for ext in DATA_EXTENSIONS):
            if not low_p.startswith(".git") and "package-lock" not in low_p and size_kb >= 0.5:
                data_kb.append({"path": p, "size_kb": size_kb})

        if any(low_p.endswith(ext) for ext in ENGINE_EXTENSIONS):
            if "test" not in low_p and "spec" not in low_p and not low_p.startswith("vendor/") and not low_p.startswith("node_modules/"):
                core_engine.append({"path": p, "size_kb": size_kb})

    # Sort loot by size / density
    data_kb.sort(key=lambda x: x["size_kb"], reverse=True)
    core_engine.sort(key=lambda x: x["size_kb"], reverse=True)
    prompts_agents.sort(key=lambda x: x["size_kb"], reverse=True)

    deps_preview = extract_manifest_deps(slug, branch, manifests)

    return {
        "repo": slug,
        "url": f"https://github.com/{slug}",
        "metadata": meta,
        "hygiene": {
            "tree_health_score": tree_health,
            "maintenance_score": round(maint_score, 2),
            "days_since_last_push": days_since_push,
            "has_tests": has_tests,
            "has_ci": has_ci,
        },
        "total_files": len(files),
        "tree_source": tree_source,
        "top_level_structure": dict(sorted(top_level.items(), key=lambda x: x[1], reverse=True)[:10]),
        "loot": {
            "data_and_kb_files": data_kb,
            "core_engine_files": core_engine,
            "prompts_skills_agents": prompts_agents,
        },
        "dependencies_preview": deps_preview,
    }

