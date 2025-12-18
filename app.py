#!/usr/bin/env python3
"""
Streamlit GUI for CSV Profiler.

Usage:
    streamlit run app.py
"""

import sys
import json
import tempfile
from pathlib import Path

# Fix Windows console encoding for Unicode support
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

# Add src directory to Python path
script_dir = Path(__file__).parent.absolute()
src_dir = script_dir / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from csv_profiler.io import read_csv_rows
from csv_profiler.profiling import profile_rows
from csv_profiler.render import render_markdown


st.set_page_config(
    page_title="CSV Profiler",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CSV Profiler")
st.markdown("Upload a CSV file to analyze its structure and statistics")

# Sidebar for file upload
with st.sidebar:
    st.header("Upload CSV File")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file to profile"
    )

    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This tool analyzes CSV files and provides:
    - Column type detection (number vs text)
    - Statistical summaries
    - Missing value detection
    - Top frequent values
    """)

# Main content area
if uploaded_file is not None:
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = Path(tmp_file.name)

        # Read and profile the CSV
        with st.spinner("Reading CSV file..."):
            rows = read_csv_rows(tmp_path)
            # Also create a pandas DataFrame for visualizations
            df = pd.DataFrame(rows)

        with st.spinner("Profiling data..."):
            report = profile_rows(rows)

        # Clean up temp file
        tmp_path.unlink()

        # Display summary metrics
        st.header("📋 Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Rows", f"{report['n_rows']:,}")
        with col2:
            st.metric("Total Columns", report['n_cols'])

        st.markdown("---")

        # Display overview table
        st.header("📊 Column Overview")

        # Create overview data
        overview_data = []
        for col in report['columns']:
            overview_data.append({
                "Column": col['name'],
                "Type": col['type'],
                "Missing": col['missing'],
                "Missing %": f"{col['missing_pct']:.1f}%",
                "Unique": col['unique']
            })

        st.dataframe(overview_data, use_container_width=True)

        st.markdown("---")

        # Detailed statistics per column
        st.header("📈 Detailed Statistics")

        for col in report['columns']:
            with st.expander(f"**{col['name']}** ({col['type']})"):
                # Display quality issues if present
                if col.get('quality_issues'):
                    st.markdown("### ⚠️ Data Quality Issues")
                    for issue in col['quality_issues']:
                        icon = "⚠️" if issue['level'] == 'warning' else "ℹ️"
                        if issue['level'] == 'warning':
                            st.warning(f"{icon} {issue['message']}")
                        else:
                            st.info(f"{icon} {issue['message']}")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Non-missing Count", f"{col['count']:,}")
                with col2:
                    st.metric("Missing", f"{col['missing']} ({col['missing_pct']:.1f}%)")
                with col3:
                    st.metric("Unique Values", f"{col['unique']:,}")

                if col['type'] == 'number':
                    # Numeric statistics
                    if col['min'] is not None:
                        st.markdown("### Basic Statistics")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Min", f"{col['min']:.2f}")
                        with col_b:
                            st.metric("Max", f"{col['max']:.2f}")
                        with col_c:
                            st.metric("Mean", f"{col['mean']:.2f}")

                        st.markdown("### Central Tendency")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Median", f"{col['median']:.2f}")
                        with col_b:
                            if col.get('mode') is not None:
                                st.metric("Mode", f"{col['mode']:.2f}")
                            else:
                                st.metric("Mode", "Multiple")
                        with col_c:
                            st.metric("Std Dev", f"{col['std']:.2f}")

                        if col.get('q1') is not None:
                            st.markdown("### Distribution")
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Q1 (25%)", f"{col['q1']:.2f}")
                            with col_b:
                                st.metric("Q3 (75%)", f"{col['q3']:.2f}")
                            with col_c:
                                st.metric("IQR", f"{col['q3'] - col['q1']:.2f}")

                        # Histogram for numeric columns
                        st.markdown("### 📊 Distribution Histogram")
                        try:
                            numeric_data = pd.to_numeric(df[col['name']], errors='coerce').dropna()
                            if len(numeric_data) > 0:
                                fig = px.histogram(
                                    numeric_data,
                                    nbins=min(30, len(numeric_data.unique())),
                                    title=f"Distribution of {col['name']}",
                                    labels={'value': col['name'], 'count': 'Frequency'}
                                )
                                fig.update_layout(showlegend=False, height=400)
                                st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not generate histogram: {e}")

                else:
                    # Text statistics - top values
                    if col.get('top'):
                        st.markdown("### Top Values")
                        for item in col['top']:
                            st.markdown(f"- **`{item['value']}`**: {item['count']} occurrences")

                        # Bar chart for top values
                        st.markdown("### 📊 Top Values Chart")
                        try:
                            top_values = col['top'][:10]  # Limit to top 10
                            chart_data = pd.DataFrame(top_values)
                            fig = px.bar(
                                chart_data,
                                x='value',
                                y='count',
                                title=f"Top Values in {col['name']}",
                                labels={'value': col['name'], 'count': 'Count'}
                            )
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not generate chart: {e}")

        st.markdown("---")

        # Download buttons
        st.header("💾 Download Reports")

        col1, col2 = st.columns(2)

        with col1:
            # JSON download
            json_str = json.dumps(report, indent=2, ensure_ascii=False)
            st.download_button(
                label="📄 Download JSON Report",
                data=json_str,
                file_name="report.json",
                mime="application/json"
            )

        with col2:
            # Markdown download
            markdown_str = render_markdown(report)
            st.download_button(
                label="📝 Download Markdown Report",
                data=markdown_str,
                file_name="report.md",
                mime="text/markdown"
            )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")

else:
    # Welcome message
    st.info("👈 Upload a CSV file using the sidebar to get started!")

    st.markdown("### Sample Usage")
    st.markdown("""
    1. Click **'Browse files'** in the sidebar
    2. Select a CSV file from your computer
    3. View the profiling results
    4. Download JSON or Markdown reports
    """)

    st.markdown("### Features")
    st.markdown("""
    - **Automatic Type Detection**: Identifies numeric and text columns
    - **Statistical Summaries**: Min, max, mean for numbers; top values for text
    - **Missing Value Detection**: Detects empty cells and various null representations
    - **Export Options**: Download reports in JSON or Markdown format
    """)
