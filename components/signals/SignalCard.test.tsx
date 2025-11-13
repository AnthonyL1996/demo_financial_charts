import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SignalCard } from './SignalCard';
import { MantineProvider } from '@mantine/core';
import type { Signal } from '@/types';

// Wrapper for Mantine components
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <MantineProvider>{children}</MantineProvider>
);

const mockLongSignal: Signal = {
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
};

const mockShortSignal: Signal = {
  ...mockLongSignal,
  id: '2',
  ticker: 'TSLA',
  companyName: 'Tesla, Inc.',
  type: 'SHORT',
  confidence: 82,
  expectedReturn: -15.8,
};

describe('SignalCard', () => {
  it('should render signal ticker and company name', () => {
    render(<SignalCard signal={mockLongSignal} />, { wrapper });

    expect(screen.getByText('AAPL')).toBeInTheDocument();
    expect(screen.getByText('Apple Inc.')).toBeInTheDocument();
  });

  it('should render LONG badge for long signals', () => {
    render(<SignalCard signal={mockLongSignal} />, { wrapper });

    expect(screen.getByText('LONG')).toBeInTheDocument();
  });

  it('should render SHORT badge for short signals', () => {
    render(<SignalCard signal={mockShortSignal} />, { wrapper });

    expect(screen.getByText('SHORT')).toBeInTheDocument();
  });

  it('should display confidence percentage', () => {
    render(<SignalCard signal={mockLongSignal} />, { wrapper });

    expect(screen.getByText('78%')).toBeInTheDocument();
  });

  it('should display price levels', () => {
    render(<SignalCard signal={mockLongSignal} />, { wrapper });

    expect(screen.getByText('Entry')).toBeInTheDocument();
    expect(screen.getByText('Target')).toBeInTheDocument();
    expect(screen.getByText('Stop Loss')).toBeInTheDocument();
  });

  it('should display risk/reward ratio', () => {
    render(<SignalCard signal={mockLongSignal} />, { wrapper });

    expect(screen.getByText(/2.1:1/)).toBeInTheDocument();
  });

  it('should display reasoning badges', () => {
    render(<SignalCard signal={mockLongSignal} />, { wrapper });

    expect(screen.getByText('MA50 Bounce')).toBeInTheDocument();
    expect(screen.getByText('Lower BB')).toBeInTheDocument();
    expect(screen.getByText('RSI Divergence')).toBeInTheDocument();
  });
});
