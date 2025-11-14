"""
Database connector for PostgreSQL
"""
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from typing import Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """
    Handles database connections and data retrieval
    """

    def __init__(self, connection_string: str):
        """
        Initialize database connector

        Args:
            connection_string: PostgreSQL connection string
        """
        self.connection_string = connection_string
        self.engine = create_engine(
            connection_string,
            poolclass=NullPool,  # Don't pool connections
            echo=False
        )
        logger.info("Database connector initialized")

    def get_stock_id(self, ticker: str) -> Optional[int]:
        """
        Get stock ID from ticker symbol

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')

        Returns:
            Stock ID or None if not found
        """
        query = text("SELECT id FROM stocks WHERE ticker = :ticker")

        with self.engine.connect() as conn:
            result = conn.execute(query, {"ticker": ticker.upper()}).fetchone()

        if result:
            return result[0]
        else:
            logger.warning(f"Stock {ticker} not found in database")
            return None

    def get_daily_data(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch daily OHLCV data for a stock

        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with columns: date, open, high, low, close, volume
        """
        stock_id = self.get_stock_id(ticker)
        if stock_id is None:
            return pd.DataFrame()

        query = """
            SELECT
                date,
                open,
                high,
                low,
                close,
                volume,
                adj_close
            FROM stock_prices
            WHERE stock_id = :stock_id
        """

        params = {"stock_id": stock_id}

        if start_date:
            query += " AND date >= :start_date"
            params["start_date"] = start_date

        if end_date:
            query += " AND date <= :end_date"
            params["end_date"] = end_date

        query += " ORDER BY date ASC"

        df = pd.read_sql(text(query), self.engine, params=params)

        if df.empty:
            logger.warning(f"No data found for {ticker}")
            return df

        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])

        logger.info(f"Loaded {len(df)} daily records for {ticker}")
        return df

    def get_weekly_data(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Aggregate daily data to weekly OHLCV

        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with weekly OHLCV data
        """
        daily_df = self.get_daily_data(ticker, start_date, end_date)

        if daily_df.empty:
            return pd.DataFrame()

        # Resample to weekly (W-FRI: week ending on Friday)
        weekly_df = daily_df.set_index('date').resample('W-FRI').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'adj_close': 'last'
        }).reset_index()

        # Remove rows with NaN (incomplete weeks)
        weekly_df = weekly_df.dropna()

        logger.info(f"Aggregated to {len(weekly_df)} weekly records for {ticker}")
        return weekly_df

    def get_monthly_data(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Aggregate daily data to monthly OHLCV

        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with monthly OHLCV data
        """
        daily_df = self.get_daily_data(ticker, start_date, end_date)

        if daily_df.empty:
            return pd.DataFrame()

        # Resample to monthly (M: month end)
        monthly_df = daily_df.set_index('date').resample('M').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'adj_close': 'last'
        }).reset_index()

        # Remove rows with NaN
        monthly_df = monthly_df.dropna()

        logger.info(f"Aggregated to {len(monthly_df)} monthly records for {ticker}")
        return monthly_df

    def get_all_tickers(self, active_only: bool = True) -> List[str]:
        """
        Get list of all tickers in database

        Args:
            active_only: If True, only return active stocks

        Returns:
            List of ticker symbols
        """
        query = "SELECT ticker FROM stocks"

        if active_only:
            query += " WHERE is_active = true"

        query += " ORDER BY ticker"

        with self.engine.connect() as conn:
            result = conn.execute(text(query)).fetchall()

        tickers = [row[0] for row in result]
        logger.info(f"Found {len(tickers)} tickers (active_only={active_only})")

        return tickers

    def get_stock_info(self, ticker: str) -> Optional[dict]:
        """
        Get stock metadata

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with stock info or None
        """
        query = text("""
            SELECT
                id,
                ticker,
                company_name,
                sector,
                industry,
                market_cap,
                is_active
            FROM stocks
            WHERE ticker = :ticker
        """)

        with self.engine.connect() as conn:
            result = conn.execute(query, {"ticker": ticker.upper()}).fetchone()

        if result:
            return {
                'id': result[0],
                'ticker': result[1],
                'company_name': result[2],
                'sector': result[3],
                'industry': result[4],
                'market_cap': result[5],
                'is_active': result[6]
            }
        else:
            return None

    def close(self):
        """Close database connection"""
        self.engine.dispose()
        logger.info("Database connection closed")
