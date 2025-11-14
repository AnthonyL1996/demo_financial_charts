import { NextResponse } from 'next/server';
import { mockSignals } from '@/lib/mock/mockData';

export async function GET(request: Request, { params }: { params: { id: string } }) {
  const signal = mockSignals.find((s) => s.id === params.id);

  if (!signal) {
    return NextResponse.json(
      {
        success: false,
        message: `Signal with ID ${params.id} not found`,
        timestamp: new Date().toISOString(),
      },
      { status: 404 }
    );
  }

  return NextResponse.json({
    success: true,
    data: signal,
    timestamp: new Date().toISOString(),
  });
}
