#!/usr/bin/env python3
"""
Simple entry point for CSV Profiler.

Usage:
    python run.py myfile.csv
    python run.py myfile.csv --out-dir reports
    python run.py myfile.csv --name analysis
    python run.py myfile.csv -o reports -n analysis
"""

import sys
from pathlib import Path

# Add src directory to Python path
script_dir = Path(__file__).parent.absolute()
src_dir = script_dir / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import CLI after path is set
from csv_profiler.cli import main

if __name__ == '__main__':
    main()
