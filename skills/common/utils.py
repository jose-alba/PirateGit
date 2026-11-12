#!/usr/bin/env python3
"""
PirateGit Common Utilities & Zero-Quota Network Helpers
"""

from __future__ import annotations

import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CACHE_DIR = Path.home() / ".gemini" / "cache" / "agy_github_scout_cache"
CACHE_TTL_SECONDS = 3600 * 12

PERMISSIVE_LICENSES = {
    "mit", "apache-2.0", "bsd-2-clause", "bsd-3-clause", "isc", "unlicense", "cc0-1.0", "boost-1.0"
}
COPYLEFT_LICENSES = {
    "gpl-2.0", "gpl-3.0", "agpl-3.0", "lgpl-2.1", "lgpl-3.0", "mpl-2.0", "epl-2.0"
}

DATA_EXTENSIONS = {
    ".json", ".geojson", ".csv", ".tsv", ".parquet", ".xml", ".yaml", ".yml", ".txt", ".h5", ".npy",
    ".kicad_sym", ".kicad_mod", ".kicad_sch", ".kicad_pcb", ".sqlite", ".sqlite3", ".db"
}
ENGINE_EXTENSIONS = {
    ".py", ".cpp", ".c", ".h", ".hpp", ".rs", ".go", ".ts", ".js", ".java", ".cs", ".rb"
}
MANIFEST_NAMES = {
    "requirements.txt", "package.json", "Cargo.toml", "pyproject.toml", "setup.py", "go.mod", "Gemfile", "pom.xml"
}
PROMPT_EXTENSIONS = {
    ".md", ".json", ".yaml", ".txt", ".py"
}


def get_headers() -> Dict[str, str]:
    headers = {
        "User-Agent": "PirateGit-Scout/1.0 (Antigravity-Agent)",
        "Accept": "application/vnd.github.v3+json, text/plain, */*",
    }
    gh_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if gh_token:
        headers["Authorization"] = f"Bearer {gh_token}"
    return headers


def parse_repo_slug(repo: str) -> str:
    cleaned = repo.strip()
    cleaned = re.sub(r"^https?://github\.com/", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.rstrip("/").removesuffix(".git")
    parts = cleaned.split("/")
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    return cleaned


def http_get_text(url: str, timeout: int = 15) -> Tuple[Optional[str], Optional[str]]:
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            # Try utf-8 first, fallback to latin-1
            try:
                return content.decode("utf-8"), None
            except UnicodeDecodeError:
                return content.decode("latin-1", errors="replace"), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return None, str(e)


def fetch_repo_readme_digest(
    full_name: str,
    branch: str = "main",
    max_lines: int = 16,
    max_chars: int = 800,
) -> str:
    readme_candidates = [
        "README.md",
        "readme.md",
        "README.rst",
        "README.txt",
        "README",
    ]
    branches = [branch, "main", "master"] if branch not in ("main", "master") else ["main", "master"]

    for b in branches:
        for r_name in readme_candidates:
            url = f"https://raw.githubusercontent.com/{full_name}/{b}/{r_name}"
            txt, err = http_get_text(url, timeout=10)
            if txt and not err:
                # Clean badges and html comments/tags
                cleaned = re.sub(r"\[!\[.*?\]\(.*?\)\]\(.*?\)", "", txt)
                cleaned = re.sub(r"!\[.*?\]\(.*?\)", "", cleaned)
                cleaned = re.sub(r"<img[^>]*>", "", cleaned)
                cleaned = re.sub(r"<!--[\s\S]*?-->", "", cleaned)
                lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
                # Keep up to max_lines non-empty lines
                digest = " ".join(lines[:max_lines])
                digest = re.sub(r"\s+", " ", digest).strip()
                if len(digest) > max_chars:
                    digest = digest[:max_chars].rstrip() + "..."
                return digest if digest else "[Empty or non-text README]"

    return "[No README found in main/master]"
