import { NextResponse } from 'next/server';
import { generateMockOHLCVData } from '@/lib/mock/mockData';

export async function GET(request: Request, { params }: { params: { ticker: string } }) {
  const { searchParams } = new URL(request.url);

  const timeframe = searchParams.get('timeframe') || '1D';
  const start = searchParams.get('start');
  const end = searchParams.get('end');

  // Generate different amounts of data based on timeframe
  let days = 180; // Default: 6 months daily data
  if (timeframe === '1W') {
    days = 365 * 2; // 2 years of weekly data
  } else if (timeframe === '1M') {
    days = 365 * 5; // 5 years of monthly data
  }

  const data = generateMockOHLCVData(params.ticker, days);

  // Filter by date range if provided
  let filteredData = data;
  if (start) {
    filteredData = filteredData.filter((d) => d.time >= start);
  }
  if (end) {
    filteredData = filteredData.filter((d) => d.time <= end);
  }

  return NextResponse.json({
    success: true,
    data: filteredData,
    meta: {
      ticker: params.ticker.toUpperCase(),
      timeframe,
      count: filteredData.length,
    },
    timestamp: new Date().toISOString(),
  });
}
