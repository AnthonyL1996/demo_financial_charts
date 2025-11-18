"""
Pytest configuration and shared fixtures
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_ohlcv_data():
    """
    Generate sample OHLCV data for testing
    """
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=250, freq='D')

    # Generate realistic price data with trend
    base_price = 100
    returns = np.random.normal(0.0005, 0.02, 250)
    prices = base_price * (1 + returns).cumprod()

    df = pd.DataFrame({
        'date': dates,
        'open': prices * (1 + np.random.uniform(-0.01, 0.01, 250)),
        'high': prices * (1 + np.random.uniform(0, 0.02, 250)),
        'low': prices * (1 - np.random.uniform(0, 0.02, 250)),
        'close': prices,
        'volume': np.random.randint(1_000_000, 10_000_000, 250)
    })

    # Ensure high is highest and low is lowest
    df['high'] = df[['open', 'high', 'low', 'close']].max(axis=1)
    df['low'] = df[['open', 'high', 'low', 'close']].min(axis=1)

    return df


@pytest.fixture
def sample_features_data(sample_ohlcv_data):
    """
    Sample data with technical features already calculated
    """
    df = sample_ohlcv_data.copy()

    # Add some basic features
    df['ma20'] = df['close'].rolling(20).mean()
    df['ma50'] = df['close'].rolling(50).mean()
    df['rsi'] = 50 + np.random.uniform(-30, 30, len(df))
    df['volume_ma'] = df['volume'].rolling(20).mean()

    return df.dropna()


@pytest.fixture
def small_ohlcv_data():
    """
    Small dataset for testing insufficient data scenarios
    """
    df = pd.DataFrame({
        'date': pd.date_range(end=datetime.now(), periods=10, freq='D'),
        'open': [100, 101, 102, 101, 100, 99, 100, 101, 102, 103],
        'high': [102, 103, 104, 103, 102, 101, 102, 103, 104, 105],
        'low': [99, 100, 101, 100, 99, 98, 99, 100, 101, 102],
        'close': [101, 102, 103, 102, 101, 100, 101, 102, 103, 104],
        'volume': [1_000_000] * 10
    })
    return df
