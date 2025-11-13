import { NextResponse } from 'next/server';
import { mockPortfolio } from '@/lib/mock/mockData';

export async function GET() {
  return NextResponse.json({
    success: true,
    data: mockPortfolio,
    timestamp: new Date().toISOString(),
  });
}
