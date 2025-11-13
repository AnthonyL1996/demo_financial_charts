'use client';

import { Container, Grid, Title, Text, Group, Badge, Card, Stack, SimpleGrid } from '@mantine/core';
import { IconTrendingUp, IconTrendingDown, IconClock, IconChartLine } from '@tabler/icons-react';
import { CandlestickChart } from '@/components/charts/CandlestickChart';
import { SignalCard } from '@/components/signals/SignalCard';
import { mockSignals, mockPortfolio, generateMockOHLCVData } from '@/lib/mock/mockData';
import { formatCurrency, formatPercent } from '@/lib/utils/formatters';

export default function DashboardPage() {
  // Use mock data for now
  const activeSignals = mockSignals.filter((s) => s.status === 'ACTIVE');
  const longSignals = activeSignals.filter((s) => s.type === 'LONG');
  const shortSignals = activeSignals.filter((s) => s.type === 'SHORT');
  const portfolio = mockPortfolio;

  // Generate sample chart data for AAPL
  const chartData = generateMockOHLCVData('AAPL', 180);

  return (
    <Container size="xl" py="xl">
      {/* Header */}
      <Stack gap="xl">
        <Group justify="space-between" align="center">
          <div>
            <Title order={1}>JDB Trading System</Title>
            <Text c="dimmed" size="sm">
              Quantitative trading signals based on JDB methodology
            </Text>
          </div>
          <Badge size="lg" color="green" variant="dot">
            Live
          </Badge>
        </Group>

        {/* Stats Cards */}
        <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }}>
          {/* Total Signals */}
          <Card withBorder padding="lg">
            <Stack gap="xs">
              <Group gap="xs">
                <IconChartLine size={20} color="#4C6EF5" />
                <Text size="sm" c="dimmed">
                  Active Signals
                </Text>
              </Group>
              <Text size="xl" fw={700}>
                {activeSignals.length}
              </Text>
              <Group gap="xs">
                <Text size="xs" c="teal">
                  {longSignals.length} Long
                </Text>
                <Text size="xs" c="dimmed">
                  •
                </Text>
                <Text size="xs" c="red">
                  {shortSignals.length} Short
                </Text>
              </Group>
            </Stack>
          </Card>

          {/* Portfolio Value */}
          <Card withBorder padding="lg">
            <Stack gap="xs">
              <Group gap="xs">
                <IconTrendingUp size={20} color="#12B886" />
                <Text size="sm" c="dimmed">
                  Portfolio Value
                </Text>
              </Group>
              <Text size="xl" fw={700}>
                {formatCurrency(portfolio.totalValue, 0)}
              </Text>
              <Text size="xs" c={portfolio.totalPnLPercent > 0 ? 'teal' : 'red'}>
                {formatPercent(portfolio.totalPnLPercent)} ({formatCurrency(portfolio.totalPnL)})
              </Text>
            </Stack>
          </Card>

          {/* Day P&L */}
          <Card withBorder padding="lg">
            <Stack gap="xs">
              <Group gap="xs">
                <IconClock size={20} color="#FFA500" />
                <Text size="sm" c="dimmed">
                  Today&apos;s P&L
                </Text>
              </Group>
              <Text size="xl" fw={700} c={portfolio.dayPnL > 0 ? 'teal' : 'red'}>
                {formatCurrency(portfolio.dayPnL)}
              </Text>
              <Text size="xs" c={portfolio.dayPnLPercent > 0 ? 'teal' : 'red'}>
                {formatPercent(portfolio.dayPnLPercent)}
              </Text>
            </Stack>
          </Card>

          {/* Sharpe Ratio */}
          <Card withBorder padding="lg">
            <Stack gap="xs">
              <Group gap="xs">
                <IconChartLine size={20} color="#7950F2" />
                <Text size="sm" c="dimmed">
                  Sharpe Ratio
                </Text>
              </Group>
              <Text size="xl" fw={700}>
                {portfolio.riskMetrics.sharpeRatio.toFixed(2)}
              </Text>
              <Text size="xs" c="dimmed">
                Risk-Adjusted Return
              </Text>
            </Stack>
          </Card>
        </SimpleGrid>

        {/* Main Content */}
        <Grid>
          {/* Chart Section */}
          <Grid.Col span={{ base: 12, md: 8 }}>
            <Stack gap="md">
              <Card withBorder padding="lg">
                <Title order={3} mb="md">
                  Market Overview - AAPL
                </Title>
                <CandlestickChart
                  data={chartData}
                  ticker="AAPL"
                  height={500}
                  showVolume={true}
                  indicators={{
                    ma20: true,
                    ma50: true,
                    ma200: true,
                  }}
                  signals={mockSignals.filter((s) => s.ticker === 'AAPL')}
                />
              </Card>
            </Stack>
          </Grid.Col>

          {/* Signals Section */}
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Stack gap="md">
              <Group justify="space-between" align="center">
                <Title order={3}>Active Signals</Title>
                <Badge color="blue">{activeSignals.length}</Badge>
              </Group>

              {activeSignals.length > 0 ? (
                activeSignals.map((signal) => (
                  <SignalCard key={signal.id} signal={signal} />
                ))
              ) : (
                <Card withBorder padding="lg">
                  <Text c="dimmed" ta="center">
                    No active signals at the moment
                  </Text>
                </Card>
              )}
            </Stack>
          </Grid.Col>
        </Grid>

        {/* Portfolio Positions */}
        <div>
          <Title order={3} mb="md">
            Current Positions
          </Title>
          <SimpleGrid cols={{ base: 1, sm: 2, md: 3 }}>
            {portfolio.positions.map((position) => (
              <Card key={position.ticker} withBorder padding="lg">
                <Stack gap="xs">
                  <Group justify="space-between">
                    <div>
                      <Text fw={700}>{position.ticker}</Text>
                      <Text size="xs" c="dimmed">
                        {position.companyName}
                      </Text>
                    </div>
                    <Badge color={position.type === 'LONG' ? 'teal' : 'red'} variant="light">
                      {position.type}
                    </Badge>
                  </Group>

                  <Group grow>
                    <div>
                      <Text size="xs" c="dimmed">
                        Shares
                      </Text>
                      <Text fw={600}>{position.shares}</Text>
                    </div>
                    <div>
                      <Text size="xs" c="dimmed">
                        Value
                      </Text>
                      <Text fw={600}>{formatCurrency(position.marketValue, 0)}</Text>
                    </div>
                  </Group>

                  <Group grow>
                    <div>
                      <Text size="xs" c="dimmed">
                        Entry
                      </Text>
                      <Text size="sm">{formatCurrency(position.entryPrice)}</Text>
                    </div>
                    <div>
                      <Text size="xs" c="dimmed">
                        Current
                      </Text>
                      <Text size="sm">{formatCurrency(position.currentPrice)}</Text>
                    </div>
                  </Group>

                  <div>
                    <Text size="xs" c="dimmed">
                      P&L
                    </Text>
                    <Group gap="xs">
                      <Text fw={700} c={position.pnl > 0 ? 'teal' : 'red'}>
                        {formatCurrency(position.pnl)}
                      </Text>
                      <Text size="sm" c={position.pnl > 0 ? 'teal' : 'red'}>
                        ({formatPercent(position.pnlPercent)})
                      </Text>
                    </Group>
                  </div>
                </Stack>
              </Card>
            ))}
          </SimpleGrid>
        </div>
      </Stack>
    </Container>
  );
}
