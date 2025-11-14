import dayjs from 'dayjs';

/**
 * Format number as currency
 */
export function formatCurrency(value: number, decimals: number = 2): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format number as percentage
 */
export function formatPercent(value: number, decimals: number = 2): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(decimals)}%`;
}

/**
 * Format large numbers (K, M, B, T)
 */
export function formatLargeNumber(value: number): string {
  const absValue = Math.abs(value);
  const sign = value < 0 ? '-' : '';

  if (absValue >= 1e12) {
    return `${sign}${(absValue / 1e12).toFixed(2)}T`;
  } else if (absValue >= 1e9) {
    return `${sign}${(absValue / 1e9).toFixed(2)}B`;
  } else if (absValue >= 1e6) {
    return `${sign}${(absValue / 1e6).toFixed(2)}M`;
  } else if (absValue >= 1e3) {
    return `${sign}${(absValue / 1e3).toFixed(2)}K`;
  }
  return `${sign}${absValue.toFixed(2)}`;
}

/**
 * Format date
 */
export function formatDate(date: string | Date, format: string = 'MMM DD, YYYY'): string {
  return dayjs(date).format(format);
}

/**
 * Format date relative to now
 */
export function formatRelativeDate(date: string | Date): string {
  const now = dayjs();
  const targetDate = dayjs(date);
  const diffDays = now.diff(targetDate, 'day');

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
  return `${Math.floor(diffDays / 365)} years ago`;
}

/**
 * Get color based on value (positive/negative)
 */
export function getValueColor(value: number): string {
  if (value > 0) return 'green';
  if (value < 0) return 'red';
  return 'gray';
}

/**
 * Format confidence as percentage with color
 */
export function formatConfidence(confidence: number): {
  text: string;
  color: string;
} {
  const color = confidence >= 75 ? 'green' : confidence >= 60 ? 'yellow' : 'orange';
  return {
    text: `${confidence.toFixed(0)}%`,
    color,
  };
}

/**
 * Format risk/reward ratio
 */
export function formatRiskReward(ratio: number): string {
  return `${ratio.toFixed(1)}:1`;
}
