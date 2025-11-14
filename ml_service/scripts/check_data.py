#!/usr/bin/env python3
"""
Data Validation Script
Checks Parquet files for data quality and integrity.

Usage:
    python check_data.py --file /data/SPY_daily_2020_2024.parquet
    python check_data.py --dir /data
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from loguru import logger

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config.config import settings


def check_parquet_file(filepath: Path) -> dict:
    """
    Validate a single Parquet file.

    Args:
        filepath: Path to Parquet file

    Returns:
        Dictionary with validation results
    """
    results = {
        "filepath": str(filepath),
        "filename": filepath.name,
        "valid": True,
        "issues": [],
        "warnings": [],
        "info": {},
    }

    try:
        # Load file
        logger.info(f"Checking {filepath.name}...")
        df = pd.read_parquet(filepath)

        # Basic info
        results["info"]["rows"] = len(df)
        results["info"]["columns"] = df.columns.tolist()
        results["info"]["size_mb"] = filepath.stat().st_size / (1024 * 1024)

        # Check required columns
        required = ["timestamp", "open", "high", "low", "close", "volume"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            results["valid"] = False
            results["issues"].append(f"Missing required columns: {missing}")

        # Check data types
        if "timestamp" in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
                results["warnings"].append("timestamp column is not datetime type")

        # Check for missing values
        missing_counts = df.isnull().sum()
        if missing_counts.any():
            missing_info = missing_counts[missing_counts > 0].to_dict()
            results["warnings"].append(f"Missing values found: {missing_info}")

        # Check minimum rows
        if len(df) < 100:
            results["valid"] = False
            results["issues"].append(f"Insufficient data: only {len(df)} rows (need >= 100)")

        # Check price consistency
        if all(col in df.columns for col in ["open", "high", "low", "close"]):
            # Check for zero/negative prices
            for col in ["open", "high", "low", "close"]:
                if (df[col] <= 0).any():
                    results["valid"] = False
                    results["issues"].append(f"Zero or negative values in {col}")

            # Check high >= low
            if (df["high"] < df["low"]).any():
                results["valid"] = False
                results["issues"].append("Found rows where high < low")

            # Check close within high/low
            invalid_close = ((df["close"] > df["high"]) | (df["close"] < df["low"])).sum()
            if invalid_close > 0:
                results["valid"] = False
                results["issues"].append(
                    f"{invalid_close} rows where close is outside high/low range"
                )

        # Check volume
        if "volume" in df.columns:
            if (df["volume"] < 0).any():
                results["valid"] = False
                results["issues"].append("Negative volume values found")

            zero_volume = (df["volume"] == 0).sum()
            zero_volume_pct = zero_volume / len(df) * 100
            if zero_volume_pct > 10:
                results["warnings"].append(
                    f"High percentage of zero volume days: {zero_volume_pct:.1f}%"
                )

        # Check date range and gaps
        if "timestamp" in df.columns and pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df_sorted = df.sort_values("timestamp")
            results["info"]["start_date"] = str(df_sorted["timestamp"].min())
            results["info"]["end_date"] = str(df_sorted["timestamp"].max())

            # Check for large gaps
            date_diffs = df_sorted["timestamp"].diff().dt.days
            large_gaps = date_diffs[date_diffs > 7]
            if len(large_gaps) > 5:
                results["warnings"].append(f"Found {len(large_gaps)} large date gaps (>7 days)")

            # Check for duplicates
            duplicates = df_sorted["timestamp"].duplicated().sum()
            if duplicates > 0:
                results["valid"] = False
                results["issues"].append(f"Found {duplicates} duplicate timestamps")

        # Summary
        if results["valid"]:
            logger.success(f"✅ {filepath.name} - Valid")
        else:
            logger.error(f"❌ {filepath.name} - Invalid ({len(results['issues'])} issues)")

        if results["warnings"]:
            logger.warning(f"⚠️  {filepath.name} - {len(results['warnings'])} warnings")

    except Exception as e:
        results["valid"] = False
        results["issues"].append(f"Error reading file: {str(e)}")
        logger.error(f"Error checking {filepath.name}: {str(e)}")

    return results


def print_validation_report(results_list: list):
    """Print formatted validation report."""
    logger.info("\n" + "=" * 70)
    logger.info("DATA VALIDATION REPORT")
    logger.info("=" * 70)

    total = len(results_list)
    valid = sum(1 for r in results_list if r["valid"])
    invalid = total - valid

    for result in results_list:
        logger.info(f"\n📄 File: {result['filename']}")
        logger.info(f"   Size: {result['info'].get('size_mb', 0):.2f} MB")
        logger.info(f"   Rows: {result['info'].get('rows', 0)}")

        if "start_date" in result["info"]:
            logger.info(
                f"   Date Range: {result['info']['start_date']} to {result['info']['end_date']}"
            )

        if result["valid"]:
            logger.success("   Status: ✅ VALID")
        else:
            logger.error("   Status: ❌ INVALID")

        if result["issues"]:
            logger.error("   Issues:")
            for issue in result["issues"]:
                logger.error(f"     - {issue}")

        if result["warnings"]:
            logger.warning("   Warnings:")
            for warning in result["warnings"]:
                logger.warning(f"     - {warning}")

    logger.info("\n" + "=" * 70)
    logger.info(f"SUMMARY: {valid}/{total} files valid, {invalid} invalid")
    logger.info("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate Parquet data files")

    parser.add_argument(
        "--file",
        type=str,
        help="Single Parquet file to check",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=str(settings.DATA_DIR),
        help=f"Directory containing Parquet files (default: {settings.DATA_DIR})",
    )

    args = parser.parse_args()

    results_list = []

    if args.file:
        # Check single file
        filepath = Path(args.file)
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            sys.exit(1)

        results = check_parquet_file(filepath)
        results_list.append(results)

    else:
        # Check all files in directory
        data_dir = Path(args.dir)
        if not data_dir.exists():
            logger.error(f"Directory not found: {data_dir}")
            sys.exit(1)

        parquet_files = list(data_dir.glob("*.parquet"))
        if not parquet_files:
            logger.warning(f"No Parquet files found in {data_dir}")
            sys.exit(0)

        logger.info(f"Found {len(parquet_files)} Parquet files")

        for filepath in parquet_files:
            results = check_parquet_file(filepath)
            results_list.append(results)

    # Print report
    print_validation_report(results_list)

    # Exit with error if any files invalid
    if any(not r["valid"] for r in results_list):
        sys.exit(1)


if __name__ == "__main__":
    main()
