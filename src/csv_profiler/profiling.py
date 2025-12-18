"""
Core data profiling logic for CSV analysis.
"""

from __future__ import annotations

from collections import Counter


def detect_quality_issues(col_profile: dict, n_rows: int) -> list[dict]:
    """
    Detect data quality issues in a column.

    Args:
        col_profile: Column profile dictionary
        n_rows: Total number of rows in dataset

    Returns:
        List of quality issue dictionaries with 'level' (warning/info) and 'message'
    """
    issues = []

    # High missing percentage
    if col_profile['missing_pct'] > 50:
        issues.append({
            "level": "warning",
            "message": f"High missing data: {col_profile['missing_pct']:.1f}% of values are missing"
        })
    elif col_profile['missing_pct'] > 20:
        issues.append({
            "level": "info",
            "message": f"Moderate missing data: {col_profile['missing_pct']:.1f}% of values are missing"
        })

    # Low cardinality (very few unique values for large dataset)
    if n_rows > 100 and col_profile['unique'] < 5 and col_profile['type'] != 'text':
        issues.append({
            "level": "info",
            "message": f"Low cardinality: Only {col_profile['unique']} unique values in {n_rows} rows"
        })

    # All values unique (potential identifier)
    if col_profile['unique'] == col_profile['count'] and col_profile['count'] > 10:
        issues.append({
            "level": "info",
            "message": "All values are unique - this may be an identifier column"
        })

    # Numeric column specific checks
    if col_profile['type'] == 'number' and col_profile.get('std') is not None:
        # Check for potential outliers using IQR method
        if col_profile.get('q1') is not None and col_profile.get('q3') is not None:
            iqr = col_profile['q3'] - col_profile['q1']
            lower_bound = col_profile['q1'] - 1.5 * iqr
            upper_bound = col_profile['q3'] + 1.5 * iqr

            if col_profile['min'] < lower_bound or col_profile['max'] > upper_bound:
                issues.append({
                    "level": "info",
                    "message": f"Potential outliers detected (values outside [{lower_bound:.2f}, {upper_bound:.2f}])"
                })

        # High standard deviation relative to mean (high variability)
        if col_profile['mean'] != 0 and col_profile['std'] / abs(col_profile['mean']) > 1:
            issues.append({
                "level": "info",
                "message": f"High variability: Standard deviation ({col_profile['std']:.2f}) is large relative to mean ({col_profile['mean']:.2f})"
            })

    # Text column specific checks
    if col_profile['type'] == 'text':
        # Single dominant value
        if col_profile.get('top') and len(col_profile['top']) > 0:
            top_count = col_profile['top'][0]['count']
            top_pct = (top_count / n_rows) * 100
            if top_pct > 90:
                issues.append({
                    "level": "info",
                    "message": f"Single dominant value: '{col_profile['top'][0]['value']}' appears in {top_pct:.1f}% of rows"
                })

    return issues


def is_missing(value: str | None) -> bool:
    """
    Check if a value is considered missing.

    Missing values include: None, empty string, "na", "n/a", "null", "none", "nan"
    (case-insensitive, whitespace is stripped).

    Args:
        value: The value to check

    Returns:
        True if the value is missing, False otherwise
    """
    if value is None:
        return True

    value_stripped = value.strip().lower()

    if value_stripped == "":
        return True

    if value_stripped in {"na", "n/a", "null", "none", "nan"}:
        return True

    return False


def try_float(value: str) -> float | None:
    """
    Safely convert a string to float.

    Args:
        value: The string to convert

    Returns:
        Float value if conversion succeeds, None otherwise
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def infer_type(values: list[str]) -> str:
    """
    Infer the type of a column based on its values.

    Args:
        values: List of string values from the column

    Returns:
        "number" if all non-missing values can be parsed as floats,
        "text" otherwise
    """
    non_missing = [v for v in values if not is_missing(v)]

    if not non_missing:
        return "text"

    # Check if all non-missing values can be converted to float
    for val in non_missing:
        if try_float(val) is None:
            return "text"

    return "number"


def numeric_stats(values: list[str]) -> dict:
    """
    Calculate statistics for numeric columns.

    Args:
        values: List of string values from the column

    Returns:
        Dictionary with keys: count, missing, unique, min, max, mean, median, mode, std, q1, q3
    """
    total_count = len(values)
    missing_count = sum(1 for v in values if is_missing(v))
    non_missing_count = total_count - missing_count

    non_missing_values = [v for v in values if not is_missing(v)]
    floats = [try_float(v) for v in non_missing_values]
    floats = [f for f in floats if f is not None]

    unique_count = len(set(floats))

    stats = {
        "count": non_missing_count,
        "missing": missing_count,
        "missing_pct": round(missing_count / total_count * 100, 1) if total_count > 0 else 0.0,
        "unique": unique_count,
    }

    if floats:
        sorted_floats = sorted(floats)
        n = len(sorted_floats)

        # Basic stats
        stats["min"] = min(floats)
        stats["max"] = max(floats)
        stats["mean"] = sum(floats) / len(floats)

        # Median
        if n % 2 == 0:
            stats["median"] = (sorted_floats[n//2 - 1] + sorted_floats[n//2]) / 2
        else:
            stats["median"] = sorted_floats[n//2]

        # Mode (most frequent value)
        freq_map = {}
        for val in floats:
            freq_map[val] = freq_map.get(val, 0) + 1
        max_freq = max(freq_map.values())
        modes = [k for k, v in freq_map.items() if v == max_freq]
        stats["mode"] = modes[0] if len(modes) == 1 else None  # Only if unique mode exists

        # Standard deviation
        mean = stats["mean"]
        variance = sum((x - mean) ** 2 for x in floats) / len(floats)
        stats["std"] = variance ** 0.5

        # Quartiles
        if n >= 4:
            stats["q1"] = sorted_floats[n // 4]
            stats["q3"] = sorted_floats[(3 * n) // 4]
        else:
            stats["q1"] = None
            stats["q3"] = None
    else:
        stats["min"] = None
        stats["max"] = None
        stats["mean"] = None
        stats["median"] = None
        stats["mode"] = None
        stats["std"] = None
        stats["q1"] = None
        stats["q3"] = None

    return stats


def text_stats(values: list[str], top_k: int = 5) -> dict:
    """
    Calculate statistics for text columns.

    Args:
        values: List of string values from the column
        top_k: Number of top frequent values to return

    Returns:
        Dictionary with keys: count, missing, unique, top
        "top" is a list of dicts with "value" and "count" keys
    """
    total_count = len(values)
    missing_count = sum(1 for v in values if is_missing(v))
    non_missing_count = total_count - missing_count

    non_missing_values = [v for v in values if not is_missing(v)]
    unique_count = len(set(non_missing_values))

    # Get top K most frequent values
    counter = Counter(non_missing_values)
    top_items = counter.most_common(top_k)
    top_list = [{"value": value, "count": count} for value, count in top_items]

    stats = {
        "count": non_missing_count,
        "missing": missing_count,
        "missing_pct": round(missing_count / total_count * 100, 1) if total_count > 0 else 0.0,
        "unique": unique_count,
        "top": top_list,
    }

    return stats


def profile_rows(rows: list[dict[str, str]]) -> dict:
    """
    Profile all columns in the dataset.

    Args:
        rows: List of dictionaries representing rows

    Returns:
        Dictionary with profiling report containing:
        - n_rows: number of rows
        - n_cols: number of columns
        - columns: list of column profiles
    """
    if not rows:
        return {
            "n_rows": 0,
            "n_cols": 0,
            "columns": [],
        }

    n_rows = len(rows)
    column_names = list(rows[0].keys())
    n_cols = len(column_names)

    columns_profile = []

    for col_name in column_names:
        # Extract all values for this column
        values = [row.get(col_name, "") for row in rows]

        # Infer the type
        col_type = infer_type(values)

        # Calculate statistics based on type
        if col_type == "number":
            stats = numeric_stats(values)
            col_profile = {
                "name": col_name,
                "type": col_type,
                **stats,
            }
        else:  # text
            stats = text_stats(values)
            col_profile = {
                "name": col_name,
                "type": col_type,
                **stats,
            }

        # Detect data quality issues
        quality_issues = detect_quality_issues(col_profile, n_rows)
        if quality_issues:
            col_profile["quality_issues"] = quality_issues

        columns_profile.append(col_profile)

    return {
        "n_rows": n_rows,
        "n_cols": n_cols,
        "columns": columns_profile,
    }
