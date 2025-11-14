"""
Parquet data loader for training ML models

Loads stock data directly from Parquet files instead of PostgreSQL.
Useful for large historical datasets (1970-2024).
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Literal, List
import logging

logger = logging.getLogger(__name__)


class ParquetDataLoader:
    """
    Load stock data from Parquet files for ML training
    """

    def __init__(self, data_dir: str = "/data"):
        """
        Initialize Parquet data loader

        Args:
            data_dir: Directory containing Parquet files
        """
        self.data_dir = Path(data_dir)
        logger.info(f"ParquetDataLoader initialized (data_dir={self.data_dir})")

    def load_data(
        self,
        ticker: str,
        timeframe: Literal['daily', 'weekly'] = 'daily',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load OHLCV data for a ticker from Parquet files

        Args:
            ticker: Stock ticker symbol
            timeframe: Data timeframe (daily or weekly)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with OHLCV data
        """
        logger.info(f"Loading {timeframe} data for {ticker} from Parquet files")

        # Find all Parquet files for timeframe
        pattern = f"US_*_{timeframe}.parquet"
        parquet_files = sorted(self.data_dir.glob(pattern))

        if not parquet_files:
            logger.error(f"No Parquet files found matching: {pattern}")
            return pd.DataFrame()

        logger.info(f"Found {len(parquet_files)} Parquet files")

        # Load and filter data
        dfs = []
        ticker_upper = ticker.upper()

        for file in parquet_files:
            try:
                # Read Parquet file
                df = pd.read_parquet(file)

                # Filter by ticker
                if 'ticker' in df.columns:
                    df_ticker = df[df['ticker'] == ticker_upper].copy()
                elif 'symbol' in df.columns:
                    df_ticker = df[df['symbol'] == ticker_upper].copy()
                else:
                    logger.warning(f"No ticker column found in {file.name}")
                    continue

                if not df_ticker.empty:
                    dfs.append(df_ticker)
                    logger.debug(f"Loaded {len(df_ticker)} rows from {file.name}")

            except Exception as e:
                logger.error(f"Error reading {file.name}: {e}")
                continue

        if not dfs:
            logger.warning(f"No data found for {ticker} in Parquet files")
            return pd.DataFrame()

        # Concatenate all dataframes
        data = pd.concat(dfs, ignore_index=True)

        logger.info(f"Loaded {len(data)} total rows for {ticker}")

        # Standardize column names and prepare data
        data = self._standardize_columns(data)

        # Filter by date range
        if start_date or end_date:
            data = self._filter_by_date(data, start_date, end_date)

        # Sort by date
        data = data.sort_values('date').reset_index(drop=True)

        # Add calculated columns
        data = self._add_calculated_columns(data)

        logger.info(f"Final dataset: {len(data)} rows for {ticker}")

        return data

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names to match expected format

        Expected columns: date, open, high, low, close, volume, adj_close
        """
        # Make a copy
        df = df.copy()

        # Column mapping (handle various naming conventions)
        column_mapping = {
            # Date columns
            'Date': 'date',
            'DATE': 'date',
            'time': 'date',
            'timestamp': 'date',

            # OHLC columns
            'Open': 'open',
            'OPEN': 'open',
            'High': 'high',
            'HIGH': 'high',
            'Low': 'low',
            'LOW': 'low',
            'Close': 'close',
            'CLOSE': 'close',

            # Volume
            'Volume': 'volume',
            'VOLUME': 'volume',
            'vol': 'volume',

            # Adjusted close
            'Adj Close': 'adj_close',
            'adj_close': 'adj_close',
            'adjusted_close': 'adj_close',
            'close_adj': 'adj_close',

            # Ticker
            'Ticker': 'ticker',
            'TICKER': 'ticker',
            'Symbol': 'ticker',
            'symbol': 'ticker'
        }

        # Rename columns
        df = df.rename(columns=column_mapping)

        # Ensure date is datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        # If adj_close doesn't exist, use close
        if 'adj_close' not in df.columns and 'close' in df.columns:
            df['adj_close'] = df['close']

        # Select only required columns (if they exist)
        required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        optional_cols = ['adj_close', 'ticker']

        available_cols = [col for col in required_cols + optional_cols if col in df.columns]

        df = df[available_cols]

        # Check for missing required columns
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            logger.warning(f"Missing required columns: {missing}")

        return df

    def _filter_by_date(
        self,
        df: pd.DataFrame,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> pd.DataFrame:
        """Filter dataframe by date range"""
        if start_date:
            df = df[df['date'] >= pd.to_datetime(start_date)]

        if end_date:
            df = df[df['date'] <= pd.to_datetime(end_date)]

        return df

    def _add_calculated_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add calculated columns needed for training

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with additional columns
        """
        if df.empty:
            return df

        # Year for time-based splitting
        df['year'] = df['date'].dt.year

        # Forward returns (will be used for labels)
        df['returns'] = df['close'].pct_change()

        # OHLC ratios
        df['high_low_ratio'] = df['high'] / df['low']
        df['close_open_ratio'] = df['close'] / df['open']

        # Price changes
        df['price_change'] = df['close'] - df['open']
        df['price_change_pct'] = (df['close'] - df['open']) / df['open']

        return df

    def get_available_tickers(self, timeframe: Literal['daily', 'weekly'] = 'daily') -> List[str]:
        """
        Get list of unique tickers available in Parquet files

        Args:
            timeframe: Data timeframe

        Returns:
            List of ticker symbols
        """
        logger.info(f"Scanning for available tickers in {timeframe} files")

        pattern = f"US_*_{timeframe}.parquet"
        parquet_files = sorted(self.data_dir.glob(pattern))

        if not parquet_files:
            logger.warning(f"No Parquet files found matching: {pattern}")
            return []

        # Sample first file to get ticker column name
        sample_df = pd.read_parquet(parquet_files[0], columns=None)

        ticker_col = None
        for col in ['ticker', 'Ticker', 'TICKER', 'symbol', 'Symbol', 'SYMBOL']:
            if col in sample_df.columns:
                ticker_col = col
                break

        if not ticker_col:
            logger.error("No ticker column found in Parquet files")
            return []

        # Get unique tickers from all files
        all_tickers = set()

        for file in parquet_files:
            try:
                df = pd.read_parquet(file, columns=[ticker_col])
                tickers = df[ticker_col].unique()
                all_tickers.update(tickers)
            except Exception as e:
                logger.error(f"Error reading {file.name}: {e}")

        tickers_list = sorted(list(all_tickers))
        logger.info(f"Found {len(tickers_list)} unique tickers")

        return tickers_list

    def get_date_range(self, ticker: str, timeframe: Literal['daily', 'weekly'] = 'daily') -> tuple:
        """
        Get date range available for a ticker

        Args:
            ticker: Stock ticker symbol
            timeframe: Data timeframe

        Returns:
            Tuple of (min_date, max_date)
        """
        data = self.load_data(ticker, timeframe)

        if data.empty:
            return None, None

        return data['date'].min(), data['date'].max()

    def get_data_info(self, timeframe: Literal['daily', 'weekly'] = 'daily') -> dict:
        """
        Get information about available Parquet files

        Args:
            timeframe: Data timeframe

        Returns:
            Dictionary with file information
        """
        pattern = f"US_*_{timeframe}.parquet"
        parquet_files = sorted(self.data_dir.glob(pattern))

        info = {
            'timeframe': timeframe,
            'num_files': len(parquet_files),
            'files': []
        }

        for file in parquet_files:
            try:
                df = pd.read_parquet(file)
                file_info = {
                    'filename': file.name,
                    'rows': len(df),
                    'size_mb': file.stat().st_size / (1024 * 1024),
                    'columns': list(df.columns)
                }
                info['files'].append(file_info)
            except Exception as e:
                logger.error(f"Error reading {file.name}: {e}")

        return info
