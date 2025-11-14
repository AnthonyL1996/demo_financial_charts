# JDB Trading Backend

Spring Boot + Kotlin backend for the JDB Trading System with Yahoo Finance integration.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Java 21 (optional, for local development without Docker)

### Run with Docker (Recommended)

1. **Copy environment file:**
```bash
cp .env.example .env
```

2. **Start services:**
```bash
docker-compose up -d
```

3. **Check health:**
```bash
curl http://localhost:8080/api/health
```

4. **View logs:**
```bash
docker-compose logs -f backend
```

### Run Locally (Without Docker)

1. **Start PostgreSQL:**
```bash
docker-compose up -d postgres
```

2. **Run application:**
```bash
./gradlew bootRun
```

## 📡 API Endpoints

### Stock Endpoints

#### Get Stock List
```bash
GET /api/stocks
GET /api/stocks?search=AAPL
GET /api/stocks?limit=5
```

Response:
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
      "technicals": {...},
      "activeSignals": []
    }
  ],
  "timestamp": "2025-11-14T..."
}
```

#### Get Stock Details
```bash
GET /api/stocks/AAPL
```

#### Get Stock Price Data (OHLCV)
```bash
GET /api/stocks/AAPL/data
GET /api/stocks/AAPL/data?timeframe=1W
GET /api/stocks/AAPL/data?timeframe=1D&start=2025-01-01&end=2025-11-14
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "time": "2025-11-14T00:00:00Z",
      "open": 175.23,
      "high": 178.45,
      "low": 174.12,
      "close": 176.89,
      "volume": 52341567
    }
  ]
}
```

#### Get Technical Indicators
```bash
GET /api/stocks/AAPL/technicals
```

### Health Check
```bash
GET /api/health
```

## 🏗️ Project Structure

```
backend/
├── src/
│   ├── main/
│   │   ├── kotlin/com/jdb/trading/
│   │   │   ├── JdbTradingApplication.kt
│   │   │   ├── config/
│   │   │   │   └── CorsConfig.kt
│   │   │   ├── controller/
│   │   │   │   ├── HealthController.kt
│   │   │   │   └── StockController.kt
│   │   │   ├── service/
│   │   │   │   └── YahooFinanceService.kt
│   │   │   └── dto/
│   │   │       ├── ApiResponse.kt
│   │   │       ├── OHLCVDto.kt
│   │   │       ├── StockDto.kt
│   │   │       └── SignalDto.kt
│   │   └── resources/
│   │       ├── application.yml
│   │       └── db/migration/
│   │           ├── V1__create_stocks_table.sql
│   │           ├── V2__create_stock_prices_table.sql
│   │           └── V3__create_signals_table.sql
│   └── test/
├── build.gradle.kts
├── docker-compose.yml
└── Dockerfile
```

## 🔧 Technology Stack

- **Framework:** Spring Boot 3.2.5
- **Language:** Kotlin 1.9.23
- **Database:** PostgreSQL 16
- **Data Source:** Yahoo Finance API
- **Build Tool:** Gradle 8.5
- **Java Version:** 21

## 📦 Dependencies

- Spring Boot Starter Web
- Spring Boot Starter Data JPA
- Spring Boot Starter Validation
- PostgreSQL Driver
- Flyway (Database Migrations)
- Yahoo Finance API
- ta4j (Technical Analysis)
- Kotlin Logging

## 🗄️ Database

### Connect to Database
```bash
docker-compose exec postgres psql -U jdb_user -d jdb_trading
```

### View Tables
```sql
\dt
```

### View Migrations
```sql
SELECT * FROM flyway_schema_history;
```

## 🧪 Testing

```bash
./gradlew test
```

## 🛠️ Development

### Hot Reload
The application includes Spring Boot DevTools for automatic restart on code changes.

### Database Migrations
Flyway migrations run automatically on startup. Place new migrations in:
```
src/main/resources/db/migration/
```

Naming convention: `V{version}__{description}.sql`
Example: `V4__add_portfolio_table.sql`

### Logging
Adjust logging levels in `application.yml`:
```yaml
logging:
  level:
    com.jdb.trading: DEBUG
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in .env file
BACKEND_PORT=8081
```

### Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs postgres
```

### Yahoo Finance API Rate Limit
The service includes:
- 5-minute caching
- Retry logic with exponential backoff
- Configurable retry attempts

Adjust in `application.yml`:
```yaml
yahoo-finance:
  cache-duration-seconds: 300
  retry-attempts: 3
```

## 📝 Next Steps

- [ ] Implement Technical Analysis Service
- [ ] Add Signal Generation Logic
- [ ] Create Portfolio Management
- [ ] Add Backtesting Engine
- [ ] Implement WebSocket Support
- [ ] Add Authentication (JWT)
- [ ] Set up Redis Caching

## 🔗 Related

- [Frontend Repository](../README.md)
- [Implementation Plan](../IMPLEMENTATION_PLAN.md)
- [Backend Architecture](../BACKEND_ARCHITECTURE.md)

## 📄 License

Private - All Rights Reserved
