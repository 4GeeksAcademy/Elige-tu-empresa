"""Import a CSV by trimming values and normalizing its column names.

Usage: python demo-importer.py input.csv output.csv
"""

import argparse
import csv
from pathlib import Path


def normalize_header(header: str) -> str:
    return "_".join(header.strip().lower().split())


def import_csv(source: Path, destination: Path) -> None:
    if source.resolve() == destination.resolve():
        raise ValueError("Source and destination must be different files.")

    with source.open("r", encoding="utf-8", newline="") as source_file:
        reader = csv.reader(source_file)
        headers = next(reader, None)
        if headers is None:
            raise ValueError("The source CSV is empty.")

        normalized_headers = [normalize_header(header) for header in headers]
        if any(not header for header in normalized_headers):
            raise ValueError("Column names cannot be empty.")
        if len(normalized_headers) != len(set(normalized_headers)):
            raise ValueError("Column names must be unique after normalization.")

        with destination.open("w", encoding="utf-8", newline="") as destination_file:
            writer = csv.writer(destination_file)
            writer.writerow(normalized_headers)
            for line_number, row in enumerate(reader, start=2):
                if len(row) != len(normalized_headers):
                    raise ValueError(f"Unexpected number of columns on line {line_number}.")
                writer.writerow([value.strip() for value in row])


def main() -> None:
    parser = argparse.ArgumentParser(description="Import and normalize a CSV file.")
    parser.add_argument("source", type=Path, help="Path to the input CSV.")
    parser.add_argument("destination", type=Path, help="Path to the output CSV.")
    args = parser.parse_args()
    import_csv(args.source, args.destination)


if __name__ == "__main__":
    main()
