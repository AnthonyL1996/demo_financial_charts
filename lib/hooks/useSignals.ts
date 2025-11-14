import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { signalsApi } from '@/lib/api/endpoints';
import type { Signal, SignalFilters } from '@/types';

// Query keys
export const signalKeys = {
  all: ['signals'] as const,
  lists: () => [...signalKeys.all, 'list'] as const,
  list: (filters?: SignalFilters) => [...signalKeys.lists(), filters] as const,
  details: () => [...signalKeys.all, 'detail'] as const,
  detail: (id: string) => [...signalKeys.details(), id] as const,
  ticker: (ticker: string) => [...signalKeys.all, 'ticker', ticker] as const,
};

/**
 * Hook to fetch all signals with optional filters
 */
export function useSignals(filters?: SignalFilters) {
  return useQuery({
    queryKey: signalKeys.list(filters),
    queryFn: () => signalsApi.getSignals(filters),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

/**
 * Hook to fetch a specific signal by ID
 */
export function useSignal(id: string, enabled = true) {
  return useQuery({
    queryKey: signalKeys.detail(id),
    queryFn: () => signalsApi.getSignal(id),
    enabled: !!id && enabled,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch signals for a specific ticker
 */
export function useTickerSignals(ticker: string, enabled = true) {
  return useQuery({
    queryKey: signalKeys.ticker(ticker),
    queryFn: () => signalsApi.getSignalsByTicker(ticker),
    enabled: !!ticker && enabled,
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}
