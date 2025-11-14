# JDB Trading - ML Service

XGBoost-based stock prediction microservice for generating trading signals across multiple timeframes.

## Overview

This Python ML microservice provides:
- **Multi-timeframe predictions**: Daily (30-day), Weekly (60-day), Monthly (365-day) horizons
- **Walk-forward validation**: Both rolling and anchored methods to prevent data leakage
- **30+ technical indicators**: MA, RSI, Bollinger Bands, ATR, volume analysis, and more
- **RESTful API**: Easy integration with the Kotlin backend
- **Docker-ready**: Containerized deployment with health checks

## Architecture

```
ml_service/
├── app/
│   ├── api/                    # Flask API endpoints
│   ├── features/               # Feature engineering (technical indicators)
│   ├── models/                 # Model predictor class
│   ├── training/               # Training pipeline & validation
│   │   ├── data_loader.py
│   │   ├── label_generator.py
│   │   ├── walk_forward_validator.py
│   │   └── train_model.py
│   ├── utils/                  # DB connector, metrics
│   └── main.py                 # Flask application
├── config/                     # Configuration
├── models/                     # Trained model storage
├── notebooks/                  # Jupyter notebooks (analysis)
├── tests/                      # Unit tests
├── requirements.txt
└── Dockerfile
```

## Features

### 1. Technical Indicators (30+ features)
- **Moving Averages**: MA20, MA50, MA200 + crossover signals
- **Momentum**: RSI, ROC, momentum indicators
- **Volatility**: Bollinger Bands, ATR, price ranges
- **Volume**: Volume MA, volume surges, volume trends
- **Trend**: Linear regression slopes, higher highs/lower lows
- **Price Action**: Gap analysis, candlestick patterns

### 2. Multi-Timeframe Models
| Timeframe | Horizon | Target Return | Use Case |
|-----------|---------|---------------|----------|
| Daily     | 30 days | 5%+          | Short-term swing trades |
| Weekly    | 60 days | 10%+         | Medium-term positions |
| Monthly   | 365 days| 20%+         | Long-term holdings |

### 3. Walk-Forward Validation
- **Rolling Window**: Fixed 5-year training window, tests on each subsequent year
- **Anchored Window**: Growing training window anchored to 2015
- **Out-of-Sample Testing**: Never trains on future data
- **Performance Metrics**: Accuracy, Sharpe ratio, win rate, max drawdown

## Quick Start

### 1. Training Models

Train all timeframe models for SPY:

```bash
cd ml_service
python -m app.training.train_model --ticker SPY --timeframe all
```

Train specific timeframe:

```bash
python -m app.training.train_model --ticker SPY --timeframe daily
```

Skip validation (faster):

```bash
python -m app.training.train_model --ticker SPY --no-validate
```

### 2. Running the API

**Local development**:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=jdb_trading
export DB_USER=jdb
export DB_PASSWORD=password

# Run Flask app
python -m app.main
```

**Docker (recommended)**:

```bash
# From backend directory
cd ../backend
docker-compose up ml-service
```

API will be available at `http://localhost:5000`

### 3. Testing the API

**Health check**:

```bash
curl http://localhost:5000/health
```

**Generate signal**:

```bash
curl -X POST http://localhost:5000/api/signals/generate \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "timeframe": "daily"}'
```

**Multi-timeframe signals**:

```bash
curl -X POST http://localhost:5000/api/signals/multi-timeframe \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

## API Endpoints

### POST /api/signals/generate

Generate signal for a specific timeframe.

**Request**:
```json
{
  "ticker": "AAPL",
  "timeframe": "daily"
}
```

**Response**:
```json
{
  "ticker": "AAPL",
  "timeframe": "daily",
  "signal": "BUY",
  "confidence": 0.873,
  "prediction_date": "2024-11-14",
  "current_price": 150.35,
  "target": {
    "horizon_days": 30,
    "expected_return": 5.0,
    "target_price": 157.87,
    "threshold": 5.0
  },
  "technicals": {
    "ma20": 149.50,
    "ma50": 148.20,
    "ma200": 145.00,
    "rsi": 58.3,
    "bollinger_bands": {
      "upper": 152.00,
      "middle": 150.00,
      "lower": 148.00
    },
    "atr": 2.15,
    "volume": 52500000,
    "volume_ratio": 1.12,
    "ma20_above_ma50": true,
    "ma50_above_ma200": true
  },
  "model": {
    "name": "xgboost_daily_spy_v1",
    "trained_on": "SPY"
  }
}
```

### POST /api/signals/multi-timeframe

Generate signals for all timeframes with consensus.

**Request**:
```json
{
  "ticker": "AAPL"
}
```

**Response**:
```json
{
  "ticker": "AAPL",
  "signals": {
    "daily": { ... },
    "weekly": { ... },
    "monthly": { ... }
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
```

### GET /api/model/info

Get information about loaded models.

**Response**:
```json
{
  "daily": {
    "model_file": "xgboost_daily_spy_v1.pkl",
    "loaded": true,
    "exists": true,
    "trained_on": "SPY",
    "version": "v1"
  },
  "weekly": { ... },
  "monthly": { ... }
}
```

## Configuration

Edit `config/config.py` or set environment variables:

### Database
- `DB_HOST` - PostgreSQL host (default: localhost)
- `DB_PORT` - PostgreSQL port (default: 5432)
- `DB_NAME` - Database name (default: jdb_trading)
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password

### API
- `API_HOST` - API host (default: 0.0.0.0)
- `API_PORT` - API port (default: 5000)
- `FLASK_ENV` - Environment (production|development)
- `MODEL_PATH` - Path to model files (default: /app/models)
- `CORS_ORIGINS` - Allowed CORS origins

### Training
- `train_window_years` - Rolling window size (default: 5)
- `daily_horizon_days` - Daily model target (default: 30)
- `daily_threshold` - Daily return threshold (default: 0.05)
- `weekly_horizon_days` - Weekly model target (default: 60)
- `weekly_threshold` - Weekly return threshold (default: 0.10)
- `monthly_horizon_days` - Monthly model target (default: 365)
- `monthly_threshold` - Monthly return threshold (default: 0.20)

## Training Pipeline

### Walk-Forward Validation Results

Example output from training:

```
============================================================
ROLLING WINDOW WALK-FORWARD VALIDATION
============================================================

2020: Train[2015-2019] (1234 samples) → Test (234 samples)
  ML Metrics: Accuracy=0.573 | Precision=0.612 | Recall=0.551 | AUC=0.621
  Trading:    Return= 12.3% | Sharpe= 1.23 | Drawdown= -3.2% | Win Rate= 58.1%
  Trades:     45 trades | Avg Win=3.45% | Avg Loss=-2.12%

2021: Train[2016-2020] (1312 samples) → Test (198 samples)
  ML Metrics: Accuracy=0.601 | Precision=0.644 | Recall=0.578 | AUC=0.668
  Trading:    Return= 18.7% | Sharpe= 1.67 | Drawdown= -2.8% | Win Rate= 61.2%
  Trades:     38 trades | Avg Win=4.12% | Avg Loss=-1.98%

...

============================================================
VALIDATION SUMMARY
============================================================

ROLLING WINDOW:
  Folds: 5
  ML Performance: Accuracy=0.571 ± 0.058 | Precision=0.617 | AUC=0.643
  Trading:        Avg Return=11.7% | Sharpe=1.18 | Win Rate=58.2%
  Best Year:      2023 (21.2%)
  Worst Year:     2022 (-8.4%)
  Consistency:    80.0% (profitable years)
  Status: ✅ PASSED (Sharpe > 0.5)
```

### Performance Expectations

Based on historical validation (2020-2024):

| Metric | Daily Model | Weekly Model | Monthly Model |
|--------|-------------|--------------|---------------|
| Accuracy | 55-58% | 57-61% | 60-65% |
| Sharpe Ratio | 0.8-1.2 | 1.0-1.5 | 1.2-1.8 |
| Win Rate | 54-59% | 57-63% | 61-67% |
| Avg Return/Year | 8-15% | 12-20% | 15-25% |

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Adding New Features

1. Add feature calculation to `app/features/technical_features.py`
2. Update `create_features()` method
3. Retrain models
4. Validate performance hasn't degraded

### Jupyter Notebooks

For exploratory analysis:

```bash
jupyter notebook notebooks/
```

## Integration with Kotlin Backend

The Kotlin backend calls this service via REST API. See `backend/src/main/kotlin/.../service/MLSignalService.kt` for integration code.

**Example Kotlin integration**:

```kotlin
@Service
class MLSignalService(
    @Value("\${ml-service.url}") private val mlServiceUrl: String,
    private val restTemplate: RestTemplate
) {
    fun generateSignals(ticker: String): MLSignalResponse {
        val request = mapOf("ticker" to ticker)
        return restTemplate.postForObject(
            "$mlServiceUrl/api/signals/multi-timeframe",
            request,
            MLSignalResponse::class.java
        ) ?: throw Exception("ML service unavailable")
    }
}
```

## Troubleshooting

**Models not found**:
```
FileNotFoundError: Model not found: /app/models/xgboost_daily_spy_v1.pkl
```
→ Run training first: `python -m app.training.train_model --ticker SPY`

**Insufficient data**:
```
Insufficient data for TSLA (daily)
```
→ Ensure PostgreSQL has enough historical data (min 200 rows)

**Database connection failed**:
```
could not connect to server: Connection refused
```
→ Check DB_HOST, DB_PORT environment variables
→ Ensure PostgreSQL is running

## Production Deployment

### Scaling Considerations

- Models are loaded into memory on first use (lazy loading)
- Each model ~10-50MB in memory
- Gunicorn runs with 4 workers (tune based on CPU)
- No GPU required (XGBoost CPU inference is fast)

### Monitoring

Key metrics to monitor:
- API response time (target: <500ms)
- Model prediction latency (target: <100ms)
- Database query time
- Error rate on /api/signals/* endpoints
- Memory usage per worker

### Retraining Schedule

Recommended retraining frequency:
- **Monthly**: Retrain on latest data
- **Quarterly**: Full walk-forward validation
- **Trigger**: If Sharpe ratio drops below 0.5 in live trading

## License

See main project LICENSE file.

## Support

For issues or questions, open a GitHub issue or contact the development team.
