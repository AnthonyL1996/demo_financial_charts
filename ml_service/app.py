"""
ML Service Flask API
REST API for model training, predictions, and management.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from loguru import logger

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config.config import settings, init_directories
from services.model_predictor import get_predictor

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize directories
init_directories()

# Initialize predictor
predictor = get_predictor()

# Configure logging
logger.add(
    settings.LOGS_DIR / "api_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
)


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "ml-service",
        "version": settings.MODEL_VERSION,
        "timestamp": datetime.now().isoformat(),
    })


@app.route("/api/models", methods=["GET"])
def list_models():
    """List all available models."""
    try:
        models = predictor.list_available_models()

        return jsonify({
            "success": True,
            "models": models,
            "count": len(models),
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


@app.route("/api/models/<model_name>", methods=["GET"])
def get_model_info(model_name: str):
    """Get detailed information about a specific model."""
    try:
        info = predictor.get_model_info(model_name)

        if info is None:
            return jsonify({
                "success": False,
                "error": f"Model not found: {model_name}",
            }), 404

        return jsonify({
            "success": True,
            "model": model_name,
            "info": info,
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


@app.route("/api/signals/generate", methods=["POST"])
def generate_signal():
    """
    Generate trading signal from OHLCV data.

    Request body:
    {
        "ticker": "AAPL",
        "data": [
            {
                "timestamp": "2024-01-01",
                "open": 180.0,
                "high": 182.0,
                "low": 179.0,
                "close": 181.0,
                "volume": 50000000
            },
            ...
        ],
        "model": "xgboost_daily_spy.pkl"  // optional
    }

    Response:
    {
        "success": true,
        "ticker": "AAPL",
        "signal": "BUY",
        "confidence": 0.73,
        "probabilities": {
            "down": 0.27,
            "up": 0.73
        },
        "latest_price": 181.0,
        "timestamp": "2024-01-01T00:00:00",
        "model_used": "xgboost_daily_spy.pkl"
    }
    """
    try:
        # Parse request
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided",
            }), 400

        ticker = data.get("ticker")
        ohlcv_data = data.get("data")
        model_name = data.get("model", "xgboost_daily_spy.pkl")

        if not ticker:
            return jsonify({
                "success": False,
                "error": "ticker is required",
            }), 400

        if not ohlcv_data or not isinstance(ohlcv_data, list):
            return jsonify({
                "success": False,
                "error": "data must be a list of OHLCV records",
            }), 400

        # Convert to DataFrame
        df = pd.DataFrame(ohlcv_data)

        # Validate required columns
        required_columns = ["timestamp", "open", "high", "low", "close", "volume"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            return jsonify({
                "success": False,
                "error": f"Missing required columns: {missing}",
            }), 400

        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Generate signal
        logger.info(f"Generating signal for {ticker} using {model_name}")
        signal = predictor.generate_signal(df, model_name, ticker)

        return jsonify(signal)

    except Exception as e:
        logger.error(f"Error generating signal: {str(e)}")
        logger.exception(e)
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


@app.route("/api/signals/batch", methods=["POST"])
def batch_generate_signals():
    """
    Generate signals for multiple tickers.

    Request body:
    {
        "tickers": {
            "AAPL": [...ohlcv data...],
            "MSFT": [...ohlcv data...],
            ...
        },
        "model": "xgboost_daily_spy.pkl"  // optional
    }

    Response:
    {
        "success": true,
        "signals": {
            "AAPL": { signal data },
            "MSFT": { signal data },
            ...
        },
        "timestamp": "2024-01-01T00:00:00"
    }
    """
    try:
        # Parse request
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided",
            }), 400

        tickers_data = data.get("tickers")
        model_name = data.get("model", "xgboost_daily_spy.pkl")

        if not tickers_data or not isinstance(tickers_data, dict):
            return jsonify({
                "success": False,
                "error": "tickers must be a dictionary",
            }), 400

        # Convert each ticker's data to DataFrame
        data_dict = {}
        for ticker, ohlcv_data in tickers_data.items():
            df = pd.DataFrame(ohlcv_data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            data_dict[ticker] = df

        # Generate signals
        logger.info(f"Batch generating signals for {len(data_dict)} tickers")
        signals = predictor.batch_predict(data_dict, model_name)

        return jsonify({
            "success": True,
            "signals": signals,
            "count": len(signals),
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"Error in batch signal generation: {str(e)}")
        logger.exception(e)
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


@app.route("/api/features/calculate", methods=["POST"])
def calculate_features():
    """
    Calculate technical indicators for OHLCV data.

    Request body:
    {
        "data": [
            {
                "timestamp": "2024-01-01",
                "open": 180.0,
                "high": 182.0,
                "low": 179.0,
                "close": 181.0,
                "volume": 50000000
            },
            ...
        ]
    }

    Response:
    {
        "success": true,
        "data": [...data with indicators...],
        "features": ["sma_20", "rsi_14", ...],
        "timestamp": "2024-01-01T00:00:00"
    }
    """
    try:
        from services.feature_engineering import add_all_features

        # Parse request
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided",
            }), 400

        ohlcv_data = data.get("data")

        if not ohlcv_data or not isinstance(ohlcv_data, list):
            return jsonify({
                "success": False,
                "error": "data must be a list of OHLCV records",
            }), 400

        # Convert to DataFrame
        df = pd.DataFrame(ohlcv_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Calculate features
        logger.info("Calculating technical indicators")
        df_with_features = add_all_features(df)

        # Convert back to dict
        result_data = df_with_features.to_dict(orient="records")

        # Get list of added features
        original_columns = ["timestamp", "open", "high", "low", "close", "volume"]
        added_features = [col for col in df_with_features.columns if col not in original_columns]

        return jsonify({
            "success": True,
            "data": result_data,
            "features": added_features,
            "count": len(result_data),
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"Error calculating features: {str(e)}")
        logger.exception(e)
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


@app.route("/api/config", methods=["GET"])
def get_config():
    """Get current ML service configuration."""
    return jsonify({
        "success": True,
        "config": {
            "model_version": settings.MODEL_VERSION,
            "buy_threshold": settings.BUY_THRESHOLD,
            "sell_threshold": settings.SELL_THRESHOLD,
            "min_confidence": settings.MIN_CONFIDENCE,
            "sma_periods": settings.SMA_PERIODS,
            "ema_periods": settings.EMA_PERIODS,
            "rsi_period": settings.RSI_PERIOD,
            "macd_fast": settings.MACD_FAST,
            "macd_slow": settings.MACD_SLOW,
            "macd_signal": settings.MACD_SIGNAL,
        },
        "timestamp": datetime.now().isoformat(),
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "status": 404,
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "status": 500,
    }), 500


if __name__ == "__main__":
    logger.info("Starting ML Service API")
    logger.info(f"Host: {settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    app.run(
        host=settings.API_HOST,
        port=settings.API_PORT,
        debug=settings.DEBUG,
    )
