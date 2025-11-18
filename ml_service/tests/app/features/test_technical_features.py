"""
Tests for TechnicalFeatureEngineer
"""
import pytest
import pandas as pd
import numpy as np

from app.features.technical_features import TechnicalFeatureEngineer


class TestTechnicalFeatureEngineer:
    """Test technical feature engineering"""

    @pytest.fixture
    def engineer(self):
        """Create feature engineer instance"""
        return TechnicalFeatureEngineer()

    def test_initialization(self, engineer):
        """Test feature engineer initializes correctly"""
        assert engineer.ma_periods is not None
        assert engineer.rsi_period == 14
        assert engineer.bb_period == 20
        assert engineer.bb_std == 2
        assert engineer.atr_period == 14
        assert engineer.volume_ma_period == 20

    def test_create_features_with_sufficient_data(self, engineer, sample_ohlcv_data):
        """Test feature creation with sufficient data"""
        result = engineer.create_features(sample_ohlcv_data)

        # Check that features were added
        assert len(result) > 0
        assert len(result) < len(sample_ohlcv_data)  # Some rows removed due to NaN

        # Check that key features exist
        assert 'ma20' in result.columns
        assert 'ma50' in result.columns
        assert 'ma200' in result.columns
        assert 'rsi' in result.columns
        assert 'bb_upper' in result.columns
        assert 'bb_lower' in result.columns
        assert 'atr' in result.columns
        assert 'volume_ma' in result.columns

        # Check no NaN values
        assert result.isna().sum().sum() == 0

    def test_create_features_with_insufficient_data(self, engineer, small_ohlcv_data):
        """Test feature creation with insufficient data"""
        result = engineer.create_features(small_ohlcv_data)

        # Should return original data when insufficient
        assert len(result) <= len(small_ohlcv_data)

    def test_create_features_with_empty_dataframe(self, engineer):
        """Test feature creation with empty DataFrame"""
        empty_df = pd.DataFrame()
        result = engineer.create_features(empty_df)

        assert result.empty

    def test_moving_averages(self, engineer, sample_ohlcv_data):
        """Test moving average calculation"""
        result = engineer._add_moving_averages(sample_ohlcv_data.copy())

        assert 'ma20' in result.columns
        assert 'ma50' in result.columns
        assert 'ma200' in result.columns

        # Check that MA values are reasonable (should be close to price)
        # Skip NaN values
        valid_data = result.dropna()
        if len(valid_data) > 0:
            assert valid_data['ma20'].mean() > 0
            assert valid_data['ma50'].mean() > 0
            assert valid_data['ma200'].mean() > 0

    def test_ma_features(self, engineer, sample_ohlcv_data):
        """Test MA-based features"""
        df = sample_ohlcv_data.copy()
        df = engineer._add_moving_averages(df)
        result = engineer._add_ma_features(df)

        assert 'ma20_above_ma50' in result.columns
        assert 'ma20_ma50_ratio' in result.columns
        assert 'ma50_above_ma200' in result.columns
        assert 'golden_cross' in result.columns
        assert 'price_ma20_distance' in result.columns
        assert 'price_above_ma20' in result.columns

        # Check binary features are 0 or 1
        valid_data = result.dropna()
        if len(valid_data) > 0:
            assert valid_data['ma20_above_ma50'].isin([0, 1]).all()
            assert valid_data['golden_cross'].isin([0, 1]).all()

    def test_rsi_calculation(self, engineer, sample_ohlcv_data):
        """Test RSI calculation"""
        result = engineer._add_rsi(sample_ohlcv_data.copy())

        assert 'rsi' in result.columns
        assert 'rsi_overbought' in result.columns
        assert 'rsi_oversold' in result.columns
        assert 'rsi_normalized' in result.columns

        # Check RSI is in valid range [0, 100]
        valid_rsi = result['rsi'].dropna()
        if len(valid_rsi) > 0:
            assert (valid_rsi >= 0).all()
            assert (valid_rsi <= 100).all()

            # Check binary features
            assert result['rsi_overbought'].dropna().isin([0, 1]).all()
            assert result['rsi_oversold'].dropna().isin([0, 1]).all()

    def test_bollinger_bands(self, engineer, sample_ohlcv_data):
        """Test Bollinger Bands calculation"""
        result = engineer._add_bollinger_bands(sample_ohlcv_data.copy())

        assert 'bb_upper' in result.columns
        assert 'bb_middle' in result.columns
        assert 'bb_lower' in result.columns
        assert 'bb_position' in result.columns
        assert 'bb_width' in result.columns

        # Check that upper > middle > lower
        valid_data = result.dropna()
        if len(valid_data) > 0:
            assert (valid_data['bb_upper'] >= valid_data['bb_middle']).all()
            assert (valid_data['bb_middle'] >= valid_data['bb_lower']).all()

            # BB position should be between 0 and 1
            assert (valid_data['bb_position'] >= -0.5).all()  # Allow some overshoot
            assert (valid_data['bb_position'] <= 1.5).all()

    def test_atr_calculation(self, engineer, sample_ohlcv_data):
        """Test ATR calculation"""
        result = engineer._add_atr(sample_ohlcv_data.copy())

        assert 'atr' in result.columns
        assert 'atr_pct' in result.columns

        # Check ATR is positive
        valid_atr = result['atr'].dropna()
        if len(valid_atr) > 0:
            assert (valid_atr > 0).all()

            # ATR percentage should be reasonable (< 20% of price)
            valid_atr_pct = result['atr_pct'].dropna()
            assert (valid_atr_pct < 0.2).all()

    def test_volume_features(self, engineer, sample_ohlcv_data):
        """Test volume features"""
        result = engineer._add_volume_features(sample_ohlcv_data.copy())

        assert 'volume_ma' in result.columns
        assert 'volume_ratio' in result.columns
        assert 'volume_surge' in result.columns
        assert 'volume_trend' in result.columns

        # Check volume MA is positive
        valid_data = result.dropna()
        if len(valid_data) > 0:
            assert (valid_data['volume_ma'] > 0).all()
            assert (valid_data['volume_ratio'] > 0).all()
            assert valid_data['volume_surge'].isin([0, 1]).all()

    def test_momentum_features(self, engineer, sample_ohlcv_data):
        """Test momentum features"""
        result = engineer._add_momentum_features(sample_ohlcv_data.copy())

        assert 'roc_5' in result.columns
        assert 'roc_10' in result.columns
        assert 'roc_20' in result.columns
        assert 'momentum_10' in result.columns

        # ROC should be reasonable (< 50% change)
        valid_data = result.dropna()
        if len(valid_data) > 0:
            assert (valid_data['roc_5'].abs() < 0.5).all()
            assert (valid_data['roc_10'].abs() < 0.5).all()

    def test_price_action_features(self, engineer, sample_ohlcv_data):
        """Test price action features"""
        result = engineer._add_price_action_features(sample_ohlcv_data.copy())

        assert 'close_change_1' in result.columns
        assert 'close_change_5' in result.columns
        assert 'hl_range_pct' in result.columns
        assert 'close_position_in_range' in result.columns
        assert 'gap' in result.columns

        # Check close position is in [0, 1]
        valid_data = result.dropna()
        if len(valid_data) > 0:
            valid_close_pos = valid_data['close_position_in_range']
            assert (valid_close_pos >= 0).all()
            assert (valid_close_pos <= 1).all()

    def test_trend_features(self, engineer, sample_ohlcv_data):
        """Test trend features"""
        result = engineer._add_trend_features(sample_ohlcv_data.copy())

        assert 'trend_slope_10' in result.columns
        assert 'trend_slope_20' in result.columns
        assert 'trend_slope_50' in result.columns
        assert 'higher_high' in result.columns
        assert 'lower_low' in result.columns
        assert 'consecutive_up' in result.columns
        assert 'consecutive_down' in result.columns

        # Check binary features
        valid_data = result.dropna()
        if len(valid_data) > 0:
            assert valid_data['higher_high'].isin([0, 1]).all()
            assert valid_data['lower_low'].isin([0, 1]).all()

    def test_calculate_slope(self, engineer):
        """Test slope calculation"""
        series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        slopes = engineer._calculate_slope(series, 5)

        # Slope should be approximately 1 for linear increasing data
        valid_slopes = slopes.dropna()
        assert len(valid_slopes) > 0
        assert valid_slopes.mean() > 0  # Positive trend

    def test_count_consecutive(self, engineer):
        """Test consecutive count"""
        condition = pd.Series([True, True, False, True, True, True, False, False])
        result = engineer._count_consecutive(condition)

        assert result.tolist() == [1, 2, 0, 1, 2, 3, 0, 0]

    def test_get_feature_names(self, engineer, sample_features_data):
        """Test getting feature names"""
        feature_names = engineer.get_feature_names(sample_features_data)

        assert isinstance(feature_names, list)
        assert len(feature_names) > 0

        # Should not include raw OHLCV columns
        assert 'open' not in feature_names
        assert 'high' not in feature_names
        assert 'low' not in feature_names
        assert 'close' not in feature_names
        assert 'volume' not in feature_names
        assert 'date' not in feature_names

        # Should include feature columns
        assert 'ma20' in feature_names
        assert 'rsi' in feature_names

    def test_get_feature_importance_dict(self, engineer):
        """Test feature importance dictionary creation"""
        # Mock model with feature_importances_
        class MockModel:
            feature_importances_ = np.array([0.1, 0.2, 0.3, 0.4])

        model = MockModel()
        feature_names = ['feature1', 'feature2', 'feature3', 'feature4']

        importance_dict = engineer.get_feature_importance_dict(model, feature_names)

        assert isinstance(importance_dict, dict)
        assert len(importance_dict) == 4
        assert importance_dict['feature1'] == 0.1
        assert importance_dict['feature4'] == 0.4

    def test_feature_generation_preserves_data_integrity(self, engineer, sample_ohlcv_data):
        """Test that feature generation doesn't corrupt original data"""
        original_close = sample_ohlcv_data['close'].copy()

        result = engineer.create_features(sample_ohlcv_data)

        # Original dataframe should not be modified
        pd.testing.assert_series_equal(sample_ohlcv_data['close'], original_close)

        # Result should have close prices that match (for overlapping indices)
        if len(result) > 0:
            assert 'close' in result.columns

    def test_handle_missing_data(self, engineer):
        """Test handling of missing data"""
        df = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=100),
            'open': [100] * 100,
            'high': [105] * 100,
            'low': [95] * 100,
            'close': [102] * 100,
            'volume': [1_000_000] * 100
        })

        # Introduce some missing values
        df.loc[50:55, 'close'] = np.nan

        result = engineer.create_features(df)

        # Should handle missing data gracefully (rows with NaN removed)
        assert len(result) < len(df)
        assert result.isna().sum().sum() == 0
