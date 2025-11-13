'use client';

import { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ISeriesApi, ColorType } from 'lightweight-charts';
import { Paper, Group, Button, Stack, Text } from '@mantine/core';
import { IconZoomIn, IconZoomOut, IconZoomCancel } from '@tabler/icons-react';
import type { OHLCVData, Signal } from '@/types';

interface CandlestickChartProps {
  data: OHLCVData[];
  ticker?: string;
  height?: number;
  showVolume?: boolean;
  indicators?: {
    ma20?: boolean;
    ma50?: boolean;
    ma200?: boolean;
  };
  signals?: Signal[];
}

export function CandlestickChart({
  data,
  ticker,
  height = 500,
  showVolume = true,
  indicators = { ma20: true, ma50: true, ma200: true },
  signals = [],
}: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);

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
        vertLines: { color: '#2C2E33' },
        horzLines: { color: '#2C2E33' },
      },
      crosshair: {
        mode: 1,
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

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26A69A',
      downColor: '#EF5350',
      borderVisible: false,
      wickUpColor: '#26A69A',
      wickDownColor: '#EF5350',
    });

    candlestickSeriesRef.current = candlestickSeries;

    // Convert data to lightweight-charts format
    const chartData = data.map((d) => ({
      time: d.time as string,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));

    candlestickSeries.setData(chartData);

    // Add volume histogram if enabled
    if (showVolume) {
      const volumeSeries = chart.addHistogramSeries({
        color: '#26a69a',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: 'volume',
      });

      volumeSeriesRef.current = volumeSeries;

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

    // Add Moving Averages
    if (indicators.ma20) {
      const ma20Series = chart.addLineSeries({
        color: '#4C6EF5',
        lineWidth: 2,
        title: 'MA 20',
      });
      ma20Series.setData(calculateMA(chartData, 20));
    }

    if (indicators.ma50) {
      const ma50Series = chart.addLineSeries({
        color: '#FFA500',
        lineWidth: 2,
        title: 'MA 50',
      });
      ma50Series.setData(calculateMA(chartData, 50));
    }

    if (indicators.ma200) {
      const ma200Series = chart.addLineSeries({
        color: '#F44336',
        lineWidth: 2,
        title: 'MA 200',
      });
      ma200Series.setData(calculateMA(chartData, 200));
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
  }, [data, height, showVolume, indicators, signals]);

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

// Helper function to calculate moving average
function calculateMA(data: any[], period: number): any[] {
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
