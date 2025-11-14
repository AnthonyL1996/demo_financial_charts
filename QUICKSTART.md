# 🚀 Quick Start Guide - JDB Trading System

Get the backend running and connected to your frontend in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- Ports 8080 (backend) and 5432 (database) available

## Step 1: Start the Backend

```bash
cd backend
docker-compose up -d
```

This will:
- Start PostgreSQL database
- Build and start Spring Boot backend
- Run Flyway database migrations automatically

## Step 2: Verify Backend is Running

```bash
# Check health endpoint
curl http://localhost:8080/api/health

# Expected response:
# {
#   "status": "UP",
#   "service": "jdb-trading-backend",
#   "timestamp": "2025-11-14T..."
# }
```

## Step 3: Test Yahoo Finance Integration

```bash
# Get stock list
curl http://localhost:8080/api/stocks

# Get Apple stock data
curl http://localhost:8080/api/stocks/AAPL

# Get OHLCV price data
curl "http://localhost:8080/api/stocks/AAPL/data?timeframe=1D"

# Get weekly data for the last year
curl "http://localhost:8080/api/stocks/AAPL/data?timeframe=1W&start=2024-01-01"
```

## Step 4: View Logs

```bash
# View backend logs
docker-compose logs -f backend

# View database logs
docker-compose logs -f postgres
```

## Step 5: Connect Frontend to Backend

Update your Next.js `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8080/api
```

Then restart your frontend:

```bash
cd ..  # Back to project root
npm run dev
```

## Testing the Integration

### Test Stock Data API

```bash
# Fetch Tesla stock data
curl http://localhost:8080/api/stocks/TSLA | jq

# Expected response structure:
# {
#   "success": true,
#   "data": {
#     "ticker": "TSLA",
#     "companyName": "Tesla, Inc.",
#     "currentPrice": 242.75,
#     "priceChange": 5.67,
#     "volume": 98765432,
#     "marketCap": 770000000000,
#     "technicals": {...},
#     "activeSignals": []
#   },
#   "timestamp": "2025-11-14T..."
# }
```

### Test OHLCV Data Endpoint

```bash
# Get daily OHLCV data for Microsoft
curl "http://localhost:8080/api/stocks/MSFT/data?timeframe=1D" | jq

# Expected response:
# {
#   "success": true,
#   "data": [
#     {
#       "time": "2025-11-14T00:00:00Z",
#       "open": 368.45,
#       "high": 372.15,
#       "low": 366.23,
#       "close": 370.89,
#       "volume": 34567890
#     },
#     ...
#   ]
# }
```

## Troubleshooting

### Backend Not Starting

```bash
# Check if containers are running
docker-compose ps

# Check logs for errors
docker-compose logs backend

# Restart services
docker-compose restart
```

### Port Already in Use

Edit `backend/.env`:
```env
BACKEND_PORT=8081
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

### Yahoo Finance API Errors

The Yahoo Finance API sometimes has rate limits or temporary outages. The backend includes:
- Automatic retry with exponential backoff (3 attempts)
- 5-minute caching to reduce API calls
- Graceful error handling

If you see errors, wait a few minutes and try again.

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose exec postgres psql -U jdb_user -d jdb_trading

# View tables
\dt

# Exit PostgreSQL
\q
```

## Stop the Backend

```bash
cd backend
docker-compose down

# To remove volumes (database data):
docker-compose down -v
```

## Next Steps

### 1. Implement Technical Analysis

See `IMPLEMENTATION_PLAN.md` Phase 2:
- Moving Averages (20, 50, 200)
- RSI calculation
- Bollinger Bands
- ATR (Average True Range)

### 2. Add Signal Generation

Implement the JDB "Kruispunt" methodology:
- Dominant MA detection
- Fibonacci retracement levels
- RSI divergence detection
- Volume confirmation

### 3. Add Portfolio Management

- Create portfolio endpoints
- Position tracking
- P&L calculations
- Risk metrics

### 4. Deploy to Proxmox

See `backend/README.md` for Proxmox deployment instructions.

## Useful Commands

```bash
# Rebuild backend after code changes
cd backend
docker-compose up -d --build

# View all logs
docker-compose logs

# Access database
docker-compose exec postgres psql -U jdb_user -d jdb_trading

# Stop all containers
docker-compose down

# Remove everything including volumes
docker-compose down -v

# Check backend health
curl http://localhost:8080/api/health

# Test with different stocks
for ticker in AAPL TSLA MSFT NVDA GOOGL; do
  echo "=== $ticker ==="
  curl -s "http://localhost:8080/api/stocks/$ticker" | jq '.data.currentPrice'
done
```

## Frontend Integration

Once the backend is running, update your Next.js API client in `lib/api/client.ts`:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api';

export const apiClient = {
  get: async <T>(endpoint: string, config?: AxiosRequestConfig): Promise<T> => {
    const response = await axios.get(`${API_BASE_URL}${endpoint}`, config);
    // Backend returns ApiResponse wrapper with success, data, timestamp
    return response.data.data;  // Extract data field
  },
  // ... other methods
};
```

## Support

- **Backend Architecture:** See `BACKEND_ARCHITECTURE.md`
- **Implementation Plan:** See `IMPLEMENTATION_PLAN.md`
- **Backend README:** See `backend/README.md`
- **Issues:** Check Docker logs and Yahoo Finance API status

---

**That's it!** Your backend is now running with real Yahoo Finance data. 🎉

Test it by navigating to your Next.js frontend and viewing stock charts - they should now display real market data instead of mock data.
