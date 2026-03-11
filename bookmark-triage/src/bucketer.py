"""Mechanical domain-based bucketing. No AI, just deterministic rules."""

from src.db import get_connection, get_bookmarks, update_bookmark

# Domain-to-bucket mapping (checked with endswith for flexibility)
DOMAIN_BUCKETS = {
    "x.com": "x",
    "twitter.com": "x",
    "instagram.com": "instagram",
    "youtube.com": "youtube",
    "youtu.be": "youtube",
    "github.com": "github",
    "gitlab.com": "github",
    "bitbucket.org": "github",
    "reddit.com": "reddit",
    "old.reddit.com": "reddit",
    "stackoverflow.com": "stackoverflow",
    "stackexchange.com": "stackoverflow",
    "superuser.com": "stackoverflow",
    "serverfault.com": "stackoverflow",
    "askubuntu.com": "stackoverflow",
}

# Domains/patterns that indicate documentation
DOCS_PATTERNS = [
    "docs.", "developer.", "devdocs.", "readthedocs.",
    "gitbook.io", "readme.io", "docusaurus",
    "docs.python.org", "docs.microsoft.com", "learn.microsoft.com",
    "docs.github.com", "docs.google.com", "docs.aws.amazon.com",
    "wiki.", "documentation.",
]


def classify_domain(domain):
    """Return a site_bucket string for a given domain."""
    if not domain:
        return "other"

    # Exact match first
    if domain in DOMAIN_BUCKETS:
        return DOMAIN_BUCKETS[domain]

    # Check docs patterns
    for pattern in DOCS_PATTERNS:
        if domain.startswith(pattern) or pattern in domain:
            return "docs"

    # Subdomain match (e.g. m.youtube.com)
    for key, bucket in DOMAIN_BUCKETS.items():
        if domain.endswith("." + key):
            return bucket

    return "web"


def bucket_all():
    """Assign site_bucket to all unbucketed bookmarks."""
    conn = get_connection()
    bookmarks = get_bookmarks(conn, "site_bucket = '' OR site_bucket IS NULL")

    counts = {}
    for bm in bookmarks:
        bucket = classify_domain(bm["domain"])
        update_bookmark(conn, bm["id"], site_bucket=bucket, status="bucketed")
        counts[bucket] = counts.get(bucket, 0) + 1

    conn.commit()
    conn.close()

    print("Bucketing complete:")
    for bucket, count in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {bucket}: {count}")
    return counts
