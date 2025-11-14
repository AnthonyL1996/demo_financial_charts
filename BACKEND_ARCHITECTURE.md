# JDB Trading System - Backend Architecture Proposal
## Spring Boot + Kotlin + PostgreSQL

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Database Schema](#database-schema)
5. [Domain Model](#domain-model)
6. [API Architecture](#api-architecture)
7. [Security Architecture](#security-architecture)
8. [Data Flow](#data-flow)
9. [Additional Features](#additional-features)
10. [Deployment Strategy](#deployment-strategy)

---

## 1. Overview

The JDB Trading System backend is a production-ready REST API built with Spring Boot 3.x and Kotlin 1.9+, designed to support the JDB "Kruispunt" (Crossroads) trading methodology. The system manages trading signals, stock data, portfolio tracking, backtesting, and user management.

### Key Requirements
- **Real-time trading signal generation and management**
- **Historical stock data storage and retrieval**
- **Portfolio tracking with P&L calculations**
- **Backtesting engine for strategy validation**
- **JWT-based authentication and authorization**
- **WebSocket support for real-time updates**
- **Scalable architecture for high-frequency data**

---

## 2. Technology Stack

### Core Framework
- **Spring Boot 3.2+** - Application framework
- **Kotlin 1.9+** - Programming language
- **Spring WebFlux** (Optional) - Reactive programming for real-time features
- **Gradle Kotlin DSL** - Build tool

### Database
- **PostgreSQL 16+** - Primary relational database
- **Redis 7+** - Caching and session management
- **TimescaleDB** (PostgreSQL extension) - Time-series data optimization

### Security
- **Spring Security 6.x** - Authentication and authorization
- **JWT (JSON Web Tokens)** - Stateless authentication
- **BCrypt** - Password hashing

### Data Processing
- **Spring Data JPA** - ORM and database access
- **Hibernate 6.x** - JPA implementation
- **Flyway** - Database migrations

### Real-time Communication
- **Spring WebSocket** - WebSocket support
- **STOMP** - Messaging protocol
- **RabbitMQ** or **Kafka** - Message broker (for async processing)

### API Documentation
- **SpringDoc OpenAPI 3** - API documentation (Swagger UI)
- **Kotlin Serialization** - JSON serialization

### Testing
- **JUnit 5** - Unit testing
- **MockK** - Mocking library for Kotlin
- **Testcontainers** - Integration testing with Docker
- **Rest Assured** - API testing

### Monitoring & Observability
- **Spring Actuator** - Health checks and metrics
- **Micrometer** - Metrics collection
- **Prometheus** - Metrics storage
- **Grafana** - Metrics visualization
- **Logback** - Logging

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Local development
- **GitHub Actions** - CI/CD

---

## 3. Project Structure

```
jdb-trading-backend/
├── src/
│   ├── main/
│   │   ├── kotlin/
│   │   │   └── com/
│   │   │       └── jdb/
│   │   │           └── trading/
│   │   │               ├── JdbTradingApplication.kt
│   │   │               │
│   │   │               ├── config/
│   │   │               │   ├── SecurityConfig.kt
│   │   │               │   ├── WebSocketConfig.kt
│   │   │               │   ├── RedisConfig.kt
│   │   │               │   ├── JpaConfig.kt
│   │   │               │   └── OpenApiConfig.kt
│   │   │               │
│   │   │               ├── controller/
│   │   │               │   ├── AuthController.kt
│   │   │               │   ├── SignalController.kt
│   │   │               │   ├── StockController.kt
│   │   │               │   ├── PortfolioController.kt
│   │   │               │   ├── BacktestController.kt
│   │   │               │   ├── UserController.kt
│   │   │               │   └── HealthController.kt
│   │   │               │
│   │   │               ├── dto/
│   │   │               │   ├── request/
│   │   │               │   │   ├── LoginRequest.kt
│   │   │               │   │   ├── RegisterRequest.kt
│   │   │               │   │   ├── CreateSignalRequest.kt
│   │   │               │   │   ├── UpdateSignalRequest.kt
│   │   │               │   │   └── BacktestRequest.kt
│   │   │               │   │
│   │   │               │   └── response/
│   │   │               │       ├── AuthResponse.kt
│   │   │               │       ├── SignalResponse.kt
│   │   │               │       ├── StockResponse.kt
│   │   │               │       ├── PortfolioResponse.kt
│   │   │               │       ├── BacktestResponse.kt
│   │   │               │       ├── ApiResponse.kt
│   │   │               │       └── PagedResponse.kt
│   │   │               │
│   │   │               ├── domain/
│   │   │               │   ├── entity/
│   │   │               │   │   ├── User.kt
│   │   │               │   │   ├── Signal.kt
│   │   │               │   │   ├── Stock.kt
│   │   │               │   │   ├── StockPrice.kt
│   │   │               │   │   ├── Portfolio.kt
│   │   │               │   │   ├── Position.kt
│   │   │               │   │   ├── Backtest.kt
│   │   │               │   │   ├── Trade.kt
│   │   │               │   │   ├── EquityPoint.kt
│   │   │               │   │   └── Watchlist.kt
│   │   │               │   │
│   │   │               │   ├── enum/
│   │   │               │   │   ├── SignalType.kt
│   │   │               │   │   ├── SignalStatus.kt
│   │   │               │   │   ├── TimeFrame.kt
│   │   │               │   │   ├── TrendStrength.kt
│   │   │               │   │   └── UserRole.kt
│   │   │               │   │
│   │   │               │   └── valueobject/
│   │   │               │       ├── SignalReasoning.kt
│   │   │               │       ├── TechnicalIndicators.kt
│   │   │               │       ├── BacktestMetrics.kt
│   │   │               │       └── RiskMetrics.kt
│   │   │               │
│   │   │               ├── repository/
│   │   │               │   ├── UserRepository.kt
│   │   │               │   ├── SignalRepository.kt
│   │   │               │   ├── StockRepository.kt
│   │   │               │   ├── StockPriceRepository.kt
│   │   │               │   ├── PortfolioRepository.kt
│   │   │               │   ├── PositionRepository.kt
│   │   │               │   ├── BacktestRepository.kt
│   │   │               │   ├── TradeRepository.kt
│   │   │               │   └── WatchlistRepository.kt
│   │   │               │
│   │   │               ├── service/
│   │   │               │   ├── AuthService.kt
│   │   │               │   ├── SignalService.kt
│   │   │               │   ├── StockService.kt
│   │   │               │   ├── PortfolioService.kt
│   │   │               │   ├── BacktestService.kt
│   │   │               │   ├── UserService.kt
│   │   │               │   ├── TechnicalAnalysisService.kt
│   │   │               │   ├── SignalGeneratorService.kt
│   │   │               │   ├── RiskCalculationService.kt
│   │   │               │   └── NotificationService.kt
│   │   │               │
│   │   │               ├── security/
│   │   │               │   ├── JwtTokenProvider.kt
│   │   │               │   ├── JwtAuthenticationFilter.kt
│   │   │               │   ├── JwtAuthenticationEntryPoint.kt
│   │   │               │   └── UserPrincipal.kt
│   │   │               │
│   │   │               ├── exception/
│   │   │               │   ├── GlobalExceptionHandler.kt
│   │   │               │   ├── ResourceNotFoundException.kt
│   │   │               │   ├── BadRequestException.kt
│   │   │               │   ├── UnauthorizedException.kt
│   │   │               │   └── ApiException.kt
│   │   │               │
│   │   │               ├── websocket/
│   │   │               │   ├── WebSocketHandler.kt
│   │   │               │   └── SignalUpdateBroadcaster.kt
│   │   │               │
│   │   │               ├── util/
│   │   │               │   ├── DateTimeUtil.kt
│   │   │               │   ├── CalculationUtil.kt
│   │   │               │   └── ValidationUtil.kt
│   │   │               │
│   │   │               └── scheduler/
│   │   │                   ├── SignalGenerationScheduler.kt
│   │   │                   ├── StockDataUpdateScheduler.kt
│   │   │                   └── PortfolioPnLScheduler.kt
│   │   │
│   │   └── resources/
│   │       ├── application.yml
│   │       ├── application-dev.yml
│   │       ├── application-prod.yml
│   │       └── db/
│   │           └── migration/
│   │               ├── V1__create_users_table.sql
│   │               ├── V2__create_stocks_table.sql
│   │               ├── V3__create_stock_prices_table.sql
│   │               ├── V4__create_signals_table.sql
│   │               ├── V5__create_portfolios_table.sql
│   │               ├── V6__create_positions_table.sql
│   │               ├── V7__create_backtests_table.sql
│   │               ├── V8__create_trades_table.sql
│   │               └── V9__create_watchlists_table.sql
│   │
│   └── test/
│       └── kotlin/
│           └── com/
│               └── jdb/
│                   └── trading/
│                       ├── integration/
│                       │   ├── SignalControllerIntegrationTest.kt
│                       │   ├── StockControllerIntegrationTest.kt
│                       │   └── AuthControllerIntegrationTest.kt
│                       │
│                       ├── service/
│                       │   ├── SignalServiceTest.kt
│                       │   ├── TechnicalAnalysisServiceTest.kt
│                       │   └── BacktestServiceTest.kt
│                       │
│                       └── repository/
│                           ├── SignalRepositoryTest.kt
│                           └── StockPriceRepositoryTest.kt
│
├── build.gradle.kts
├── settings.gradle.kts
├── gradle.properties
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 4. Database Schema

### 4.1 Entity Relationship Diagram (ERD)

```
┌─────────────────┐         ┌─────────────────┐
│     USERS       │         │    WATCHLISTS   │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │────┬───<│ id (PK)         │
│ email (UNIQUE)  │    │    │ user_id (FK)    │
│ username        │    │    │ stock_id (FK)   │
│ password_hash   │    │    │ created_at      │
│ first_name      │    │    └─────────────────┘
│ last_name       │    │
│ role            │    │    ┌─────────────────┐
│ is_active       │    ├───<│   PORTFOLIOS    │
│ created_at      │    │    ├─────────────────┤
│ updated_at      │    │    │ id (PK)         │
└─────────────────┘    │    │ user_id (FK)    │
                       │    │ name            │
                       │    │ initial_capital │
                       │    │ current_value   │
┌─────────────────┐    │    │ cash            │
│     STOCKS      │    │    │ total_pnl       │
├─────────────────┤    │    │ created_at      │
│ id (PK)         │    │    │ updated_at      │
│ ticker (UNIQUE) │    │    └─────────────────┘
│ company_name    │    │            │
│ sector          │    │            │
│ industry        │    │            ├───────────┐
│ market_cap      │    │            │           │
│ is_active       │    │    ┌───────▼───────┐   │
│ created_at      │    │    │   POSITIONS   │   │
│ updated_at      │    │    ├───────────────┤   │
└─────────────────┘    │    │ id (PK)       │   │
        │              │    │ portfolio_id  │   │
        │              │    │ stock_id (FK) │   │
        ├──────────────┼───>│ signal_id (FK)│   │
        │              │    │ type (L/S)    │   │
        │              │    │ shares        │   │
┌───────▼─────────┐    │    │ entry_price   │   │
│  STOCK_PRICES   │    │    │ current_price │   │
├─────────────────┤    │    │ market_value  │   │
│ id (PK)         │    │    │ pnl           │   │
│ stock_id (FK)   │    │    │ opened_at     │   │
│ date            │    │    │ closed_at     │   │
│ open            │    │    └───────────────┘   │
│ high            │    │                        │
│ low             │    │    ┌───────────────┐   │
│ close           │    └───<│    SIGNALS    │   │
│ volume          │         ├───────────────┤   │
│ adj_close       │         │ id (PK)       │   │
└─────────────────┘         │ user_id (FK)  │   │
(TimescaleDB hypertable)    │ stock_id (FK) │   │
                            │ type (L/S/N)  │   │
                            │ status        │   │
                            │ confidence    │   │
                            │ expected_ret  │   │
┌─────────────────┐         │ entry_price   │   │
│   BACKTESTS     │         │ target_price  │   │
├─────────────────┤         │ stop_loss     │   │
│ id (PK)         │         │ risk_reward   │   │
│ user_id (FK)    │         │ generated_at  │   │
│ name            │         │ expires_at    │   │
│ description     │         │ closed_at     │   │
│ start_date      │         │ timeframe     │   │
│ end_date        │         │ reasoning     │   │
│ initial_capital │         │ actual_return │   │
│ final_capital   │         │ exit_price    │   │
│ total_return    │         │ created_at    │   │
│ metrics (JSON)  │         │ updated_at    │   │
│ created_at      │         └───────────────┘   │
│ updated_at      │                 │           │
└─────────────────┘                 │           │
        │                           └───────────┘
        │                                   │
        │                           ┌───────▼───────┐
        └──────────────────────────>│     TRADES    │
                                    ├───────────────┤
                                    │ id (PK)       │
                                    │ backtest_id   │
                                    │ signal_id (FK)│
                                    │ stock_id (FK) │
                                    │ type (L/S)    │
                                    │ entry_date    │
                                    │ exit_date     │
                                    │ entry_price   │
                                    │ exit_price    │
                                    │ shares        │
                                    │ pnl           │
                                    │ pnl_percent   │
                                    │ holding_days  │
                                    └───────────────┘

┌─────────────────┐
│  EQUITY_CURVE   │
├─────────────────┤
│ id (PK)         │
│ backtest_id (FK)│
│ date            │
│ equity          │
│ drawdown        │
└─────────────────┘
```

### 4.2 Table Definitions

#### 4.2.1 USERS Table
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) NOT NULL DEFAULT 'USER', -- USER, ADMIN, PREMIUM
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

#### 4.2.2 STOCKS Table
```sql
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
CREATE INDEX idx_stocks_industry ON stocks(industry);
```

#### 4.2.3 STOCK_PRICES Table (TimescaleDB Hypertable)
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

-- Convert to TimescaleDB hypertable for optimized time-series queries
SELECT create_hypertable('stock_prices', 'date');

-- Create indexes for efficient queries
CREATE INDEX idx_stock_prices_stock_date ON stock_prices(stock_id, date DESC);
CREATE INDEX idx_stock_prices_date ON stock_prices(date DESC);
```

#### 4.2.4 SIGNALS Table
```sql
CREATE TABLE signals (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    stock_id BIGINT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL, -- LONG, SHORT, NEUTRAL
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, CLOSED, EXPIRED
    confidence SMALLINT NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    expected_return DECIMAL(8, 4) NOT NULL,
    entry_price DECIMAL(12, 4) NOT NULL,
    target_price DECIMAL(12, 4) NOT NULL,
    stop_loss DECIMAL(12, 4) NOT NULL,
    risk_reward_ratio DECIMAL(8, 2) NOT NULL,
    timeframe VARCHAR(10) NOT NULL, -- 1D, 1W, 1M, 3M

    -- JDB Methodology Reasoning (stored as JSONB)
    reasoning JSONB NOT NULL,

    -- Timestamps
    generated_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP,

    -- Performance tracking
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

#### 4.2.5 PORTFOLIOS Table
```sql
CREATE TABLE portfolios (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    initial_capital DECIMAL(15, 2) NOT NULL,
    current_value DECIMAL(15, 2) NOT NULL,
    cash DECIMAL(15, 2) NOT NULL,
    total_pnl DECIMAL(15, 2) NOT NULL DEFAULT 0,
    total_pnl_percent DECIMAL(8, 4) NOT NULL DEFAULT 0,
    day_pnl DECIMAL(15, 2) NOT NULL DEFAULT 0,
    day_pnl_percent DECIMAL(8, 4) NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, name)
);

CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX idx_portfolios_is_active ON portfolios(is_active);
```

#### 4.2.6 POSITIONS Table
```sql
CREATE TABLE positions (
    id BIGSERIAL PRIMARY KEY,
    portfolio_id BIGINT NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    stock_id BIGINT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    signal_id BIGINT REFERENCES signals(id) ON DELETE SET NULL,
    type VARCHAR(10) NOT NULL, -- LONG, SHORT
    shares INTEGER NOT NULL,
    entry_price DECIMAL(12, 4) NOT NULL,
    current_price DECIMAL(12, 4) NOT NULL,
    market_value DECIMAL(15, 2) NOT NULL,
    pnl DECIMAL(15, 2) NOT NULL,
    pnl_percent DECIMAL(8, 4) NOT NULL,
    weight DECIMAL(8, 4) NOT NULL, -- Portfolio weight
    opened_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_positions_portfolio_id ON positions(portfolio_id);
CREATE INDEX idx_positions_stock_id ON positions(stock_id);
CREATE INDEX idx_positions_signal_id ON positions(signal_id);
CREATE INDEX idx_positions_opened_at ON positions(opened_at DESC);
```

#### 4.2.7 BACKTESTS Table
```sql
CREATE TABLE backtests (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(15, 2) NOT NULL,
    final_capital DECIMAL(15, 2) NOT NULL,
    total_return DECIMAL(8, 4) NOT NULL,

    -- Performance metrics stored as JSONB
    metrics JSONB NOT NULL,

    -- Monthly returns stored as JSONB array
    monthly_returns JSONB,

    status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, RUNNING, COMPLETED, FAILED
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_backtests_user_id ON backtests(user_id);
CREATE INDEX idx_backtests_status ON backtests(status);
CREATE INDEX idx_backtests_created_at ON backtests(created_at DESC);
```

#### 4.2.8 TRADES Table
```sql
CREATE TABLE trades (
    id BIGSERIAL PRIMARY KEY,
    backtest_id BIGINT REFERENCES backtests(id) ON DELETE CASCADE,
    signal_id BIGINT REFERENCES signals(id) ON DELETE SET NULL,
    stock_id BIGINT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    type VARCHAR(10) NOT NULL, -- LONG, SHORT
    entry_date TIMESTAMP NOT NULL,
    exit_date TIMESTAMP NOT NULL,
    entry_price DECIMAL(12, 4) NOT NULL,
    exit_price DECIMAL(12, 4) NOT NULL,
    shares INTEGER NOT NULL,
    pnl DECIMAL(15, 2) NOT NULL,
    pnl_percent DECIMAL(8, 4) NOT NULL,
    holding_days INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_trades_backtest_id ON trades(backtest_id);
CREATE INDEX idx_trades_stock_id ON trades(stock_id);
CREATE INDEX idx_trades_entry_date ON trades(entry_date);
```

#### 4.2.9 EQUITY_CURVE Table
```sql
CREATE TABLE equity_curve (
    id BIGSERIAL PRIMARY KEY,
    backtest_id BIGINT NOT NULL REFERENCES backtests(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    equity DECIMAL(15, 2) NOT NULL,
    drawdown DECIMAL(8, 4) NOT NULL,

    UNIQUE(backtest_id, date)
);

CREATE INDEX idx_equity_curve_backtest_id ON equity_curve(backtest_id);
CREATE INDEX idx_equity_curve_date ON equity_curve(date);
```

#### 4.2.10 WATCHLISTS Table
```sql
CREATE TABLE watchlists (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stock_id BIGINT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, stock_id)
);

CREATE INDEX idx_watchlists_user_id ON watchlists(user_id);
CREATE INDEX idx_watchlists_stock_id ON watchlists(stock_id);
```

---

## 5. Domain Model

### 5.1 Entity Classes (Kotlin)

#### User Entity
```kotlin
@Entity
@Table(name = "users")
data class User(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(unique = true, nullable = false)
    val email: String,

    @Column(unique = true, nullable = false)
    val username: String,

    @Column(name = "password_hash", nullable = false)
    val passwordHash: String,

    @Column(name = "first_name")
    val firstName: String? = null,

    @Column(name = "last_name")
    val lastName: String? = null,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val role: UserRole = UserRole.USER,

    @Column(name = "is_active", nullable = false)
    val isActive: Boolean = true,

    @Column(name = "email_verified", nullable = false)
    val emailVerified: Boolean = false,

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @LastModifiedDate
    @Column(name = "updated_at", nullable = false)
    val updatedAt: LocalDateTime = LocalDateTime.now(),

    // Relationships
    @OneToMany(mappedBy = "user", cascade = [CascadeType.ALL])
    val portfolios: MutableList<Portfolio> = mutableListOf(),

    @OneToMany(mappedBy = "user", cascade = [CascadeType.ALL])
    val signals: MutableList<Signal> = mutableListOf(),

    @OneToMany(mappedBy = "user", cascade = [CascadeType.ALL])
    val watchlists: MutableList<Watchlist> = mutableListOf()
)

enum class UserRole {
    USER, PREMIUM, ADMIN
}
```

#### Signal Entity
```kotlin
@Entity
@Table(name = "signals")
data class Signal(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    val user: User? = null,

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "stock_id", nullable = false)
    val stock: Stock,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val type: SignalType,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val status: SignalStatus = SignalStatus.ACTIVE,

    @Column(nullable = false)
    val confidence: Int, // 0-100

    @Column(name = "expected_return", nullable = false, precision = 8, scale = 4)
    val expectedReturn: BigDecimal,

    @Column(name = "entry_price", nullable = false, precision = 12, scale = 4)
    val entryPrice: BigDecimal,

    @Column(name = "target_price", nullable = false, precision = 12, scale = 4)
    val targetPrice: BigDecimal,

    @Column(name = "stop_loss", nullable = false, precision = 12, scale = 4)
    val stopLoss: BigDecimal,

    @Column(name = "risk_reward_ratio", nullable = false, precision = 8, scale = 2)
    val riskRewardRatio: BigDecimal,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val timeframe: TimeFrame,

    // JDB Methodology Reasoning (stored as JSONB)
    @Type(JsonBinaryType::class)
    @Column(columnDefinition = "jsonb", nullable = false)
    val reasoning: SignalReasoning,

    @Column(name = "generated_at", nullable = false)
    val generatedAt: LocalDateTime,

    @Column(name = "expires_at", nullable = false)
    val expiresAt: LocalDateTime,

    @Column(name = "closed_at")
    val closedAt: LocalDateTime? = null,

    // Performance tracking
    @Column(name = "actual_return", precision = 8, scale = 4)
    val actualReturn: BigDecimal? = null,

    @Column(name = "exit_price", precision = 12, scale = 4)
    val exitPrice: BigDecimal? = null,

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @LastModifiedDate
    @Column(name = "updated_at", nullable = false)
    val updatedAt: LocalDateTime = LocalDateTime.now()
)

enum class SignalType {
    LONG, SHORT, NEUTRAL
}

enum class SignalStatus {
    ACTIVE, CLOSED, EXPIRED
}

enum class TimeFrame {
    ONE_DAY, ONE_WEEK, ONE_MONTH, THREE_MONTHS
}
```

#### SignalReasoning Value Object
```kotlin
@Embeddable
data class SignalReasoning(
    val dominantMA: DominantMAInfo,
    val bollingerBands: BollingerBandsInfo,
    val fibonacci: FibonacciInfo,
    val rsiDivergence: RSIDivergenceInfo,
    val volumeConfirmation: Boolean,
    val trendStrength: TrendStrength
)

data class DominantMAInfo(
    val period: Int, // 20, 50, or 200
    val respected: Boolean,
    val distance: BigDecimal // Percentage from MA
)

data class BollingerBandsInfo(
    val position: BollingerPosition,
    val bandwidth: BigDecimal
)

enum class BollingerPosition {
    LOWER, MIDDLE, UPPER, BELOW, ABOVE
}

data class FibonacciInfo(
    val level: BigDecimal, // 0, 0.236, 0.382, 0.5, 0.618, 0.786, 1
    val inRetracementZone: Boolean
)

data class RSIDivergenceInfo(
    val detected: Boolean,
    val type: RSIDivergenceType?,
    val strength: BigDecimal?
)

enum class RSIDivergenceType {
    BULLISH, BEARISH
}

enum class TrendStrength {
    STRONG, MODERATE, WEAK
}
```

#### Stock Entity
```kotlin
@Entity
@Table(name = "stocks")
data class Stock(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(unique = true, nullable = false)
    val ticker: String,

    @Column(name = "company_name", nullable = false)
    val companyName: String,

    @Column
    val sector: String? = null,

    @Column
    val industry: String? = null,

    @Column(name = "market_cap")
    val marketCap: Long? = null,

    @Column(name = "is_active", nullable = false)
    val isActive: Boolean = true,

    @Column(name = "last_updated")
    val lastUpdated: LocalDateTime? = null,

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @LastModifiedDate
    @Column(name = "updated_at", nullable = false)
    val updatedAt: LocalDateTime = LocalDateTime.now(),

    // Relationships
    @OneToMany(mappedBy = "stock", cascade = [CascadeType.ALL])
    val prices: MutableList<StockPrice> = mutableListOf(),

    @OneToMany(mappedBy = "stock")
    val signals: MutableList<Signal> = mutableListOf()
)
```

#### StockPrice Entity (TimescaleDB)
```kotlin
@Entity
@Table(name = "stock_prices")
@IdClass(StockPriceId::class)
data class StockPrice(
    @Id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "stock_id", nullable = false)
    val stock: Stock,

    @Id
    @Column(nullable = false)
    val date: LocalDateTime,

    @Column(nullable = false, precision = 12, scale = 4)
    val open: BigDecimal,

    @Column(nullable = false, precision = 12, scale = 4)
    val high: BigDecimal,

    @Column(nullable = false, precision = 12, scale = 4)
    val low: BigDecimal,

    @Column(nullable = false, precision = 12, scale = 4)
    val close: BigDecimal,

    @Column(nullable = false)
    val volume: Long,

    @Column(name = "adj_close", precision = 12, scale = 4)
    val adjClose: BigDecimal? = null
)

data class StockPriceId(
    val stock: Long = 0,
    val date: LocalDateTime = LocalDateTime.now()
) : Serializable
```

#### Portfolio Entity
```kotlin
@Entity
@Table(name = "portfolios")
data class Portfolio(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    val user: User,

    @Column(nullable = false)
    val name: String,

    @Column
    val description: String? = null,

    @Column(name = "initial_capital", nullable = false, precision = 15, scale = 2)
    val initialCapital: BigDecimal,

    @Column(name = "current_value", nullable = false, precision = 15, scale = 2)
    var currentValue: BigDecimal,

    @Column(nullable = false, precision = 15, scale = 2)
    var cash: BigDecimal,

    @Column(name = "total_pnl", nullable = false, precision = 15, scale = 2)
    var totalPnL: BigDecimal = BigDecimal.ZERO,

    @Column(name = "total_pnl_percent", nullable = false, precision = 8, scale = 4)
    var totalPnLPercent: BigDecimal = BigDecimal.ZERO,

    @Column(name = "day_pnl", nullable = false, precision = 15, scale = 2)
    var dayPnL: BigDecimal = BigDecimal.ZERO,

    @Column(name = "day_pnl_percent", nullable = false, precision = 8, scale = 4)
    var dayPnLPercent: BigDecimal = BigDecimal.ZERO,

    @Column(name = "is_active", nullable = false)
    val isActive: Boolean = true,

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @LastModifiedDate
    @Column(name = "updated_at", nullable = false)
    val updatedAt: LocalDateTime = LocalDateTime.now(),

    // Relationships
    @OneToMany(mappedBy = "portfolio", cascade = [CascadeType.ALL])
    val positions: MutableList<Position> = mutableListOf()
)
```

#### Position Entity
```kotlin
@Entity
@Table(name = "positions")
data class Position(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "portfolio_id", nullable = false)
    val portfolio: Portfolio,

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "stock_id", nullable = false)
    val stock: Stock,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "signal_id")
    val signal: Signal? = null,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val type: PositionType,

    @Column(nullable = false)
    val shares: Int,

    @Column(name = "entry_price", nullable = false, precision = 12, scale = 4)
    val entryPrice: BigDecimal,

    @Column(name = "current_price", nullable = false, precision = 12, scale = 4)
    var currentPrice: BigDecimal,

    @Column(name = "market_value", nullable = false, precision = 15, scale = 2)
    var marketValue: BigDecimal,

    @Column(nullable = false, precision = 15, scale = 2)
    var pnl: BigDecimal,

    @Column(name = "pnl_percent", nullable = false, precision = 8, scale = 4)
    var pnlPercent: BigDecimal,

    @Column(nullable = false, precision = 8, scale = 4)
    var weight: BigDecimal,

    @Column(name = "opened_at", nullable = false)
    val openedAt: LocalDateTime,

    @Column(name = "closed_at")
    val closedAt: LocalDateTime? = null,

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @LastModifiedDate
    @Column(name = "updated_at", nullable = false)
    val updatedAt: LocalDateTime = LocalDateTime.now()
)

enum class PositionType {
    LONG, SHORT
}
```

#### Backtest Entity
```kotlin
@Entity
@Table(name = "backtests")
data class Backtest(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    val user: User,

    @Column(nullable = false)
    val name: String,

    @Column
    val description: String? = null,

    @Column(name = "start_date", nullable = false)
    val startDate: LocalDate,

    @Column(name = "end_date", nullable = false)
    val endDate: LocalDate,

    @Column(name = "initial_capital", nullable = false, precision = 15, scale = 2)
    val initialCapital: BigDecimal,

    @Column(name = "final_capital", nullable = false, precision = 15, scale = 2)
    val finalCapital: BigDecimal,

    @Column(name = "total_return", nullable = false, precision = 8, scale = 4)
    val totalReturn: BigDecimal,

    // Performance metrics stored as JSONB
    @Type(JsonBinaryType::class)
    @Column(columnDefinition = "jsonb", nullable = false)
    val metrics: BacktestMetrics,

    // Monthly returns stored as JSONB
    @Type(JsonBinaryType::class)
    @Column(name = "monthly_returns", columnDefinition = "jsonb")
    val monthlyReturns: List<MonthlyReturn>? = null,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val status: BacktestStatus = BacktestStatus.PENDING,

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @LastModifiedDate
    @Column(name = "updated_at", nullable = false)
    val updatedAt: LocalDateTime = LocalDateTime.now(),

    // Relationships
    @OneToMany(mappedBy = "backtest", cascade = [CascadeType.ALL])
    val trades: MutableList<Trade> = mutableListOf(),

    @OneToMany(mappedBy = "backtest", cascade = [CascadeType.ALL])
    val equityCurve: MutableList<EquityPoint> = mutableListOf()
)

enum class BacktestStatus {
    PENDING, RUNNING, COMPLETED, FAILED
}

data class BacktestMetrics(
    val totalTrades: Int,
    val winningTrades: Int,
    val losingTrades: Int,
    val winRate: BigDecimal,
    val profitFactor: BigDecimal,
    val sharpeRatio: BigDecimal,
    val sortinoRatio: BigDecimal,
    val maxDrawdown: BigDecimal,
    val maxDrawdownDuration: Int,
    val averageWin: BigDecimal,
    val averageLoss: BigDecimal,
    val expectancy: BigDecimal,
    val calmarRatio: BigDecimal
)

data class MonthlyReturn(
    val year: Int,
    val month: Int,
    val returnPercent: BigDecimal
)
```

---

## 6. API Architecture

### 6.1 REST API Endpoints

#### Base URL
```
https://api.jdb-trading.com/v1
```

#### 6.1.1 Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login user | No |
| POST | `/auth/refresh` | Refresh JWT token | Yes |
| POST | `/auth/logout` | Logout user | Yes |
| POST | `/auth/forgot-password` | Request password reset | No |
| POST | `/auth/reset-password` | Reset password | No |
| GET | `/auth/verify-email/{token}` | Verify email | No |

#### 6.1.2 User Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/users/me` | Get current user | Yes |
| PUT | `/users/me` | Update current user | Yes |
| PUT | `/users/me/password` | Change password | Yes |
| DELETE | `/users/me` | Delete account | Yes |
| GET | `/users/me/settings` | Get user settings | Yes |
| PUT | `/users/me/settings` | Update user settings | Yes |

#### 6.1.3 Signal Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/signals` | Get all signals (with filters) | Optional |
| GET | `/signals/{id}` | Get signal by ID | Optional |
| POST | `/signals` | Create signal (admin/system) | Yes (Admin) |
| PUT | `/signals/{id}` | Update signal | Yes (Admin) |
| DELETE | `/signals/{id}` | Delete signal | Yes (Admin) |
| GET | `/signals/active` | Get active signals | Optional |
| GET | `/signals/expired` | Get expired signals | Optional |
| POST | `/signals/{id}/close` | Close signal | Yes |
| GET | `/signals/user/me` | Get user's signals | Yes |

**Query Parameters for GET /signals:**
- `type`: LONG, SHORT, NEUTRAL
- `status`: ACTIVE, CLOSED, EXPIRED
- `ticker`: Stock ticker
- `minConfidence`: Minimum confidence (0-100)
- `timeframe`: 1D, 1W, 1M, 3M
- `page`: Page number (default: 0)
- `size`: Page size (default: 20)
- `sort`: Sort field (default: generatedAt)
- `order`: ASC, DESC (default: DESC)

#### 6.1.4 Stock Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/stocks` | Get all stocks (with search) | No |
| GET | `/stocks/{ticker}` | Get stock by ticker | No |
| GET | `/stocks/{ticker}/data` | Get stock price data (OHLCV) | No |
| GET | `/stocks/{ticker}/technicals` | Get technical indicators | No |
| GET | `/stocks/{ticker}/signals` | Get signals for stock | No |
| POST | `/stocks` | Add new stock (admin) | Yes (Admin) |
| PUT | `/stocks/{ticker}` | Update stock (admin) | Yes (Admin) |
| DELETE | `/stocks/{ticker}` | Delete stock (admin) | Yes (Admin) |

**Query Parameters for GET /stocks/{ticker}/data:**
- `timeframe`: 1D, 1W, 1M (default: 1D)
- `from`: Start date (ISO 8601)
- `to`: End date (ISO 8601)
- `limit`: Max records (default: 180)

#### 6.1.5 Portfolio Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/portfolios` | Get user's portfolios | Yes |
| GET | `/portfolios/{id}` | Get portfolio by ID | Yes |
| POST | `/portfolios` | Create portfolio | Yes |
| PUT | `/portfolios/{id}` | Update portfolio | Yes |
| DELETE | `/portfolios/{id}` | Delete portfolio | Yes |
| GET | `/portfolios/{id}/positions` | Get positions | Yes |
| POST | `/portfolios/{id}/positions` | Open position | Yes |
| PUT | `/portfolios/{id}/positions/{positionId}` | Update position | Yes |
| DELETE | `/portfolios/{id}/positions/{positionId}` | Close position | Yes |
| GET | `/portfolios/{id}/performance` | Get performance metrics | Yes |
| GET | `/portfolios/{id}/risk` | Get risk metrics | Yes |

#### 6.1.6 Backtest Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/backtests` | Get user's backtests | Yes |
| GET | `/backtests/{id}` | Get backtest by ID | Yes |
| POST | `/backtests` | Create backtest | Yes |
| DELETE | `/backtests/{id}` | Delete backtest | Yes |
| POST | `/backtests/{id}/run` | Run backtest | Yes |
| GET | `/backtests/{id}/trades` | Get backtest trades | Yes |
| GET | `/backtests/{id}/equity-curve` | Get equity curve | Yes |
| GET | `/backtests/{id}/metrics` | Get metrics | Yes |
| GET | `/backtests/{id}/monthly-returns` | Get monthly returns | Yes |

#### 6.1.7 Watchlist Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/watchlists` | Get user's watchlist | Yes |
| POST | `/watchlists` | Add stock to watchlist | Yes |
| DELETE | `/watchlists/{stockId}` | Remove from watchlist | Yes |

#### 6.1.8 Health & System Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Health check | No |
| GET | `/health/db` | Database health | No |
| GET | `/health/redis` | Redis health | No |
| GET | `/actuator/metrics` | System metrics | Yes (Admin) |
| GET | `/actuator/info` | App info | No |

### 6.2 WebSocket Endpoints

#### WebSocket Base URL
```
wss://api.jdb-trading.com/ws
```

#### Topics

| Topic | Description | Subscription |
|-------|-------------|--------------|
| `/topic/signals` | Real-time signal updates | Public |
| `/topic/signals/new` | New signals | Public |
| `/topic/signals/{id}` | Signal updates | Public |
| `/topic/stocks/{ticker}` | Stock price updates | Public |
| `/user/queue/portfolio` | Portfolio updates | User-specific |
| `/user/queue/positions` | Position updates | User-specific |
| `/user/queue/notifications` | User notifications | User-specific |

#### Example Usage
```kotlin
// Subscribe to signal updates
stompClient.subscribe("/topic/signals/new") { message ->
    val signal: Signal = objectMapper.readValue(message.body)
    // Handle new signal
}

// Subscribe to user-specific portfolio updates
stompClient.subscribe("/user/queue/portfolio") { message ->
    val portfolio: Portfolio = objectMapper.readValue(message.body)
    // Update portfolio UI
}
```

---

## 7. Security Architecture

### 7.1 Authentication Flow

```
┌─────────┐                ┌──────────────┐                ┌──────────┐
│ Client  │                │   Backend    │                │   Redis  │
└────┬────┘                └──────┬───────┘                └────┬─────┘
     │                            │                             │
     │  POST /auth/login          │                             │
     ├───────────────────────────>│                             │
     │  {email, password}         │                             │
     │                            │                             │
     │                            │ Validate credentials        │
     │                            ├─────────────────────────────┤
     │                            │                             │
     │                            │ Generate JWT Access Token   │
     │                            │ Generate Refresh Token      │
     │                            │                             │
     │                            │ Store Refresh Token         │
     │                            ├────────────────────────────>│
     │                            │                             │
     │  200 OK                    │                             │
     │<───────────────────────────┤                             │
     │  {                         │                             │
     │    accessToken: "...",     │                             │
     │    refreshToken: "...",    │                             │
     │    expiresIn: 3600         │                             │
     │  }                         │                             │
     │                            │                             │
     │  Subsequent API Requests   │                             │
     │  Authorization: Bearer ... │                             │
     ├───────────────────────────>│                             │
     │                            │                             │
     │                            │ Validate JWT                │
     │                            ├────────────────┐            │
     │                            │                │            │
     │                            │<───────────────┘            │
     │                            │                             │
     │  200 OK (with data)        │                             │
     │<───────────────────────────┤                             │
     │                            │                             │
```

### 7.2 JWT Token Structure

**Access Token (expires in 1 hour):**
```json
{
  "sub": "user@example.com",
  "userId": 123,
  "username": "trader1",
  "role": "USER",
  "iat": 1699876543,
  "exp": 1699880143
}
```

**Refresh Token (expires in 7 days):**
```json
{
  "sub": "user@example.com",
  "userId": 123,
  "tokenId": "uuid",
  "iat": 1699876543,
  "exp": 1700481343
}
```

### 7.3 Security Configuration

#### Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character

#### Rate Limiting
- Login attempts: 5 per 15 minutes
- API requests: 100 per minute (authenticated)
- API requests: 20 per minute (unauthenticated)
- WebSocket connections: 5 per user

#### CORS Configuration
```yaml
cors:
  allowed-origins:
    - https://jdb-trading.com
    - https://www.jdb-trading.com
    - http://localhost:3000
  allowed-methods:
    - GET
    - POST
    - PUT
    - DELETE
    - PATCH
  allowed-headers:
    - Authorization
    - Content-Type
  max-age: 3600
```

---

## 8. Data Flow

### 8.1 Signal Generation Flow

```
┌──────────────────┐
│  Scheduler       │
│  (Daily at 6 PM) │
└────────┬─────────┘
         │
         │ Trigger Signal Generation
         │
         ▼
┌─────────────────────────┐
│ SignalGeneratorService  │
└────────┬────────────────┘
         │
         │ 1. Fetch Active Stocks
         │
         ▼
┌─────────────────────────┐
│  StockRepository        │
└────────┬────────────────┘
         │
         │ 2. Get Historical Price Data
         │
         ▼
┌─────────────────────────┐
│  StockPriceRepository   │
└────────┬────────────────┘
         │
         │ 3. Calculate Technical Indicators
         │
         ▼
┌─────────────────────────────┐
│  TechnicalAnalysisService   │
│  - MA (20, 50, 200)         │
│  - RSI                      │
│  - Bollinger Bands          │
│  - Fibonacci Levels         │
│  - Volume Analysis          │
└────────┬────────────────────┘
         │
         │ 4. Apply JDB Methodology
         │
         ▼
┌─────────────────────────────┐
│  JDB Signal Logic           │
│  - Dominant MA Detection    │
│  - BB Position Analysis     │
│  - Fibonacci Zone Check     │
│  - RSI Divergence Detection │
│  - Volume Confirmation      │
│  - Risk/Reward Calculation  │
└────────┬────────────────────┘
         │
         │ 5. Generate Signal
         │
         ▼
┌─────────────────────────┐
│  Signal (Entity)        │
│  - Confidence Score     │
│  - Entry/Target/Stop    │
│  - Reasoning (JSONB)    │
└────────┬────────────────┘
         │
         │ 6. Persist Signal
         │
         ▼
┌─────────────────────────┐
│  SignalRepository       │
└────────┬────────────────┘
         │
         │ 7. Broadcast via WebSocket
         │
         ▼
┌─────────────────────────────┐
│  SignalUpdateBroadcaster    │
│  - Notify Subscribers       │
│  - Send Email Notifications │
└─────────────────────────────┘
```

### 8.2 Portfolio P&L Calculation Flow

```
┌──────────────────────┐
│  Scheduler           │
│  (Every 5 minutes)   │
└──────────┬───────────┘
           │
           │ Update Portfolio Values
           │
           ▼
┌────────────────────────┐
│  PortfolioPnLScheduler │
└──────────┬─────────────┘
           │
           │ 1. Get Active Portfolios
           │
           ▼
┌────────────────────────┐
│  PortfolioRepository   │
└──────────┬─────────────┘
           │
           │ 2. For Each Portfolio
           │
           ▼
┌────────────────────────┐
│  Get All Positions     │
└──────────┬─────────────┘
           │
           │ 3. Fetch Current Prices
           │
           ▼
┌────────────────────────┐
│  StockService          │
└──────────┬─────────────┘
           │
           │ 4. Calculate Position Values
           │
           ▼
┌─────────────────────────────┐
│  RiskCalculationService     │
│  - Market Value             │
│  - P&L per Position         │
│  - Portfolio Weight         │
│  - Total P&L                │
│  - Day P&L                  │
└──────────┬──────────────────┘
           │
           │ 5. Update Portfolio
           │
           ▼
┌────────────────────────┐
│  Portfolio (Entity)    │
│  - Current Value       │
│  - Total P&L           │
│  - Day P&L             │
└──────────┬─────────────┘
           │
           │ 6. Persist Changes
           │
           ▼
┌────────────────────────┐
│  PortfolioRepository   │
└──────────┬─────────────┘
           │
           │ 7. Broadcast Update
           │
           ▼
┌────────────────────────┐
│  WebSocket             │
│  /user/queue/portfolio │
└────────────────────────┘
```

---

## 9. Additional Features

### 9.1 Caching Strategy

**Redis Caching Layers:**

| Cache Key | TTL | Purpose |
|-----------|-----|---------|
| `stock:{ticker}` | 5 min | Stock details |
| `stock:{ticker}:price` | 1 min | Current price |
| `stock:{ticker}:technicals` | 5 min | Technical indicators |
| `signals:active` | 1 min | Active signals list |
| `signal:{id}` | 5 min | Signal details |
| `user:{id}:portfolio` | 30 sec | Portfolio data |
| `market:status` | 1 hour | Market open/close |

**Cache Invalidation:**
- On signal update/creation
- On position open/close
- On stock price update
- On user action

### 9.2 Scheduled Jobs

| Job | Schedule | Description |
|-----|----------|-------------|
| Signal Generation | Daily at 6 PM | Generate trading signals |
| Stock Data Update | Every 15 min (market hours) | Update stock prices |
| Portfolio P&L Update | Every 5 min | Calculate portfolio values |
| Signal Expiration | Hourly | Mark expired signals |
| Database Cleanup | Daily at 2 AM | Archive old data |
| Email Notifications | Every 10 min | Send pending notifications |

### 9.3 Monitoring & Alerts

**Health Checks:**
- Database connectivity
- Redis connectivity
- External API availability
- Disk space
- Memory usage
- CPU usage

**Metrics to Track:**
- API response times
- Database query times
- Cache hit rates
- Active WebSocket connections
- Signal generation success rate
- User registration rate
- Error rates by endpoint

**Alerts:**
- API response time > 1 second
- Database connection pool exhausted
- Redis unavailable
- Error rate > 5%
- Disk space < 10%
- Memory usage > 90%

### 9.4 Data Retention Policy

| Data Type | Retention Period | Archive Strategy |
|-----------|-----------------|------------------|
| Stock Prices | 10 years | Compress after 1 year |
| Signals (Active) | Until closed/expired | - |
| Signals (Closed) | 5 years | Archive after 2 years |
| Trades | 10 years | Compress after 1 year |
| Backtests | 2 years | Delete after expiry |
| User Activity Logs | 1 year | Delete after expiry |
| Error Logs | 90 days | Delete after expiry |

---

## 10. Deployment Strategy

### 10.1 Docker Configuration

**Dockerfile:**
```dockerfile
FROM gradle:8.5-jdk21 AS build
WORKDIR /app
COPY . .
RUN gradle clean build --no-daemon -x test

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /app/build/libs/*.jar app.jar
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/actuator/health || exit 1
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg16
    environment:
      POSTGRES_DB: jdb_trading
      POSTGRES_USER: jdb_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U jdb_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  backend:
    build: .
    ports:
      - "8080:8080"
    environment:
      SPRING_PROFILES_ACTIVE: prod
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: jdb_trading
      DB_USER: jdb_user
      DB_PASSWORD: ${DB_PASSWORD}
      REDIS_HOST: redis
      REDIS_PORT: 6379
      JWT_SECRET: ${JWT_SECRET}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 5s
      retries: 3

volumes:
  postgres_data:
  redis_data:
```

### 10.2 Environment Configuration

**application.yml (Base):**
```yaml
spring:
  application:
    name: jdb-trading-backend

  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        jdbc:
          time_zone: UTC

  flyway:
    enabled: true
    baseline-on-migrate: true
    locations: classpath:db/migration

server:
  port: 8080
  compression:
    enabled: true

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: when-authorized

jwt:
  access-token-expiration: 3600000 # 1 hour
  refresh-token-expiration: 604800000 # 7 days
```

**application-prod.yml:**
```yaml
spring:
  datasource:
    url: jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}
    username: ${DB_USER}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000

  data:
    redis:
      host: ${REDIS_HOST}
      port: ${REDIS_PORT}
      timeout: 2000ms

  jpa:
    show-sql: false

logging:
  level:
    root: INFO
    com.jdb.trading: DEBUG
```

### 10.3 CI/CD Pipeline (GitHub Actions)

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-java@v3
        with:
          java-version: '21'
      - name: Run tests
        run: ./gradlew test
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-java@v3
        with:
          java-version: '21'
      - name: Build
        run: ./gradlew build -x test
      - name: Build Docker image
        run: docker build -t jdb-trading-backend:${{ github.sha }} .
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push jdb-trading-backend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # Add deployment steps (AWS ECS, K8s, etc.)
```

---

## 11. Summary & Next Steps

### Proposed Architecture Highlights

✅ **Modern Tech Stack**: Spring Boot 3.x + Kotlin + PostgreSQL + Redis
✅ **Scalable Design**: Microservice-ready, horizontal scalability
✅ **Time-Series Optimization**: TimescaleDB for efficient OHLCV data
✅ **Real-time Capabilities**: WebSocket support for live updates
✅ **Security First**: JWT authentication, rate limiting, CORS
✅ **Comprehensive Testing**: Unit, integration, and E2E tests
✅ **Production Ready**: Docker, monitoring, health checks
✅ **Well-Documented**: OpenAPI/Swagger documentation

### Recommended Implementation Order

1. **Phase 1: Core Setup** (Week 1-2)
   - Project structure
   - Database setup (PostgreSQL + TimescaleDB)
   - Flyway migrations
   - Spring Security + JWT
   - User authentication

2. **Phase 2: Stock Management** (Week 3-4)
   - Stock entity & repository
   - Stock price management
   - Technical indicators calculation
   - Stock CRUD endpoints

3. **Phase 3: Signal Generation** (Week 5-6)
   - Signal entity & reasoning
   - JDB methodology implementation
   - Technical analysis service
   - Signal generation scheduler
   - Signal endpoints

4. **Phase 4: Portfolio Management** (Week 7-8)
   - Portfolio & position entities
   - Portfolio CRUD operations
   - P&L calculations
   - Risk metrics
   - Portfolio endpoints

5. **Phase 5: Backtesting Engine** (Week 9-10)
   - Backtest entity & trades
   - Backtesting algorithm
   - Performance metrics calculation
   - Equity curve generation
   - Backtest endpoints

6. **Phase 6: Real-time Features** (Week 11-12)
   - WebSocket configuration
   - Real-time signal updates
   - Portfolio live updates
   - Notifications

7. **Phase 7: Production Readiness** (Week 13-14)
   - Redis caching
   - Monitoring & alerting
   - Performance optimization
   - Load testing
   - Documentation
   - Deployment

### Questions for Clarification

Before starting implementation, please confirm:

1. **External Data Sources**: Which stock data provider should we use? (Alpha Vantage, Yahoo Finance, Polygon.io, etc.)
2. **User Tiers**: What features differentiate FREE vs PREMIUM users?
3. **Email Provider**: Which email service for notifications? (SendGrid, AWS SES, etc.)
4. **Cloud Provider**: AWS, GCP, Azure, or self-hosted?
5. **CI/CD Platform**: GitHub Actions, GitLab CI, Jenkins?
6. **Monitoring**: Preferred monitoring stack? (Prometheus + Grafana, Datadog, New Relic?)

---

**Ready to start implementation? Let me know which phase to begin with!** 🚀
