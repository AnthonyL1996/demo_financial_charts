import { NextResponse } from 'next/server';
import { mockBacktest } from '@/lib/mock/mockData';

export async function GET() {
  // Return array of backtests (we only have one mock)
  return NextResponse.json({
    success: true,
    data: [mockBacktest],
    timestamp: new Date().toISOString(),
  });
}
