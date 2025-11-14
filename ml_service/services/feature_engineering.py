"""
Feature Engineering Module
Calculates technical indicators and creates features for ML models.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Optional
from loguru import logger

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config.config import settings


def calculate_sma(df: pd.DataFrame, period: int, column: str = "close") -> pd.Series:
    """Calculate Simple Moving Average."""
    return df[column].rolling(window=period, min_periods=period).mean()


def calculate_ema(df: pd.DataFrame, period: int, column: str = "close") -> pd.Series:
    """Calculate Exponential Moving Average."""
    return df[column].ewm(span=period, adjust=False, min_periods=period).mean()


def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = "close") -> pd.Series:
    """Calculate Relative Strength Index."""
    delta = df[column].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    column: str = "close",
) -> tuple:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    Returns:
        Tuple of (macd_line, signal_line, macd_diff)
    """
    ema_fast = calculate_ema(df, fast, column)
    ema_slow = calculate_ema(df, slow, column)

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False, min_periods=signal).mean()
    macd_diff = macd_line - signal_line

    return macd_line, signal_line, macd_diff


def calculate_bollinger_bands(
    df: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2.0,
    column: str = "close",
) -> tuple:
    """
    Calculate Bollinger Bands.

    Returns:
        Tuple of (upper_band, middle_band, lower_band, width)
    """
    middle_band = calculate_sma(df, period, column)
    std = df[column].rolling(window=period, min_periods=period).std()

    upper_band = middle_band + (std_dev * std)
    lower_band = middle_band - (std_dev * std)
    width = (upper_band - lower_band) / middle_band

    return upper_band, middle_band, lower_band, width


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate Average True Range."""
    high_low = df["high"] - df["low"]
    high_close = abs(df["high"] - df["close"].shift())
    low_close = abs(df["low"] - df["close"].shift())

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period, min_periods=period).mean()

    return atr


def calculate_volume_indicators(df: pd.DataFrame) -> tuple:
    """
    Calculate volume-based indicators.

    Returns:
        Tuple of (volume_sma, volume_ratio)
    """
    volume_sma = df["volume"].rolling(window=20, min_periods=20).mean()
    volume_ratio = df["volume"] / volume_sma

    return volume_sma, volume_ratio


def calculate_price_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate price-based features.

    Returns:
        DataFrame with additional price features
    """
    df = df.copy()

    # Returns
    df["returns"] = df["close"].pct_change()
    df["log_returns"] = np.log(df["close"] / df["close"].shift(1))

    # Price ranges
    df["high_low_range"] = df["high"] - df["low"]
    df["close_open_ratio"] = df["close"] / df["open"]

    return df


def add_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all technical indicators and features to DataFrame.

    Args:
        df: DataFrame with OHLCV data

    Returns:
        DataFrame with all features added
    """
    logger.info("Calculating technical indicators...")

    df = df.copy()

    # Ensure we have required columns
    required_columns = ["timestamp", "open", "high", "low", "close", "volume"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Sort by timestamp
    df = df.sort_values("timestamp").reset_index(drop=True)

    try:
        # Simple Moving Averages
        for period in settings.SMA_PERIODS:
            df[f"sma_{period}"] = calculate_sma(df, period)
            logger.debug(f"Calculated SMA-{period}")

        # Exponential Moving Averages
        for period in settings.EMA_PERIODS:
            df[f"ema_{period}"] = calculate_ema(df, period)
            logger.debug(f"Calculated EMA-{period}")

        # RSI
        df[f"rsi_{settings.RSI_PERIOD}"] = calculate_rsi(df, settings.RSI_PERIOD)
        logger.debug(f"Calculated RSI-{settings.RSI_PERIOD}")

        # MACD
        macd, signal, diff = calculate_macd(
            df,
            settings.MACD_FAST,
            settings.MACD_SLOW,
            settings.MACD_SIGNAL,
        )
        df["macd"] = macd
        df["macd_signal"] = signal
        df["macd_diff"] = diff
        logger.debug("Calculated MACD")

        # Bollinger Bands
        bb_upper, bb_middle, bb_lower, bb_width = calculate_bollinger_bands(
            df,
            settings.BB_PERIOD,
            settings.BB_STD,
        )
        df[f"bb_upper_{settings.BB_PERIOD}"] = bb_upper
        df[f"bb_middle_{settings.BB_PERIOD}"] = bb_middle
        df[f"bb_lower_{settings.BB_PERIOD}"] = bb_lower
        df["bb_width"] = bb_width
        logger.debug(f"Calculated Bollinger Bands-{settings.BB_PERIOD}")

        # ATR
        df[f"atr_{settings.ATR_PERIOD}"] = calculate_atr(df, settings.ATR_PERIOD)
        logger.debug(f"Calculated ATR-{settings.ATR_PERIOD}")

        # Volume indicators
        volume_sma, volume_ratio = calculate_volume_indicators(df)
        df["volume_sma_20"] = volume_sma
        df["volume_ratio"] = volume_ratio
        logger.debug("Calculated volume indicators")

        # Price features
        df = calculate_price_features(df)
        logger.debug("Calculated price features")

        # Drop rows with NaN values (from indicator calculations)
        original_len = len(df)
        df = df.dropna()
        dropped = original_len - len(df)

        if dropped > 0:
            logger.info(f"Dropped {dropped} rows with NaN values (from indicator warm-up period)")

        logger.success(f"Feature engineering complete. Final dataset: {len(df)} rows")

        return df

    except Exception as e:
        logger.error(f"Error calculating features: {str(e)}")
        raise


def create_labels(df: pd.DataFrame, forward_periods: int = 5, threshold: float = 0.02) -> pd.Series:
    """
    Create binary labels for classification (1 = price up, 0 = price down).

    Args:
        df: DataFrame with price data
        forward_periods: Number of periods to look ahead
        threshold: Minimum return to be considered a "buy" signal

    Returns:
        Series with binary labels
    """
    # Calculate forward returns
    forward_returns = df["close"].pct_change(periods=forward_periods).shift(-forward_periods)

    # Create binary labels (1 if price goes up by threshold, else 0)
    labels = (forward_returns > threshold).astype(int)

    return labels


def prepare_training_data(df: pd.DataFrame, feature_columns: list) -> tuple:
    """
    Prepare data for training by separating features and labels.

    Args:
        df: DataFrame with features and labels
        feature_columns: List of feature column names

    Returns:
        Tuple of (X, y) where X is features and y is labels
    """
    # Add features if not present
    if "sma_20" not in df.columns:
        df = add_all_features(df)

    # Create labels if not present
    if "target" not in df.columns:
        df["target"] = create_labels(df)

    # Remove rows where we can't calculate forward returns
    df = df.dropna(subset=["target"])

    # Verify all feature columns exist
    missing = [col for col in feature_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")

    # Extract features and labels
    X = df[feature_columns].values
    y = df["target"].values

    logger.info(f"Training data prepared: {X.shape[0]} samples, {X.shape[1]} features")
    logger.info(f"Class distribution: {np.bincount(y)}")

    return X, y, df


if __name__ == "__main__":
    # Test feature engineering
    from config.config import get_feature_columns

    # Create sample data
    dates = pd.date_range("2023-01-01", periods=200, freq="D")
    sample_data = pd.DataFrame(
        {
            "timestamp": dates,
            "open": 100 + np.random.randn(200).cumsum(),
            "high": 102 + np.random.randn(200).cumsum(),
            "low": 98 + np.random.randn(200).cumsum(),
            "close": 100 + np.random.randn(200).cumsum(),
            "volume": np.random.randint(1000000, 5000000, 200),
        }
    )

    # Ensure high >= low
    sample_data["high"] = sample_data[["high", "low"]].max(axis=1) + 1
    sample_data["low"] = sample_data[["high", "low"]].min(axis=1) - 1

    print("Sample data created")
    print(sample_data.head())

    # Add features
    df_with_features = add_all_features(sample_data)
    print(f"\nFeatures added. Shape: {df_with_features.shape}")
    print(f"Columns: {df_with_features.columns.tolist()}")

    # Prepare training data
    feature_cols = get_feature_columns()
    X, y, df_final = prepare_training_data(df_with_features, feature_cols)
    print(f"\nTraining data: X.shape={X.shape}, y.shape={y.shape}")
    print(f"Target distribution: {np.bincount(y)}")
