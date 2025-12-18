"""
CSV file reading utilities.
"""

from __future__ import annotations

import csv
from pathlib import Path


def read_csv_rows(path: Path | str) -> list[dict[str, str]]:
    """
    Read a CSV file and return rows as a list of dictionaries.

    Args:
        path: Path to the CSV file

    Returns:
        List of dictionaries where keys are column names and values are cell values

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the CSV has no rows
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    rows = []
    try:
        with open(path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")

    if not rows:
        raise ValueError(f"CSV file has no data rows: {path}")

    return rows
