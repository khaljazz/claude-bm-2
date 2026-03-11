"""URL normalization and helpers."""

from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


# Tracking params to strip
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_id", "fbclid", "gclid", "ref", "source",
}


def normalize_url(url):
    """Light normalization: lowercase host, strip fragment, strip trailing slash, remove tracking params."""
    url = url.strip()
    if not url:
        return ""

    # Add scheme if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)

    # Lowercase the host
    host = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port and parsed.port not in (80, 443) else ""

    # Strip tracking params
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    filtered = {k: v for k, v in query_params.items() if k.lower() not in TRACKING_PARAMS}
    clean_query = urlencode(filtered, doseq=True) if filtered else ""

    # Rebuild: no fragment, strip trailing slash from path
    path = parsed.path.rstrip("/") or ""

    normalized = urlunparse((
        parsed.scheme,
        host + port,
        path,
        parsed.params,
        clean_query,
        "",  # no fragment
    ))
    return normalized


def extract_domain(url):
    """Extract the domain from a URL, stripping www."""
    try:
        parsed = urlparse(url if "://" in url else "https://" + url)
        host = parsed.hostname or ""
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return ""
