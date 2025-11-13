# JDB Trading System - Frontend

A modern quantitative trading signal system built with Next.js, TypeScript, Mantine UI, and Lightweight Charts. This frontend application displays trading signals based on the JDB Trading methodology.

## 🚀 Features

- **Real-time Trading Signals**: Display LONG/SHORT signals with confidence levels
- **Interactive Charts**: Professional-grade candlestick charts with:
  - Moving Averages (MA 20, 50, 200)
  - Volume histograms
  - Bollinger Bands
  - Fibonacci retracements
  - Signal markers
- **Portfolio Tracking**: Monitor active positions and P&L
- **Dark Mode**: Beautiful dark theme optimized for trading
- **Responsive Design**: Works seamlessly on desktop and mobile
- **JDB Methodology**: Based on:
  - Dominant Moving Average identification
  - Bollinger Bands positioning
  - Fibonacci retracement zones (50-61.8%)
  - RSI divergence detection

## 🛠️ Technology Stack

### Core
- **Next.js 14.2** - React framework with App Router
- **TypeScript 5.3** - Type-safe JavaScript
- **React 18.2** - UI library

### UI Components
- **Mantine UI 7.5** - Comprehensive component library
  - @mantine/core - Core components
  - @mantine/hooks - React hooks
  - @mantine/charts - Chart components
  - @mantine/notifications - Toast notifications
  - @mantine/modals - Modal dialogs
- **Tabler Icons** - Icon set

### Data Visualization
- **Lightweight Charts 4.1** - High-performance financial charts
- **TanStack Query 5.x** - Data fetching and caching
- **TanStack Table 8.x** - Table management

### Forms & Validation
- **React Hook Form 7.x** - Form management
- **Zod 3.x** - Schema validation

### State Management
- **Zustand 4.5** - Lightweight state management
- **Axios 1.6** - HTTP client

### Utilities
- **Day.js** - Date manipulation

## 📁 Project Structure

```
.
├── app/
│   ├── layout.tsx              # Root layout with providers
│   ├── page.tsx                # Dashboard home page
│   ├── signals/                # Signals pages
│   ├── stocks/                 # Stocks pages
│   ├── backtests/              # Backtesting pages
│   └── portfolio/              # Portfolio pages
│
├── components/
│   ├── charts/
│   │   └── CandlestickChart.tsx    # Main chart component
│   ├── signals/
│   │   └── SignalCard.tsx          # Signal display card
│   └── ...
│
├── lib/
│   ├── api/
│   │   ├── client.ts           # API client with JWT support
│   │   └── endpoints.ts        # API endpoint functions
│   ├── hooks/
│   │   ├── useSignals.ts       # Signal data hooks
│   │   └── useStocks.ts        # Stock data hooks
│   ├── mock/
│   │   └── mockData.ts         # Mock data for development
│   ├── utils/
│   │   └── formatters.ts       # Utility functions
│   └── theme.ts                # Mantine theme configuration
│
├── types/
│   └── index.ts                # TypeScript type definitions
│
└── public/                     # Static assets
```

## 🚦 Getting Started

### Prerequisites

- Node.js 18.17 or higher
- npm, yarn, or pnpm

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd demo_financial_charts
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env.local
```

Edit `.env.local` and configure:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building for Production

```bash
npm run build
npm start
```

### Other Commands

```bash
npm run lint        # Run ESLint
npm run type-check  # Run TypeScript compiler check
npm run format      # Format code with Prettier
```

## 🎨 Theme Customization

The application uses a custom blue color scheme with dark mode as default. You can customize the theme in `lib/theme.ts`:

```typescript
export const theme = createTheme({
  primaryColor: 'blue',
  defaultRadius: 'md',
  // ... customize more
});
```

## 🔌 API Integration

The application is ready to connect to a backend API. The API client is configured with:

- **JWT Authentication**: Automatic token management
- **Request Interceptors**: Add auth headers
- **Response Interceptors**: Handle errors and token refresh
- **Type Safety**: Full TypeScript support

### Connecting to Your Backend

1. Update the API base URL in `.env.local`
2. The API client expects responses in this format:
```typescript
{
  success: boolean;
  data: T;
  message?: string;
  timestamp: string;
}
```

3. Replace mock data usage with actual API calls:
```typescript
// Instead of:
import { mockSignals } from '@/lib/mock/mockData';

// Use:
import { useSignals } from '@/lib/hooks/useSignals';
const { data: signals } = useSignals();
```

## 📊 Mock Data

The application includes comprehensive mock data for development:

- **Signals**: Sample LONG/SHORT signals with JDB reasoning
- **Stocks**: Stock data with technical indicators
- **Portfolio**: Positions and P&L
- **OHLCV Data**: Historical price data generator
- **Backtests**: Performance metrics and trade history

Mock data is located in `lib/mock/mockData.ts`.

## 🎯 JDB Trading Methodology

This system implements the "Kruispunt" (Crossroads) methodology:

### Four Key Components:

1. **Dominant Moving Average**
   - Identifies which MA (20, 50, 200) a stock respects most
   - Looks for bounces/breaks at these levels

2. **Bollinger Bands**
   - Entry timing tool within trends
   - Buy at lower band in uptrends
   - Sell at upper band in downtrends

3. **Fibonacci Retracement (50-61.8%)**
   - Identifies trend reversals/continuations
   - Key zone for bearish setups after corrective rallies

4. **RSI Divergence**
   - Confirmatory signal only
   - Bullish: Price lower lows, RSI higher lows
   - Bearish: Price higher highs, RSI lower highs

### Risk Philosophy
- 2:1 risk/reward ratio minimum
- Target: +15% profit before -7.5% stop loss
- "Wrong turn at crossroads = small loss, never Big Loss"

## 🔐 Authentication

JWT authentication is prepared but not implemented. To enable:

1. Backend should return JWT token on login
2. Token is automatically stored in localStorage
3. All API requests include `Authorization: Bearer <token>` header
4. Token refresh is handled automatically

## 📱 Responsive Design

The application is fully responsive with breakpoints:
- **xs**: 36em (576px)
- **sm**: 48em (768px)
- **md**: 62em (992px)
- **lg**: 75em (1200px)
- **xl**: 88em (1408px)

## 🧪 Testing

Testing infrastructure is set up but tests need to be written. The stack includes:
- Vitest for unit tests
- Testing Library for component tests
- Playwright for E2E tests (optional)

## 📈 Performance

- **Code Splitting**: Automatic with Next.js
- **Image Optimization**: Next.js Image component
- **Lazy Loading**: React.lazy for heavy components
- **Memoization**: React.memo for expensive components
- **Query Caching**: TanStack Query for efficient data fetching

## 🚀 Deployment

### Vercel (Recommended)
```bash
vercel deploy
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

### Environment Variables
Make sure to set these in production:
- `NEXT_PUBLIC_API_BASE_URL`
- Any other API keys or secrets

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the ISC License.

## 🙏 Acknowledgments

- **JDB Trading** (@JDB_trading) for the trading methodology
- **TradingView** for the lightweight-charts library
- **Mantine** for the excellent UI components

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation
- Review the mock data examples

---

**Built with ❤️ for quantitative traders**
