"""
Model Predictor Service
Loads trained models and generates trading signals.
"""

import sys
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import pandas as pd
import numpy as np
import joblib
from loguru import logger

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config.config import settings
from services.feature_engineering import add_all_features


class ModelPredictor:
    """
    Handles model loading and prediction generation.
    """

    def __init__(self, models_dir: Optional[Path] = None):
        """
        Initialize ModelPredictor.

        Args:
            models_dir: Directory containing model files
        """
        self.models_dir = models_dir or settings.MODELS_DIR
        self.models = {}  # Cache loaded models
        self.model_metadata = {}  # Cache model metadata

    def load_model(self, model_name: str) -> bool:
        """
        Load a trained model from disk.

        Args:
            model_name: Name of model file (e.g., 'xgboost_daily_spy.pkl')

        Returns:
            True if model loaded successfully
        """
        try:
            # Check current directory first
            model_path = self.models_dir / "current" / model_name
            if not model_path.exists():
                # Try root models directory
                model_path = self.models_dir / model_name

            if not model_path.exists():
                logger.error(f"Model not found: {model_name}")
                return False

            logger.info(f"Loading model: {model_path}")

            # Load model data
            model_data = joblib.load(model_path)

            # Validate model data structure
            if not isinstance(model_data, dict) or "model" not in model_data:
                logger.error(f"Invalid model file format: {model_name}")
                return False

            # Cache model and metadata
            self.models[model_name] = model_data["model"]
            self.model_metadata[model_name] = {
                "ticker": model_data.get("ticker", "UNKNOWN"),
                "timeframe": model_data.get("timeframe", "UNKNOWN"),
                "metrics": model_data.get("metrics", {}),
                "feature_columns": model_data.get("feature_columns", []),
                "version": model_data.get("version", "unknown"),
                "trained_at": model_data.get("trained_at", "unknown"),
                "config": model_data.get("config", {}),
            }

            logger.success(f"Model loaded: {model_name}")
            logger.info(f"  Trained on: {model_data.get('ticker', 'N/A')}")
            logger.info(f"  Timeframe: {model_data.get('timeframe', 'N/A')}")
            logger.info(f"  Accuracy: {model_data.get('metrics', {}).get('test_accuracy', 0):.2%}")

            return True

        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")
            return False

    def get_model(self, model_name: str):
        """
        Get a cached model or load it if not cached.

        Args:
            model_name: Name of model file

        Returns:
            Loaded model or None if not found
        """
        if model_name not in self.models:
            if not self.load_model(model_name):
                return None

        return self.models[model_name]

    def prepare_features(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
    ) -> Optional[np.ndarray]:
        """
        Prepare features from raw OHLCV data.

        Args:
            df: DataFrame with OHLCV data
            feature_columns: List of required feature columns

        Returns:
            Feature array or None if preparation fails
        """
        try:
            # Need at least 200 rows for proper indicator calculation
            if len(df) < 200:
                logger.warning(f"Insufficient data for feature calculation: {len(df)} rows")
                return None

            # Add technical indicators
            df_features = add_all_features(df)

            # Check if we have all required features
            missing = [col for col in feature_columns if col not in df_features.columns]
            if missing:
                logger.error(f"Missing features after calculation: {missing}")
                return None

            # Extract features (use last row for latest prediction)
            features = df_features[feature_columns].iloc[-1:].values

            # Check for NaN
            if np.isnan(features).any():
                logger.warning("NaN values in features - cannot generate prediction")
                return None

            return features

        except Exception as e:
            logger.error(f"Error preparing features: {str(e)}")
            return None

    def generate_signal(
        self,
        df: pd.DataFrame,
        model_name: str = "xgboost_daily_spy.pkl",
        ticker: Optional[str] = None,
    ) -> Dict:
        """
        Generate trading signal from OHLCV data.

        Args:
            df: DataFrame with OHLCV data (timestamp, open, high, low, close, volume)
            model_name: Name of model to use
            ticker: Optional ticker symbol for response

        Returns:
            Dictionary with signal, confidence, and metadata
        """
        try:
            # Get model
            model = self.get_model(model_name)
            if model is None:
                return {
                    "success": False,
                    "error": f"Model not found: {model_name}",
                }

            # Get model metadata
            metadata = self.model_metadata.get(model_name, {})
            feature_columns = metadata.get("feature_columns", [])

            if not feature_columns:
                return {
                    "success": False,
                    "error": "Model feature columns not found",
                }

            # Prepare features
            features = self.prepare_features(df, feature_columns)
            if features is None:
                return {
                    "success": False,
                    "error": "Failed to prepare features",
                }

            # Generate prediction
            prediction_proba = model.predict_proba(features)[0]
            prediction_class = model.predict(features)[0]

            # Get confidence scores
            down_confidence = float(prediction_proba[0])
            up_confidence = float(prediction_proba[1])

            # Determine signal based on thresholds
            buy_threshold = metadata.get("config", {}).get("buy_threshold", settings.BUY_THRESHOLD)
            sell_threshold = metadata.get("config", {}).get("sell_threshold", settings.SELL_THRESHOLD)

            if up_confidence >= buy_threshold:
                signal = "BUY"
                confidence = up_confidence
            elif down_confidence >= sell_threshold:
                signal = "SELL"
                confidence = down_confidence
            else:
                signal = "HOLD"
                confidence = max(up_confidence, down_confidence)

            # Get latest price for context
            latest_price = float(df["close"].iloc[-1])
            latest_timestamp = df["timestamp"].iloc[-1]

            return {
                "success": True,
                "ticker": ticker or "UNKNOWN",
                "signal": signal,
                "confidence": confidence,
                "probabilities": {
                    "down": down_confidence,
                    "up": up_confidence,
                },
                "latest_price": latest_price,
                "timestamp": latest_timestamp.isoformat() if hasattr(latest_timestamp, "isoformat") else str(latest_timestamp),
                "model_used": model_name,
                "model_metadata": {
                    "trained_on": metadata.get("ticker"),
                    "timeframe": metadata.get("timeframe"),
                    "accuracy": metadata.get("metrics", {}).get("test_accuracy"),
                },
            }

        except Exception as e:
            logger.error(f"Error generating signal: {str(e)}")
            logger.exception(e)
            return {
                "success": False,
                "error": str(e),
            }

    def batch_predict(
        self,
        data_dict: Dict[str, pd.DataFrame],
        model_name: str = "xgboost_daily_spy.pkl",
    ) -> Dict[str, Dict]:
        """
        Generate signals for multiple tickers.

        Args:
            data_dict: Dictionary of {ticker: DataFrame}
            model_name: Model to use for predictions

        Returns:
            Dictionary of {ticker: signal_dict}
        """
        results = {}

        for ticker, df in data_dict.items():
            logger.info(f"Generating signal for {ticker}...")
            results[ticker] = self.generate_signal(df, model_name, ticker)

        return results

    def list_available_models(self) -> List[Dict]:
        """
        List all available models in the models directory.

        Returns:
            List of model info dictionaries
        """
        models = []

        # Check current directory
        current_dir = self.models_dir / "current"
        if current_dir.exists():
            for filepath in current_dir.glob("*.pkl"):
                models.append({
                    "name": filepath.name,
                    "path": str(filepath),
                    "size_kb": filepath.stat().st_size / 1024,
                    "location": "current",
                })

        # Check root directory
        for filepath in self.models_dir.glob("*.pkl"):
            models.append({
                "name": filepath.name,
                "path": str(filepath),
                "size_kb": filepath.stat().st_size / 1024,
                "location": "archive",
            })

        return models

    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """
        Get detailed information about a model.

        Args:
            model_name: Name of model file

        Returns:
            Dictionary with model info or None if not found
        """
        if model_name not in self.model_metadata:
            if not self.load_model(model_name):
                return None

        return self.model_metadata.get(model_name)


# Singleton instance
_predictor_instance: Optional[ModelPredictor] = None


def get_predictor() -> ModelPredictor:
    """Get singleton ModelPredictor instance."""
    global _predictor_instance

    if _predictor_instance is None:
        _predictor_instance = ModelPredictor()

    return _predictor_instance


if __name__ == "__main__":
    # Test model predictor
    from datetime import datetime, timedelta

    print("Testing ModelPredictor...")

    # Create sample data
    dates = pd.date_range(end=datetime.now(), periods=200, freq="D")
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

    # Ensure price consistency
    sample_data["high"] = sample_data[["high", "close", "open"]].max(axis=1)
    sample_data["low"] = sample_data[["low", "close", "open"]].min(axis=1)

    print("\nSample data created")
    print(sample_data.tail())

    # Initialize predictor
    predictor = get_predictor()

    # List available models
    print("\nAvailable models:")
    models = predictor.list_available_models()
    for model in models:
        print(f"  - {model['name']} ({model['size_kb']:.1f} KB) [{model['location']}]")

    if models:
        # Test prediction with first available model
        model_name = models[0]["name"]
        print(f"\nTesting prediction with {model_name}...")

        signal = predictor.generate_signal(sample_data, model_name, "TEST")

        if signal["success"]:
            print(f"\n✅ Signal generated successfully:")
            print(f"  Signal: {signal['signal']}")
            print(f"  Confidence: {signal['confidence']:.2%}")
            print(f"  Latest Price: ${signal['latest_price']:.2f}")
            print(f"  Probabilities: Up={signal['probabilities']['up']:.2%}, Down={signal['probabilities']['down']:.2%}")
        else:
            print(f"\n❌ Signal generation failed: {signal.get('error')}")
    else:
        print("\n⚠️  No models found - train a model first!")
