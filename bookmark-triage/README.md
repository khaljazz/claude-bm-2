# Bookmark Triage Tool

A local Python tool to import, bucket, and pre-filter ~6000 bookmarks. Phases 1-3: no AI/LLM integration yet.

## What it does

1. **Import** bookmarks from TXT or CSV files into SQLite
2. **Bucket** them by domain (GitHub, YouTube, Reddit, X, Instagram, StackOverflow, docs, web, other)
3. **Pre-filter** to flag build-related candidates (AI, coding, APIs, tools, repos, docs, workflows)
4. **Export** CSVs per bucket + build candidates + summary report

## Setup (Windows 10)

```
cd bookmark-triage
```

No dependencies to install — uses Python standard library only.

## Usage

Place your bookmark file in `data/input/`. Supported formats:
- `.txt` — one URL per line
- `.csv` — must have a column named `url` (or `link`/`href`), optionally `title`

### Run full pipeline

```
python src/main.py all data/input/bookmarks.txt
```

### Run individual steps

```
python src/main.py import data/input/bookmarks.csv
python src/main.py bucket
python src/main.py prefilter
python src/main.py export
python src/main.py summary
```

## Output

After running, you'll find in `data/exports/`:
- `build_candidates.csv` — bookmarks flagged as build-related
- `instagram_bucket.csv`
- `youtube_bucket.csv`
- `x_bucket.csv`
- `other_buckets.csv`
- `summary_report.txt`

The SQLite database is at `data/bookmarks.db`.

## Project structure

```
bookmark-triage/
  data/
    input/          ← put your bookmark files here
    exports/        ← CSV exports land here
    bookmarks.db    ← SQLite database (auto-created)
  src/
    main.py         ← CLI entry point
    db.py           ← database schema and helpers
    importer.py     ← TXT/CSV file import
    bucketer.py     ← domain-based bucketing
    prefilter.py    ← keyword-based build candidate detection
    exporter.py     ← CSV export and summary report
    utils.py        ← URL normalization
```
