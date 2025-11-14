# 🚀 START HERE - Quick Setup Guide

Get your JDB Trading Backend running in **5 commands**!

## Step 1: Navigate to Backend

```bash
cd backend
```

## Step 2: Start Everything

```bash
docker compose up -d
```

This starts:
- ✅ PostgreSQL database
- ✅ Spring Boot backend with Yahoo Finance integration

## Step 3: Wait for Startup (30 seconds)

```bash
sleep 30
```

Or watch the logs:
```bash
docker compose logs -f
# Press Ctrl+C when you see "Started JdbTradingApplicationKt"
```

## Step 4: Test the API

```bash
./test-api.sh
```

**Expected Output:**
```
===========================================
JDB Trading Backend API Test Suite
===========================================
Testing: Health endpoint ... ✓ PASS (HTTP 200)
Testing: Get all stocks ... ✓ PASS (HTTP 200)
Testing: Get AAPL stock ... ✓ PASS (HTTP 200)
Testing: Get AAPL daily data ... ✓ PASS (HTTP 200)
...
All tests passed! 🎉
```

## Step 5: Try It Yourself

```bash
# Get Apple stock data
curl http://localhost:8080/api/stocks/AAPL | jq

# Get Tesla price history
curl "http://localhost:8080/api/stocks/TSLA/data?timeframe=1D" | jq
```

---

## ✅ Success! What's Next?

### Connect Your Frontend

1. Update `.env.local` in your Next.js project:
```env
NEXT_PUBLIC_API_URL=http://localhost:8080/api
```

2. Restart your Next.js dev server:
```bash
npm run dev
```

3. Open http://localhost:3000

Your stock charts should now show **real Yahoo Finance data**! 📊

### View Real-Time Logs

```bash
docker compose logs -f backend
```

### Stop the Backend

```bash
docker compose down
```

---

## 📚 More Information

- **Detailed Testing Guide:** See [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Backend Documentation:** See [backend/README.md](backend/README.md)
- **Implementation Roadmap:** See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
- **5-Minute Quick Start:** See [QUICKSTART.md](QUICKSTART.md)

---

## 🆘 Having Issues?

### Backend won't start?
```bash
docker compose logs backend
```

### Port 8080 in use?
Edit `backend/.env`:
```env
BACKEND_PORT=8081
```

Then restart:
```bash
docker compose down
docker compose up -d
```

### Yahoo Finance errors?
Wait 1-2 minutes (rate limiting). The backend auto-retries with backoff.

---

## 🎯 What You Just Built

- ✅ Production-ready Spring Boot + Kotlin backend
- ✅ Real-time stock data from Yahoo Finance
- ✅ RESTful API matching your frontend
- ✅ PostgreSQL database with migrations
- ✅ Docker containerization
- ✅ Automatic retries and caching
- ✅ CORS configured for Next.js

**Total files created:** 25+ files across backend architecture

**Technologies:**
- Spring Boot 3.2.5
- Kotlin 1.9.23
- PostgreSQL 16
- Yahoo Finance API
- Docker & Docker Compose
- Flyway migrations
- ta4j (technical analysis library - ready for Phase 2)

---

**Ready to trade! 📈**
