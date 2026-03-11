"""Import bookmarks from TXT or CSV files into SQLite."""

import csv
import os
from src.db import get_connection, init_db, insert_bookmark, save_import_stats
from src.utils import normalize_url, extract_domain


def detect_format(filepath):
    """Detect if file is CSV (has commas) or plain text (one URL per line)."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".csv":
        return "csv"
    return "txt"


def read_txt(filepath):
    """Read a text file with one URL per line. Returns list of (url, title)."""
    entries = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                entries.append((line, ""))
    return entries


def read_csv(filepath):
    """Read a CSV file. Looks for 'url' column, optionally 'title'."""
    entries = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return entries

        # Find the URL column (case-insensitive)
        fields_lower = {fn.lower().strip(): fn for fn in reader.fieldnames}
        url_col = None
        for candidate in ["url", "link", "href", "bookmark"]:
            if candidate in fields_lower:
                url_col = fields_lower[candidate]
                break

        if url_col is None:
            # Fall back: treat as single-column, first column is URL
            f.seek(0)
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if row and row[0].strip():
                    entries.append((row[0].strip(), ""))
            return entries

        title_col = fields_lower.get("title", fields_lower.get("name"))

        for row in reader:
            url = row.get(url_col, "").strip()
            title = row.get(title_col, "").strip() if title_col else ""
            if url:
                entries.append((url, title))
    return entries


def import_file(filepath):
    """Import bookmarks from a file. Returns (imported_count, duplicate_count, error_count)."""
    if not os.path.isfile(filepath):
        print(f"Error: file not found: {filepath}")
        return 0, 0, 0

    init_db()
    fmt = detect_format(filepath)
    entries = read_csv(filepath) if fmt == "csv" else read_txt(filepath)

    conn = get_connection()
    imported = 0
    duplicates = 0
    errors = 0

    for url, title in entries:
        try:
            norm = normalize_url(url)
            if not norm:
                errors += 1
                continue
            domain = extract_domain(norm)
            row_id, was_inserted = insert_bookmark(conn, url, norm, title)
            if was_inserted:
                from src.db import update_bookmark
                update_bookmark(conn, row_id, domain=domain)
                imported += 1
            else:
                duplicates += 1
        except Exception as e:
            print(f"  Error importing {url}: {e}")
            errors += 1

    save_import_stats(conn, imported, duplicates, errors)
    conn.commit()
    conn.close()
    print(f"Import complete: {imported} imported, {duplicates} duplicates, {errors} errors")
    return imported, duplicates, errors
