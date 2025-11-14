"""
Data loader for fetching stock data from PostgreSQL
"""
import pandas as pd
import numpy as np
from typing import Optional, Literal
import logging

from app.utils.db_connector import DatabaseConnector
from config.config import config

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Loads and prepares stock data for ML training
    """

    def __init__(self, db_connector: Optional[DatabaseConnector] = None):
        """
        Initialize data loader

        Args:
            db_connector: Database connector instance (creates new if None)
        """
        if db_connector is None:
            self.db = DatabaseConnector(config.database.connection_string)
        else:
            self.db = db_connector

        logger.info("DataLoader initialized")

    def load_data(
        self,
        ticker: str,
        timeframe: Literal['daily', 'weekly', 'monthly'] = 'daily',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load OHLCV data for a ticker

        Args:
            ticker: Stock ticker symbol
            timeframe: Data timeframe (daily, weekly, monthly)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with OHLCV data
        """
        logger.info(f"Loading {timeframe} data for {ticker} from {start_date} to {end_date}")

        # Use config defaults if not provided
        if start_date is None:
            start_date = config.training.start_date
        if end_date is None:
            end_date = config.training.end_date

        # Fetch data based on timeframe
        if timeframe == 'daily':
            df = self.db.get_daily_data(ticker, start_date, end_date)
        elif timeframe == 'weekly':
            df = self.db.get_weekly_data(ticker, start_date, end_date)
        elif timeframe == 'monthly':
            df = self.db.get_monthly_data(ticker, start_date, end_date)
        else:
            raise ValueError(f"Invalid timeframe: {timeframe}")

        if df.empty:
            logger.warning(f"No data loaded for {ticker}")
            return df

        # Add basic calculated columns
        df = self._add_calculated_columns(df)

        logger.info(f"Loaded {len(df)} {timeframe} records for {ticker}")
        return df

    def _add_calculated_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add calculated columns to raw OHLCV data

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

    def prepare_dataset(
        self,
        ticker: str,
        timeframe: Literal['daily', 'weekly', 'monthly'] = 'daily'
    ) -> pd.DataFrame:
        """
        Load data and prepare complete dataset with all columns needed for training

        This is a convenience method that loads data and adds year/returns columns.
        Feature engineering and label generation are done separately.

        Args:
            ticker: Stock ticker symbol
            timeframe: Data timeframe

        Returns:
            Prepared DataFrame
        """
        df = self.load_data(ticker, timeframe)

        if df.empty:
            return df

        # Validate minimum samples
        if len(df) < config.training.min_samples:
            logger.warning(
                f"Insufficient data for {ticker}: {len(df)} < {config.training.min_samples}"
            )
            return pd.DataFrame()

        return df

    def get_ticker_list(self, active_only: bool = True) -> list:
        """
        Get list of available tickers

        Args:
            active_only: Only return active stocks

        Returns:
            List of ticker symbols
        """
        return self.db.get_all_tickers(active_only=active_only)

    def close(self):
        """Close database connection"""
        self.db.close()
