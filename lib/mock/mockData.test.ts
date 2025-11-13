import { describe, it, expect } from 'vitest';
import { generateMockOHLCVData, mockSignals, mockStocks, mockPortfolio } from './mockData';

describe('mockData', () => {
  describe('generateMockOHLCVData', () => {
    it('should generate correct number of data points', () => {
      const data = generateMockOHLCVData('AAPL', 100);
      expect(data).toHaveLength(100);
    });

    it('should have all required OHLCV fields', () => {
      const data = generateMockOHLCVData('AAPL', 10);
      const firstPoint = data[0];

      expect(firstPoint).toHaveProperty('time');
      expect(firstPoint).toHaveProperty('open');
      expect(firstPoint).toHaveProperty('high');
      expect(firstPoint).toHaveProperty('low');
      expect(firstPoint).toHaveProperty('close');
      expect(firstPoint).toHaveProperty('volume');
    });

    it('should have high >= open, close and low <= open, close', () => {
      const data = generateMockOHLCVData('AAPL', 50);

      data.forEach((point) => {
        expect(point.high).toBeGreaterThanOrEqual(point.open);
        expect(point.high).toBeGreaterThanOrEqual(point.close);
        expect(point.low).toBeLessThanOrEqual(point.open);
        expect(point.low).toBeLessThanOrEqual(point.close);
      });
    });

    it('should have positive volume', () => {
      const data = generateMockOHLCVData('AAPL', 50);

      data.forEach((point) => {
        expect(point.volume).toBeGreaterThan(0);
      });
    });

    it('should have chronological dates', () => {
      const data = generateMockOHLCVData('AAPL', 10);

      for (let i = 1; i < data.length; i++) {
        const prevDate = new Date(data[i - 1].time);
        const currDate = new Date(data[i].time);
        expect(currDate.getTime()).toBeGreaterThan(prevDate.getTime());
      }
    });
  });

  describe('mockSignals', () => {
    it('should have at least one signal', () => {
      expect(mockSignals.length).toBeGreaterThan(0);
    });

    it('should have both LONG and SHORT signals', () => {
      const hasLong = mockSignals.some((s) => s.type === 'LONG');
      const hasShort = mockSignals.some((s) => s.type === 'SHORT');

      expect(hasLong).toBe(true);
      expect(hasShort).toBe(true);
    });

    it('should have valid confidence values (0-100)', () => {
      mockSignals.forEach((signal) => {
        expect(signal.confidence).toBeGreaterThanOrEqual(0);
        expect(signal.confidence).toBeLessThanOrEqual(100);
      });
    });

    it('should have positive risk/reward ratios', () => {
      mockSignals.forEach((signal) => {
        expect(signal.riskRewardRatio).toBeGreaterThan(0);
      });
    });
  });

  describe('mockStocks', () => {
    it('should have at least one stock', () => {
      expect(mockStocks.length).toBeGreaterThan(0);
    });

    it('should have valid ticker symbols', () => {
      mockStocks.forEach((stock) => {
        expect(stock.ticker).toMatch(/^[A-Z]+$/);
        expect(stock.ticker.length).toBeGreaterThan(0);
      });
    });

    it('should have positive current prices', () => {
      mockStocks.forEach((stock) => {
        expect(stock.currentPrice).toBeGreaterThan(0);
      });
    });

    it('should have technical indicators', () => {
      mockStocks.forEach((stock) => {
        expect(stock.technicals).toBeDefined();
        expect(stock.technicals.ma20).toBeGreaterThan(0);
        expect(stock.technicals.ma50).toBeGreaterThan(0);
        expect(stock.technicals.ma200).toBeGreaterThan(0);
        expect(stock.technicals.rsi).toBeGreaterThanOrEqual(0);
        expect(stock.technicals.rsi).toBeLessThanOrEqual(100);
      });
    });
  });

  describe('mockPortfolio', () => {
    it('should have valid total value', () => {
      expect(mockPortfolio.totalValue).toBeGreaterThan(0);
    });

    it('should have positions array', () => {
      expect(Array.isArray(mockPortfolio.positions)).toBe(true);
      expect(mockPortfolio.positions.length).toBeGreaterThan(0);
    });

    it('should have both LONG and SHORT positions', () => {
      const hasLong = mockPortfolio.positions.some((p) => p.type === 'LONG');
      const hasShort = mockPortfolio.positions.some((p) => p.type === 'SHORT');

      expect(hasLong).toBe(true);
      expect(hasShort).toBe(true);
    });

    it('should have risk metrics', () => {
      expect(mockPortfolio.riskMetrics).toBeDefined();
      expect(mockPortfolio.riskMetrics.sharpeRatio).toBeGreaterThan(0);
      expect(mockPortfolio.riskMetrics.exposure).toBeGreaterThanOrEqual(0);
      expect(mockPortfolio.riskMetrics.exposure).toBeLessThanOrEqual(100);
    });

    it('should have positions with valid market values', () => {
      mockPortfolio.positions.forEach((position) => {
        expect(position.marketValue).toBeGreaterThan(0);
        expect(position.shares).toBeGreaterThan(0);
        expect(position.entryPrice).toBeGreaterThan(0);
        expect(position.currentPrice).toBeGreaterThan(0);
      });
    });
  });
});
