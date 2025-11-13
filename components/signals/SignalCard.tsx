'use client';

import { Card, Group, Badge, Text, Stack, Progress, Divider } from '@mantine/core';
import { IconTrendingUp, IconTrendingDown, IconTarget, IconShieldOff } from '@tabler/icons-react';
import type { Signal } from '@/types';
import { formatCurrency, formatPercent, formatRelativeDate } from '@/lib/utils/formatters';

interface SignalCardProps {
  signal: Signal;
  onClick?: () => void;
}

export function SignalCard({ signal, onClick }: SignalCardProps) {
  const isLong = signal.type === 'LONG';
  const signalColor = isLong ? 'teal' : 'red';
  const SignalIcon = isLong ? IconTrendingUp : IconTrendingDown;

  const confidenceColor =
    signal.confidence >= 75 ? 'teal' : signal.confidence >= 60 ? 'yellow' : 'orange';

  return (
    <Card
      withBorder
      padding="lg"
      radius="md"
      style={{ cursor: onClick ? 'pointer' : 'default' }}
      onClick={onClick}
    >
      <Stack gap="md">
        {/* Header */}
        <Group justify="space-between">
          <Group gap="sm">
            <SignalIcon size={24} color={isLong ? '#12B886' : '#FA5252'} />
            <div>
              <Text size="lg" fw={700}>
                {signal.ticker}
              </Text>
              <Text size="xs" c="dimmed">
                {signal.companyName}
              </Text>
            </div>
          </Group>
          <Group gap="xs">
            <Badge color={signalColor} variant="light" size="lg">
              {signal.type}
            </Badge>
            <Badge color={signal.status === 'ACTIVE' ? 'blue' : 'gray'} variant="dot">
              {signal.status}
            </Badge>
          </Group>
        </Group>

        {/* Confidence */}
        <div>
          <Group justify="space-between" mb={5}>
            <Text size="sm" fw={500}>
              Confidence
            </Text>
            <Text size="sm" fw={700} c={confidenceColor}>
              {signal.confidence}%
            </Text>
          </Group>
          <Progress value={signal.confidence} color={confidenceColor} size="sm" radius="xl" />
        </div>

        <Divider />

        {/* Price Levels */}
        <Group grow>
          <Stack gap="xs">
            <Group gap="xs">
              <IconTarget size={16} color="#4C6EF5" />
              <Text size="xs" c="dimmed">
                Entry
              </Text>
            </Group>
            <Text size="md" fw={600}>
              {formatCurrency(signal.entryPrice)}
            </Text>
          </Stack>

          <Stack gap="xs">
            <Group gap="xs">
              <IconTrendingUp size={16} color="#12B886" />
              <Text size="xs" c="dimmed">
                Target
              </Text>
            </Group>
            <Text size="md" fw={600} c="teal">
              {formatCurrency(signal.targetPrice)}
            </Text>
          </Stack>

          <Stack gap="xs">
            <Group gap="xs">
              <IconShieldOff size={16} color="#FA5252" />
              <Text size="xs" c="dimmed">
                Stop Loss
              </Text>
            </Group>
            <Text size="md" fw={600} c="red">
              {formatCurrency(signal.stopLoss)}
            </Text>
          </Stack>
        </Group>

        <Divider />

        {/* Expected Return & Risk/Reward */}
        <Group grow>
          <div>
            <Text size="xs" c="dimmed">
              Expected Return
            </Text>
            <Text size="lg" fw={700} c={isLong ? 'teal' : 'red'}>
              {formatPercent(signal.expectedReturn)}
            </Text>
          </div>
          <div>
            <Text size="xs" c="dimmed">
              Risk/Reward
            </Text>
            <Text size="lg" fw={700}>
              {signal.riskRewardRatio.toFixed(1)}:1
            </Text>
          </div>
        </Group>

        {/* JDB Reasoning Summary */}
        <Stack gap="xs">
          <Text size="sm" fw={500}>
            Signal Reasoning:
          </Text>
          <Group gap="xs">
            {signal.reasoning.dominantMA.respected && (
              <Badge variant="light" size="sm">
                MA{signal.reasoning.dominantMA.period} Bounce
              </Badge>
            )}
            {signal.reasoning.bollingerBands.position === 'LOWER' && (
              <Badge variant="light" size="sm" color="blue">
                Lower BB
              </Badge>
            )}
            {signal.reasoning.bollingerBands.position === 'UPPER' && (
              <Badge variant="light" size="sm" color="orange">
                Upper BB
              </Badge>
            )}
            {signal.reasoning.fibonacci.inRetracementZone && (
              <Badge variant="light" size="sm" color="violet">
                Fib {(signal.reasoning.fibonacci.level * 100).toFixed(1)}%
              </Badge>
            )}
            {signal.reasoning.rsiDivergence.detected && (
              <Badge variant="light" size="sm" color="grape">
                RSI Divergence
              </Badge>
            )}
          </Group>
        </Stack>

        {/* Timestamp */}
        <Text size="xs" c="dimmed">
          Generated {formatRelativeDate(signal.generatedAt)} • Expires{' '}
          {formatRelativeDate(signal.expiresAt)}
        </Text>
      </Stack>
    </Card>
  );
}
