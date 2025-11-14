# 🧪 Backend Testing Guide

Complete step-by-step guide to test your JDB Trading Backend.

## Prerequisites Check

Before starting, verify you have:

```bash
# Docker
docker --version
# Should show: Docker version 20.x or higher

# Docker Compose
docker compose version
# Should show: Docker Compose version 2.x or higher

# curl (for testing)
curl --version

# jq (optional, for pretty JSON)
jq --version
```

## Step 1: Start the Backend

Navigate to the backend directory and start services:

```bash
cd backend
docker compose up -d
```

**Expected Output:**
```
[+] Running 3/3
 ✔ Network backend_jdb-network  Created
 ✔ Container jdb-postgres        Started
 ✔ Container jdb-backend         Started
```

## Step 2: Monitor Startup

Watch the logs to see when everything is ready:

```bash
docker compose logs -f
```

**Look for these SUCCESS indicators:**

### PostgreSQL Ready:
```
jdb-postgres  | PostgreSQL init process complete; ready for start up.
jdb-postgres  | database system is ready to accept connections
```

### Backend Ready:
```
jdb-backend   | Started JdbTradingApplicationKt in X.XXX seconds
jdb-backend   | Tomcat started on port 8080
```

Press `Ctrl+C` to stop following logs.

## Step 3: Verify Containers are Running

```bash
docker compose ps
```

**Expected Output:**
```
NAME            IMAGE               STATUS          PORTS
jdb-backend     backend-backend     Up (healthy)    0.0.0.0:8080->8080/tcp
jdb-postgres    postgres:16-alpine  Up (healthy)    0.0.0.0:5432->5432/tcp
```

Both should show status as **"Up (healthy)"**.

## Step 4: Test Health Endpoint

```bash
curl http://localhost:8080/api/health
```

**Expected Response:**
```json
{
  "status": "UP",
  "service": "jdb-trading-backend",
  "timestamp": "2025-11-14T12:34:56.789Z"
}
```

✅ If you see this, **your backend is running!**

## Step 5: Test Stock List API

```bash
curl http://localhost:8080/api/stocks | jq
```

**Expected Response:**
```json
{
  "success": true,
  "data": [
    {
      "ticker": "AAPL",
      "companyName": "Apple Inc.",
      "currentPrice": 175.23,
      "priceChange": -2.34,
      "volume": 52341567,
      "marketCap": 2750000000000,
      "technicals": {
        "ma20": 0.0,
        "ma50": 0.0,
        "ma200": 0.0,
        "rsi": 50.0,
        "bollingerUpper": 0.0,
        "bollingerMiddle": 0.0,
        "bollingerLower": 0.0,
        "atr": 0.0,
        "volume": 0,
        "volumeMA": 0
      },
      "activeSignals": []
    },
    {
      "ticker": "TSLA",
      "companyName": "Tesla, Inc.",
      ...
    }
  ],
  "timestamp": "2025-11-14T12:34:56.789Z"
}
```

**Note:** The `currentPrice` and other values are **REAL** data from Yahoo Finance!

## Step 6: Test Individual Stock Data

```bash
# Get Apple stock info
curl http://localhost:8080/api/stocks/AAPL | jq

# Get Tesla stock info
curl http://localhost:8080/api/stocks/TSLA | jq

# Get NVIDIA stock info
curl http://localhost:8080/api/stocks/NVDA | jq
```

**Expected Response Format:**
```json
{
  "success": true,
  "data": {
    "ticker": "AAPL",
    "companyName": "Apple Inc.",
    "sector": null,
    "industry": null,
    "currentPrice": 175.23,
    "priceChange": -1.25,
    "volume": 52341567,
    "marketCap": 2750000000000,
    "technicals": {...},
    "activeSignals": []
  },
  "timestamp": "2025-11-14T12:34:56.789Z"
}
```

## Step 7: Test OHLCV Price Data

### Get Daily Data (Last 6 Months)

```bash
curl "http://localhost:8080/api/stocks/AAPL/data?timeframe=1D" | jq
```

**Expected Response:**
```json
{
  "success": true,
  "data": [
    {
      "time": "2025-05-14T00:00:00Z",
      "open": 170.23,
      "high": 172.45,
      "low": 169.12,
      "close": 171.89,
      "volume": 45234567
    },
    {
      "time": "2025-05-15T00:00:00Z",
      "open": 172.01,
      "high": 174.23,
      "low": 171.34,
      "close": 173.45,
      "volume": 52341234
    },
    ...
    {
      "time": "2025-11-14T00:00:00Z",
      "open": 175.23,
      "high": 176.89,
      "low": 174.12,
      "close": 175.67,
      "volume": 48567890
    }
  ],
  "timestamp": "2025-11-14T12:34:56.789Z"
}
```

### Get Weekly Data

```bash
curl "http://localhost:8080/api/stocks/TSLA/data?timeframe=1W" | jq
```

### Get Monthly Data

```bash
curl "http://localhost:8080/api/stocks/MSFT/data?timeframe=1M" | jq
```

### Get Data for Specific Date Range

```bash
curl "http://localhost:8080/api/stocks/NVDA/data?timeframe=1D&start=2025-01-01&end=2025-11-14" | jq
```

## Step 8: Test Multiple Tickers

Create a quick test script:

```bash
#!/bin/bash
for ticker in AAPL TSLA MSFT NVDA GOOGL AMZN META; do
  echo "=== $ticker ==="
  curl -s "http://localhost:8080/api/stocks/$ticker" | jq '.data | {ticker, companyName, currentPrice, priceChange}'
  echo ""
done
```

Save as `test-stocks.sh`, make executable, and run:

```bash
chmod +x test-stocks.sh
./test-stocks.sh
```

## Step 9: Performance Testing

Test caching (should be much faster on second request):

```bash
# First request (hits Yahoo Finance API)
time curl -s "http://localhost:8080/api/stocks/AAPL/data?timeframe=1D" > /dev/null

# Second request (served from cache - should be < 100ms)
time curl -s "http://localhost:8080/api/stocks/AAPL/data?timeframe=1D" > /dev/null
```

## Step 10: Check Database

Connect to PostgreSQL and verify data:

```bash
docker compose exec postgres psql -U jdb_user -d jdb_trading
```

**Inside PostgreSQL:**

```sql
-- List all tables
\dt

-- Expected output:
--  Schema |         Name          | Type  |  Owner
-- --------+-----------------------+-------+----------
--  public | flyway_schema_history | table | jdb_user
--  public | signals               | table | jdb_user
--  public | stock_prices          | table | jdb_user
--  public | stocks                | table | jdb_user

-- View stocks table (should be empty initially)
SELECT * FROM stocks;

-- View migration history
SELECT * FROM flyway_schema_history;

-- Expected output shows 3 successful migrations:
-- V1__create_stocks_table.sql
-- V2__create_stock_prices_table.sql
-- V3__create_signals_table.sql

-- Exit PostgreSQL
\q
```

## Common Issues and Solutions

### Issue 1: Port 8080 Already in Use

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8080: bind: address already in use
```

**Solution:**
Edit `backend/.env`:
```env
BACKEND_PORT=8081
```

Restart:
```bash
docker compose down
docker compose up -d
```

### Issue 2: Yahoo Finance Rate Limit

**Error in logs:**
```
Failed to fetch quote for AAPL: Too Many Requests
```

**Solution:**
Wait 1-2 minutes. The backend has automatic retry logic and caching.

### Issue 3: Container Unhealthy

**Check:**
```bash
docker compose ps
# Shows: jdb-backend  Up (unhealthy)
```

**Debug:**
```bash
# View detailed logs
docker compose logs backend

# Check health endpoint manually
docker compose exec backend wget -O- http://localhost:8080/api/health
```

**Solution:**
Usually fixed by restarting:
```bash
docker compose restart backend
```

### Issue 4: Database Connection Failed

**Error in logs:**
```
Connection to localhost:5432 refused
```

**Solution:**
```bash
# Check PostgreSQL is running
docker compose ps postgres

# Restart database
docker compose restart postgres

# Wait 10 seconds, then restart backend
sleep 10
docker compose restart backend
```

## Cleanup

### Stop Services (Keep Data)

```bash
docker compose down
```

### Stop Services and Remove Data

```bash
docker compose down -v
```

### Remove Everything

```bash
docker compose down -v --rmi all
```

## Success Checklist

- [ ] Health endpoint returns "UP"
- [ ] Stock list shows real prices from Yahoo Finance
- [ ] Individual stock endpoint works (AAPL, TSLA, etc.)
- [ ] OHLCV data endpoint returns historical prices
- [ ] Daily timeframe works
- [ ] Weekly timeframe works
- [ ] Monthly timeframe works
- [ ] Date range filtering works
- [ ] Second request is faster (caching works)
- [ ] Database has 3 tables and 3 migrations
- [ ] Both containers show "healthy" status

## Next Steps

Once all tests pass:

1. **Connect Frontend:**
   - Update `.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8080/api`
   - Restart Next.js dev server
   - Verify charts show real Yahoo Finance data

2. **Implement Phase 2:**
   - Add technical indicators calculation
   - Calculate Moving Averages (MA20, MA50, MA200)
   - Implement RSI, Bollinger Bands, ATR

3. **Add Signal Generation:**
   - Implement JDB "Kruispunt" methodology
   - Generate trading signals
   - Store signals in database

4. **Deploy to Proxmox:**
   - Transfer backend to Proxmox server
   - Set up production environment
   - Configure reverse proxy

## Useful Monitoring Commands

```bash
# View live logs
docker compose logs -f

# View only backend logs
docker compose logs -f backend

# View only database logs
docker compose logs -f postgres

# Check resource usage
docker stats

# Restart specific service
docker compose restart backend

# Rebuild after code changes
docker compose up -d --build backend
```

## API Reference Quick Guide

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/stocks` | GET | List stocks with real-time data |
| `/api/stocks?search=AAPL` | GET | Search for specific stock |
| `/api/stocks/{ticker}` | GET | Get stock details |
| `/api/stocks/{ticker}/data` | GET | Get OHLCV price history |
| `/api/stocks/{ticker}/data?timeframe=1W` | GET | Weekly data |
| `/api/stocks/{ticker}/data?start=2025-01-01` | GET | Data from specific date |
| `/api/stocks/{ticker}/technicals` | GET | Technical indicators |

---

**Happy Testing!** 🚀

If you encounter any issues not covered here, check the logs with `docker compose logs -f` and look for error messages.
