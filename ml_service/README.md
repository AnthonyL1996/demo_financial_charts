# ML Service

Machine Learning service for training and serving trading signal prediction models.

## Overview

This service provides:
- **Data Ingestion**: Download historical stock data from Yahoo Finance
- **Model Training**: Train XGBoost models on technical indicators
- **Signal Generation**: REST API for generating BUY/SELL/HOLD signals
- **Model Management**: Load, serve, and monitor trained models

## Quick Start

### 1. Start the Service

```bash
# From backend directory
cd backend
docker-compose up -d ml-service

# Check service health
curl http://localhost:5000/health
```

### 2. Download Data

```bash
# Download SPY data (recommended for general model)
docker exec -it jdb-ml-service python scripts/download_data.py \
  --ticker SPY \
  --timeframe all \
  --start 2020-01-01 \
  --end 2024-11-14

# Verify data
docker exec -it jdb-ml-service python scripts/check_data.py --dir /app/data
```

### 3. Train Model

```bash
# Train on SPY (daily + weekly)
docker exec -it jdb-ml-service python scripts/train_from_parquet.py \
  --ticker SPY \
  --timeframe all \
  --data-dir /app/data

# Training takes ~5-10 minutes
# Models are saved to /app/models/
```

### 4. Generate Predictions

```bash
# Test the API
curl -X POST http://localhost:5000/api/signals/generate \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "data": [
      {
        "timestamp": "2024-01-01",
        "open": 180.0,
        "high": 182.0,
        "low": 179.0,
        "close": 181.0,
        "volume": 50000000
      }
      ...more data points (need 200+ for proper indicators)
    ],
    "model": "xgboost_daily_spy.pkl"
  }'
```

## Directory Structure

```
ml_service/
├── app.py                      # Flask API application
├── config/
│   └── config.py              # Configuration and settings
├── services/
│   ├── feature_engineering.py # Technical indicator calculations
│   └── model_predictor.py     # Model loading and predictions
├── scripts/
│   ├── download_data.py       # Data ingestion from Yahoo Finance
│   ├── train_from_parquet.py # Model training script
│   └── check_data.py          # Data validation utility
├── data/                      # Downloaded stock data (Parquet)
├── models/                    # Trained models
│   └── current/              # Active models for serving
├── logs/                      # Application logs
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
└── README.md                  # This file
```

## API Endpoints

### Health Check
```http
GET /health

Response:
{
  "status": "healthy",
  "service": "ml-service",
  "version": "v1",
  "timestamp": "2024-11-14T10:00:00"
}
```

### List Models
```http
GET /api/models

Response:
{
  "success": true,
  "models": [
    {
      "name": "xgboost_daily_spy.pkl",
      "path": "/app/models/current/xgboost_daily_spy.pkl",
      "size_kb": 2048.5,
      "location": "current"
    }
  ],
  "count": 1
}
```

### Get Model Info
```http
GET /api/models/{model_name}

Response:
{
  "success": true,
  "model": "xgboost_daily_spy.pkl",
  "info": {
    "ticker": "SPY",
    "timeframe": "daily",
    "metrics": {
      "test_accuracy": 0.568,
      "win_rate": 0.542,
      "sharpe_approx": 1.24
    },
    "version": "v1",
    "trained_at": "2024-11-14T10:00:00"
  }
}
```

### Generate Signal
```http
POST /api/signals/generate

Request:
{
  "ticker": "AAPL",
  "data": [...OHLCV data...],
  "model": "xgboost_daily_spy.pkl"
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
```

### Batch Generate Signals
```http
POST /api/signals/batch

Request:
{
  "tickers": {
    "AAPL": [...OHLCV data...],
    "MSFT": [...OHLCV data...]
  },
  "model": "xgboost_daily_spy.pkl"
}

Response:
{
  "success": true,
  "signals": {
    "AAPL": { signal data },
    "MSFT": { signal data }
  },
  "count": 2
}
```

### Calculate Features
```http
POST /api/features/calculate

Request:
{
  "data": [...OHLCV data...]
}

Response:
{
  "success": true,
  "data": [...data with technical indicators...],
  "features": ["sma_20", "sma_50", "rsi_14", "macd", ...]
}
```

### Get Configuration
```http
GET /api/config

Response:
{
  "success": true,
  "config": {
    "model_version": "v1",
    "buy_threshold": 0.6,
    "sell_threshold": 0.6,
    "sma_periods": [20, 50, 200],
    "rsi_period": 14,
    "macd_fast": 12,
    "macd_slow": 26
  }
}
```

## Training Workflow

### Recommended: Train on SPY

Train one general model on SPY (S&P 500) for use with all stocks:

```bash
# 1. Download SPY data
docker exec -it jdb-ml-service python scripts/download_data.py \
  --ticker SPY --timeframe all

# 2. Train model
docker exec -it jdb-ml-service python scripts/train_from_parquet.py \
  --ticker SPY --timeframe all

# 3. Model is now available at /app/models/current/xgboost_daily_spy.pkl
```

**Why SPY?**
- Contains patterns from 500 stocks
- Highest quality data
- Generalizes well to individual stocks
- One model for everything

### Advanced: Sector-Specific Models

For better sector-specific performance:

```bash
# Train on tech sector (QQQ)
docker exec -it jdb-ml-service python scripts/download_data.py --ticker QQQ --timeframe all
docker exec -it jdb-ml-service python scripts/train_from_parquet.py --ticker QQQ --timeframe all

# Train on finance sector (XLF)
docker exec -it jdb-ml-service python scripts/download_data.py --ticker XLF --timeframe all
docker exec -it jdb-ml-service python scripts/train_from_parquet.py --ticker XLF --timeframe all
```

Then route tech stocks (AAPL, MSFT) to QQQ model, finance stocks (JPM, BAC) to XLF model.

## Configuration

Edit `config/config.py` or set environment variables:

### Model Training Parameters
```python
N_ESTIMATORS = 200          # Number of trees
MAX_DEPTH = 6               # Tree depth
LEARNING_RATE = 0.1         # Learning rate
```

### Prediction Thresholds
```python
BUY_THRESHOLD = 0.6         # Confidence needed for BUY signal
SELL_THRESHOLD = 0.6        # Confidence needed for SELL signal
MIN_CONFIDENCE = 0.5        # Minimum confidence to show signal
```

### Technical Indicators
```python
SMA_PERIODS = [20, 50, 200] # Simple moving averages
RSI_PERIOD = 14              # RSI period
MACD_FAST = 12              # MACD fast period
MACD_SLOW = 26              # MACD slow period
```

## Model Performance Metrics

### Accuracy
Percentage of correct predictions. Target: **56-58%** for general model.

### Sharpe Ratio
Risk-adjusted returns. Target: **1.0-1.3** for good performance.

### Win Rate
Percentage of profitable trades. Target: **52-55%**.

### Interpretation
- **Accuracy > 55%**: Good model
- **Sharpe > 1.0**: Tradeable strategy
- **Win Rate > 52%**: Profitable with proper risk management

## Data Requirements

### Minimum Data
- **Daily**: 500 rows (2 years)
- **Weekly**: 200 rows (4 years)

### Recommended Data
- **Daily**: 1,000-2,000 rows (4-8 years)
- **Weekly**: 250-500 rows (5-10 years)

### Your Data (2020-2024)
- ~1,250 daily rows ✅
- ~250 weekly rows ✅
- **Perfect for training!**

## Troubleshooting

### Model Not Found
```bash
# List available models
docker exec -it jdb-ml-service ls -la /app/models/current/

# Train a model if missing
docker exec -it jdb-ml-service python scripts/train_from_parquet.py \
  --ticker SPY --timeframe daily
```

### Low Accuracy
- Ensure sufficient data (500+ rows)
- Check data quality: `python scripts/check_data.py`
- Try different hyperparameters in `config/config.py`
- Use SPY instead of individual ticker

### Data Download Fails
- Check internet connection
- Verify ticker symbol is valid
- Try different date range
- Yahoo Finance may rate-limit - retry after delay

### Container Won't Start
```bash
# Check logs
docker logs jdb-ml-service

# Rebuild container
cd backend
docker-compose build ml-service
docker-compose up -d ml-service
```

## Development

### Run Locally (without Docker)

```bash
# Install dependencies
cd ml_service
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Set environment variables
export API_HOST=0.0.0.0
export API_PORT=5000
export DEBUG=True

# Run Flask app
python app.py
```

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## Integration with Backend

The Spring Boot backend can call the ML service:

```kotlin
// Kotlin example
@Service
class MLServiceClient(
    @Value("\${ml.service.url}") private val mlServiceUrl: String
) {
    fun generateSignal(ticker: String, data: List<OHLCVData>): Signal {
        val request = SignalRequest(ticker, data)
        return restTemplate.postForObject(
            "$mlServiceUrl/api/signals/generate",
            request,
            SignalResponse::class.java
        )
    }
}
```

Configure in `application.yml`:
```yaml
ml:
  service:
    url: http://ml-service:5000
```

## Performance

- **Training time**: 5-10 minutes for SPY (daily + weekly)
- **Prediction time**: <100ms per request
- **Memory usage**: ~500MB with model loaded
- **CPU usage**: Minimal when idle, spikes during training

## Monitoring

### Check Service Health
```bash
curl http://localhost:5000/health
```

### View Logs
```bash
docker logs jdb-ml-service --tail 100 -f
```

### Check Model Performance
```bash
curl http://localhost:5000/api/models/xgboost_daily_spy.pkl
```

## Maintenance

### Monthly Retraining

Set up a cron job to retrain models monthly:

```bash
# On host machine, add to crontab
0 2 1 * * docker exec jdb-ml-service python scripts/train_from_parquet.py \
  --ticker SPY --timeframe all >> /var/log/ml_training.log 2>&1
```

### Model Versioning

Models are automatically versioned by date:
```
xgboost_daily_spy_v1_20241114.pkl  # Trained Nov 14, 2024
xgboost_daily_spy_v1_20241201.pkl  # Retrained Dec 1, 2024
```

The `current/` directory always contains the latest model.

### Backup Models

```bash
# Backup models directory
docker cp jdb-ml-service:/app/models ./ml_models_backup

# Restore from backup
docker cp ./ml_models_backup jdb-ml-service:/app/models
```

## Resources

- **Training Guide**: See `ML_TRAINING_GUIDE.md` in project root
- **XGBoost Documentation**: https://xgboost.readthedocs.io/
- **Yahoo Finance**: https://pypi.org/project/yfinance/
- **Technical Analysis**: https://technical-analysis-library-in-python.readthedocs.io/

## Support

For issues or questions:
1. Check logs: `docker logs jdb-ml-service`
2. Validate data: `python scripts/check_data.py`
3. Review training guide: `ML_TRAINING_GUIDE.md`
4. Open GitHub issue with error details

---

**Last Updated**: 2024-11-14
**Version**: 1.0
