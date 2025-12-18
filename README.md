# CSV Profiler

A powerful command-line tool for profiling CSV files and generating comprehensive data quality reports.

## Features

- **Advanced Statistics**: Mean, median, mode, standard deviation, quartiles, IQR
- **Data Quality Checks**: Automatic detection of missing data, outliers, and anomalies
- **Multiple Output Formats**: JSON and Markdown reports
- **Interactive GUI**: Optional Streamlit interface with visualizations
- **Fast & Efficient**: Processes datasets in milliseconds

## Installation

```bash
# Clone or download the project
cd csv-profiler

# Install dependencies
uv pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```bash
# Profile a CSV file
python run.py data/sample.csv

# Specify output directory
python run.py myfile.csv -o reports

# Custom report name
python run.py myfile.csv -n analysis

# Quiet mode (no progress output)
python run.py myfile.csv -q
```

### All Options

```bash
python run.py [CSV_FILE] [OPTIONS]

Options:
  -o, --out-dir PATH   Output directory (default: outputs)
  -n, --name TEXT      Report name (default: report)
  -q, --quiet          Suppress progress messages
  --help               Show help message
```

## Examples

```bash
# Basic profiling
python run.py sales_data.csv

# Custom output location and name
python run.py sales_data.csv -o monthly_reports -n january_2025

# Multiple files
python run.py file1.csv -n report1
python run.py file2.csv -n report2

# Quiet mode for automation
python run.py data.csv -q
```

## Output

The profiler generates two files:

### 1. JSON Report (`report.json`)
Machine-readable format with complete statistics:
- Row and column counts
- Type detection (numeric/text)
- Statistical metrics (mean, median, mode, std, quartiles)
- Missing value analysis
- Data quality warnings

### 2. Markdown Report (`report.md`)
Human-readable format with:
- Summary statistics
- Column overview table
- Detailed statistics per column
- Quality issue warnings

## Statistical Metrics

### Numeric Columns
- **Basic**: Count, Missing, Unique
- **Range**: Min, Max
- **Central Tendency**: Mean, Median, Mode
- **Spread**: Standard Deviation
- **Distribution**: Q1, Q3, IQR

### Text Columns
- Count, Missing, Unique
- Top frequent values

## Data Quality Checks

Automatically detects:
- ⚠️ High missing data (>50%)
- ℹ️ Moderate missing data (>20%)
- ℹ️ Potential outliers (IQR method)
- ℹ️ High variability (CV > 1)
- ℹ️ Identifier columns
- ℹ️ Dominant single values

## GUI Mode (Optional)

Launch the interactive Streamlit interface with visualizations:

```bash
streamlit run app.py
```

Features:
- Interactive histograms for numeric columns
- Bar charts for categorical data
- Upload CSV files via browser
- Download reports

## Requirements

### CLI (Core)
- Python 3.10+
- typer
- rich

### GUI (Optional)
- streamlit
- plotly
- pandas

## Project Structure

```
csv-profiler/
├── run.py                    # Main entry point
├── app.py                    # Streamlit GUI
├── requirements.txt          # Dependencies
├── README.md                 # This file
│
├── data/
│   └── sample.csv           # Sample dataset
│
├── outputs/                 # Default output directory
│
└── src/csv_profiler/
    ├── cli.py              # CLI interface (Typer)
    ├── io.py               # CSV reading
    ├── profiling.py        # Statistical analysis
    └── render.py           # Report generation
```

## Development

```bash
# Run tests with sample data
python run.py data/sample.csv

# Check help
python run.py --help

# Development mode
python -m csv_profiler.cli --help
```

## License

MIT

## Author

Built with Claude AI
