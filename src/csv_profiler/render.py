"""
Report rendering utilities for generating Markdown output.
"""

from __future__ import annotations

from datetime import datetime


def render_markdown(report: dict) -> str:
    """
    Generate a Markdown report from profiling results.

    Args:
        report: Dictionary containing profiling results

    Returns:
        Markdown-formatted string
    """
    lines = []

    # Title and timestamp
    lines.append("# CSV Profiling Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Summary section
    lines.append("## 📊 Summary")
    lines.append("")
    lines.append(f"- **Total Rows:** {report['n_rows']:,}")
    lines.append(f"- **Total Columns:** {report['n_cols']}")
    lines.append("")

    # Overview table
    lines.append("## 📋 Column Overview")
    lines.append("")
    lines.append("| Column | Type | Missing | Missing % | Unique |")
    lines.append("|--------|------|--------:|----------:|-------:|")

    for col in report['columns']:
        name = col['name']
        col_type = col['type']
        missing = col['missing']
        missing_pct = col['missing_pct']
        unique = col['unique']

        lines.append(f"| {name} | {col_type} | {missing} | {missing_pct:.1f}% | {unique} |")

    lines.append("")

    # Detailed statistics per column
    lines.append("## 📈 Detailed Statistics")
    lines.append("")

    for col in report['columns']:
        lines.append(f"### {col['name']}")
        lines.append("")

        # Display quality issues if present
        if col.get('quality_issues'):
            lines.append("**⚠️ Data Quality Issues:**")
            for issue in col['quality_issues']:
                icon = "⚠️" if issue['level'] == 'warning' else "ℹ️"
                lines.append(f"- {icon} {issue['message']}")
            lines.append("")

        lines.append(f"- **Type:** {col['type']}")
        lines.append(f"- **Non-missing count:** {col['count']:,}")
        lines.append(f"- **Missing:** {col['missing']} ({col['missing_pct']:.1f}%)")
        lines.append(f"- **Unique values:** {col['unique']:,}")

        if col['type'] == 'number':
            # Numeric statistics
            if col['min'] is not None:
                lines.append(f"- **Min:** {col['min']:.2f}")
                lines.append(f"- **Max:** {col['max']:.2f}")
                lines.append(f"- **Mean:** {col['mean']:.2f}")
                lines.append(f"- **Median:** {col['median']:.2f}")
                if col.get('mode') is not None:
                    lines.append(f"- **Mode:** {col['mode']:.2f}")
                lines.append(f"- **Std Dev:** {col['std']:.2f}")
                if col.get('q1') is not None:
                    lines.append(f"- **Q1 (25th percentile):** {col['q1']:.2f}")
                    lines.append(f"- **Q3 (75th percentile):** {col['q3']:.2f}")
                    lines.append(f"- **IQR (Interquartile Range):** {col['q3'] - col['q1']:.2f}")
        else:
            # Text statistics - top values
            if col.get('top'):
                lines.append("- **Top values:**")
                for item in col['top']:
                    value = item['value']
                    count = item['count']
                    lines.append(f"  - `{value}`: {count} occurrences")

        lines.append("")

    return "\n".join(lines)
