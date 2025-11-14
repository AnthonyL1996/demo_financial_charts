#!/usr/bin/env python3
"""
Data Ingestion Script
Downloads stock data from Yahoo Finance and saves as Parquet files.

Usage:
    python download_data.py --ticker SPY --start 2020-01-01 --end 2024-11-14
    python download_data.py --tickers SPY,QQQ,AAPL --interval 1d
    python download_data.py --ticker SPY --timeframe all
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import pandas as pd
import yfinance as yf
from loguru import logger

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config.config import settings, init_directories


def download_stock_data(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
) -> Optional[pd.DataFrame]:
    """
    Download stock data from Yahoo Finance.

    Args:
        ticker: Stock ticker symbol (e.g., 'SPY', 'AAPL')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval ('1d', '1wk', '1mo')

    Returns:
        DataFrame with OHLCV data or None if download fails
    """
    try:
        logger.info(f"Downloading {ticker} data ({interval}) from {start_date} to {end_date}...")

        # Download data using yfinance
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date, interval=interval)

        if df.empty:
            logger.error(f"No data returned for {ticker}")
            return None

        # Clean up the data
        df = df.reset_index()

        # Rename columns to lowercase
        df.columns = df.columns.str.lower()

        # Ensure we have the required columns
        required_columns = ["date", "open", "high", "low", "close", "volume"]
        if not all(col in df.columns for col in required_columns):
            logger.error(f"Missing required columns. Got: {df.columns.tolist()}")
            return None

        # Rename 'date' to 'timestamp' for consistency
        df = df.rename(columns={"date": "timestamp"})

        # Sort by timestamp
        df = df.sort_values("timestamp").reset_index(drop=True)

        # Remove any rows with missing values
        original_len = len(df)
        df = df.dropna()
        if len(df) < original_len:
            logger.warning(f"Removed {original_len - len(df)} rows with missing values")

        logger.success(f"Downloaded {len(df)} rows for {ticker}")
        logger.info(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

        return df

    except Exception as e:
        logger.error(f"Error downloading {ticker}: {str(e)}")
        return None


def save_to_parquet(
    df: pd.DataFrame,
    ticker: str,
    interval: str,
    output_dir: Path,
) -> Optional[Path]:
    """
    Save DataFrame to Parquet file.

    Args:
        df: DataFrame to save
        ticker: Stock ticker symbol
        interval: Data interval
        output_dir: Directory to save the file

    Returns:
        Path to saved file or None if save fails
    """
    try:
        # Create filename
        interval_name = interval.replace("1", "").replace("d", "daily").replace("wk", "weekly").replace("mo", "monthly")
        start_date = df["timestamp"].min().strftime("%Y_%m_%d")
        end_date = df["timestamp"].max().strftime("%Y_%m_%d")
        filename = f"{ticker}_{interval_name}_{start_date}_to_{end_date}.parquet"
        filepath = output_dir / filename

        # Save to parquet
        df.to_parquet(filepath, engine="pyarrow", compression="snappy", index=False)

        logger.success(f"Saved to: {filepath}")
        logger.info(f"File size: {filepath.stat().st_size / 1024:.2f} KB")

        return filepath

    except Exception as e:
        logger.error(f"Error saving to Parquet: {str(e)}")
        return None


def download_multiple_timeframes(
    ticker: str,
    start_date: str,
    end_date: str,
    output_dir: Path,
) -> dict:
    """
    Download data for multiple timeframes (daily, weekly, monthly).

    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        output_dir: Directory to save files

    Returns:
        Dictionary with results for each timeframe
    """
    results = {}
    timeframes = [
        ("1d", "daily"),
        ("1wk", "weekly"),
        # ("1mo", "monthly"),  # Uncomment if needed
    ]

    for interval, name in timeframes:
        logger.info(f"\n{'='*60}")
        logger.info(f"Downloading {name} data for {ticker}")
        logger.info(f"{'='*60}")

        df = download_stock_data(ticker, start_date, end_date, interval)

        if df is not None:
            filepath = save_to_parquet(df, ticker, interval, output_dir)
            results[name] = {
                "success": filepath is not None,
                "filepath": filepath,
                "rows": len(df),
            }
        else:
            results[name] = {
                "success": False,
                "filepath": None,
                "rows": 0,
            }

    return results


def validate_data(df: pd.DataFrame, ticker: str) -> bool:
    """
    Validate downloaded data for quality issues.

    Args:
        df: DataFrame to validate
        ticker: Stock ticker symbol

    Returns:
        True if data passes validation, False otherwise
    """
    logger.info(f"\nValidating data for {ticker}...")

    issues = []

    # Check for minimum rows
    if len(df) < 100:
        issues.append(f"Insufficient data: only {len(df)} rows (need at least 100)")

    # Check for missing values
    missing = df.isnull().sum()
    if missing.any():
        issues.append(f"Missing values found: {missing[missing > 0].to_dict()}")

    # Check for zero/negative prices
    price_columns = ["open", "high", "low", "close"]
    for col in price_columns:
        if (df[col] <= 0).any():
            issues.append(f"Zero or negative values in {col}")

    # Check for zero volume
    if (df["volume"] == 0).sum() > len(df) * 0.1:  # More than 10% zero volume
        zero_vol_pct = (df["volume"] == 0).sum() / len(df) * 100
        issues.append(f"Too many zero volume days: {zero_vol_pct:.1f}%")

    # Check for price consistency (high >= low)
    if (df["high"] < df["low"]).any():
        issues.append("Found rows where high < low")

    # Check for price consistency (high >= close >= low)
    if ((df["close"] > df["high"]) | (df["close"] < df["low"])).any():
        issues.append("Found rows where close is outside high/low range")

    # Check for date gaps (only for daily data)
    if len(df) > 1:
        df_sorted = df.sort_values("timestamp")
        date_diffs = df_sorted["timestamp"].diff().dt.days
        large_gaps = date_diffs[date_diffs > 7].count()
        if large_gaps > 5:
            issues.append(f"Found {large_gaps} large date gaps (>7 days)")

    # Report results
    if issues:
        logger.warning(f"⚠️  Data validation found {len(issues)} issue(s):")
        for issue in issues:
            logger.warning(f"  - {issue}")
        return False
    else:
        logger.success("✅ Data validation passed!")
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Download stock data from Yahoo Finance")

    parser.add_argument(
        "--ticker",
        type=str,
        help="Single ticker to download (e.g., SPY, AAPL)",
    )
    parser.add_argument(
        "--tickers",
        type=str,
        help="Comma-separated list of tickers (e.g., SPY,QQQ,AAPL)",
    )
    parser.add_argument(
        "--start",
        type=str,
        default=settings.DEFAULT_START_DATE,
        help=f"Start date (YYYY-MM-DD), default: {settings.DEFAULT_START_DATE}",
    )
    parser.add_argument(
        "--end",
        type=str,
        default=settings.DEFAULT_END_DATE,
        help=f"End date (YYYY-MM-DD), default: {settings.DEFAULT_END_DATE}",
    )
    parser.add_argument(
        "--interval",
        type=str,
        default="1d",
        choices=["1d", "1wk", "1mo"],
        help="Data interval (default: 1d)",
    )
    parser.add_argument(
        "--timeframe",
        type=str,
        choices=["daily", "weekly", "monthly", "all"],
        help="Download specific timeframe or 'all' for daily+weekly",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(settings.DATA_DIR),
        help=f"Output directory (default: {settings.DATA_DIR})",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run data validation after download",
    )

    args = parser.parse_args()

    # Initialize directories
    init_directories()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get list of tickers
    tickers: List[str] = []
    if args.ticker:
        tickers.append(args.ticker.upper())
    if args.tickers:
        tickers.extend([t.strip().upper() for t in args.tickers.split(",")])

    if not tickers:
        logger.error("No tickers specified. Use --ticker or --tickers")
        parser.print_help()
        sys.exit(1)

    # Remove duplicates
    tickers = list(set(tickers))

    logger.info(f"Starting download for {len(tickers)} ticker(s): {', '.join(tickers)}")
    logger.info(f"Date range: {args.start} to {args.end}")
    logger.info(f"Output directory: {output_dir}")

    # Download data for each ticker
    all_results = {}
    for ticker in tickers:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {ticker}")
        logger.info(f"{'='*60}")

        if args.timeframe == "all":
            # Download multiple timeframes
            results = download_multiple_timeframes(ticker, args.start, args.end, output_dir)
            all_results[ticker] = results
        else:
            # Download single timeframe
            interval = args.interval
            if args.timeframe:
                interval_map = {"daily": "1d", "weekly": "1wk", "monthly": "1mo"}
                interval = interval_map[args.timeframe]

            df = download_stock_data(ticker, args.start, args.end, interval)

            if df is not None:
                # Validate if requested
                if args.validate:
                    validate_data(df, ticker)

                filepath = save_to_parquet(df, ticker, interval, output_dir)
                all_results[ticker] = {
                    "success": filepath is not None,
                    "filepath": filepath,
                    "rows": len(df),
                }
            else:
                all_results[ticker] = {
                    "success": False,
                    "filepath": None,
                    "rows": 0,
                }

    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("Download Summary")
    logger.info(f"{'='*60}")

    successful = 0
    failed = 0

    for ticker, result in all_results.items():
        if isinstance(result, dict) and "success" in result:
            # Single timeframe result
            if result["success"]:
                logger.success(f"✅ {ticker}: {result['rows']} rows")
                successful += 1
            else:
                logger.error(f"❌ {ticker}: Failed")
                failed += 1
        else:
            # Multiple timeframe result
            logger.info(f"\n{ticker}:")
            for timeframe, data in result.items():
                if data["success"]:
                    logger.success(f"  ✅ {timeframe}: {data['rows']} rows")
                    successful += 1
                else:
                    logger.error(f"  ❌ {timeframe}: Failed")
                    failed += 1

    logger.info(f"\nTotal: {successful} successful, {failed} failed")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
