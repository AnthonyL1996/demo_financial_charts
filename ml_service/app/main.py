"""
Flask application for ML service API
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import sys
from datetime import datetime

from app.models.model_predictor import ModelPredictor
from config.config import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, origins=config.api.cors_origins_list)

# Initialize model predictor
predictor = ModelPredictor()

logger.info("Flask application initialized")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'UP',
        'service': 'ml-service',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200


@app.route('/api/signals/generate', methods=['POST'])
def generate_signal():
    """
    Generate trading signal for a ticker

    Request body:
    {
        "ticker": "AAPL",
        "timeframe": "daily"  # optional, defaults to "daily"
    }

    Response:
    {
        "ticker": "AAPL",
        "timeframe": "daily",
        "signal": "BUY" | "NONE",
        "confidence": 0.87,
        "prediction_date": "2024-11-14",
        "current_price": 150.35,
        "target": {
            "horizon_days": 30,
            "expected_return": 5.0,
            "target_price": 157.87,
            "threshold": 5.0
        },
        "technicals": {...},
        "model": {...}
    }
    """
    try:
        data = request.get_json()

        if not data or 'ticker' not in data:
            return jsonify({
                'error': 'Missing required field: ticker'
            }), 400

        ticker = data['ticker'].upper()
        timeframe = data.get('timeframe', 'daily').lower()

        if timeframe not in ['daily', 'weekly', 'monthly']:
            return jsonify({
                'error': f'Invalid timeframe: {timeframe}. Must be daily, weekly, or monthly'
            }), 400

        # Generate signal
        result = predictor.generate_signal(ticker, timeframe)

        # Check for errors
        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in generate_signal: {e}", exc_info=True)
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/signals/multi-timeframe', methods=['POST'])
def generate_multi_timeframe_signals():
    """
    Generate signals for all timeframes

    Request body:
    {
        "ticker": "AAPL"
    }

    Response:
    {
        "ticker": "AAPL",
        "signals": {
            "daily": {...},
            "weekly": {...},
            "monthly": {...}
        },
        "consensus": {
            "recommendation": "STRONG_BUY",
            "strength": "STRONG",
            "bullish_timeframes": 3,
            "avg_confidence": 0.85,
            "suggested_position_size": 0.10,
            "notes": "All timeframes bullish"
        }
    }
    """
    try:
        data = request.get_json()

        if not data or 'ticker' not in data:
            return jsonify({
                'error': 'Missing required field: ticker'
            }), 400

        ticker = data['ticker'].upper()

        # Generate multi-timeframe signals
        result = predictor.generate_multi_timeframe_signals(ticker)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in generate_multi_timeframe_signals: {e}", exc_info=True)
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/model/info', methods=['GET'])
def get_model_info():
    """
    Get information about loaded models

    Query params:
    - timeframe: daily, weekly, monthly, or all (default: all)

    Response:
    {
        "daily": {
            "model_file": "xgboost_daily_spy_v1.pkl",
            "loaded": true,
            "trained_on": "SPY",
            "version": "v1"
        },
        ...
    }
    """
    try:
        timeframe = request.args.get('timeframe', 'all').lower()

        timeframes = ['daily', 'weekly', 'monthly'] if timeframe == 'all' else [timeframe]

        info = {}

        for tf in timeframes:
            model_file = f"xgboost_{tf}_spy_v1.pkl"
            model_path = config.api.model_path / model_file

            info[tf] = {
                'model_file': model_file,
                'loaded': f"{tf}_spy" in predictor.models,
                'exists': model_path.exists(),
                'trained_on': 'SPY',
                'version': 'v1'
            }

        return jsonify(info), 200

    except Exception as e:
        logger.error(f"Error in get_model_info: {e}", exc_info=True)
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


def main():
    """Run Flask application"""
    logger.info(f"Starting ML Service on {config.api.host}:{config.api.port}")
    logger.info(f"Debug mode: {config.api.debug}")
    logger.info(f"CORS origins: {config.api.cors_origins_list}")
    logger.info(f"Model path: {config.api.model_path}")

    app.run(
        host=config.api.host,
        port=config.api.port,
        debug=config.api.debug
    )


if __name__ == '__main__':
    main()
