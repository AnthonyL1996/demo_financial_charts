# JDB Trading System Backend - Implementation Plan
## Spring Boot + Kotlin + PostgreSQL + Redis

---

## 📋 Configuration Summary

Based on your requirements:

| Component | Technology/Provider |
|-----------|-------------------|
| **Stock Data** | Yahoo Finance API (yfinance) |
| **User Tiers** | Simplified: USER and ADMIN only |
| **Email** | Spring Mail + Gmail SMTP |
| **Hosting** | Self-hosted Proxmox |
| **Monitoring** | Prometheus + Grafana |
| **Database** | PostgreSQL 16 + TimescaleDB |
| **Cache** | Redis 7 |

---

## 🎯 Project Overview

**Project Name**: `jdb-trading-backend`
**Tech Stack**: Spring Boot 3.2 + Kotlin 1.9 + Gradle 8.5
**Development Time**: 14 weeks (7 phases)
**Team Size**: 1-3 developers

---

## 📦 Phase 0: Prerequisites & Environment Setup (Week 0)

### 0.1 Development Environment

#### Required Software
```bash
# Java Development Kit
- OpenJDK 21 (LTS)
- JAVA_HOME environment variable configured

# Kotlin
- Kotlin 1.9+ (bundled with Gradle)

# Build Tool
- Gradle 8.5+

# Database
- PostgreSQL 16
- pgAdmin 4 (optional, for DB management)
- TimescaleDB extension

# Cache
- Redis 7

# IDE
- IntelliJ IDEA Ultimate (recommended)
  OR
- IntelliJ IDEA Community + Kotlin plugin

# Version Control
- Git 2.40+

# API Testing
- Postman or Insomnia
- cURL

# Docker
- Docker 24+
- Docker Compose 2.20+
```

#### Development Tools
```bash
# Install SDKMAN (for Java/Kotlin management)
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

# Install Java 21
sdk install java 21.0.1-tem
sdk use java 21.0.1-tem

# Install Gradle
sdk install gradle 8.5

# Verify installations
java -version
gradle -v
```

### 0.2 Local Development Database Setup

#### PostgreSQL + TimescaleDB (Docker)
```bash
# Create docker-compose-dev.yml
version: '3.8'

services:
  postgres-dev:
    image: timescale/timescaledb:latest-pg16
    container_name: jdb-postgres-dev
    environment:
      POSTGRES_DB: jdb_trading_dev
      POSTGRES_USER: jdb_dev
      POSTGRES_PASSWORD: dev_password_123
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    command: postgres -c shared_preload_libraries=timescaledb

  redis-dev:
    image: redis:7-alpine
    container_name: jdb-redis-dev
    ports:
      - "6379:6379"
    volumes:
      - redis_dev_data:/data

  # Optional: Database GUI
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: jdb-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@jdb.local
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      - postgres-dev

volumes:
  postgres_dev_data:
  redis_dev_data:

# Start development databases
docker-compose -f docker-compose-dev.yml up -d
```

#### Initialize TimescaleDB Extension
```sql
-- Connect to database and enable TimescaleDB
-- File: init-scripts/01-init-timescaledb.sql

CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Verify installation
SELECT default_version, installed_version
FROM pg_available_extensions
WHERE name = 'timescaledb';
```

### 0.3 Yahoo Finance API Setup

#### Yahoo Finance Integration Options

**Option 1: yahoofinance-api (Java Library)**
```kotlin
// Add to build.gradle.kts
dependencies {
    implementation("com.yahoofinance-api:YahooFinanceAPI:3.17.0")
}

// Usage
val stock = YahooFinance.get("AAPL")
val quote = stock.quote
val history = stock.history
```

**Option 2: yfinance-python (via REST wrapper)**
```python
# Create a simple Python microservice
# File: stock-data-service/main.py

from flask import Flask, jsonify
import yfinance as yf

app = Flask(__name__)

@app.route('/stock/<ticker>')
def get_stock(ticker):
    stock = yf.Ticker(ticker)
    return jsonify(stock.info)

@app.route('/stock/<ticker>/history')
def get_history(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    return jsonify(hist.to_dict())
```

**Option 3: Direct REST API Calls**
```kotlin
// Yahoo Finance v8 API endpoint
// https://query1.finance.yahoo.com/v8/finance/chart/{ticker}

@Service
class YahooFinanceService(
    private val restClient: RestClient
) {
    fun getStockData(ticker: String): StockData {
        val url = "https://query1.finance.yahoo.com/v8/finance/chart/$ticker"
        return restClient.get()
            .uri(url)
            .retrieve()
            .body(StockData::class.java)!!
    }
}
```

**Recommended**: Option 1 (yahoofinance-api) for simplicity and Java compatibility.

### 0.4 Gmail SMTP Configuration

#### Gmail Account Setup
1. Create a Gmail account for the application (e.g., `jdb.trading.notifications@gmail.com`)
2. Enable 2-Factor Authentication
3. Generate App Password:
   - Go to Google Account → Security
   - 2-Step Verification → App passwords
   - Select "Mail" and "Other (Custom name)"
   - Copy the 16-character app password

#### Spring Mail Configuration
```yaml
# application-dev.yml
spring:
  mail:
    host: smtp.gmail.com
    port: 587
    username: ${GMAIL_USERNAME}  # jdb.trading.notifications@gmail.com
    password: ${GMAIL_APP_PASSWORD}  # 16-char app password
    properties:
      mail:
        smtp:
          auth: true
          starttls:
            enable: true
            required: true
          connectiontimeout: 5000
          timeout: 5000
          writetimeout: 5000
```

---

## 🏗️ Phase 1: Project Setup & Core Infrastructure (Week 1-2)

### 1.1 Create Spring Boot Project

#### Initialize Project with Spring Initializr
```bash
# Using Spring Initializr CLI or web interface
# https://start.spring.io/

Project: Gradle - Kotlin
Language: Kotlin
Spring Boot: 3.2.1
Packaging: Jar
Java: 21

Group: com.jdb
Artifact: trading-backend
Name: JDB Trading Backend
Package: com.jdb.trading

Dependencies:
- Spring Web
- Spring Security
- Spring Data JPA
- PostgreSQL Driver
- Spring Data Redis
- Spring Boot Actuator
- Spring Boot DevTools
- Validation
- WebSocket
- Spring Mail
```

#### Alternative: Manual Setup
```bash
# Create project structure
mkdir jdb-trading-backend
cd jdb-trading-backend

# Initialize Gradle project
gradle init --type kotlin-application --dsl kotlin

# Or clone from template
git clone https://github.com/spring-projects/spring-boot-kotlin-template.git jdb-trading-backend
```

### 1.2 Project Structure Setup

```bash
# Create directory structure
mkdir -p src/main/kotlin/com/jdb/trading/{config,controller,domain,dto,repository,service,security,exception,websocket,scheduler,util}
mkdir -p src/main/kotlin/com/jdb/trading/domain/{entity,enum,valueobject}
mkdir -p src/main/kotlin/com/jdb/trading/dto/{request,response}
mkdir -p src/main/resources/db/migration
mkdir -p src/test/kotlin/com/jdb/trading/{integration,service,repository}
```

### 1.3 Configure build.gradle.kts

```kotlin
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    id("org.springframework.boot") version "3.2.1"
    id("io.spring.dependency-management") version "1.1.4"
    kotlin("jvm") version "1.9.22"
    kotlin("plugin.spring") version "1.9.22"
    kotlin("plugin.jpa") version "1.9.22"
    id("org.flywaydb.flyway") version "10.4.1"
}

group = "com.jdb"
version = "0.1.0"

java {
    sourceCompatibility = JavaVersion.VERSION_21
}

repositories {
    mavenCentral()
}

dependencies {
    // Spring Boot Starters
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-security")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-data-redis")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    implementation("org.springframework.boot:spring-boot-starter-websocket")
    implementation("org.springframework.boot:spring-boot-starter-mail")
    implementation("org.springframework.boot:spring-boot-starter-actuator")
    implementation("org.springframework.boot:spring-boot-devtools")

    // Kotlin
    implementation("org.jetbrains.kotlin:kotlin-reflect")
    implementation("org.jetbrains.kotlin:kotlin-stdlib")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")

    // Database
    implementation("org.postgresql:postgresql")
    implementation("org.flywaydb:flyway-core")

    // JWT
    implementation("io.jsonwebtoken:jjwt-api:0.12.3")
    runtimeOnly("io.jsonwebtoken:jjwt-impl:0.12.3")
    runtimeOnly("io.jsonwebtoken:jjwt-jackson:0.12.3")

    // Yahoo Finance
    implementation("com.yahoofinance-api:YahooFinanceAPI:3.17.0")

    // Hibernate Types (for JSONB)
    implementation("io.hypersistence:hypersistence-utils-hibernate-63:3.7.0")

    // OpenAPI/Swagger
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.3.0")

    // Micrometer (Prometheus)
    implementation("io.micrometer:micrometer-registry-prometheus")

    // Testing
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.springframework.security:spring-security-test")
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation("com.ninja-squad:springmockk:4.0.2")
    testImplementation("org.testcontainers:testcontainers:1.19.3")
    testImplementation("org.testcontainers:postgresql:1.19.3")
    testImplementation("org.testcontainers:junit-jupiter:1.19.3")
}

tasks.withType<KotlinCompile> {
    kotlinOptions {
        freeCompilerArgs += "-Xjsr305=strict"
        jvmTarget = "21"
    }
}

tasks.withType<Test> {
    useJUnitPlatform()
}
```

### 1.4 Application Configuration Files

#### application.yml (Base Configuration)
```yaml
spring:
  application:
    name: jdb-trading-backend

  profiles:
    active: dev

  jpa:
    open-in-view: false
    hibernate:
      ddl-auto: validate
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        jdbc:
          time_zone: UTC
        format_sql: true

  flyway:
    enabled: true
    baseline-on-migrate: true
    locations: classpath:db/migration
    schemas: public

server:
  port: 8080
  compression:
    enabled: true
  error:
    include-message: always
    include-binding-errors: always

# Actuator endpoints
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
      base-path: /actuator
  endpoint:
    health:
      show-details: when-authorized
  metrics:
    export:
      prometheus:
        enabled: true

# Logging
logging:
  level:
    root: INFO
    com.jdb.trading: DEBUG
    org.springframework.web: DEBUG
    org.hibernate.SQL: DEBUG
    org.hibernate.type.descriptor.sql.BasicBinder: TRACE

# Application-specific properties
jdb:
  jwt:
    secret: ${JWT_SECRET:change-this-in-production-must-be-at-least-256-bits-long-for-hs256}
    access-token-expiration: 3600000      # 1 hour
    refresh-token-expiration: 604800000   # 7 days

  yahoo-finance:
    rate-limit: 2000  # requests per hour
    timeout: 5000     # milliseconds

  scheduler:
    signal-generation:
      cron: "0 0 18 * * ?"  # Daily at 6 PM
      enabled: true
    stock-data-update:
      cron: "0 */15 9-16 ? * MON-FRI"  # Every 15 min during market hours
      enabled: true
    portfolio-pnl:
      cron: "0 */5 * * * ?"  # Every 5 minutes
      enabled: true
```

#### application-dev.yml (Development)
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/jdb_trading_dev
    username: jdb_dev
    password: dev_password_123
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
      connection-timeout: 30000

  data:
    redis:
      host: localhost
      port: 6379
      timeout: 2000ms

  jpa:
    show-sql: true

  mail:
    host: smtp.gmail.com
    port: 587
    username: ${GMAIL_USERNAME:your-email@gmail.com}
    password: ${GMAIL_APP_PASSWORD:your-app-password}
    properties:
      mail:
        smtp:
          auth: true
          starttls:
            enable: true
            required: true

logging:
  level:
    com.jdb.trading: DEBUG
```

#### application-prod.yml (Production)
```yaml
spring:
  datasource:
    url: jdbc:postgresql://${DB_HOST:localhost}:${DB_PORT:5432}/${DB_NAME:jdb_trading}
    username: ${DB_USER:jdb_user}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000

  data:
    redis:
      host: ${REDIS_HOST:localhost}
      port: ${REDIS_PORT:6379}
      password: ${REDIS_PASSWORD:}
      timeout: 2000ms

  jpa:
    show-sql: false

  mail:
    host: smtp.gmail.com
    port: 587
    username: ${GMAIL_USERNAME}
    password: ${GMAIL_APP_PASSWORD}
    properties:
      mail:
        smtp:
          auth: true
          starttls:
            enable: true
            required: true

logging:
  level:
    root: INFO
    com.jdb.trading: INFO
```

### 1.5 Main Application Class

```kotlin
package com.jdb.trading

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.data.jpa.repository.config.EnableJpaAuditing
import org.springframework.scheduling.annotation.EnableScheduling

@SpringBootApplication
@EnableJpaAuditing
@EnableScheduling
class JdbTradingApplication

fun main(args: Array<String>) {
    runApplication<JdbTradingApplication>(*args)
}
```

### 1.6 Database Migrations Setup (Flyway)

#### V1__create_users_table.sql
```sql
-- Migration: V1__create_users_table.sql
-- Description: Create users table with authentication

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) NOT NULL DEFAULT 'USER',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- Insert default admin user (password: Admin123!)
INSERT INTO users (email, username, password_hash, first_name, last_name, role, is_active, email_verified)
VALUES (
    'admin@jdb.local',
    'admin',
    '$2a$10$xJ/CXXXYYYZZZxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', -- BCrypt hash
    'Admin',
    'User',
    'ADMIN',
    true,
    true
);
```

---

## 🔐 Phase 2: Authentication & Security (Week 2)

### 2.1 Security Configuration

#### Task Checklist
- [ ] Create JWT token provider
- [ ] Implement JWT authentication filter
- [ ] Configure Spring Security
- [ ] Create user entity and repository
- [ ] Implement authentication service
- [ ] Create auth endpoints (register, login, refresh)
- [ ] Add password validation
- [ ] Implement BCrypt password encoding
- [ ] Add rate limiting for login attempts
- [ ] Create authentication integration tests

### 2.2 Key Files to Create

```
security/
  ├── JwtTokenProvider.kt          # Generate and validate JWT tokens
  ├── JwtAuthenticationFilter.kt   # Intercept requests and validate tokens
  ├── JwtAuthenticationEntryPoint.kt
  ├── UserPrincipal.kt             # Spring Security user details
  └── SecurityConfig.kt            # Main security configuration

domain/entity/
  └── User.kt                      # User entity

repository/
  └── UserRepository.kt            # User data access

service/
  ├── AuthService.kt               # Authentication logic
  └── UserService.kt               # User management

controller/
  └── AuthController.kt            # Auth endpoints

dto/request/
  ├── LoginRequest.kt
  ├── RegisterRequest.kt
  └── RefreshTokenRequest.kt

dto/response/
  ├── AuthResponse.kt
  └── UserResponse.kt
```

### 2.3 Testing Strategy

```kotlin
// AuthControllerIntegrationTest.kt
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Testcontainers
class AuthControllerIntegrationTest {

    @Container
    val postgres = PostgreSQLContainer("postgres:16-alpine")

    @Test
    fun `should register new user successfully`() {
        // Test implementation
    }

    @Test
    fun `should login with valid credentials`() {
        // Test implementation
    }

    @Test
    fun `should reject invalid credentials`() {
        // Test implementation
    }
}
```

---

## 📊 Phase 3: Stock Management & Data Integration (Week 3-4)

### 3.1 Stock Data Infrastructure

#### Task Checklist
- [ ] Create Stock entity and repository
- [ ] Create StockPrice entity (TimescaleDB hypertable)
- [ ] Implement Yahoo Finance integration service
- [ ] Create stock data sync scheduler
- [ ] Implement stock CRUD endpoints
- [ ] Create stock price endpoints (OHLCV data)
- [ ] Add data validation and error handling
- [ ] Implement caching for stock data
- [ ] Create stock data tests
- [ ] Seed database with initial stock list (S&P 500)

### 3.2 Yahoo Finance Integration

```kotlin
// YahooFinanceService.kt
@Service
class YahooFinanceService {

    fun fetchStockData(ticker: String): Stock {
        val yahooStock = YahooFinance.get(ticker)
        val quote = yahooStock.quote

        return Stock(
            ticker = ticker.uppercase(),
            companyName = yahooStock.name,
            currentPrice = quote.price,
            marketCap = yahooStock.stats.marketCap.toLong(),
            // ... map other fields
        )
    }

    fun fetchHistoricalData(
        ticker: String,
        from: LocalDate,
        to: LocalDate
    ): List<StockPrice> {
        val yahooStock = YahooFinance.get(ticker)
        val history = yahooStock.getHistory(
            Calendar.getInstance().apply { time = Date.from(from.atStartOfDay(ZoneId.systemDefault()).toInstant()) },
            Calendar.getInstance().apply { time = Date.from(to.atStartOfDay(ZoneId.systemDefault()).toInstant()) },
            Interval.DAILY
        )

        return history.map { quote ->
            StockPrice(
                stock = stock,
                date = quote.date.toInstant().atZone(ZoneId.systemDefault()).toLocalDateTime(),
                open = quote.open,
                high = quote.high,
                low = quote.low,
                close = quote.close,
                volume = quote.volume,
                adjClose = quote.adjClose
            )
        }
    }
}
```

### 3.3 Stock Data Sync Scheduler

```kotlin
// StockDataUpdateScheduler.kt
@Component
class StockDataUpdateScheduler(
    private val stockService: StockService,
    private val yahooFinanceService: YahooFinanceService
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    @Scheduled(cron = "\${jdb.scheduler.stock-data-update.cron}")
    fun updateStockPrices() {
        if (!isMarketOpen()) {
            logger.info("Market is closed, skipping stock data update")
            return
        }

        logger.info("Starting stock data update...")
        val activeStocks = stockService.getActiveStocks()

        activeStocks.forEach { stock ->
            try {
                val latestData = yahooFinanceService.fetchStockData(stock.ticker)
                stockService.updateStockPrice(stock, latestData)
            } catch (e: Exception) {
                logger.error("Failed to update stock ${stock.ticker}", e)
            }
        }

        logger.info("Stock data update completed for ${activeStocks.size} stocks")
    }

    private fun isMarketOpen(): Boolean {
        val now = LocalDateTime.now(ZoneId.of("America/New_York"))
        val dayOfWeek = now.dayOfWeek
        val time = now.toLocalTime()

        return dayOfWeek !in listOf(DayOfWeek.SATURDAY, DayOfWeek.SUNDAY) &&
               time.isAfter(LocalTime.of(9, 30)) &&
               time.isBefore(LocalTime.of(16, 0))
    }
}
```

### 3.4 Database Migration for Stock Tables

```sql
-- V2__create_stocks_table.sql
CREATE TABLE stocks (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_updated TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_stocks_ticker ON stocks(ticker);
CREATE INDEX idx_stocks_sector ON stocks(sector);
CREATE INDEX idx_stocks_is_active ON stocks(is_active);

-- V3__create_stock_prices_table.sql
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
SELECT create_hypertable('stock_prices', 'date', if_not_exists => TRUE);

-- Create indexes
CREATE INDEX idx_stock_prices_stock_date ON stock_prices(stock_id, date DESC);
CREATE INDEX idx_stock_prices_date ON stock_prices(date DESC);

-- Add compression policy (compress data older than 7 days)
ALTER TABLE stock_prices SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'stock_id'
);

SELECT add_compression_policy('stock_prices', INTERVAL '7 days');
```

---

## 🎯 Phase 4: Signal Generation & JDB Methodology (Week 5-6)

### 4.1 Technical Analysis Service

#### Task Checklist
- [ ] Create TechnicalAnalysisService
- [ ] Implement Moving Average calculations (SMA 20, 50, 200)
- [ ] Implement EMA calculations (EMA 12, 26)
- [ ] Implement RSI calculation
- [ ] Implement Bollinger Bands calculation
- [ ] Implement Fibonacci retracement calculation
- [ ] Implement volume analysis
- [ ] Create technical indicator tests

### 4.2 JDB Methodology Implementation

```kotlin
// SignalGeneratorService.kt
@Service
class SignalGeneratorService(
    private val stockRepository: StockRepository,
    private val stockPriceRepository: StockPriceRepository,
    private val signalRepository: SignalRepository,
    private val technicalAnalysisService: TechnicalAnalysisService
) {

    fun generateSignals(): List<Signal> {
        val activeStocks = stockRepository.findByIsActive(true)
        val signals = mutableListOf<Signal>()

        activeStocks.forEach { stock ->
            try {
                val signal = analyzeStock(stock)
                if (signal != null) {
                    signals.add(signal)
                }
            } catch (e: Exception) {
                logger.error("Failed to analyze stock ${stock.ticker}", e)
            }
        }

        return signalRepository.saveAll(signals)
    }

    private fun analyzeStock(stock: Stock): Signal? {
        // Get historical data (e.g., last 200 days)
        val priceData = stockPriceRepository.findByStockIdOrderByDateDesc(
            stock.id,
            limit = 200
        )

        if (priceData.size < 200) {
            return null // Not enough data
        }

        // Calculate technical indicators
        val indicators = technicalAnalysisService.calculateIndicators(priceData)

        // Apply JDB Methodology
        val reasoning = analyzeJDBCriteria(stock, priceData, indicators)

        // Generate signal if all criteria met
        return if (reasoning.meetsSignalCriteria()) {
            createSignal(stock, reasoning, indicators)
        } else {
            null
        }
    }

    private fun analyzeJDBCriteria(
        stock: Stock,
        priceData: List<StockPrice>,
        indicators: TechnicalIndicators
    ): SignalReasoning {
        val currentPrice = priceData.first().close

        // 1. Dominant MA Detection
        val dominantMA = detectDominantMA(priceData, indicators)

        // 2. Bollinger Bands Position
        val bbPosition = analyzeBollingerBands(currentPrice, indicators.bollingerBands)

        // 3. Fibonacci Retracement
        val fibAnalysis = analyzeFibonacci(priceData)

        // 4. RSI Divergence
        val rsiDivergence = detectRSIDivergence(priceData, indicators.rsi)

        // 5. Volume Confirmation
        val volumeConfirmation = analyzeVolume(priceData)

        // 6. Trend Strength
        val trendStrength = calculateTrendStrength(indicators)

        return SignalReasoning(
            dominantMA = dominantMA,
            bollingerBands = bbPosition,
            fibonacci = fibAnalysis,
            rsiDivergence = rsiDivergence,
            volumeConfirmation = volumeConfirmation,
            trendStrength = trendStrength
        )
    }
}
```

### 4.3 Signal Database Migration

```sql
-- V4__create_signals_table.sql
CREATE TABLE signals (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    stock_id BIGINT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
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

CREATE INDEX idx_signals_user_id ON signals(user_id);
CREATE INDEX idx_signals_stock_id ON signals(stock_id);
CREATE INDEX idx_signals_status ON signals(status);
CREATE INDEX idx_signals_type ON signals(type);
CREATE INDEX idx_signals_generated_at ON signals(generated_at DESC);
CREATE INDEX idx_signals_confidence ON signals(confidence DESC);
CREATE INDEX idx_signals_reasoning ON signals USING GIN (reasoning);
```

---

## 💼 Phase 5: Portfolio Management (Week 7-8)

### 5.1 Portfolio & Position Management

#### Task Checklist
- [ ] Create Portfolio entity and repository
- [ ] Create Position entity and repository
- [ ] Implement portfolio CRUD operations
- [ ] Implement position open/close operations
- [ ] Create P&L calculation service
- [ ] Create risk calculation service
- [ ] Implement portfolio performance metrics
- [ ] Create portfolio endpoints
- [ ] Add portfolio data validation
- [ ] Create portfolio tests

### 5.2 P&L Calculation Scheduler

```kotlin
// PortfolioPnLScheduler.kt
@Component
class PortfolioPnLScheduler(
    private val portfolioRepository: PortfolioRepository,
    private val positionRepository: PositionRepository,
    private val stockService: StockService,
    private val riskCalculationService: RiskCalculationService
) {

    @Scheduled(cron = "\${jdb.scheduler.portfolio-pnl.cron}")
    fun updatePortfolioValues() {
        val activePortfolios = portfolioRepository.findByIsActive(true)

        activePortfolios.forEach { portfolio ->
            try {
                updatePortfolio(portfolio)
            } catch (e: Exception) {
                logger.error("Failed to update portfolio ${portfolio.id}", e)
            }
        }
    }

    private fun updatePortfolio(portfolio: Portfolio) {
        val positions = positionRepository.findByPortfolioIdAndClosedAtIsNull(portfolio.id)

        var totalValue = portfolio.cash
        var totalPnL = BigDecimal.ZERO

        positions.forEach { position ->
            val currentPrice = stockService.getCurrentPrice(position.stock.ticker)

            // Update position
            position.currentPrice = currentPrice
            position.marketValue = currentPrice * position.shares.toBigDecimal()
            position.pnl = position.marketValue - (position.entryPrice * position.shares.toBigDecimal())
            position.pnlPercent = (position.pnl / (position.entryPrice * position.shares.toBigDecimal())) * BigDecimal(100)

            totalValue += position.marketValue
            totalPnL += position.pnl
        }

        // Update portfolio
        portfolio.currentValue = totalValue
        portfolio.totalPnL = totalPnL
        portfolio.totalPnLPercent = (totalPnL / portfolio.initialCapital) * BigDecimal(100)

        // Calculate weights
        positions.forEach { position ->
            position.weight = (position.marketValue / totalValue) * BigDecimal(100)
        }

        // Save updates
        positionRepository.saveAll(positions)
        portfolioRepository.save(portfolio)
    }
}
```

---

## 🔄 Phase 6: Real-time Features & WebSocket (Week 9-10)

### 6.1 WebSocket Configuration

```kotlin
// WebSocketConfig.kt
@Configuration
@EnableWebSocketMessageBroker
class WebSocketConfig : WebSocketMessageBrokerConfigurer {

    override fun configureMessageBroker(registry: MessageBrokerRegistry) {
        registry.enableSimpleBroker("/topic", "/queue")
        registry.setApplicationDestinationPrefixes("/app")
        registry.setUserDestinationPrefix("/user")
    }

    override fun registerStompEndpoints(registry: StompEndpointRegistry) {
        registry.addEndpoint("/ws")
            .setAllowedOrigins("http://localhost:3000", "https://yourdomain.com")
            .withSockJS()
    }
}
```

### 6.2 Signal Broadcasting

```kotlin
// SignalUpdateBroadcaster.kt
@Component
class SignalUpdateBroadcaster(
    private val messagingTemplate: SimpMessagingTemplate
) {

    fun broadcastNewSignal(signal: Signal) {
        messagingTemplate.convertAndSend("/topic/signals/new", signal.toResponse())
    }

    fun broadcastSignalUpdate(signal: Signal) {
        messagingTemplate.convertAndSend("/topic/signals/${signal.id}", signal.toResponse())
    }

    fun notifyUser(userId: Long, notification: Notification) {
        messagingTemplate.convertAndSendToUser(
            userId.toString(),
            "/queue/notifications",
            notification
        )
    }
}
```

---

## 📊 Phase 7: Production Readiness (Week 11-12)

### 7.1 Monitoring Setup (Prometheus + Grafana)

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'jdb-trading-backend'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['backend:8080']
```

#### Grafana Dashboard
- JVM Metrics (heap, GC, threads)
- HTTP Request metrics (rate, duration, errors)
- Database connection pool metrics
- Redis cache hit/miss rates
- Custom business metrics (signals generated, trades executed)

### 7.2 Docker Production Build

```dockerfile
# Dockerfile
FROM gradle:8.5-jdk21 AS build
WORKDIR /app

# Copy Gradle files
COPY build.gradle.kts settings.gradle.kts ./
COPY gradle gradle

# Download dependencies
RUN gradle dependencies --no-daemon

# Copy source
COPY src src

# Build application
RUN gradle clean build --no-daemon -x test

# Production image
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S spring && adduser -u 1001 -S spring -G spring
USER spring:spring

# Copy JAR
COPY --from=build /app/build/libs/*.jar app.jar

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", \
    "-XX:+UseContainerSupport", \
    "-XX:MaxRAMPercentage=75.0", \
    "-Djava.security.egd=file:/dev/./urandom", \
    "-jar", "app.jar"]
```

### 7.3 Docker Compose Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg16
    container_name: jdb-postgres
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - jdb-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: jdb-redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - jdb-network
    restart: unless-stopped

  backend:
    build: .
    container_name: jdb-backend
    environment:
      SPRING_PROFILES_ACTIVE: prod
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      REDIS_HOST: redis
      REDIS_PORT: 6379
      REDIS_PASSWORD: ${REDIS_PASSWORD}
      JWT_SECRET: ${JWT_SECRET}
      GMAIL_USERNAME: ${GMAIL_USERNAME}
      GMAIL_APP_PASSWORD: ${GMAIL_APP_PASSWORD}
    ports:
      - "8080:8080"
    depends_on:
      - postgres
      - redis
    networks:
      - jdb-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  prometheus:
    image: prom/prometheus:latest
    container_name: jdb-prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - "9090:9090"
    networks:
      - jdb-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: jdb-grafana
    environment:
      GF_SECURITY_ADMIN_USER: ${GRAFANA_USER:-admin}
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:-admin}
      GF_INSTALL_PLUGINS: grafana-piechart-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    ports:
      - "3001:3000"
    networks:
      - jdb-network
    restart: unless-stopped
    depends_on:
      - prometheus

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  jdb-network:
    driver: bridge
```

---

## 🖥️ Proxmox Deployment (Week 13)

### 8.1 Proxmox VM Setup

#### Create Ubuntu LTS VM
```bash
# VM Specifications (Recommended)
CPU: 4 cores
RAM: 8 GB
Disk: 100 GB
OS: Ubuntu 22.04 LTS Server
```

#### SSH into VM and Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Git
sudo apt install git -y
```

### 8.2 Deploy Application

```bash
# Clone repository
git clone <your-backend-repo-url>
cd jdb-trading-backend

# Create .env file
cat > .env << EOF
DB_NAME=jdb_trading
DB_USER=jdb_user
DB_PASSWORD=<generate-strong-password>
REDIS_PASSWORD=<generate-strong-password>
JWT_SECRET=<generate-256-bit-secret>
GMAIL_USERNAME=your-email@gmail.com
GMAIL_APP_PASSWORD=<your-16-char-app-password>
GRAFANA_USER=admin
GRAFANA_PASSWORD=<generate-strong-password>
EOF

# Start services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Check health
curl http://localhost:8080/actuator/health
```

### 8.3 Reverse Proxy Setup (Nginx)

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/jdb-trading
```

```nginx
# /etc/nginx/sites-available/jdb-trading
server {
    listen 80;
    server_name api.yourdomain.com;

    # API Backend
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8080/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}

# Grafana
server {
    listen 80;
    server_name monitoring.yourdomain.com;

    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/jdb-trading /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Enable Nginx on boot
sudo systemctl enable nginx
```

### 8.4 SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d api.yourdomain.com -d monitoring.yourdomain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

### 8.5 Firewall Configuration

```bash
# Install UFW
sudo apt install ufw -y

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## 🧪 Testing Strategy (Week 14)

### 9.1 Unit Tests

```kotlin
// SignalGeneratorServiceTest.kt
@ExtendWith(MockKExtension::class)
class SignalGeneratorServiceTest {

    @MockK
    lateinit var stockRepository: StockRepository

    @MockK
    lateinit var technicalAnalysisService: TechnicalAnalysisService

    @InjectMockKs
    lateinit var signalGeneratorService: SignalGeneratorService

    @Test
    fun `should generate LONG signal when criteria met`() {
        // Arrange
        val stock = createTestStock()
        val priceData = createTestPriceData()
        every { stockRepository.findByIsActive(true) } returns listOf(stock)
        every { technicalAnalysisService.calculateIndicators(any()) } returns createBullishIndicators()

        // Act
        val signals = signalGeneratorService.generateSignals()

        // Assert
        assertEquals(1, signals.size)
        assertEquals(SignalType.LONG, signals[0].type)
    }
}
```

### 9.2 Integration Tests

```kotlin
// StockControllerIntegrationTest.kt
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Testcontainers
class StockControllerIntegrationTest {

    @Container
    val postgres = PostgreSQLContainer("timescale/timescaledb:latest-pg16")

    @Autowired
    lateinit var restTemplate: TestRestTemplate

    @Test
    fun `should fetch stock data successfully`() {
        // Test implementation
    }
}
```

### 9.3 Performance Tests

```kotlin
// Load test with Gatling or JMeter
// Target: 1000 concurrent users, 10000 requests/min
// Response time: p95 < 500ms
```

---

## 📝 Documentation (Week 14)

### 10.1 API Documentation (Swagger/OpenAPI)

```kotlin
// OpenApiConfig.kt
@Configuration
class OpenApiConfig {

    @Bean
    fun customOpenAPI(): OpenAPI {
        return OpenAPI()
            .info(
                Info()
                    .title("JDB Trading System API")
                    .version("0.1.0")
                    .description("REST API for JDB Trading System")
                    .contact(
                        Contact()
                            .name("JDB Trading Team")
                            .email("support@jdb-trading.com")
                    )
            )
            .addSecurityItem(SecurityRequirement().addList("Bearer Authentication"))
            .components(
                Components()
                    .addSecuritySchemes(
                        "Bearer Authentication",
                        SecurityScheme()
                            .type(SecurityScheme.Type.HTTP)
                            .scheme("bearer")
                            .bearerFormat("JWT")
                    )
            )
    }
}
```

Access Swagger UI at: `http://localhost:8080/swagger-ui.html`

### 10.2 README.md

Create comprehensive README with:
- Project overview
- Prerequisites
- Setup instructions
- API endpoints
- Configuration
- Deployment guide
- Monitoring
- Troubleshooting

---

## 📊 Progress Tracking

### Implementation Timeline

| Phase | Duration | Status | Deliverables |
|-------|----------|--------|--------------|
| **Phase 0** | Week 0 | ⬜ Not Started | Environment setup |
| **Phase 1** | Week 1-2 | ⬜ Not Started | Project structure, configs |
| **Phase 2** | Week 2 | ⬜ Not Started | Authentication & security |
| **Phase 3** | Week 3-4 | ⬜ Not Started | Stock management |
| **Phase 4** | Week 5-6 | ⬜ Not Started | Signal generation |
| **Phase 5** | Week 7-8 | ⬜ Not Started | Portfolio management |
| **Phase 6** | Week 9-10 | ⬜ Not Started | Real-time features |
| **Phase 7** | Week 11-12 | ⬜ Not Started | Production readiness |
| **Phase 8** | Week 13 | ⬜ Not Started | Proxmox deployment |
| **Phase 9** | Week 14 | ⬜ Not Started | Testing & documentation |

### Key Milestones

- [ ] ✅ Week 0: Development environment ready
- [ ] ✅ Week 2: User authentication working
- [ ] ✅ Week 4: Stock data syncing from Yahoo Finance
- [ ] ✅ Week 6: Signal generation operational
- [ ] ✅ Week 8: Portfolio tracking functional
- [ ] ✅ Week 10: WebSocket real-time updates working
- [ ] ✅ Week 12: Docker deployment ready
- [ ] ✅ Week 13: Production deployment on Proxmox
- [ ] ✅ Week 14: Complete testing and documentation

---

## 🚀 Quick Start Commands

### Development Environment

```bash
# Start development databases
docker-compose -f docker-compose-dev.yml up -d

# Run application
./gradlew bootRun

# Run with profile
./gradlew bootRun --args='--spring.profiles.active=dev'

# Run tests
./gradlew test

# Build JAR
./gradlew build
```

### Production Deployment

```bash
# Build Docker image
docker build -t jdb-trading-backend:latest .

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose -f docker-compose.prod.yml down

# Clean rebuild
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📚 Additional Resources

### Learning Resources
- [Spring Boot Documentation](https://docs.spring.io/spring-boot/docs/current/reference/html/)
- [Kotlin for Spring](https://spring.io/guides/tutorials/spring-boot-kotlin/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [Yahoo Finance API Guide](https://github.com/sstrickx/yahoofinance-api)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

### Tools & IDEs
- [IntelliJ IDEA](https://www.jetbrains.com/idea/)
- [Postman](https://www.postman.com/)
- [DBeaver](https://dbeaver.io/) (Database GUI)
- [Redis Insight](https://redis.com/redis-enterprise/redis-insight/)

---

## ❓ Troubleshooting

### Common Issues

**Issue**: Database connection refused
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check logs
docker logs jdb-postgres

# Test connection
psql -h localhost -U jdb_dev -d jdb_trading_dev
```

**Issue**: Redis connection timeout
```bash
# Check Redis
docker ps | grep redis

# Test connection
redis-cli ping
```

**Issue**: Yahoo Finance rate limit
```bash
# Implement exponential backoff
# Add delay between requests
# Consider caching frequently accessed data
```

---

## 🎯 Success Criteria

### Phase Completion Checklist

**Phase 1 Complete When**:
- [ ] Application starts without errors
- [ ] Database migrations run successfully
- [ ] Can access Swagger UI
- [ ] Health endpoint returns 200 OK

**Phase 2 Complete When**:
- [ ] Users can register
- [ ] Users can login and receive JWT
- [ ] Protected endpoints require authentication
- [ ] Token refresh works

**Phase 3 Complete When**:
- [ ] Can fetch stock data from Yahoo Finance
- [ ] Stock prices stored in TimescaleDB
- [ ] Scheduled sync runs successfully
- [ ] Can query historical OHLCV data

**Phase 4 Complete When**:
- [ ] Signal generation scheduler runs
- [ ] Signals stored with JDB reasoning
- [ ] Can query signals with filters
- [ ] Signal endpoints working

**Phase 5 Complete When**:
- [ ] Can create portfolios
- [ ] Can open/close positions
- [ ] P&L calculated correctly
- [ ] Portfolio value updates automatically

**Phase 6 Complete When**:
- [ ] WebSocket connection established
- [ ] Real-time signal broadcasts work
- [ ] Portfolio updates pushed to clients

**Phase 7 Complete When**:
- [ ] Docker build succeeds
- [ ] All services start with docker-compose
- [ ] Prometheus scrapes metrics
- [ ] Grafana dashboards display data

**Phase 8 Complete When**:
- [ ] Application deployed on Proxmox
- [ ] Accessible via domain name
- [ ] SSL certificate installed
- [ ] Monitoring accessible

---

**Ready to start implementation? Begin with Phase 0! 🚀**

**Next Steps:**
1. Set up your development environment
2. Create the Spring Boot project
3. Configure PostgreSQL + TimescaleDB
4. Start with Phase 1 implementation

Good luck! 💪
