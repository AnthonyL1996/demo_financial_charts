import { NextResponse } from 'next/server';
import { mockStocks } from '@/lib/mock/mockData';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);

  const search = searchParams.get('search');
  const limit = searchParams.get('limit');

  let filteredStocks = [...mockStocks];

  // Search by ticker or company name
  if (search) {
    const searchLower = search.toLowerCase();
    filteredStocks = filteredStocks.filter(
      (s) =>
        s.ticker.toLowerCase().includes(searchLower) ||
        s.companyName.toLowerCase().includes(searchLower)
    );
  }

  if (limit) {
    filteredStocks = filteredStocks.slice(0, parseInt(limit));
  }

  return NextResponse.json({
    success: true,
    data: filteredStocks,
    timestamp: new Date().toISOString(),
  });
}
