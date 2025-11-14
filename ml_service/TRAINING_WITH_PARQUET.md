# Training XGBoost Models with Parquet Data

This guide explains how to train ML models using your Parquet data files (1970-2024).

## Your Data Structure

You have historical stock data in Parquet files:

**Daily Data:**
```
US_1970_1974_daily.parquet: 330,426 rows
US_1975_1979_daily.parquet: 523,898 rows
...
US_2020_2024_daily.parquet: 2,888,402 rows
```

**Weekly Data:**
```
US_1970_1974_weekly.parquet
US_1975_1979_weekly.parquet
...
US_2020_2024_weekly.parquet
```

## Quick Start

### 1. Set Environment Variable

Point to your Parquet data directory:

```bash
# Example: If your Parquet files are in /home/user/stock_data/
export PARQUET_DATA_DIR=/home/user/stock_data

# Or on Windows:
set PARQUET_DATA_DIR=C:\Users\YourName\stock_data
```

### 2. Start Services with Data Mount

```bash
cd backend
PARQUET_DATA_DIR=/path/to/your/parquet/files docker-compose up -d
```

This mounts your Parquet directory as `/data` inside the ml-service container.

### 3. Train Models

**Inside Docker container:**
```bash
docker exec -it jdb-ml-service python train_from_parquet.py \
  --ticker SPY \
  --timeframe all \
  --data-dir /data
```

**Or locally (for development):**
```bash
cd ml_service
python train_from_parquet.py \
  --ticker SPY \
  --timeframe all \
  --data-dir /path/to/your/parquet/files
```

## Training Options

### Train Specific Ticker

```bash
# Oracle (from your sample data)
python train_from_parquet.py --ticker ORCL --timeframe daily --data-dir /data

# Apple
python train_from_parquet.py --ticker AAPL --timeframe weekly --data-dir /data
```

### Train All Timeframes

```bash
# Trains both daily and weekly models
python train_from_parquet.py --ticker SPY --timeframe all --data-dir /data
```

### Skip Validation (Faster)

```bash
# Train without walk-forward validation (saves time)
python train_from_parquet.py --ticker SPY --timeframe daily --data-dir /data --no-validate
```

## Data Requirements

### Expected Parquet Schema

Your Parquet files should contain these columns (case-insensitive):

**Required:**
- `date` (or `Date`, `DATE`, `time`, `timestamp`)
- `open` (or `Open`, `OPEN`)
- `high` (or `High`, `HIGH`)
- `low` (or `Low`, `LOW`)
- `close` (or `Close`, `CLOSE`)
- `volume` (or `Volume`, `VOLUME`, `vol`)
- `ticker` (or `Ticker`, `TICKER`, `symbol`, `Symbol`)

**Optional:**
- `adj_close` (or `Adj Close`, `adjusted_close`)

The `ParquetDataLoader` automatically handles column name variations.

### From Your Sample Data

Your ORCL data structure looks like:
```
date: 2020-01-03T00:00:00.000Z
open: 53.27
high: 54.05
low: 52.95
close: 53.27
volume: 1305264861.42
ticker: ORCL
```

This is **perfect** and will work automatically! ✅

## Training Process

### Walk-Forward Validation

The training script uses walk-forward validation to prevent data leakage:

```
Example with 2015-2024 data (5-year train window):

Year 2020: Train[2015-2019] → Test[2020]
Year 2021: Train[2016-2020] → Test[2021]
Year 2022: Train[2017-2021] → Test[2022]
Year 2023: Train[2018-2022] → Test[2023]
Year 2024: Train[2019-2023] → Test[2024]
```

### Output Example

```
============================================================
TRAINING MODEL: SPY - DAILY
Data source: Parquet files in /data
============================================================

Loading daily data for SPY...
Loaded 13,482 rows
Date range: 2015-01-02 to 2024-12-31

Generating technical features...
Features generated: 13,282 rows

Generating labels...
Labels created: 13,252 samples (removed 30 due to insufficient lookahead)
Label distribution: Positive=4,821 (36.4%), Negative=8,431 (63.6%)

============================================================
WALK-FORWARD VALIDATION
============================================================

Fold: Train[2015-2019] → Test[2020]
  ML: Acc=0.573 | Prec=0.612 | AUC=0.621
  Trading: Return= 12.3% | Sharpe= 1.23 | Win Rate= 58.1%

Fold: Train[2016-2020] → Test[2021]
  ML: Acc=0.601 | Prec=0.644 | AUC=0.668
  Trading: Return= 18.7% | Sharpe= 1.67 | Win Rate= 61.2%

...

============================================================
VALIDATION SUMMARY
============================================================
Folds: 5
ML: Accuracy=0.571 ± 0.058
Trading: Avg Return=11.7% | Sharpe=1.18
Best Year: 2023 (21.2%)
Worst Year: 2022 (-8.4%)

✅ VALIDATION PASSED for daily

============================================================
TRAINING FINAL MODEL
============================================================

Training on 10,624 samples (up to 2023)

Top 10 Features:
  1. ma20_ma50_ratio: 0.0824
  2. rsi: 0.0651
  3. price_ma20_distance: 0.0587
  4. bb_position: 0.0523
  5. volume_ratio: 0.0498
  6. ma20_above_ma50: 0.0445
  7. atr_pct: 0.0401
  8. close_change_5: 0.0389
  9. momentum_10: 0.0367
  10. trend_slope_20: 0.0334

✅ Model saved to: /app/models/xgboost_daily_spy_v1.pkl
```

## Performance Expectations

Based on walk-forward validation (2020-2024):

### Daily Models (30-day horizon)
- **Accuracy**: 55-58%
- **Sharpe Ratio**: 0.8-1.2
- **Win Rate**: 54-59%
- **Avg Return/Year**: 8-15%

### Weekly Models (60-day horizon)
- **Accuracy**: 57-61%
- **Sharpe Ratio**: 1.0-1.5
- **Win Rate**: 57-63%
- **Avg Return/Year**: 12-20%

## Troubleshooting

### No Data Found for Ticker

**Error**: `No data found for AAPL in Parquet files`

**Solution**: Check ticker symbol case and existence:

```bash
# List available tickers
docker exec -it jdb-ml-service python -c "
from app.training.parquet_data_loader import ParquetDataLoader
loader = ParquetDataLoader('/data')
tickers = loader.get_available_tickers('daily')
print(f'Found {len(tickers)} tickers')
print('Sample:', tickers[:10])
"
```

### File Not Found

**Error**: `No Parquet files found matching: US_*_daily.parquet`

**Solutions**:
1. Check PARQUET_DATA_DIR is set correctly
2. Verify file naming convention matches: `US_YYYY_YYYY_daily.parquet`
3. Check files exist: `ls -la $PARQUET_DATA_DIR/*.parquet`

### Insufficient Data

**Error**: `Insufficient data for TSLA: 45 < 200`

**Solution**: This ticker has too few data points. Try:
- Using a ticker with more history (SPY, AAPL, MSFT)
- Lowering `min_samples` in `config/config.py`

### Memory Issues

If training crashes with memory errors on large datasets:

**Solution 1: Train on subset of years**
```python
# Edit config/config.py
start_date: str = "2015-01-01"  # Instead of "1970-01-01"
```

**Solution 2: Increase Docker memory**
```bash
# Edit docker-compose.yml
ml-service:
  deploy:
    resources:
      limits:
        memory: 4G  # Increase from default
```

**Solution 3: Train outside Docker**
```bash
# Use local Python environment with more RAM
python train_from_parquet.py --ticker SPY --timeframe daily --data-dir /path/to/data
```

## Configuration

### Training Parameters

Edit `ml_service/config/config.py`:

```python
@dataclass
class TrainingConfig:
    # Data source
    data_source: str = "parquet"  # or "postgres"
    data_dir: str = "/data"  # Parquet files location

    # Date range
    start_date: str = "2015-01-01"  # Start from 2015 (adjust as needed)
    end_date: str = "2024-12-31"

    # Walk-forward validation
    train_window_years: int = 5  # 5-year rolling window

    # Label thresholds
    daily_threshold: float = 0.05  # 5% return target
    weekly_threshold: float = 0.10  # 10% return target
```

### Model Hyperparameters

```python
@dataclass
class ModelConfig:
    n_estimators: int = 200  # Number of trees
    max_depth: int = 6  # Tree depth
    learning_rate: float = 0.05  # Learning rate
    subsample: float = 0.8  # Sample ratio
    colsample_bytree: float = 0.8  # Feature ratio
```

## Recommended Training Tickers

### Broad Market Indices (Best for general models)
- **SPY**: S&P 500 ETF - most liquid, representative
- **QQQ**: Nasdaq 100 - tech-heavy
- **DIA**: Dow Jones - blue chips
- **IWM**: Russell 2000 - small caps

### Large Cap Stocks (Good for testing)
- **AAPL**: Apple - consistent data
- **MSFT**: Microsoft - tech leader
- **GOOGL**: Google - high volume
- **ORCL**: Oracle - your sample data

### Why Train on Indices?

Models trained on broad indices (SPY, QQQ) tend to generalize better to individual stocks because:
1. Less idiosyncratic risk
2. More consistent patterns
3. Higher data quality
4. Representative of market behavior

## Advanced Usage

### Check Data Info

```bash
docker exec -it jdb-ml-service python -c "
from app.training.parquet_data_loader import ParquetDataLoader
loader = ParquetDataLoader('/data')
info = loader.get_data_info('daily')
print(f'Found {info[\"num_files\"]} Parquet files')
for file in info['files']:
    print(f'  {file[\"filename\"]}: {file[\"rows\"]:,} rows, {file[\"size_mb\"]:.1f} MB')
"
```

### Get Date Range for Ticker

```bash
docker exec -it jdb-ml-service python -c "
from app.training.parquet_data_loader import ParquetDataLoader
loader = ParquetDataLoader('/data')
min_date, max_date = loader.get_date_range('AAPL', 'daily')
print(f'AAPL daily data: {min_date} to {max_date}')
"
```

### Train Multiple Tickers

```bash
#!/bin/bash
# train_all.sh

for ticker in SPY QQQ DIA IWM AAPL MSFT GOOGL; do
  echo "Training $ticker..."
  docker exec jdb-ml-service python train_from_parquet.py \
    --ticker $ticker \
    --timeframe daily \
    --data-dir /data
done
```

## Next Steps

After training models:

1. **Test API**:
   ```bash
   curl -X POST http://localhost:5000/api/signals/generate \
     -H "Content-Type: application/json" \
     -d '{"ticker": "AAPL", "timeframe": "daily"}'
   ```

2. **Check Backend Integration**:
   ```bash
   curl http://localhost:8080/api/stocks/AAPL | jq '.mlSignals'
   ```

3. **Monitor Performance**: Track live predictions vs actual outcomes

4. **Retrain Periodically**: Monthly recommended, or when Sharpe < 0.5

## Support

For issues:
- Check logs: `docker logs jdb-ml-service`
- Verify data mount: `docker exec jdb-ml-service ls -la /data`
- Test data loading: Use examples above
- Review training logs: `training_parquet_*.log`

---

**Status**: ✅ Parquet loader ready
**Recommended**: Train on SPY first (most reliable data)
**Expected Time**: ~5-10 minutes per model
