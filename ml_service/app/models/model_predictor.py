"""
Model predictor for generating signals
"""
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Literal, Optional
import logging

from app.features.technical_features import TechnicalFeatureEngineer
from app.training.data_loader import DataLoader
from config.config import config

logger = logging.getLogger(__name__)


class ModelPredictor:
    """
    Load trained models and generate predictions
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize model predictor

        Args:
            model_path: Path to model directory (uses config default if None)
        """
        self.model_path = Path(model_path or config.api.model_path)
        self.models = {}  # Cache loaded models
        self.feature_engineer = TechnicalFeatureEngineer()
        self.data_loader = DataLoader()

        logger.info(f"ModelPredictor initialized (model_path={self.model_path})")

    def load_model(
        self,
        timeframe: Literal['daily', 'weekly', 'monthly'],
        ticker: str = 'spy'
    ):
        """
        Load a trained model

        Args:
            timeframe: Model timeframe
            ticker: Ticker the model was trained on

        Returns:
            Loaded XGBoost model

        Raises:
            FileNotFoundError: If model file doesn't exist
        """
        model_key = f"{timeframe}_{ticker.lower()}"

        # Return cached model if already loaded
        if model_key in self.models:
            logger.debug(f"Using cached model: {model_key}")
            return self.models[model_key]

        # Load model from disk
        model_filename = f"xgboost_{timeframe}_{ticker.lower()}_v1.pkl"
        model_file = self.model_path / model_filename

        if not model_file.exists():
            raise FileNotFoundError(
                f"Model not found: {model_file}. "
                f"Please train the model first using train_model.py"
            )

        logger.info(f"Loading model from: {model_file}")
        model = joblib.load(model_file)

        # Cache model
        self.models[model_key] = model

        return model

    def generate_signal(
        self,
        ticker: str,
        timeframe: Literal['daily', 'weekly', 'monthly'] = 'daily',
        model_ticker: str = 'spy'
    ) -> Dict[str, Any]:
        """
        Generate trading signal for a ticker

        Args:
            ticker: Stock ticker to generate signal for
            timeframe: Timeframe for signal
            model_ticker: Ticker the model was trained on (default: SPY)

        Returns:
            Dictionary with signal and metadata
        """
        logger.info(f"Generating {timeframe} signal for {ticker}")

        try:
            # Load model
            model = self.load_model(timeframe, model_ticker)

            # Get recent data for ticker
            recent_data = self.data_loader.load_data(
                ticker=ticker,
                timeframe=timeframe,
                start_date=None,  # Get all available data
                end_date=None
            )

            if recent_data.empty or len(recent_data) < 200:
                return {
                    'error': f'Insufficient data for {ticker} ({timeframe})',
                    'ticker': ticker,
                    'timeframe': timeframe
                }

            # Engineer features
            data_with_features = self.feature_engineer.create_features(recent_data)

            if data_with_features.empty:
                return {
                    'error': 'Feature generation failed',
                    'ticker': ticker,
                    'timeframe': timeframe
                }

            # Get most recent row (latest signal)
            latest_data = data_with_features.iloc[[-1]].copy()

            # Get feature columns
            feature_cols = self.feature_engineer.get_feature_names(latest_data)

            # Make prediction
            X = latest_data[feature_cols].values

            prediction = model.predict(X)[0]
            probability = model.predict_proba(X)[0]

            # Confidence is probability of predicted class
            confidence = probability[prediction]

            # Signal type
            signal_type = "BUY" if prediction == 1 else "NONE"

            # Get latest price data
            latest_price = float(latest_data['close'].iloc[0])
            latest_date = latest_data['date'].iloc[0]

            # Calculate expected return and target based on timeframe
            horizon_days, threshold = self._get_timeframe_params(timeframe)

            expected_return = threshold if prediction == 1 else 0
            target_price = latest_price * (1 + expected_return) if prediction == 1 else None

            # Get key technical indicators
            technicals = self._extract_technicals(latest_data)

            return {
                'ticker': ticker,
                'timeframe': timeframe,
                'signal': signal_type,
                'confidence': round(float(confidence), 3),
                'prediction_date': latest_date.strftime('%Y-%m-%d'),
                'current_price': round(latest_price, 2),
                'target': {
                    'horizon_days': horizon_days,
                    'expected_return': round(expected_return * 100, 2),  # as percentage
                    'target_price': round(target_price, 2) if target_price else None,
                    'threshold': round(threshold * 100, 2)
                },
                'technicals': technicals,
                'model': {
                    'name': f"xgboost_{timeframe}_{model_ticker}_v1",
                    'trained_on': model_ticker.upper()
                }
            }

        except FileNotFoundError as e:
            logger.error(str(e))
            return {
                'error': str(e),
                'ticker': ticker,
                'timeframe': timeframe
            }

        except Exception as e:
            logger.error(f"Error generating signal: {e}", exc_info=True)
            return {
                'error': f"Failed to generate signal: {str(e)}",
                'ticker': ticker,
                'timeframe': timeframe
            }

    def generate_multi_timeframe_signals(
        self,
        ticker: str,
        model_ticker: str = 'spy'
    ) -> Dict[str, Any]:
        """
        Generate signals for all timeframes

        Args:
            ticker: Stock ticker
            model_ticker: Ticker the models were trained on

        Returns:
            Dictionary with signals for all timeframes and consensus
        """
        logger.info(f"Generating multi-timeframe signals for {ticker}")

        signals = {}
        timeframes = ['daily', 'weekly', 'monthly']

        for timeframe in timeframes:
            signals[timeframe] = self.generate_signal(ticker, timeframe, model_ticker)

        # Calculate consensus
        consensus = self._calculate_consensus(signals)

        return {
            'ticker': ticker,
            'signals': signals,
            'consensus': consensus
        }

    def _calculate_consensus(self, signals: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate consensus across timeframes

        Args:
            signals: Dictionary of signals for each timeframe

        Returns:
            Consensus recommendation
        """
        # Count BUY signals
        buy_count = sum(
            1 for s in signals.values()
            if 'signal' in s and s['signal'] == 'BUY'
        )

        # Calculate average confidence (only for BUY signals)
        buy_confidences = [
            s['confidence']
            for s in signals.values()
            if 'signal' in s and s['signal'] == 'BUY'
        ]

        avg_confidence = np.mean(buy_confidences) if buy_confidences else 0

        # Determine recommendation
        if buy_count == 3:
            recommendation = "STRONG_BUY"
            strength = "STRONG"
            notes = "All timeframes bullish"
        elif buy_count == 2:
            recommendation = "BUY"
            strength = "MODERATE"
            notes = "2 out of 3 timeframes bullish"
        elif buy_count == 1:
            recommendation = "WEAK_BUY"
            strength = "WEAK"
            notes = "1 out of 3 timeframes bullish"
        else:
            recommendation = "NONE"
            strength = "NONE"
            notes = "No bullish signals"

        # Suggested position size based on consensus
        position_size = min(buy_count / 3 * 0.10, 0.10)  # Max 10% of portfolio

        return {
            'recommendation': recommendation,
            'strength': strength,
            'bullish_timeframes': buy_count,
            'avg_confidence': round(avg_confidence, 3),
            'suggested_position_size': round(position_size, 3),
            'notes': notes
        }

    def _get_timeframe_params(self, timeframe: str) -> tuple:
        """Get horizon_days and threshold for timeframe"""
        if timeframe == 'daily':
            return config.training.daily_horizon_days, config.training.daily_threshold
        elif timeframe == 'weekly':
            return config.training.weekly_horizon_days, config.training.weekly_threshold
        elif timeframe == 'monthly':
            return config.training.monthly_horizon_days, config.training.monthly_threshold
        else:
            return 30, 0.05  # defaults

    def _extract_technicals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Extract key technical indicators from data"""
        row = data.iloc[0]

        technicals = {}

        # Moving averages
        if 'ma20' in data.columns:
            technicals['ma20'] = round(float(row['ma20']), 2)
        if 'ma50' in data.columns:
            technicals['ma50'] = round(float(row['ma50']), 2)
        if 'ma200' in data.columns:
            technicals['ma200'] = round(float(row['ma200']), 2)

        # RSI
        if 'rsi' in data.columns:
            technicals['rsi'] = round(float(row['rsi']), 2)

        # Bollinger Bands
        if all(col in data.columns for col in ['bb_upper', 'bb_middle', 'bb_lower']):
            technicals['bollinger_bands'] = {
                'upper': round(float(row['bb_upper']), 2),
                'middle': round(float(row['bb_middle']), 2),
                'lower': round(float(row['bb_lower']), 2)
            }

        # ATR
        if 'atr' in data.columns:
            technicals['atr'] = round(float(row['atr']), 2)

        # Volume
        if 'volume' in data.columns:
            technicals['volume'] = int(row['volume'])
        if 'volume_ratio' in data.columns:
            technicals['volume_ratio'] = round(float(row['volume_ratio']), 2)

        # Trend indicators
        if 'ma20_above_ma50' in data.columns:
            technicals['ma20_above_ma50'] = bool(row['ma20_above_ma50'])
        if 'ma50_above_ma200' in data.columns:
            technicals['ma50_above_ma200'] = bool(row['ma50_above_ma200'])

        return technicals
