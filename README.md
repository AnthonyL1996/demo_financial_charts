# JDB Trading System Frontend

A modern, production-ready frontend application for the JDB Trading System, implementing the "Kruispunt" (Crossroads) trading methodology. Built with Next.js 14, TypeScript, Mantine UI, and Lightweight Charts for professional financial charting and trading signal management.

![Next.js](https://img.shields.io/badge/Next.js-14.2-black?logo=next.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue?logo=typescript)
![Mantine UI](https://img.shields.io/badge/Mantine-7.5-339af0?logo=mantine)
![License](https://img.shields.io/badge/license-MIT-green)

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Development](#development)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)

## ✨ Features

### Core Functionality
- **Interactive Financial Charts**: Real-time candlestick charts using Lightweight Charts library
- **Technical Indicators**: Support for multiple indicators including:
  - Simple Moving Averages (SMA 20, 50, 200)
  - Exponential Moving Averages (EMA 12, 26)
  - Bollinger Bands with configurable parameters
  - Volume analysis
- **Trading Signals**: Real-time display of LONG/SHORT signals based on JDB methodology
- **Signal Management**: Filter and manage trading signals by status, type, and confidence
- **Portfolio Tracking**: Overview of positions and performance metrics
- **Backtest Results**: Historical performance analysis

### Technical Features
- **Dark Mode**: Default dark theme optimized for trading environments
- **Responsive Design**: Mobile-first approach with desktop optimization
- **Type Safety**: Full TypeScript coverage throughout the application
- **Real-time Updates**: Ready for WebSocket integration (TanStack Query configured)
- **JWT Authentication Ready**: Prepared for secure API authentication
- **Comprehensive Testing**: 53+ tests with Vitest and React Testing Library
- **Mock Backend API**: Development API with realistic trading data

## 🛠 Tech Stack

### Frontend Framework
- **Next.js 14.2** - React framework with App Router
- **React 18** - UI library
- **TypeScript 5.3** - Type safety and enhanced DX

### UI & Styling
- **Mantine UI 7.5** - Component library with dark mode support
- **Lightweight Charts 4.1** - TradingView-powered charting library
- **CSS Modules** - Scoped styling

### Data Management
- **TanStack Query 5.x** - Data fetching, caching, and synchronization
- **React Hooks** - State management

### Development & Testing
- **Vitest** - Fast unit testing framework
- **React Testing Library** - Component testing
- **MSW** - API mocking
- **ESLint** - Code linting
- **TypeScript** - Static type checking

### DevOps
- **Docker** - Containerization
- **Node.js 20** - Runtime environment

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js**: v20.x or higher ([Download](https://nodejs.org/))
- **npm**: v10.x or higher (comes with Node.js)
- **Docker**: v24.x or higher (optional, for containerized deployment) ([Download](https://www.docker.com/))
- **Git**: Latest version ([Download](https://git-scm.com/))

Check your versions:
```bash
node --version  # Should be v20.x or higher
npm --version   # Should be v10.x or higher
docker --version # Should be v24.x or higher (if using Docker)
```

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/demo_financial_charts.git
cd demo_financial_charts
```

### 2. Install Dependencies

```bash
npm install
```

This will install all required dependencies including:
- Next.js and React
- Mantine UI components
- Lightweight Charts
- TanStack Query
- Testing libraries (Vitest, React Testing Library)
- TypeScript and type definitions

### 3. Environment Setup

Create a `.env.local` file in the root directory:

```bash
# Optional: Add environment variables
# NEXT_PUBLIC_API_URL=http://localhost:3000/api
# NEXT_PUBLIC_WS_URL=ws://localhost:3000
```

For production, create a `.env.production` file with production values.

## 💻 Development

### Start Development Server

```bash
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Mock API**: http://localhost:3000/api

The development server features:
- Hot Module Replacement (HMR)
- Fast Refresh for instant updates
- TypeScript type checking
- ESLint linting

### Development Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint

# Run tests
npm test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### Code Quality

The project uses ESLint for code quality. Run the linter:

```bash
npm run lint
```

## 🧪 Testing

The project includes comprehensive test coverage using Vitest and React Testing Library.

### Running Tests

```bash
# Run all tests in watch mode
npm test

# Run tests once (CI mode)
npm run test:run

# Run tests with UI
npm run test:ui

# Run tests with coverage report
npm run test:coverage
```

### Test Coverage

Current test coverage: **53 tests** across 4 test suites

- **Utility Tests** (24 tests): `lib/utils/formatters.test.ts`
  - Currency formatting
  - Percentage formatting
  - Date formatting
  - Number formatting

- **Mock Data Tests** (18 tests): `lib/mock/mockData.test.ts`
  - OHLCV data generation
  - Signal data validation
  - Stock data validation

- **Component Tests** (11 tests):
  - `components/signals/SignalCard.test.tsx` (7 tests)
  - `components/charts/ChartControls.test.tsx` (4 tests)

### Writing Tests

Tests are located next to their source files with `.test.ts` or `.test.tsx` extensions.

Example test:
```typescript
import { describe, it, expect } from 'vitest';
import { formatCurrency } from './formatters';

describe('formatCurrency', () => {
  it('should format positive numbers as currency', () => {
    expect(formatCurrency(1234.56)).toBe('$1,234.56');
  });
});
```

For detailed testing documentation, see [TESTING.md](./TESTING.md).

## 🐳 Docker Deployment

### Quick Start with Docker

#### 1. Build the Docker Image

```bash
docker build -t jdb-trading-frontend:latest .
```

This creates an optimized production image using multi-stage builds:
- **Stage 1 (deps)**: Installs production dependencies
- **Stage 2 (builder)**: Builds the Next.js application
- **Stage 3 (runner)**: Creates minimal runtime image (~150MB)

#### 2. Run the Container

```bash
docker run -p 3000:3000 jdb-trading-frontend:latest
```

The application will be available at http://localhost:3000

#### 3. Run with Environment Variables

```bash
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://api.example.com \
  -e NODE_ENV=production \
  jdb-trading-frontend:latest
```

### Docker Compose (Recommended)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=http://localhost:3000/api
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s

  # Add your backend service here if needed
  # backend:
  #   image: your-backend-image
  #   ports:
  #     - "8000:8000"
```

Run with Docker Compose:

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Docker Image Details

- **Base Image**: node:20-alpine
- **Image Size**: ~150MB (optimized)
- **User**: Non-root user (nextjs:nodejs)
- **Port**: 3000
- **Health Check**: Enabled (checks /api/health every 30s)

### Production Deployment

For production deployments to cloud platforms:

#### AWS ECS/Fargate
```bash
# Tag the image
docker tag jdb-trading-frontend:latest YOUR_ECR_REGISTRY/jdb-trading-frontend:latest

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_REGISTRY
docker push YOUR_ECR_REGISTRY/jdb-trading-frontend:latest
```

#### Google Cloud Run
```bash
# Tag and push to Google Container Registry
docker tag jdb-trading-frontend:latest gcr.io/YOUR_PROJECT/jdb-trading-frontend:latest
docker push gcr.io/YOUR_PROJECT/jdb-trading-frontend:latest

# Deploy to Cloud Run
gcloud run deploy jdb-trading-frontend \
  --image gcr.io/YOUR_PROJECT/jdb-trading-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances
```bash
# Tag and push to Azure Container Registry
docker tag jdb-trading-frontend:latest YOUR_ACR.azurecr.io/jdb-trading-frontend:latest
docker push YOUR_ACR.azurecr.io/jdb-trading-frontend:latest

# Deploy to ACI
az container create \
  --resource-group YOUR_RG \
  --name jdb-trading-frontend \
  --image YOUR_ACR.azurecr.io/jdb-trading-frontend:latest \
  --dns-name-label jdb-trading \
  --ports 3000
```

## 📡 API Documentation

The application includes a mock backend API for development and testing.

### Base URL

```
http://localhost:3000/api
```

### Endpoints

#### Health Check
```http
GET /api/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "0.1.0"
}
```

#### Get All Signals
```http
GET /api/signals?status=ACTIVE&type=LONG&minConfidence=70&limit=20
```

Query Parameters:
- `status` (optional): Filter by status (ACTIVE, CLOSED, STOPPED)
- `type` (optional): Filter by type (LONG, SHORT)
- `ticker` (optional): Filter by stock ticker
- `minConfidence` (optional): Minimum confidence level (0-100)
- `limit` (optional): Maximum number of results

Response:
```json
{
  "success": true,
  "data": [
    {
      "id": "signal-1",
      "ticker": "AAPL",
      "companyName": "Apple Inc.",
      "type": "LONG",
      "status": "ACTIVE",
      "entryPrice": 180.50,
      "currentPrice": 185.20,
      "profitLoss": 4.70,
      "profitLossPercent": 2.60,
      "confidence": 85,
      "createdAt": "2024-01-15T10:00:00.000Z"
    }
  ],
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### Get Single Signal
```http
GET /api/signals/{id}
```

#### Get All Stocks
```http
GET /api/stocks?search=AAPL
```

Query Parameters:
- `search` (optional): Search by ticker or company name

#### Get Single Stock
```http
GET /api/stocks/{ticker}
```

#### Get Stock Chart Data
```http
GET /api/stocks/{ticker}/data?timeframe=1D&limit=180
```

Query Parameters:
- `timeframe` (optional): 1D (daily), 1W (weekly), 1M (monthly)
- `limit` (optional): Number of data points (default: 180)

Response:
```json
{
  "success": true,
  "data": [
    {
      "time": "2024-01-15",
      "open": 180.50,
      "high": 182.30,
      "low": 179.80,
      "close": 181.75,
      "volume": 52430000
    }
  ],
  "meta": {
    "ticker": "AAPL",
    "timeframe": "1D",
    "count": 180
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### Get Portfolio
```http
GET /api/portfolio
```

#### Get Backtests
```http
GET /api/backtests
```

### Testing the API

Using cURL:
```bash
# Health check
curl http://localhost:3000/api/health

# Get active LONG signals
curl http://localhost:3000/api/signals?status=ACTIVE&type=LONG

# Get AAPL stock data
curl http://localhost:3000/api/stocks/AAPL

# Get AAPL chart data (weekly)
curl http://localhost:3000/api/stocks/AAPL/data?timeframe=1W
```

For complete API documentation, see [TESTING.md](./TESTING.md).

## 📁 Project Structure

```
demo_financial_charts/
├── app/                          # Next.js App Router
│   ├── api/                      # API Routes (Mock Backend)
│   │   ├── backtests/
│   │   ├── health/
│   │   ├── portfolio/
│   │   ├── signals/
│   │   └── stocks/
│   ├── layout.tsx                # Root layout with providers
│   ├── page.tsx                  # Home page (Dashboard)
│   └── globals.css               # Global styles
├── components/                   # React Components
│   ├── charts/                   # Chart components
│   │   ├── CandlestickChart.tsx
│   │   ├── ChartControls.tsx
│   │   └── ChartControls.test.tsx
│   ├── dashboard/                # Dashboard components
│   │   └── Dashboard.tsx
│   ├── portfolio/                # Portfolio components
│   │   └── PortfolioSummary.tsx
│   └── signals/                  # Signal components
│       ├── SignalCard.tsx
│       ├── SignalCard.test.tsx
│       └── SignalList.tsx
├── lib/                          # Utilities and helpers
│   ├── api/                      # API client
│   │   └── client.ts
│   ├── mock/                     # Mock data
│   │   ├── mockData.ts
│   │   └── mockData.test.ts
│   ├── theme/                    # Mantine theme
│   │   └── theme.ts
│   ├── types/                    # TypeScript types
│   │   └── trading.ts
│   └── utils/                    # Utility functions
│       ├── formatters.ts
│       └── formatters.test.ts
├── public/                       # Static assets
│   ├── favicon.ico
│   └── images/
├── .dockerignore                 # Docker ignore patterns
├── .env.local                    # Local environment variables
├── .eslintrc.json                # ESLint configuration
├── .gitignore                    # Git ignore patterns
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose configuration
├── next.config.js                # Next.js configuration
├── package.json                  # Dependencies and scripts
├── README.md                     # This file
├── TESTING.md                    # Testing documentation
├── TECHNICAL_DEBT.md             # Technical debt tracking
├── tsconfig.json                 # TypeScript configuration
├── vitest.config.ts              # Vitest configuration
└── vitest.setup.ts               # Vitest setup
```

## 🔐 Environment Variables

### Development (.env.local)

```bash
# Optional - defaults to /api if not set
NEXT_PUBLIC_API_URL=http://localhost:3000/api

# Optional - for WebSocket connections
NEXT_PUBLIC_WS_URL=ws://localhost:3000

# Optional - enable debug mode
NEXT_PUBLIC_DEBUG=false
```

### Production (.env.production)

```bash
# Production API URL
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Production WebSocket URL
NEXT_PUBLIC_WS_URL=wss://ws.yourdomain.com

# Disable debug mode
NEXT_PUBLIC_DEBUG=false

# Node environment
NODE_ENV=production
```

### Environment Variable Naming

- Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser
- Variables without the prefix are server-side only
- Never commit `.env.local` or `.env.production` to version control

## 🎨 Customization

### Theme Configuration

Modify the theme in `lib/theme/theme.ts`:

```typescript
export const theme = createTheme({
  primaryColor: 'blue',
  defaultColorScheme: 'dark',
  // Add your customizations here
});
```

### Adding New Indicators

1. Update the indicator types in `lib/types/trading.ts`
2. Add calculation logic in `lib/utils/indicators.ts`
3. Update `components/charts/CandlestickChart.tsx` to render the indicator
4. Add toggle control in `components/charts/ChartControls.tsx`

### Connecting to Real Backend

Replace the mock API client in `lib/api/client.ts`:

```typescript
// Change from mock API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

// Add JWT authentication
const getAuthHeaders = () => ({
  'Authorization': `Bearer ${getToken()}`,
  'Content-Type': 'application/json',
});
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines

- Write TypeScript with strict type checking
- Add tests for new features (maintain >80% coverage)
- Follow the existing code style (ESLint configuration)
- Update documentation for significant changes
- Ensure all tests pass before submitting PR

### Code Style

```bash
# Run linter
npm run lint

# Run tests
npm test

# Check types
npx tsc --noEmit
```

## 📝 Documentation

- **[TESTING.md](./TESTING.md)** - Comprehensive testing guide
- **[TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md)** - Known technical debt and TODOs
- **[CLEANUP_SUMMARY.md](./CLEANUP_SUMMARY.md)** - Code cleanup history

## 🐛 Known Issues

See [TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md) for a complete list of known issues and planned improvements.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Development Team** - Initial work

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org/) - React framework
- [Mantine UI](https://mantine.dev/) - Component library
- [TradingView Lightweight Charts](https://www.tradingview.com/lightweight-charts/) - Charting library
- [TanStack Query](https://tanstack.com/query) - Data fetching
- [Vitest](https://vitest.dev/) - Testing framework

## 📞 Support

For support, please open an issue in the GitHub repository or contact the development team.

## 🚀 Roadmap

- [ ] WebSocket integration for real-time data
- [ ] JWT authentication implementation
- [ ] Advanced charting features (drawing tools)
- [ ] Mobile app (React Native)
- [ ] Trading bot integration
- [ ] Multi-language support
- [ ] Advanced backtesting features
- [ ] Social trading features

---

**Happy Trading! 📈**
