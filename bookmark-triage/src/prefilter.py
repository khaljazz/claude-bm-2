"""Cheap keyword-based pre-filter to flag likely build-related bookmarks."""

import re
from src.db import get_connection, get_bookmarks, update_bookmark

# Buckets that are strong build signals on their own
BUILD_BUCKETS = {"github", "stackoverflow", "docs"}

# Keywords to match against URL path + title (case-insensitive)
BUILD_KEYWORDS = [
    "ai", "llm", "gpt", "model", "transformer", "neural", "machine-learning",
    "ml", "deep-learning", "nlp", "embedding",
    "coding", "code", "python", "javascript", "typescript", "rust", "golang",
    "api", "sdk", "rest", "graphql", "endpoint", "webhook",
    "github", "repo", "repository", "git", "open-source",
    "agent", "agentic", "multi-agent", "crew", "langchain", "langgraph",
    "autogen", "llamaindex",
    "automation", "automate", "workflow", "pipeline", "ci-cd", "n8n", "zapier",
    "tutorial", "guide", "docs", "documentation", "reference", "handbook",
    "developer", "dev", "devtools", "devops",
    "local", "self-hosted", "ollama", "llama", "mistral", "gemma",
    "fastapi", "flask", "django", "nextjs", "react", "svelte", "vue",
    "docker", "kubernetes", "container",
    "script", "build", "deploy", "serverless", "lambda",
    "database", "sql", "sqlite", "postgres", "redis", "supabase",
    "cli", "terminal", "shell", "bash", "powershell",
    "vscode", "extension", "plugin", "package", "library", "framework",
    "prompt", "fine-tune", "finetune", "rag", "retrieval",
    "cursor", "copilot", "claude", "anthropic", "openai", "huggingface",
]

# Pre-compile a single regex for speed
_kw_pattern = re.compile(
    r"\b(" + "|".join(re.escape(kw) for kw in BUILD_KEYWORDS) + r")\b",
    re.IGNORECASE,
)


def check_build_candidate(bookmark):
    """Check if a bookmark is a build candidate. Returns (is_candidate, reason)."""
    reasons = []

    bucket = bookmark["site_bucket"] or ""
    if bucket in BUILD_BUCKETS:
        reasons.append(f"bucket:{bucket}")

    # Check URL path and title for keywords
    text = (bookmark["original_url"] or "") + " " + (bookmark["title"] or "")
    matches = set(_kw_pattern.findall(text.lower()))
    if matches:
        reasons.append("keywords:" + ",".join(sorted(matches)[:5]))

    return bool(reasons), "; ".join(reasons)


def prefilter_all():
    """Run pre-filter on all bucketed bookmarks."""
    conn = get_connection()
    bookmarks = get_bookmarks(conn, "status = 'bucketed'")

    candidate_count = 0
    for bm in bookmarks:
        is_candidate, reason = check_build_candidate(bm)
        if is_candidate:
            update_bookmark(conn, bm["id"],
                            is_build_candidate=1,
                            candidate_reason=reason,
                            status="candidate")
            candidate_count += 1
        else:
            update_bookmark(conn, bm["id"], status="side_bucket")

    conn.commit()
    conn.close()

    total = len(bookmarks)
    print(f"Pre-filter complete: {candidate_count} build candidates out of {total} bookmarks")
    return candidate_count, total
