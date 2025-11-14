import { NextResponse } from 'next/server';
import { mockStocks } from '@/lib/mock/mockData';

export async function GET(request: Request, { params }: { params: { ticker: string } }) {
  const stock = mockStocks.find((s) => s.ticker === params.ticker.toUpperCase());

  if (!stock) {
    return NextResponse.json(
      {
        success: false,
        message: `Stock ${params.ticker} not found`,
        timestamp: new Date().toISOString(),
      },
      { status: 404 }
    );
  }

  return NextResponse.json({
    success: true,
    data: stock,
    timestamp: new Date().toISOString(),
  });
}
