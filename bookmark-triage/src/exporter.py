"""Export bookmarks to CSV files and generate summary report."""

import csv
import os
from datetime import datetime
from src.db import get_connection, get_bookmarks, count_bookmarks

EXPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "exports")

CSV_FIELDS = ["id", "original_url", "normalized_url", "title", "domain",
              "site_bucket", "status", "is_build_candidate", "candidate_reason"]


def _write_csv(filename, rows):
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    filepath = os.path.join(EXPORTS_DIR, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in CSV_FIELDS})
    print(f"  Exported {len(rows)} rows to {filename}")
    return filepath


def export_all():
    """Export all bucket CSVs and build candidates."""
    conn = get_connection()

    # Build candidates
    candidates = get_bookmarks(conn, "is_build_candidate = 1")
    _write_csv("build_candidates.csv", candidates)

    # Per-bucket exports
    bucket_files = {
        "instagram": "instagram_bucket.csv",
        "youtube": "youtube_bucket.csv",
        "x": "x_bucket.csv",
    }
    for bucket, filename in bucket_files.items():
        rows = get_bookmarks(conn, "site_bucket = ?", (bucket,))
        _write_csv(filename, rows)

    # Everything else (not in the named buckets and not build candidates)
    named_buckets = tuple(bucket_files.keys())
    placeholders = ",".join("?" for _ in named_buckets)
    others = get_bookmarks(
        conn,
        f"site_bucket NOT IN ({placeholders}) AND is_build_candidate = 0",
        named_buckets,
    )
    _write_csv("other_buckets.csv", others)

    conn.close()
    print("Export complete.")


def print_summary():
    """Print a console summary of the database state."""
    conn = get_connection()

    total = count_bookmarks(conn)
    dupes = count_bookmarks(conn, "status = 'duplicate'")
    candidates = count_bookmarks(conn, "is_build_candidate = 1")

    # Bucket counts
    rows = conn.execute(
        "SELECT site_bucket, COUNT(*) as cnt FROM bookmarks WHERE status != 'duplicate' GROUP BY site_bucket ORDER BY cnt DESC"
    ).fetchall()

    print("\n=== Bookmark Triage Summary ===")
    print(f"Total imported:      {total}")
    print(f"Duplicates skipped:  {dupes}")
    print(f"Build candidates:    {candidates}")
    print(f"\nBookmarks by bucket:")
    for row in rows:
        bucket = row["site_bucket"] or "(none)"
        print(f"  {bucket:20s} {row['cnt']}")

    conn.close()
    return total, dupes, candidates


def write_summary_report():
    """Write a summary report file to data/exports/."""
    conn = get_connection()
    os.makedirs(EXPORTS_DIR, exist_ok=True)

    total = count_bookmarks(conn)
    dupes = count_bookmarks(conn, "status = 'duplicate'")
    candidates = count_bookmarks(conn, "is_build_candidate = 1")
    rows = conn.execute(
        "SELECT site_bucket, COUNT(*) as cnt FROM bookmarks WHERE status != 'duplicate' GROUP BY site_bucket ORDER BY cnt DESC"
    ).fetchall()

    filepath = os.path.join(EXPORTS_DIR, "summary_report.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Bookmark Triage Summary Report\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"{'='*40}\n\n")
        f.write(f"Total bookmarks:     {total}\n")
        f.write(f"Duplicates skipped:  {dupes}\n")
        f.write(f"Build candidates:    {candidates}\n\n")
        f.write(f"Bookmarks by bucket:\n")
        for row in rows:
            bucket = row["site_bucket"] or "(none)"
            f.write(f"  {bucket:20s} {row['cnt']}\n")

    conn.close()
    print(f"  Summary report written to {filepath}")
