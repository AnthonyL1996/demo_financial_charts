import { useQuery } from '@tanstack/react-query';
import { stocksApi } from '@/lib/api/endpoints';
import type { Stock, OHLCVData } from '@/types';

// Query keys
export const stockKeys = {
  all: ['stocks'] as const,
  lists: () => [...stockKeys.all, 'list'] as const,
  list: (params?: { search?: string; limit?: number }) => [...stockKeys.lists(), params] as const,
  details: () => [...stockKeys.all, 'detail'] as const,
  detail: (ticker: string) => [...stockKeys.details(), ticker] as const,
  data: (ticker: string, params?: any) => [...stockKeys.all, 'data', ticker, params] as const,
  technicals: (ticker: string) => [...stockKeys.all, 'technicals', ticker] as const,
};

/**
 * Hook to fetch all stocks
 */
export function useStocks(params?: { search?: string; limit?: number }) {
  return useQuery({
    queryKey: stockKeys.list(params),
    queryFn: () => stocksApi.getStocks(params),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch stock details
 */
export function useStock(ticker: string, enabled = true) {
  return useQuery({
    queryKey: stockKeys.detail(ticker),
    queryFn: () => stocksApi.getStock(ticker),
    enabled: !!ticker && enabled,
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

/**
 * Hook to fetch stock OHLCV data
 */
export function useStockData(
  ticker: string,
  params?: {
    timeframe?: '1D' | '1W' | '1M';
    start?: string;
    end?: string;
  },
  enabled = true
) {
  return useQuery({
    queryKey: stockKeys.data(ticker, params),
    queryFn: () => stocksApi.getStockData(ticker, params),
    enabled: !!ticker && enabled,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch stock technical indicators
 */
export function useStockTechnicals(ticker: string, enabled = true) {
  return useQuery({
    queryKey: stockKeys.technicals(ticker),
    queryFn: () => stocksApi.getTechnicals(ticker),
    enabled: !!ticker && enabled,
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}
