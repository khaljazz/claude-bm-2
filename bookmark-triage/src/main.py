"""CLI entry point for bookmark triage tool."""

import sys
import os

# Allow running as: python src/main.py  (from bookmark-triage/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.db import init_db
from src.importer import import_file
from src.bucketer import bucket_all
from src.prefilter import prefilter_all
from src.exporter import export_all, print_summary, write_summary_report

USAGE = """
Bookmark Triage Tool — Phases 1-3

Usage:
  python src/main.py import <file>    Import bookmarks from a TXT or CSV file
  python src/main.py bucket           Bucket all bookmarks by domain
  python src/main.py prefilter        Flag build-related candidates
  python src/main.py export           Export CSVs and summary report
  python src/main.py all <file>       Run full pipeline (import → bucket → prefilter → export)
  python src/main.py summary          Print summary to console
"""


def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "import":
        if len(sys.argv) < 3:
            print("Error: provide an input file path")
            print("  python src/main.py import data/input/bookmarks.txt")
            sys.exit(1)
        filepath = sys.argv[2]
        init_db()
        import_file(filepath)

    elif command == "bucket":
        bucket_all()

    elif command == "prefilter":
        prefilter_all()

    elif command == "export":
        print("Exporting CSVs...")
        export_all()
        write_summary_report()
        print_summary()

    elif command == "all":
        if len(sys.argv) < 3:
            print("Error: provide an input file path")
            print("  python src/main.py all data/input/bookmarks.txt")
            sys.exit(1)
        filepath = sys.argv[2]

        print("Step 1/4: Importing...")
        init_db()
        import_file(filepath)

        print("\nStep 2/4: Bucketing...")
        bucket_all()

        print("\nStep 3/4: Pre-filtering...")
        prefilter_all()

        print("\nStep 4/4: Exporting...")
        export_all()
        write_summary_report()
        print_summary()

    elif command == "summary":
        print_summary()

    else:
        print(f"Unknown command: {command}")
        print(USAGE)
        sys.exit(1)


if __name__ == "__main__":
    main()
