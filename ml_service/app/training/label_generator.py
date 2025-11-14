"""
Label generator for creating training targets
"""
import pandas as pd
import numpy as np
from typing import Literal
import logging

from config.config import config

logger = logging.getLogger(__name__)


class LabelGenerator:
    """
    Generates labels based on forward returns
    """

    def __init__(self):
        """Initialize label generator"""
        logger.info("LabelGenerator initialized")

    def create_labels(
        self,
        df: pd.DataFrame,
        timeframe: Literal['daily', 'weekly', 'monthly'] = 'daily',
        horizon_days: int = None,
        threshold: float = None
    ) -> pd.DataFrame:
        """
        Create binary labels based on forward returns

        Label = 1 if forward return > threshold, else 0

        Args:
            df: DataFrame with OHLCV data
            timeframe: Timeframe (determines default horizon and threshold)
            horizon_days: Number of days to look forward (overrides defaults)
            threshold: Return threshold for positive label (overrides defaults)

        Returns:
            DataFrame with 'label' and 'forward_return' columns added
        """
        if df.empty:
            return df

        df = df.copy()

        # Use timeframe defaults if not provided
        if horizon_days is None or threshold is None:
            horizon_days, threshold = self._get_defaults(timeframe)

        logger.info(
            f"Generating labels: timeframe={timeframe}, "
            f"horizon={horizon_days} days, threshold={threshold*100:.1f}%"
        )

        # Calculate forward return
        df['forward_return'] = df['close'].pct_change(horizon_days).shift(-horizon_days)

        # Create binary label
        df['label'] = (df['forward_return'] > threshold).astype(int)

        # Remove rows where we can't calculate forward return
        initial_rows = len(df)
        df = df.dropna(subset=['forward_return', 'label'])

        logger.info(
            f"Labels created: {initial_rows} → {len(df)} rows "
            f"(removed {initial_rows - len(df)} due to insufficient lookahead)"
        )

        # Log label distribution
        label_counts = df['label'].value_counts()
        pos_pct = label_counts.get(1, 0) / len(df) * 100 if len(df) > 0 else 0

        logger.info(
            f"Label distribution: "
            f"Positive={label_counts.get(1, 0)} ({pos_pct:.1f}%), "
            f"Negative={label_counts.get(0, 0)} ({100-pos_pct:.1f}%)"
        )

        # Warn if severe class imbalance
        if pos_pct < 20 or pos_pct > 80:
            logger.warning(
                f"Severe class imbalance detected: {pos_pct:.1f}% positive labels. "
                f"Consider adjusting threshold."
            )

        return df

    def _get_defaults(self, timeframe: str) -> tuple:
        """
        Get default horizon and threshold for timeframe

        Args:
            timeframe: Timeframe string

        Returns:
            Tuple of (horizon_days, threshold)
        """
        if timeframe == 'daily':
            return config.training.daily_horizon_days, config.training.daily_threshold
        elif timeframe == 'weekly':
            return config.training.weekly_horizon_days, config.training.weekly_threshold
        elif timeframe == 'monthly':
            return config.training.monthly_horizon_days, config.training.monthly_threshold
        else:
            raise ValueError(f"Invalid timeframe: {timeframe}")

    def create_multi_class_labels(
        self,
        df: pd.DataFrame,
        timeframe: Literal['daily', 'weekly', 'monthly'] = 'daily',
        horizon_days: int = None,
        buy_threshold: float = None,
        sell_threshold: float = None
    ) -> pd.DataFrame:
        """
        Create 3-class labels: BUY (2), NONE (0), SELL (1)

        This is useful for future enhancement if you want to predict both
        long and short positions.

        Args:
            df: DataFrame with OHLCV data
            timeframe: Timeframe
            horizon_days: Number of days to look forward
            buy_threshold: Return threshold for BUY label (positive)
            sell_threshold: Return threshold for SELL label (negative)

        Returns:
            DataFrame with 'label' column (0=NONE, 1=SELL, 2=BUY)
        """
        if df.empty:
            return df

        df = df.copy()

        # Use defaults if not provided
        if horizon_days is None:
            horizon_days, default_threshold = self._get_defaults(timeframe)
            if buy_threshold is None:
                buy_threshold = default_threshold
            if sell_threshold is None:
                sell_threshold = -default_threshold
        else:
            if buy_threshold is None:
                buy_threshold = 0.05
            if sell_threshold is None:
                sell_threshold = -0.05

        # Calculate forward return
        df['forward_return'] = df['close'].pct_change(horizon_days).shift(-horizon_days)

        # Create 3-class label
        df['label'] = 0  # Default: NONE

        df.loc[df['forward_return'] > buy_threshold, 'label'] = 2  # BUY
        df.loc[df['forward_return'] < sell_threshold, 'label'] = 1  # SELL

        # Remove rows where we can't calculate forward return
        df = df.dropna(subset=['forward_return', 'label'])

        # Log label distribution
        label_counts = df['label'].value_counts().sort_index()
        logger.info(
            f"Multi-class labels: "
            f"NONE={label_counts.get(0, 0)}, "
            f"SELL={label_counts.get(1, 0)}, "
            f"BUY={label_counts.get(2, 0)}"
        )

        return df

    def analyze_label_distribution(self, df: pd.DataFrame) -> dict:
        """
        Analyze label distribution and return statistics

        Args:
            df: DataFrame with labels

        Returns:
            Dictionary with statistics
        """
        if 'label' not in df.columns:
            return {}

        label_counts = df['label'].value_counts()
        total = len(df)

        stats = {
            'total_samples': total,
            'positive_samples': int(label_counts.get(1, 0)),
            'negative_samples': int(label_counts.get(0, 0)),
            'positive_pct': round(label_counts.get(1, 0) / total * 100, 2) if total > 0 else 0,
            'negative_pct': round(label_counts.get(0, 0) / total * 100, 2) if total > 0 else 0,
        }

        if 'forward_return' in df.columns:
            stats['avg_forward_return'] = round(df['forward_return'].mean(), 4)
            stats['median_forward_return'] = round(df['forward_return'].median(), 4)
            stats['max_forward_return'] = round(df['forward_return'].max(), 4)
            stats['min_forward_return'] = round(df['forward_return'].min(), 4)

        return stats
