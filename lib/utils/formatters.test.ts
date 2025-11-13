import { describe, it, expect } from 'vitest';
import {
  formatCurrency,
  formatPercent,
  formatLargeNumber,
  formatDate,
  getValueColor,
  formatConfidence,
  formatRiskReward,
} from './formatters';

describe('formatters', () => {
  describe('formatCurrency', () => {
    it('should format positive numbers as currency', () => {
      expect(formatCurrency(1234.56)).toBe('$1,234.56');
    });

    it('should format negative numbers as currency', () => {
      expect(formatCurrency(-1234.56)).toBe('-$1,234.56');
    });

    it('should respect decimal places', () => {
      expect(formatCurrency(1234.567, 0)).toBe('$1,235');
      expect(formatCurrency(1234.567, 3)).toBe('$1,234.567');
    });

    it('should handle zero', () => {
      expect(formatCurrency(0)).toBe('$0.00');
    });
  });

  describe('formatPercent', () => {
    it('should format positive percentages with + sign', () => {
      expect(formatPercent(5.25)).toBe('+5.25%');
    });

    it('should format negative percentages', () => {
      expect(formatPercent(-3.75)).toBe('-3.75%');
    });

    it('should format zero', () => {
      expect(formatPercent(0)).toBe('+0.00%');
    });

    it('should respect decimal places', () => {
      expect(formatPercent(5.256, 1)).toBe('+5.3%');
    });
  });

  describe('formatLargeNumber', () => {
    it('should format billions', () => {
      expect(formatLargeNumber(2500000000)).toBe('2.50B');
    });

    it('should format millions', () => {
      expect(formatLargeNumber(1500000)).toBe('1.50M');
    });

    it('should format thousands', () => {
      expect(formatLargeNumber(2500)).toBe('2.50K');
    });

    it('should format small numbers', () => {
      expect(formatLargeNumber(100)).toBe('100.00');
    });

    it('should handle negative numbers', () => {
      expect(formatLargeNumber(-1500000)).toBe('-1.50M');
    });

    it('should format trillions', () => {
      expect(formatLargeNumber(2500000000000)).toBe('2.50T');
    });
  });

  describe('formatDate', () => {
    it('should format date with default format', () => {
      const date = '2025-01-15';
      const result = formatDate(date);
      expect(result).toMatch(/Jan 15, 2025/);
    });

    it('should format date with custom format', () => {
      const date = '2025-01-15';
      const result = formatDate(date, 'YYYY-MM-DD');
      expect(result).toBe('2025-01-15');
    });
  });

  describe('getValueColor', () => {
    it('should return green for positive values', () => {
      expect(getValueColor(5.5)).toBe('green');
    });

    it('should return red for negative values', () => {
      expect(getValueColor(-3.2)).toBe('red');
    });

    it('should return gray for zero', () => {
      expect(getValueColor(0)).toBe('gray');
    });
  });

  describe('formatConfidence', () => {
    it('should return green for high confidence', () => {
      const result = formatConfidence(80);
      expect(result.text).toBe('80%');
      expect(result.color).toBe('green');
    });

    it('should return yellow for medium confidence', () => {
      const result = formatConfidence(65);
      expect(result.text).toBe('65%');
      expect(result.color).toBe('yellow');
    });

    it('should return orange for low confidence', () => {
      const result = formatConfidence(55);
      expect(result.text).toBe('55%');
      expect(result.color).toBe('orange');
    });
  });

  describe('formatRiskReward', () => {
    it('should format risk/reward ratio', () => {
      expect(formatRiskReward(2.5)).toBe('2.5:1');
    });

    it('should format with one decimal', () => {
      expect(formatRiskReward(1.87)).toBe('1.9:1');
    });
  });
});
