# JDB Trading System - Backend Implementation Plan
## Spring Boot + Kotlin Backend for Existing Next.js Frontend

**Created:** 2025-11-14
**Target Deployment:** Docker on Proxmox
**Data Source:** Yahoo Finance

---

## 📋 Executive Summary

This implementation plan outlines the development of a Spring Boot + Kotlin backend that will replace the mock API currently used by the Next.js frontend. The backend will:

- Match the existing frontend API contracts exactly
- Fetch real stock data from Yahoo Finance
- Run in Docker containers locally and on Proxmox
- Support the JDB "Kruispunt" trading methodology

---

## 🎯 Phase 1: Project Setup & Yahoo Finance Integration
**Duration:** 1-2 weeks
**Priority:** CRITICAL

### 1.1 Project Structure

```
jdb-trading-backend/
├── src/
│   ├── main/
│   │   ├── kotlin/
│   │   │   └── com/jdb/trading/
│   │   │       ├── JdbTradingApplication.kt
│   │   │       ├── config/
│   │   │       │   ├── SecurityConfig.kt
│   │   │       │   ├── CorsConfig.kt
│   │   │       │   └── JpaConfig.kt
│   │   │       ├── controller/
│   │   │       │   ├── StockController.kt
│   │   │       │   ├── SignalController.kt
│   │   │       │   ├── PortfolioController.kt
│   │   │       │   └── BacktestController.kt
│   │   │       ├── service/
│   │   │       │   ├── YahooFinanceService.kt
│   │   │       │   ├── StockService.kt
│   │   │       │   ├── SignalService.kt
│   │   │       │   ├── TechnicalAnalysisService.kt
│   │   │       │   ├── PortfolioService.kt
│   │   │       │   └── BacktestService.kt
│   │   │       ├── domain/
│   │   │       │   └── entity/
│   │   │       │       ├── Stock.kt
│   │   │       │       ├── StockPrice.kt
│   │   │       │       ├── Signal.kt
│   │   │       │       ├── Portfolio.kt
│   │   │       │       └── Backtest.kt
│   │   │       ├── repository/
│   │   │       │   ├── StockRepository.kt
│   │   │       │   ├── StockPriceRepository.kt
│   │   │       │   └── SignalRepository.kt
│   │   │       └── dto/
│   │   │           ├── StockDto.kt
│   │   │           ├── SignalDto.kt
│   │   │           ├── OHLCVDto.kt
│   │   │           └── ApiResponse.kt
│   │   └── resources/
│   │       ├── application.yml
│   │       └── db/migration/
│   │           ├── V1__create_stocks.sql
│   │           ├── V2__create_stock_prices.sql
│   │           └── V3__create_signals.sql
│   └── test/
├── build.gradle.kts
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### 1.2 Dependencies (build.gradle.kts)

```kotlin
plugins {
    kotlin("jvm") version "1.9.23"
    kotlin("plugin.spring") version "1.9.23"
    kotlin("plugin.jpa") version "1.9.23"
    id("org.springframework.boot") version "3.2.5"
    id("io.spring.dependency-management") version "1.1.4"
}

dependencies {
    // Spring Boot
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-validation")

    // Database
    implementation("org.postgresql:postgresql")
    implementation("com.timescale:timescaledb:1.7.5")
    implementation("org.flywaydb:flyway-core")

    // Kotlin
    implementation("org.jetbrains.kotlin:kotlin-reflect")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")

    // Yahoo Finance Client
    implementation("com.yahoofinance-api:YahooFinanceAPI:3.17.0")

    // Technical Analysis
    implementation("org.ta4j:ta4j-core:0.15")

    // Testing
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("io.mockk:mockk:1.13.10")
}
```

### 1.3 Yahoo Finance Integration

**YahooFinanceService.kt:**
```kotlin
@Service
class YahooFinanceService {

    /**
     * Fetch OHLCV data from Yahoo Finance
     * Matches frontend API: GET /stocks/{ticker}/data
     */
    fun fetchStockData(
        ticker: String,
        timeframe: String = "1D",
        start: LocalDate? = null,
        end: LocalDate? = null
    ): List<OHLCVDto> {
        val stock = YahooFinance.get(ticker)
        val interval = when(timeframe) {
            "1W" -> Interval.WEEKLY
            "1M" -> Interval.MONTHLY
            else -> Interval.DAILY
        }

        val calendar = Calendar.getInstance()
        val from = start?.let {
            calendar.apply { time = Date.from(it.atStartOfDay(ZoneId.systemDefault()).toInstant()) }
        } ?: calendar.apply { add(Calendar.MONTH, -6) }

        val to = end?.let {
            calendar.apply { time = Date.from(it.atStartOfDay(ZoneId.systemDefault()).toInstant()) }
        } ?: Calendar.getInstance()

        val history = stock.getHistory(from, to, interval)

        return history.map { quote ->
            OHLCVDto(
                time = quote.date.toInstant().toString(),
                open = quote.open.toDouble(),
                high = quote.high.toDouble(),
                low = quote.low.toDouble(),
                close = quote.close.toDouble(),
                volume = quote.volume
            )
        }
    }

    /**
     * Fetch current stock quote
     */
    fun fetchCurrentQuote(ticker: String): Stock {
        val stock = YahooFinance.get(ticker)
        val quote = stock.quote

        return Stock(
            ticker = ticker,
            companyName = stock.name ?: ticker,
            currentPrice = quote.price.toDouble(),
            priceChange = quote.changeInPercent.toDouble(),
            volume = quote.volume,
            marketCap = stock.stats.marketCap?.toLong()
        )
    }
}
```

### 1.4 API Controllers Matching Frontend

**StockController.kt:**
```kotlin
@RestController
@RequestMapping("/api")
class StockController(
    private val stockService: StockService,
    private val yahooFinanceService: YahooFinanceService
) {

    /**
     * GET /api/stocks
     * Matches: stocksApi.getStocks()
     */
    @GetMapping("/stocks")
    fun getStocks(
        @RequestParam(required = false) search: String?,
        @RequestParam(required = false) limit: Int?
    ): ResponseEntity<ApiResponse<List<StockDto>>> {
        val stocks = stockService.getStocks(search, limit)
        return ResponseEntity.ok(ApiResponse.success(stocks))
    }

    /**
     * GET /api/stocks/{ticker}
     * Matches: stocksApi.getStock(ticker)
     */
    @GetMapping("/stocks/{ticker}")
    fun getStock(@PathVariable ticker: String): ResponseEntity<ApiResponse<StockDto>> {
        val stock = stockService.getStock(ticker)
        return ResponseEntity.ok(ApiResponse.success(stock))
    }

    /**
     * GET /api/stocks/{ticker}/data
     * Matches: stocksApi.getStockData(ticker, params)
     */
    @GetMapping("/stocks/{ticker}/data")
    fun getStockData(
        @PathVariable ticker: String,
        @RequestParam(required = false) timeframe: String?,
        @RequestParam(required = false) start: String?,
        @RequestParam(required = false) end: String?
    ): ResponseEntity<ApiResponse<List<OHLCVDto>>> {
        val data = yahooFinanceService.fetchStockData(
            ticker = ticker,
            timeframe = timeframe ?: "1D",
            start = start?.let { LocalDate.parse(it) },
            end = end?.let { LocalDate.parse(it) }
        )
        return ResponseEntity.ok(ApiResponse.success(data))
    }

    /**
     * GET /api/stocks/{ticker}/technicals
     * Matches: stocksApi.getTechnicals(ticker)
     */
    @GetMapping("/stocks/{ticker}/technicals")
    fun getTechnicals(@PathVariable ticker: String): ResponseEntity<ApiResponse<StockTechnicalsDto>> {
        val technicals = stockService.calculateTechnicals(ticker)
        return ResponseEntity.ok(ApiResponse.success(technicals))
    }
}
```

**SignalController.kt:**
```kotlin
@RestController
@RequestMapping("/api/signals")
class SignalController(private val signalService: SignalService) {

    /**
     * GET /api/signals
     * Matches: signalsApi.getSignals(filters)
     */
    @GetMapping
    fun getSignals(
        @RequestParam(required = false) type: List<String>?,
        @RequestParam(required = false) status: List<String>?,
        @RequestParam(required = false) minConfidence: Int?,
        @RequestParam(required = false) timeframe: List<String>?,
        @RequestParam(required = false) ticker: String?,
        @RequestParam(required = false) limit: Int?
    ): ResponseEntity<ApiResponse<List<SignalDto>>> {
        val signals = signalService.getSignals(
            SignalFilters(type, status, minConfidence, timeframe, ticker, limit)
        )
        return ResponseEntity.ok(ApiResponse.success(signals))
    }

    /**
     * GET /api/signals/{id}
     * Matches: signalsApi.getSignal(id)
     */
    @GetMapping("/{id}")
    fun getSignal(@PathVariable id: String): ResponseEntity<ApiResponse<SignalDto>> {
        val signal = signalService.getSignal(id)
        return ResponseEntity.ok(ApiResponse.success(signal))
    }
}
```

### 1.5 Database Schema (PostgreSQL + TimescaleDB)

**V1__create_stocks.sql:**
```sql
CREATE TABLE stocks (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_stocks_ticker ON stocks(ticker);
CREATE INDEX idx_stocks_is_active ON stocks(is_active);
```

**V2__create_stock_prices.sql:**
```sql
CREATE TABLE stock_prices (
    id BIGSERIAL,
    stock_id BIGINT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    date TIMESTAMP NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL,
    adj_close DECIMAL(12, 4),

    PRIMARY KEY (stock_id, date)
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('stock_prices', 'date');

CREATE INDEX idx_stock_prices_stock_date ON stock_prices(stock_id, date DESC);
```

**V3__create_signals.sql:**
```sql
CREATE TABLE signals (
    id VARCHAR(36) PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    confidence SMALLINT NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    expected_return DECIMAL(8, 4) NOT NULL,
    entry_price DECIMAL(12, 4) NOT NULL,
    target_price DECIMAL(12, 4) NOT NULL,
    stop_loss DECIMAL(12, 4) NOT NULL,
    risk_reward_ratio DECIMAL(8, 2) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    reasoning JSONB NOT NULL,
    generated_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP,
    actual_return DECIMAL(8, 4),
    exit_price DECIMAL(12, 4),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_signals_ticker ON signals(ticker);
CREATE INDEX idx_signals_status ON signals(status);
CREATE INDEX idx_signals_generated_at ON signals(generated_at DESC);
```

### 1.6 Docker Configuration

**Dockerfile:**
```dockerfile
FROM gradle:8.5-jdk21 AS build
WORKDIR /app

# Cache dependencies
COPY build.gradle.kts settings.gradle.kts ./
COPY gradle gradle
RUN gradle dependencies --no-daemon

# Build application
COPY src src
RUN gradle build --no-daemon -x test

# Runtime image
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# Create non-root user
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring

# Copy JAR
COPY --from=build /app/build/libs/*.jar app.jar

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/api/health || exit 1

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg16
    container_name: jdb-postgres
    environment:
      POSTGRES_DB: jdb_trading
      POSTGRES_USER: jdb_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme123}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U jdb_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - jdb-network

  backend:
    build: .
    container_name: jdb-backend
    ports:
      - "8080:8080"
    environment:
      SPRING_PROFILES_ACTIVE: dev
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: jdb_trading
      DB_USER: jdb_user
      DB_PASSWORD: ${DB_PASSWORD:-changeme123}
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8080/api/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    networks:
      - jdb-network

networks:
  jdb-network:
    driver: bridge

volumes:
  postgres_data:
```

### 1.7 Configuration Files

**application.yml:**
```yaml
spring:
  application:
    name: jdb-trading-backend

  datasource:
    url: jdbc:postgresql://${DB_HOST:localhost}:${DB_PORT:5432}/${DB_NAME:jdb_trading}
    username: ${DB_USER:jdb_user}
    password: ${DB_PASSWORD:changeme123}
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
      connection-timeout: 30000

  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect

  flyway:
    enabled: true
    baseline-on-migrate: true
    locations: classpath:db/migration

server:
  port: 8080
  servlet:
    context-path: /api

# CORS - Allow Next.js frontend
cors:
  allowed-origins:
    - http://localhost:3000
    - http://localhost:3001
  allowed-methods:
    - GET
    - POST
    - PUT
    - DELETE
  allowed-headers:
    - "*"
  max-age: 3600

# Yahoo Finance Configuration
yahoo-finance:
  cache-duration: 300  # 5 minutes
  retry-attempts: 3
```

---

## 🎯 Phase 2: Technical Analysis Service
**Duration:** 1 week

### 2.1 Technical Indicators Calculation

**TechnicalAnalysisService.kt:**
```kotlin
@Service
class TechnicalAnalysisService {

    fun calculateTechnicals(ticker: String, prices: List<StockPrice>): StockTechnicals {
        val closePrices = prices.map { it.close }.reversed()

        return StockTechnicals(
            ma20 = calculateSMA(closePrices, 20),
            ma50 = calculateSMA(closePrices, 50),
            ma200 = calculateSMA(closePrices, 200),
            rsi = calculateRSI(closePrices, 14),
            bollingerUpper = calculateBollingerUpper(closePrices, 20, 2.0),
            bollingerMiddle = calculateSMA(closePrices, 20),
            bollingerLower = calculateBollingerLower(closePrices, 20, 2.0),
            atr = calculateATR(prices, 14),
            volume = prices.last().volume,
            volumeMA = calculateVolumeSMA(prices, 20)
        )
    }

    private fun calculateSMA(prices: List<BigDecimal>, period: Int): Double {
        if (prices.size < period) return 0.0
        return prices.take(period).map { it.toDouble() }.average()
    }

    private fun calculateRSI(prices: List<BigDecimal>, period: Int): Double {
        // Standard RSI calculation
        // Implementation using ta4j library
    }

    private fun calculateATR(prices: List<StockPrice>, period: Int): Double {
        // Average True Range calculation
    }
}
```

### 2.2 JDB Signal Generation Logic

**SignalGeneratorService.kt:**
```kotlin
@Service
class SignalGeneratorService(
    private val technicalAnalysisService: TechnicalAnalysisService
) {

    fun generateSignal(ticker: String, stockData: List<StockPrice>): Signal? {
        val technicals = technicalAnalysisService.calculateTechnicals(ticker, stockData)
        val currentPrice = stockData.last().close.toDouble()

        // Step 1: Identify Dominant MA
        val dominantMA = identifyDominantMA(currentPrice, technicals)

        // Step 2: Check Bollinger Band Position
        val bbPosition = getBollingerPosition(currentPrice, technicals)

        // Step 3: Calculate Fibonacci Levels
        val fibLevel = calculateFibonacciLevel(stockData)

        // Step 4: Detect RSI Divergence
        val rsiDivergence = detectRSIDivergence(stockData)

        // Step 5: Volume Confirmation
        val volumeConfirmation = checkVolumeConfirmation(stockData)

        // Step 6: Determine Signal Type
        val signalType = determineSignalType(
            dominantMA, bbPosition, fibLevel, rsiDivergence, volumeConfirmation
        )

        if (signalType == null) return null

        // Calculate entry, target, stop loss
        val (entry, target, stopLoss) = calculateLevels(
            currentPrice, signalType, technicals, fibLevel
        )

        val confidence = calculateConfidence(
            dominantMA, bbPosition, fibLevel, rsiDivergence, volumeConfirmation
        )

        return Signal(
            ticker = ticker,
            type = signalType,
            confidence = confidence,
            entryPrice = entry,
            targetPrice = target,
            stopLoss = stopLoss,
            reasoning = SignalReasoning(
                dominantMA = dominantMA,
                bollingerBands = bbPosition,
                fibonacci = fibLevel,
                rsiDivergence = rsiDivergence,
                volumeConfirmation = volumeConfirmation,
                trendStrength = determineTrendStrength(technicals)
            )
        )
    }
}
```

---

## 🎯 Phase 3: API Response DTOs Matching Frontend
**Duration:** 3 days

### 3.1 DTO Mapping

**OHLCVDto.kt:**
```kotlin
data class OHLCVDto(
    val time: String,  // ISO date string to match frontend
    val open: Double,
    val high: Double,
    val low: Double,
    val close: Double,
    val volume: Long
)
```

**SignalDto.kt:**
```kotlin
data class SignalDto(
    val id: String,
    val ticker: String,
    val companyName: String,
    val type: String,  // LONG, SHORT, NEUTRAL
    val status: String,  // ACTIVE, CLOSED, EXPIRED
    val confidence: Int,  // 0-100
    val expectedReturn: Double,
    val entryPrice: Double,
    val targetPrice: Double,
    val stopLoss: Double,
    val riskRewardRatio: Double,
    val generatedAt: String,  // ISO date string
    val expiresAt: String,
    val closedAt: String? = null,
    val timeframe: String,  // 1D, 1W, 1M, 3M
    val reasoning: SignalReasoningDto,
    val actualReturn: Double? = null,
    val exitPrice: Double? = null
)
```

**ApiResponse.kt:**
```kotlin
data class ApiResponse<T>(
    val success: Boolean,
    val data: T,
    val message: String? = null,
    val timestamp: String = Instant.now().toString()
) {
    companion object {
        fun <T> success(data: T, message: String? = null) =
            ApiResponse(success = true, data = data, message = message)

        fun <T> error(message: String): ApiResponse<T> =
            ApiResponse(success = false, data = null as T, message = message)
    }
}
```

---

## 🎯 Phase 4: Frontend Integration
**Duration:** 2-3 days

### 4.1 Update Next.js API Client

Update `lib/api/client.ts` to point to Spring Boot backend:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api';

export const apiClient = {
  get: async <T>(endpoint: string, config?: AxiosRequestConfig): Promise<T> => {
    const response = await axios.get(`${API_BASE_URL}${endpoint}`, config);
    // Backend returns ApiResponse wrapper
    return response.data.data;  // Extract data field
  },
  // ... other methods
};
```

### 4.2 Environment Variables

Create `.env.local` in Next.js project:
```env
NEXT_PUBLIC_API_URL=http://localhost:8080/api
```

### 4.3 Testing Checklist

- [ ] Stock list loads from backend
- [ ] Stock price charts display real Yahoo Finance data
- [ ] Signals display correctly
- [ ] Technical indicators calculate properly
- [ ] Portfolio tracking works
- [ ] CORS allows frontend requests

---

## 🎯 Phase 5: Deployment to Proxmox
**Duration:** 2-3 days

### 5.1 Proxmox Setup

1. **Create VM or LXC Container**
   - Ubuntu 22.04 LTS
   - 4GB RAM, 2 CPU cores
   - 40GB disk

2. **Install Docker & Docker Compose**
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

3. **Clone Repository**
```bash
git clone https://github.com/yourusername/jdb-trading.git
cd jdb-trading/backend
```

4. **Configure Environment**
```bash
cp .env.example .env
nano .env  # Set production passwords
```

5. **Deploy**
```bash
docker-compose up -d
```

### 5.2 Production Configuration

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg16
    restart: always
    environment:
      POSTGRES_DB: jdb_trading
      POSTGRES_USER: jdb_user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - /mnt/storage/jdb/postgres:/var/lib/postgresql/data
    secrets:
      - db_password
    networks:
      - jdb-network

  backend:
    image: your-registry/jdb-backend:latest
    restart: always
    ports:
      - "8080:8080"
    environment:
      SPRING_PROFILES_ACTIVE: prod
      DB_HOST: postgres
      DB_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    depends_on:
      - postgres
    networks:
      - jdb-network

secrets:
  db_password:
    file: ./secrets/db_password.txt

networks:
  jdb-network:
    driver: bridge
```

### 5.3 Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name api.jdb-trading.local;

    location /api {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📊 Implementation Timeline

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| 1 | Project Setup | 2 days | ⏳ Not Started |
| 1 | Yahoo Finance Integration | 3 days | ⏳ Not Started |
| 1 | Database Setup | 2 days | ⏳ Not Started |
| 1 | Stock API Endpoints | 3 days | ⏳ Not Started |
| 2 | Technical Analysis Service | 5 days | ⏳ Not Started |
| 2 | Signal Generation Logic | 2 days | ⏳ Not Started |
| 3 | API Response DTOs | 2 days | ⏳ Not Started |
| 3 | Signal & Portfolio APIs | 3 days | ⏳ Not Started |
| 4 | Frontend Integration | 2 days | ⏳ Not Started |
| 4 | End-to-End Testing | 1 day | ⏳ Not Started |
| 5 | Proxmox Deployment | 2 days | ⏳ Not Started |
| 5 | Production Testing | 1 day | ⏳ Not Started |

**Total Estimated Time:** 4-5 weeks

---

## 🚀 Next Immediate Steps

### Step 1: Initialize Spring Boot Project (TODAY)
```bash
# Use Spring Initializr or IntelliJ IDEA
mkdir -p jdb-trading-backend
cd jdb-trading-backend

# Create build.gradle.kts with dependencies
# Create application.yml
# Set up project structure
```

### Step 2: Set Up Local Development Environment
```bash
# Start PostgreSQL with TimescaleDB
docker-compose up -d postgres

# Test connection
psql -h localhost -U jdb_user -d jdb_trading
```

### Step 3: Implement Yahoo Finance Service (PRIORITY)
- Create `YahooFinanceService.kt`
- Test fetching AAPL stock data
- Verify data format matches frontend expectations

### Step 4: Create First API Endpoint
- Implement `GET /api/stocks/{ticker}/data`
- Test with curl/Postman
- Verify JSON response format

### Step 5: Update Frontend to Use Backend
- Change API_BASE_URL to `http://localhost:8080/api`
- Test stock chart loads real data
- Fix any CORS issues

---

## ⚠️ Critical Success Factors

1. **API Contract Compatibility**
   - Backend responses MUST match existing TypeScript interfaces
   - Test all endpoints against frontend expectations

2. **Yahoo Finance Rate Limits**
   - Cache aggressively (5-minute cache for stock data)
   - Implement retry logic with exponential backoff
   - Consider upgrading to paid API if needed

3. **Database Performance**
   - Use TimescaleDB hypertables for stock_prices
   - Index frequently queried columns
   - Optimize query patterns

4. **CORS Configuration**
   - Allow localhost:3000 for development
   - Configure production domains properly

5. **Error Handling**
   - Graceful degradation when Yahoo Finance fails
   - Return meaningful error messages
   - Log all failures

---

## 📝 Testing Strategy

### Unit Tests
- TechnicalAnalysisService calculations
- Signal generation logic
- DTO mapping

### Integration Tests
- Yahoo Finance API calls
- Database queries
- End-to-end API flows

### Manual Testing
- Load frontend, verify stock data displays
- Generate signal, verify reasoning is correct
- Test all API endpoints with Postman

---

## 🔧 Development Tools

- **IDE:** IntelliJ IDEA or VS Code with Kotlin plugin
- **API Testing:** Postman or HTTPie
- **Database Client:** DBeaver or pgAdmin
- **Docker:** Docker Desktop or Docker CLI

---

## 📚 References

- [Yahoo Finance API Documentation](https://github.com/sstrickx/yahoofinance-api)
- [ta4j Technical Analysis Library](https://github.com/ta4j/ta4j)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [Spring Boot Documentation](https://spring.io/projects/spring-boot)

---

**Ready to start? Let's build!** 🚀
