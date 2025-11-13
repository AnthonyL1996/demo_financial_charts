import { NextResponse } from 'next/server';
import { mockSignals } from '@/lib/mock/mockData';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);

  // Get query parameters
  const status = searchParams.get('status');
  const type = searchParams.get('type');
  const ticker = searchParams.get('ticker');
  const minConfidence = searchParams.get('minConfidence');
  const limit = searchParams.get('limit');

  // Filter signals based on query parameters
  let filteredSignals = [...mockSignals];

  if (status) {
    filteredSignals = filteredSignals.filter((s) => s.status === status);
  }

  if (type) {
    filteredSignals = filteredSignals.filter((s) => s.type === type);
  }

  if (ticker) {
    filteredSignals = filteredSignals.filter((s) => s.ticker === ticker);
  }

  if (minConfidence) {
    filteredSignals = filteredSignals.filter((s) => s.confidence >= parseInt(minConfidence));
  }

  if (limit) {
    filteredSignals = filteredSignals.slice(0, parseInt(limit));
  }

  return NextResponse.json({
    success: true,
    data: filteredSignals,
    timestamp: new Date().toISOString(),
  });
}
