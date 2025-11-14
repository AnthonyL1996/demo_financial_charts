import { apiClient } from './client';
import type {
  Signal,
  SignalFilters,
  Stock,
  OHLCVData,
  Backtest,
  Portfolio,
  PaginatedResponse,
} from '@/types';

// ============================================================================
// Signals API
// ============================================================================

export const signalsApi = {
  /**
   * Get all signals with optional filters
   */
  getSignals: async (filters?: SignalFilters): Promise<Signal[]> => {
    return apiClient.get<Signal[]>('/signals', { params: filters });
  },

  /**
   * Get a specific signal by ID
   */
  getSignal: async (id: string): Promise<Signal> => {
    return apiClient.get<Signal>(`/signals/${id}`);
  },

  /**
   * Get signals for a specific ticker
   */
  getSignalsByTicker: async (ticker: string): Promise<Signal[]> => {
    return apiClient.get<Signal[]>(`/signals/ticker/${ticker}`);
  },
};

// ============================================================================
// Stocks API
// ============================================================================

export const stocksApi = {
  /**
   * Get all stocks
   */
  getStocks: async (params?: { search?: string; limit?: number }): Promise<Stock[]> => {
    return apiClient.get<Stock[]>('/stocks', { params });
  },

  /**
   * Get stock details
   */
  getStock: async (ticker: string): Promise<Stock> => {
    return apiClient.get<Stock>(`/stocks/${ticker}`);
  },

  /**
   * Get stock OHLCV data
   */
  getStockData: async (
    ticker: string,
    params?: {
      timeframe?: '1D' | '1W' | '1M';
      start?: string;
      end?: string;
    }
  ): Promise<OHLCVData[]> => {
    return apiClient.get<OHLCVData[]>(`/stocks/${ticker}/data`, { params });
  },

  /**
   * Get stock technical indicators
   */
  getTechnicals: async (ticker: string): Promise<any> => {
    return apiClient.get(`/stocks/${ticker}/technicals`);
  },
};

// ============================================================================
// Backtests API
// ============================================================================

export const backtestsApi = {
  /**
   * Get all backtests
   */
  getBacktests: async (): Promise<Backtest[]> => {
    return apiClient.get<Backtest[]>('/backtests');
  },

  /**
   * Get backtest by ID
   */
  getBacktest: async (id: string): Promise<Backtest> => {
    return apiClient.get<Backtest>(`/backtests/${id}`);
  },

  /**
   * Create new backtest
   */
  createBacktest: async (params: {
    name: string;
    description?: string;
    startDate: string;
    endDate: string;
    initialCapital: number;
  }): Promise<Backtest> => {
    return apiClient.post<Backtest>('/backtests', params);
  },
};

// ============================================================================
// Portfolio API
// ============================================================================

export const portfolioApi = {
  /**
   * Get current portfolio
   */
  getPortfolio: async (): Promise<Portfolio> => {
    return apiClient.get<Portfolio>('/portfolio');
  },

  /**
   * Get portfolio history
   */
  getPortfolioHistory: async (params?: {
    startDate?: string;
    endDate?: string;
  }): Promise<any[]> => {
    return apiClient.get('/portfolio/history', { params });
  },
};

// ============================================================================
// Authentication API (for future use)
// ============================================================================

export const authApi = {
  /**
   * Login
   */
  login: async (credentials: { username: string; password: string }): Promise<{ token: string }> => {
    return apiClient.post<{ token: string }>('/auth/login', credentials);
  },

  /**
   * Logout
   */
  logout: async (): Promise<void> => {
    return apiClient.post<void>('/auth/logout');
  },

  /**
   * Refresh token
   */
  refresh: async (): Promise<{ token: string }> => {
    return apiClient.post<{ token: string }>('/auth/refresh');
  },
};
