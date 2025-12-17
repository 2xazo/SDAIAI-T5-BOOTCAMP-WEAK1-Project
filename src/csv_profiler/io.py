"""CSV file reading utilities."""

from __future__ import annotations

import csv
from pathlib import Path


def read_csv_rows(path: Path | str) -> list[dict[str, str]]:
    """
    Read a CSV file and return rows as list of dictionaries.
    
    Args:
        path: Path to the CSV file
        
    Returns:
        List of dictionaries, where each dict represents one row
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the CSV has no data rows
    """
    # Convert to Path object if string
    path = Path(path)
    
    # Check if file exists
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    
    # Read the CSV file
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Check if CSV has data
    if not rows:
        raise ValueError(f"CSV file has no data rows: {path}")
    
    return rows