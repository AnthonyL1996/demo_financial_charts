import type { Signal, Stock, OHLCVData, Portfolio, Backtest } from '@/types';

// ============================================================================
// Mock Signals
// ============================================================================

export const mockSignals: Signal[] = [
  {
    id: '1',
    ticker: 'AAPL',
    companyName: 'Apple Inc.',
    type: 'LONG',
    status: 'ACTIVE',
    confidence: 78,
    expectedReturn: 12.5,
    entryPrice: 175.23,
    targetPrice: 197.13,
    stopLoss: 162.35,
    riskRewardRatio: 2.1,
    generatedAt: '2025-11-10T14:30:00Z',
    expiresAt: '2025-12-10T14:30:00Z',
    timeframe: '1W',
    reasoning: {
      dominantMA: {
        period: 50,
        respected: true,
        distance: -2.3,
      },
      bollingerBands: {
        position: 'LOWER',
        bandwidth: 0.12,
      },
      fibonacci: {
        level: 0.618,
        inRetracementZone: true,
      },
      rsiDivergence: {
        detected: true,
        type: 'BULLISH',
        strength: 0.75,
      },
      volumeConfirmation: true,
      trendStrength: 'STRONG',
    },
  },
  {
    id: '2',
    ticker: 'TSLA',
    companyName: 'Tesla, Inc.',
    type: 'SHORT',
    status: 'ACTIVE',
    confidence: 82,
    expectedReturn: -15.8,
    entryPrice: 242.75,
    targetPrice: 204.51,
    stopLoss: 254.89,
    riskRewardRatio: 3.2,
    generatedAt: '2025-11-11T09:15:00Z',
    expiresAt: '2025-12-11T09:15:00Z',
    timeframe: '1W',
    reasoning: {
      dominantMA: {
        period: 200,
        respected: true,
        distance: 8.5,
      },
      bollingerBands: {
        position: 'UPPER',
        bandwidth: 0.18,
      },
      fibonacci: {
        level: 0.618,
        inRetracementZone: true,
      },
      rsiDivergence: {
        detected: true,
        type: 'BEARISH',
        strength: 0.85,
      },
      volumeConfirmation: true,
      trendStrength: 'MODERATE',
    },
  },
  {
    id: '3',
    ticker: 'MSFT',
    companyName: 'Microsoft Corporation',
    type: 'LONG',
    status: 'ACTIVE',
    confidence: 72,
    expectedReturn: 10.2,
    entryPrice: 368.45,
    targetPrice: 406.10,
    stopLoss: 340.82,
    riskRewardRatio: 1.9,
    generatedAt: '2025-11-12T11:00:00Z',
    expiresAt: '2025-12-12T11:00:00Z',
    timeframe: '1W',
    reasoning: {
      dominantMA: {
        period: 20,
        respected: true,
        distance: -1.8,
      },
      bollingerBands: {
        position: 'LOWER',
        bandwidth: 0.09,
      },
      fibonacci: {
        level: 0.5,
        inRetracementZone: true,
      },
      rsiDivergence: {
        detected: false,
      },
      volumeConfirmation: true,
      trendStrength: 'STRONG',
    },
  },
  {
    id: '4',
    ticker: 'NVDA',
    companyName: 'NVIDIA Corporation',
    type: 'LONG',
    status: 'CLOSED',
    confidence: 85,
    expectedReturn: 18.5,
    entryPrice: 495.20,
    targetPrice: 586.87,
    stopLoss: 458.56,
    riskRewardRatio: 2.5,
    generatedAt: '2025-10-15T10:30:00Z',
    expiresAt: '2025-11-15T10:30:00Z',
    closedAt: '2025-11-08T15:45:00Z',
    timeframe: '1W',
    actualReturn: 16.2,
    exitPrice: 575.41,
    reasoning: {
      dominantMA: {
        period: 50,
        respected: true,
        distance: -3.2,
      },
      bollingerBands: {
        position: 'LOWER',
        bandwidth: 0.15,
      },
      fibonacci: {
        level: 0.618,
        inRetracementZone: true,
      },
      rsiDivergence: {
        detected: true,
        type: 'BULLISH',
        strength: 0.9,
      },
      volumeConfirmation: true,
      trendStrength: 'STRONG',
    },
  },
];

// ============================================================================
// Mock Stocks
// ============================================================================

export const mockStocks: Stock[] = [
  {
    ticker: 'AAPL',
    companyName: 'Apple Inc.',
    sector: 'Technology',
    industry: 'Consumer Electronics',
    currentPrice: 175.23,
    priceChange: -2.34,
    volume: 52341567,
    marketCap: 2750000000000,
    technicals: {
      ma20: 178.45,
      ma50: 172.89,
      ma200: 165.32,
      rsi: 42.5,
      bollingerUpper: 185.67,
      bollingerMiddle: 178.45,
      bollingerLower: 171.23,
      atr: 3.45,
      volume: 52341567,
      volumeMA: 48567123,
    },
    activeSignals: [mockSignals[0]],
  },
  {
    ticker: 'TSLA',
    companyName: 'Tesla, Inc.',
    sector: 'Automotive',
    industry: 'Electric Vehicles',
    currentPrice: 242.75,
    priceChange: 5.67,
    volume: 98765432,
    marketCap: 770000000000,
    technicals: {
      ma20: 235.67,
      ma50: 228.45,
      ma200: 215.89,
      rsi: 68.5,
      bollingerUpper: 255.34,
      bollingerMiddle: 235.67,
      bollingerLower: 216.00,
      atr: 8.92,
      volume: 98765432,
      volumeMA: 85432109,
    },
    activeSignals: [mockSignals[1]],
  },
  {
    ticker: 'MSFT',
    companyName: 'Microsoft Corporation',
    sector: 'Technology',
    industry: 'Software',
    currentPrice: 368.45,
    priceChange: -1.23,
    volume: 34567890,
    marketCap: 2800000000000,
    technicals: {
      ma20: 372.34,
      ma50: 365.78,
      ma200: 352.45,
      rsi: 45.2,
      bollingerUpper: 385.67,
      bollingerMiddle: 372.34,
      bollingerLower: 359.01,
      atr: 4.56,
      volume: 34567890,
      volumeMA: 31234567,
    },
    activeSignals: [mockSignals[2]],
  },
];

// ============================================================================
// Mock OHLCV Data (Sample for AAPL - Weekly)
// ============================================================================

export const generateMockOHLCVData = (ticker: string, days: number = 365): OHLCVData[] => {
  const data: OHLCVData[] = [];
  let basePrice = 150;
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  for (let i = 0; i < days; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);

    // Random walk with slight upward trend
    const change = (Math.random() - 0.48) * 5;
    basePrice = Math.max(100, basePrice + change);

    const open = basePrice;
    const close = basePrice + (Math.random() - 0.5) * 4;
    const high = Math.max(open, close) + Math.random() * 3;
    const low = Math.min(open, close) - Math.random() * 3;
    const volume = Math.floor(40000000 + Math.random() * 40000000);

    data.push({
      time: date.toISOString().split('T')[0],
      open: Number(open.toFixed(2)),
      high: Number(high.toFixed(2)),
      low: Number(low.toFixed(2)),
      close: Number(close.toFixed(2)),
      volume,
    });
  }

  return data;
};

// ============================================================================
// Mock Portfolio
// ============================================================================

export const mockPortfolio: Portfolio = {
  totalValue: 125450.75,
  cash: 45230.25,
  positions: [
    {
      ticker: 'AAPL',
      companyName: 'Apple Inc.',
      type: 'LONG',
      shares: 100,
      entryPrice: 175.23,
      currentPrice: 178.45,
      marketValue: 17845.00,
      pnl: 322.00,
      pnlPercent: 1.84,
      weight: 14.22,
      signal: mockSignals[0],
    },
    {
      ticker: 'MSFT',
      companyName: 'Microsoft Corporation',
      type: 'LONG',
      shares: 50,
      entryPrice: 368.45,
      currentPrice: 372.15,
      marketValue: 18607.50,
      pnl: 185.00,
      pnlPercent: 1.00,
      weight: 14.83,
      signal: mockSignals[2],
    },
    {
      ticker: 'TSLA',
      companyName: 'Tesla, Inc.',
      type: 'SHORT',
      shares: 150,
      entryPrice: 242.75,
      currentPrice: 238.90,
      marketValue: 35835.00,
      pnl: 577.50,
      pnlPercent: 1.59,
      weight: 28.56,
      signal: mockSignals[1],
    },
  ],
  totalPnL: 1084.50,
  totalPnLPercent: 0.87,
  dayPnL: 234.75,
  dayPnLPercent: 0.19,
  riskMetrics: {
    exposure: 57.68,
    maxPositionSize: 28.56,
    correlation: 0.42,
    beta: 1.15,
    sharpeRatio: 1.85,
  },
};

// ============================================================================
// Mock Backtest
// ============================================================================

export const mockBacktest: Backtest = {
  id: '1',
  name: 'JDB Strategy Backtest - 2023',
  description: 'Full JDB methodology backtest on S&P 500 stocks',
  startDate: '2023-01-01',
  endDate: '2023-12-31',
  initialCapital: 100000,
  finalCapital: 158750,
  totalReturn: 58.75,
  metrics: {
    totalTrades: 145,
    winningTrades: 78,
    losingTrades: 67,
    winRate: 53.79,
    profitFactor: 1.85,
    sharpeRatio: 1.92,
    sortinoRatio: 2.45,
    maxDrawdown: -18.5,
    maxDrawdownDuration: 42,
    averageWin: 8.5,
    averageLoss: -4.2,
    expectancy: 2.8,
    calmarRatio: 3.17,
  },
  trades: [],
  equityCurve: [],
  monthlyReturns: [
    { year: 2023, month: 1, return: 4.2 },
    { year: 2023, month: 2, return: 2.8 },
    { year: 2023, month: 3, return: -1.5 },
    { year: 2023, month: 4, return: 5.6 },
    { year: 2023, month: 5, return: 3.2 },
    { year: 2023, month: 6, return: 4.8 },
    { year: 2023, month: 7, return: 6.1 },
    { year: 2023, month: 8, return: -3.2 },
    { year: 2023, month: 9, return: 2.5 },
    { year: 2023, month: 10, return: 7.8 },
    { year: 2023, month: 11, return: 4.3 },
    { year: 2023, month: 12, return: 5.9 },
  ],
};
