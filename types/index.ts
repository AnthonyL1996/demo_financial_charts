// ============================================================================
// OHLCV Data Types
// ============================================================================

export interface OHLCVData {
  time: string | number; // ISO date string or timestamp
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// ============================================================================
// Signal Types
// ============================================================================

export type SignalType = 'LONG' | 'SHORT' | 'NEUTRAL';
export type SignalStatus = 'ACTIVE' | 'CLOSED' | 'EXPIRED';
export type TimeFrame = '1D' | '1W' | '1M' | '3M';

export interface Signal {
  id: string;
  ticker: string;
  companyName: string;
  type: SignalType;
  status: SignalStatus;
  confidence: number; // 0-100
  expectedReturn: number; // Percentage
  entryPrice: number;
  targetPrice: number;
  stopLoss: number;
  riskRewardRatio: number;
  generatedAt: string; // ISO date string
  expiresAt: string; // ISO date string
  closedAt?: string; // ISO date string
  timeframe: TimeFrame;

  // JDB Methodology Components
  reasoning: SignalReasoning;

  // Performance tracking (for closed signals)
  actualReturn?: number;
  exitPrice?: number;
}

export interface SignalReasoning {
  dominantMA: {
    period: 20 | 50 | 200;
    respected: boolean;
    distance: number; // Percentage from MA
  };
  bollingerBands: {
    position: 'LOWER' | 'MIDDLE' | 'UPPER' | 'BELOW' | 'ABOVE';
    bandwidth: number;
  };
  fibonacci: {
    level: 0 | 0.236 | 0.382 | 0.5 | 0.618 | 0.786 | 1;
    inRetracementZone: boolean;
  };
  rsiDivergence: {
    detected: boolean;
    type?: 'BULLISH' | 'BEARISH';
    strength?: number;
  };
  volumeConfirmation: boolean;
  trendStrength: 'STRONG' | 'MODERATE' | 'WEAK';
}

export interface SignalFilters {
  type?: SignalType[];
  status?: SignalStatus[];
  minConfidence?: number;
  timeframe?: TimeFrame[];
  ticker?: string;
  limit?: number;
}

// ============================================================================
// Stock Types
// ============================================================================

export interface Stock {
  ticker: string;
  companyName: string;
  sector?: string;
  industry?: string;
  currentPrice: number;
  priceChange: number; // Percentage
  volume: number;
  marketCap?: number;

  // Technical indicators
  technicals: StockTechnicals;

  // Active signals
  activeSignals: Signal[];
}

export interface StockTechnicals {
  ma20: number;
  ma50: number;
  ma200: number;
  rsi: number;
  bollingerUpper: number;
  bollingerMiddle: number;
  bollingerLower: number;
  atr: number; // Average True Range
  volume: number;
  volumeMA: number;
}

// ============================================================================
// Backtest Types
// ============================================================================

export interface Backtest {
  id: string;
  name: string;
  description: string;
  startDate: string;
  endDate: string;
  initialCapital: number;
  finalCapital: number;
  totalReturn: number; // Percentage

  // Performance metrics
  metrics: BacktestMetrics;

  // Trades
  trades: Trade[];

  // Equity curve
  equityCurve: EquityPoint[];

  // Monthly returns
  monthlyReturns: MonthlyReturn[];
}

export interface BacktestMetrics {
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  winRate: number; // Percentage
  profitFactor: number;
  sharpeRatio: number;
  sortinoRatio: number;
  maxDrawdown: number; // Percentage
  maxDrawdownDuration: number; // Days
  averageWin: number; // Percentage
  averageLoss: number; // Percentage
  expectancy: number;
  calmarRatio: number;
}

export interface Trade {
  id: string;
  ticker: string;
  type: 'LONG' | 'SHORT';
  entryDate: string;
  exitDate: string;
  entryPrice: number;
  exitPrice: number;
  shares: number;
  pnl: number;
  pnlPercent: number;
  holdingPeriod: number; // Days
  signal: Signal;
}

export interface EquityPoint {
  date: string;
  equity: number;
  drawdown: number; // Percentage
}

export interface MonthlyReturn {
  year: number;
  month: number;
  return: number; // Percentage
}

// ============================================================================
// Portfolio Types
// ============================================================================

export interface Portfolio {
  totalValue: number;
  cash: number;
  positions: Position[];
  totalPnL: number; // Dollar amount
  totalPnLPercent: number;
  dayPnL: number;
  dayPnLPercent: number;

  // Risk metrics
  riskMetrics: PortfolioRiskMetrics;
}

export interface Position {
  ticker: string;
  companyName: string;
  type: 'LONG' | 'SHORT';
  shares: number;
  entryPrice: number;
  currentPrice: number;
  marketValue: number;
  pnl: number;
  pnlPercent: number;
  weight: number; // Portfolio weight percentage
  signal: Signal;
}

export interface PortfolioRiskMetrics {
  exposure: number; // Percentage
  maxPositionSize: number; // Percentage
  correlation: number; // Average correlation between positions
  beta: number;
  sharpeRatio: number;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiError {
  message: string;
  code: string;
  details?: any;
}
