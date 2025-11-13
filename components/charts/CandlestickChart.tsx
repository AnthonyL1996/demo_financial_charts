'use client';

import { useEffect, useRef } from 'react';
import { createChart, IChartApi, ColorType, CrosshairMode } from 'lightweight-charts';
import { Paper, Group, Button, Stack, Text } from '@mantine/core';
import { IconZoomIn, IconZoomOut, IconZoomCancel } from '@tabler/icons-react';
import type { OHLCVData, Signal } from '@/types';
import type { IndicatorSettings } from './ChartControls';

interface CandlestickChartProps {
  data: OHLCVData[];
  ticker?: string;
  height?: number;
  indicators: IndicatorSettings;
  signals?: Signal[];
}

export function CandlestickChart({
  data,
  ticker,
  height = 500,
  indicators,
  signals = [],
}: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current || data.length === 0) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      layout: {
        background: { type: ColorType.Solid, color: '#1A1B1E' },
        textColor: '#C1C2C5',
      },
      grid: {
        vertLines: { color: indicators.grid ? '#2C2E33' : 'transparent' },
        horzLines: { color: indicators.grid ? '#2C2E33' : 'transparent' },
      },
      crosshair: {
        mode: indicators.crosshair ? CrosshairMode.Normal : CrosshairMode.Hidden,
        vertLine: {
          color: '#758BFD',
          width: 1,
          style: 2,
          labelBackgroundColor: '#4C6EF5',
        },
        horzLine: {
          color: '#758BFD',
          width: 1,
          style: 2,
          labelBackgroundColor: '#4C6EF5',
        },
      },
      rightPriceScale: {
        borderColor: '#2C2E33',
      },
      timeScale: {
        borderColor: '#2C2E33',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // Convert data to lightweight-charts format
    const chartData = data.map((d) => ({
      time: d.time as string,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26A69A',
      downColor: '#EF5350',
      borderVisible: false,
      wickUpColor: '#26A69A',
      wickDownColor: '#EF5350',
    });

    candlestickSeries.setData(chartData);

    // Add volume histogram if enabled
    if (indicators.volume) {
      const volumeSeries = chart.addHistogramSeries({
        color: '#26a69a',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: 'volume',
      });

      chart.priceScale('volume').applyOptions({
        scaleMargins: {
          top: 0.8,
          bottom: 0,
        },
      });

      const volumeData = data.map((d) => ({
        time: d.time as string,
        value: d.volume,
        color: d.close >= d.open ? '#26A69A55' : '#EF535055',
      }));

      volumeSeries.setData(volumeData);
    }

    // Add Simple Moving Averages
    if (indicators.ma20) {
      const ma20Series = chart.addLineSeries({
        color: '#4C6EF5',
        lineWidth: 2,
        title: 'MA 20',
      });
      ma20Series.setData(calculateSMA(chartData, 20));
    }

    if (indicators.ma50) {
      const ma50Series = chart.addLineSeries({
        color: '#FFA500',
        lineWidth: 2,
        title: 'MA 50',
      });
      ma50Series.setData(calculateSMA(chartData, 50));
    }

    if (indicators.ma200) {
      const ma200Series = chart.addLineSeries({
        color: '#F44336',
        lineWidth: 2,
        title: 'MA 200',
      });
      ma200Series.setData(calculateSMA(chartData, 200));
    }

    // Add Exponential Moving Averages
    if (indicators.ema12) {
      const ema12Series = chart.addLineSeries({
        color: '#12B886',
        lineWidth: 2,
        title: 'EMA 12',
      });
      ema12Series.setData(calculateEMA(chartData, 12));
    }

    if (indicators.ema26) {
      const ema26Series = chart.addLineSeries({
        color: '#15AABF',
        lineWidth: 2,
        title: 'EMA 26',
      });
      ema26Series.setData(calculateEMA(chartData, 26));
    }

    // Add Bollinger Bands
    if (indicators.bollingerBands) {
      const bollingerData = calculateBollingerBands(chartData, 20, 2);

      // Upper band
      const upperBandSeries = chart.addLineSeries({
        color: '#9775FA',
        lineWidth: 1,
        lineStyle: 2, // Dashed
        title: 'BB Upper',
      });
      upperBandSeries.setData(bollingerData.upper);

      // Middle band (same as MA20 but shown separately if MA20 is off)
      if (!indicators.ma20) {
        const middleBandSeries = chart.addLineSeries({
          color: '#9775FA',
          lineWidth: 1,
          title: 'BB Middle',
        });
        middleBandSeries.setData(bollingerData.middle);
      }

      // Lower band
      const lowerBandSeries = chart.addLineSeries({
        color: '#9775FA',
        lineWidth: 1,
        lineStyle: 2, // Dashed
        title: 'BB Lower',
      });
      lowerBandSeries.setData(bollingerData.lower);
    }

    // Add signal markers
    if (signals.length > 0) {
      const markers = signals.map((signal) => ({
        time: new Date(signal.generatedAt).toISOString().split('T')[0] as string,
        position: (signal.type === 'LONG' ? 'belowBar' : 'aboveBar') as 'belowBar' | 'aboveBar',
        color: signal.type === 'LONG' ? '#26A69A' : '#EF5350',
        shape: (signal.type === 'LONG' ? 'arrowUp' : 'arrowDown') as 'arrowUp' | 'arrowDown',
        text: `${signal.type} (${signal.confidence}%)`,
      }));
      candlestickSeries.setMarkers(markers);
    }

    // Fit content
    chart.timeScale().fitContent();

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data, height, indicators, signals]);

  const handleZoomIn = () => {
    if (chartRef.current) {
      const timeScale = chartRef.current.timeScale();
      const { from, to } = timeScale.getVisibleRange() || {};
      if (from && to) {
        const diff = (to as number) - (from as number);
        const newFrom = (from as number) + diff * 0.1;
        const newTo = (to as number) - diff * 0.1;
        timeScale.setVisibleRange({ from: newFrom as any, to: newTo as any });
      }
    }
  };

  const handleZoomOut = () => {
    if (chartRef.current) {
      const timeScale = chartRef.current.timeScale();
      const { from, to } = timeScale.getVisibleRange() || {};
      if (from && to) {
        const diff = (to as number) - (from as number);
        const newFrom = (from as number) - diff * 0.1;
        const newTo = (to as number) + diff * 0.1;
        timeScale.setVisibleRange({ from: newFrom as any, to: newTo as any });
      }
    }
  };

  const handleResetZoom = () => {
    if (chartRef.current) {
      chartRef.current.timeScale().fitContent();
    }
  };

  return (
    <Stack gap="xs">
      {ticker && (
        <Group justify="space-between" align="center">
          <Text size="lg" fw={700}>
            {ticker}
          </Text>
          <Group gap="xs">
            <Button
              size="xs"
              variant="light"
              leftSection={<IconZoomIn size={16} />}
              onClick={handleZoomIn}
            >
              Zoom In
            </Button>
            <Button
              size="xs"
              variant="light"
              leftSection={<IconZoomOut size={16} />}
              onClick={handleZoomOut}
            >
              Zoom Out
            </Button>
            <Button
              size="xs"
              variant="light"
              leftSection={<IconZoomCancel size={16} />}
              onClick={handleResetZoom}
            >
              Reset
            </Button>
          </Group>
        </Group>
      )}
      <Paper p={0} withBorder>
        <div ref={chartContainerRef} />
      </Paper>
    </Stack>
  );
}

// ============================================================================
// Helper Functions - Technical Indicators
// ============================================================================

/**
 * Calculate Simple Moving Average (SMA)
 */
function calculateSMA(data: any[], period: number): any[] {
  const result: any[] = [];

  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      continue;
    }

    let sum = 0;
    for (let j = 0; j < period; j++) {
      sum += data[i - j].close;
    }

    result.push({
      time: data[i].time,
      value: sum / period,
    });
  }

  return result;
}

/**
 * Calculate Exponential Moving Average (EMA)
 */
function calculateEMA(data: any[], period: number): any[] {
  const result: any[] = [];
  const multiplier = 2 / (period + 1);

  // First EMA value is SMA
  let ema = 0;
  for (let i = 0; i < period; i++) {
    ema += data[i].close;
  }
  ema = ema / period;

  result.push({
    time: data[period - 1].time,
    value: ema,
  });

  // Calculate EMA for remaining values
  for (let i = period; i < data.length; i++) {
    ema = (data[i].close - ema) * multiplier + ema;
    result.push({
      time: data[i].time,
      value: ema,
    });
  }

  return result;
}

/**
 * Calculate Bollinger Bands
 */
function calculateBollingerBands(
  data: any[],
  period: number,
  stdDev: number
): {
  upper: any[];
  middle: any[];
  lower: any[];
} {
  const upper: any[] = [];
  const middle: any[] = [];
  const lower: any[] = [];

  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      continue;
    }

    // Calculate SMA (middle band)
    let sum = 0;
    for (let j = 0; j < period; j++) {
      sum += data[i - j].close;
    }
    const sma = sum / period;

    // Calculate standard deviation
    let squaredDiffSum = 0;
    for (let j = 0; j < period; j++) {
      const diff = data[i - j].close - sma;
      squaredDiffSum += diff * diff;
    }
    const standardDeviation = Math.sqrt(squaredDiffSum / period);

    // Calculate bands
    const upperBand = sma + stdDev * standardDeviation;
    const lowerBand = sma - stdDev * standardDeviation;

    upper.push({
      time: data[i].time,
      value: upperBand,
    });

    middle.push({
      time: data[i].time,
      value: sma,
    });

    lower.push({
      time: data[i].time,
      value: lowerBand,
    });
  }

  return { upper, middle, lower };
}
