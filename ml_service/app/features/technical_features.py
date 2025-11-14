"""
Technical feature engineering module

Generates 30-40 technical indicators from OHLCV data
"""
import pandas as pd
import numpy as np
from typing import List, Dict
import logging

from config.config import config

logger = logging.getLogger(__name__)


class TechnicalFeatureEngineer:
    """
    Generates technical indicators as features for ML models
    """

    def __init__(self):
        """Initialize feature engineer with config parameters"""
        self.ma_periods = config.training.ma_periods
        self.rsi_period = config.training.rsi_period
        self.bb_period = config.training.bb_period
        self.bb_std = config.training.bb_std
        self.atr_period = config.training.atr_period
        self.volume_ma_period = config.training.volume_ma_period

        logger.info("TechnicalFeatureEngineer initialized")

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate all technical features

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with feature columns added
        """
        if df.empty or len(df) < max(self.ma_periods):
            logger.warning("Insufficient data for feature generation")
            return df

        logger.info(f"Generating technical features for {len(df)} rows")

        df = df.copy()

        # 1. Moving Averages (MA)
        df = self._add_moving_averages(df)

        # 2. MA-based features
        df = self._add_ma_features(df)

        # 3. RSI (Relative Strength Index)
        df = self._add_rsi(df)

        # 4. Bollinger Bands
        df = self._add_bollinger_bands(df)

        # 5. ATR (Average True Range)
        df = self._add_atr(df)

        # 6. Volume features
        df = self._add_volume_features(df)

        # 7. Momentum features
        df = self._add_momentum_features(df)

        # 8. Price action features
        df = self._add_price_action_features(df)

        # 9. Trend features
        df = self._add_trend_features(df)

        # Remove rows with NaN (due to lookback periods)
        initial_rows = len(df)
        df = df.dropna()
        logger.info(f"Generated features: {initial_rows} → {len(df)} rows (removed NaN)")

        return df

    def _add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add moving averages"""
        for period in self.ma_periods:
            df[f'ma{period}'] = df['close'].rolling(window=period).mean()

        return df

    def _add_ma_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add MA-based features"""
        # MA crossover signals
        if 20 in self.ma_periods and 50 in self.ma_periods:
            df['ma20_above_ma50'] = (df['ma20'] > df['ma50']).astype(int)
            df['ma20_ma50_ratio'] = df['ma20'] / df['ma50']
            df['ma20_ma50_distance'] = (df['ma20'] - df['ma50']) / df['ma50']

        if 50 in self.ma_periods and 200 in self.ma_periods:
            df['ma50_above_ma200'] = (df['ma50'] > df['ma200']).astype(int)
            df['ma50_ma200_ratio'] = df['ma50'] / df['ma200']
            df['ma50_ma200_distance'] = (df['ma50'] - df['ma200']) / df['ma200']

        if all(p in self.ma_periods for p in [20, 50, 200]):
            # Golden cross (all MAs aligned bullish)
            df['golden_cross'] = (
                (df['ma20'] > df['ma50']) &
                (df['ma50'] > df['ma200'])
            ).astype(int)

        # Price distance from MAs
        for period in self.ma_periods:
            df[f'price_ma{period}_distance'] = (df['close'] - df[f'ma{period}']) / df[f'ma{period}']
            df[f'price_above_ma{period}'] = (df['close'] > df[f'ma{period}']).astype(int)

        return df

    def _add_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add RSI (Relative Strength Index)"""
        delta = df['close'].diff()

        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()

        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # RSI-based features
        df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
        df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
        df['rsi_normalized'] = (df['rsi'] - 50) / 50  # Center at 0

        return df

    def _add_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Bollinger Bands"""
        df['bb_middle'] = df['close'].rolling(window=self.bb_period).mean()
        bb_std = df['close'].rolling(window=self.bb_period).std()

        df['bb_upper'] = df['bb_middle'] + (bb_std * self.bb_std)
        df['bb_lower'] = df['bb_middle'] - (bb_std * self.bb_std)

        # BB-based features
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']

        df['price_above_bb_upper'] = (df['close'] > df['bb_upper']).astype(int)
        df['price_below_bb_lower'] = (df['close'] < df['bb_lower']).astype(int)

        return df

    def _add_atr(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add ATR (Average True Range)"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = true_range.rolling(window=self.atr_period).mean()

        # ATR as percentage of price (volatility measure)
        df['atr_pct'] = df['atr'] / df['close']

        return df

    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based features"""
        df['volume_ma'] = df['volume'].rolling(window=self.volume_ma_period).mean()

        # Volume ratio
        df['volume_ratio'] = df['volume'] / df['volume_ma']

        # Volume surge (volume > 1.5x average)
        df['volume_surge'] = (df['volume'] > 1.5 * df['volume_ma']).astype(int)

        # Volume trend
        df['volume_trend'] = df['volume'].pct_change(5)

        return df

    def _add_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum indicators"""
        # Rate of change (ROC)
        for period in [5, 10, 20]:
            df[f'roc_{period}'] = df['close'].pct_change(period)

        # Momentum
        df['momentum_10'] = df['close'] - df['close'].shift(10)

        return df

    def _add_price_action_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add price action features"""
        # Recent price changes
        for period in [1, 3, 5, 10]:
            df[f'close_change_{period}'] = df['close'].pct_change(period)

        # High-low range as percentage
        df['hl_range_pct'] = (df['high'] - df['low']) / df['close']

        # Close position within day's range
        df['close_position_in_range'] = (df['close'] - df['low']) / (df['high'] - df['low'])

        # Gap (difference between today's open and yesterday's close)
        df['gap'] = (df['open'] - df['close'].shift()) / df['close'].shift()

        return df

    def _add_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add trend strength features"""
        # Linear regression slope (trend direction)
        for period in [10, 20, 50]:
            df[f'trend_slope_{period}'] = self._calculate_slope(df['close'], period)

        # Higher highs / lower lows
        df['higher_high'] = (df['high'] > df['high'].shift(1)).astype(int)
        df['lower_low'] = (df['low'] < df['low'].shift(1)).astype(int)

        # Consecutive up/down days
        df['consecutive_up'] = self._count_consecutive(df['close'] > df['close'].shift())
        df['consecutive_down'] = self._count_consecutive(df['close'] < df['close'].shift())

        return df

    def _calculate_slope(self, series: pd.Series, period: int) -> pd.Series:
        """
        Calculate linear regression slope over rolling window

        Args:
            series: Price series
            period: Lookback period

        Returns:
            Series with slope values
        """
        def slope(y):
            if len(y) < 2:
                return 0
            x = np.arange(len(y))
            return np.polyfit(x, y, 1)[0]

        return series.rolling(window=period).apply(slope, raw=True)

    def _count_consecutive(self, condition: pd.Series) -> pd.Series:
        """
        Count consecutive True values

        Args:
            condition: Boolean series

        Returns:
            Series with consecutive counts
        """
        # Create groups where condition changes
        groups = (condition != condition.shift()).cumsum()

        # Count consecutive True values
        return condition.groupby(groups).cumsum()

    def get_feature_names(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of feature column names

        Args:
            df: DataFrame with features

        Returns:
            List of feature column names
        """
        # Exclude non-feature columns
        exclude_cols = [
            'date', 'open', 'high', 'low', 'close', 'volume', 'adj_close',
            'year', 'returns', 'label', 'forward_return',
            'high_low_ratio', 'close_open_ratio', 'price_change', 'price_change_pct'
        ]

        feature_cols = [col for col in df.columns if col not in exclude_cols]

        logger.info(f"Found {len(feature_cols)} feature columns")
        return feature_cols

    def get_feature_importance_dict(self, model, feature_names: List[str]) -> Dict[str, float]:
        """
        Get feature importance from trained model

        Args:
            model: Trained XGBoost model
            feature_names: List of feature names

        Returns:
            Dictionary mapping feature names to importance scores
        """
        importance = model.feature_importances_
        return dict(zip(feature_names, importance))
