"""
PirateGit Common Library Package
"""

from .utils import (
    CACHE_DIR,
    CACHE_TTL_SECONDS,
    PERMISSIVE_LICENSES,
    COPYLEFT_LICENSES,
    DATA_EXTENSIONS,
    ENGINE_EXTENSIONS,
    MANIFEST_NAMES,
    PROMPT_EXTENSIONS,
    get_headers,
    http_get_text,
    parse_repo_slug,
    fetch_repo_readme_digest,
)
from .scoring import (
    extract_intent_terms,
    score_repository,
)
from .channels import (
    search_github_api,
    search_hn_algolia,
    search_reddit_public_fallback,
    fetch_repo_metadata,
    normalize_gh_repo,
    format_license_verdict,
)
from .tree import (
    get_repo_tree,
    xray_single_repo,
    extract_manifest_deps,
)

__all__ = [
    "CACHE_DIR",
    "CACHE_TTL_SECONDS",
    "PERMISSIVE_LICENSES",
    "COPYLEFT_LICENSES",
    "DATA_EXTENSIONS",
    "ENGINE_EXTENSIONS",
    "MANIFEST_NAMES",
    "PROMPT_EXTENSIONS",
    "get_headers",
    "http_get_text",
    "parse_repo_slug",
    "fetch_repo_readme_digest",
    "extract_intent_terms",
    "score_repository",
    "search_github_api",
    "search_hn_algolia",
    "search_reddit_public_fallback",
    "fetch_repo_metadata",
    "normalize_gh_repo",
    "format_license_verdict",
    "get_repo_tree",
    "xray_single_repo",
    "extract_manifest_deps",
]
