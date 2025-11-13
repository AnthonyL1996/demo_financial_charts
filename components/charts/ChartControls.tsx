'use client';

import { Card, Stack, Switch, Group, Text, Divider, ColorSwatch } from '@mantine/core';

export interface IndicatorSettings {
  // Moving Averages
  ma20: boolean;
  ma50: boolean;
  ma200: boolean;

  // Bollinger Bands
  bollingerBands: boolean;

  // Volume
  volume: boolean;

  // EMA
  ema12: boolean;
  ema26: boolean;

  // Other
  grid: boolean;
  crosshair: boolean;
}

interface ChartControlsProps {
  indicators: IndicatorSettings;
  onIndicatorChange: (indicator: keyof IndicatorSettings, value: boolean) => void;
}

export function ChartControls({ indicators, onIndicatorChange }: ChartControlsProps) {
  return (
    <Card withBorder padding="md">
      <Stack gap="md">
        <Text size="sm" fw={600}>
          Chart Indicators
        </Text>

        {/* Moving Averages */}
        <div>
          <Text size="xs" c="dimmed" mb="xs">
            Moving Averages (SMA)
          </Text>
          <Stack gap="xs">
            <Group justify="space-between">
              <Group gap="xs">
                <ColorSwatch color="#4C6EF5" size={16} />
                <Text size="sm">MA 20</Text>
              </Group>
              <Switch
                size="sm"
                checked={indicators.ma20}
                onChange={(e) => onIndicatorChange('ma20', e.currentTarget.checked)}
              />
            </Group>

            <Group justify="space-between">
              <Group gap="xs">
                <ColorSwatch color="#FFA500" size={16} />
                <Text size="sm">MA 50</Text>
              </Group>
              <Switch
                size="sm"
                checked={indicators.ma50}
                onChange={(e) => onIndicatorChange('ma50', e.currentTarget.checked)}
              />
            </Group>

            <Group justify="space-between">
              <Group gap="xs">
                <ColorSwatch color="#F44336" size={16} />
                <Text size="sm">MA 200</Text>
              </Group>
              <Switch
                size="sm"
                checked={indicators.ma200}
                onChange={(e) => onIndicatorChange('ma200', e.currentTarget.checked)}
              />
            </Group>
          </Stack>
        </div>

        <Divider />

        {/* Exponential Moving Averages */}
        <div>
          <Text size="xs" c="dimmed" mb="xs">
            Exponential Moving Averages (EMA)
          </Text>
          <Stack gap="xs">
            <Group justify="space-between">
              <Group gap="xs">
                <ColorSwatch color="#12B886" size={16} />
                <Text size="sm">EMA 12</Text>
              </Group>
              <Switch
                size="sm"
                checked={indicators.ema12}
                onChange={(e) => onIndicatorChange('ema12', e.currentTarget.checked)}
              />
            </Group>

            <Group justify="space-between">
              <Group gap="xs">
                <ColorSwatch color="#15AABF" size={16} />
                <Text size="sm">EMA 26</Text>
              </Group>
              <Switch
                size="sm"
                checked={indicators.ema26}
                onChange={(e) => onIndicatorChange('ema26', e.currentTarget.checked)}
              />
            </Group>
          </Stack>
        </div>

        <Divider />

        {/* Bollinger Bands */}
        <div>
          <Text size="xs" c="dimmed" mb="xs">
            Volatility
          </Text>
          <Group justify="space-between">
            <Group gap="xs">
              <ColorSwatch color="#9775FA" size={16} />
              <Text size="sm">Bollinger Bands</Text>
            </Group>
            <Switch
              size="sm"
              checked={indicators.bollingerBands}
              onChange={(e) => onIndicatorChange('bollingerBands', e.currentTarget.checked)}
            />
          </Group>
        </div>

        <Divider />

        {/* Volume */}
        <div>
          <Text size="xs" c="dimmed" mb="xs">
            Volume
          </Text>
          <Group justify="space-between">
            <Text size="sm">Volume Histogram</Text>
            <Switch
              size="sm"
              checked={indicators.volume}
              onChange={(e) => onIndicatorChange('volume', e.currentTarget.checked)}
            />
          </Group>
        </div>

        <Divider />

        {/* Display Options */}
        <div>
          <Text size="xs" c="dimmed" mb="xs">
            Display Options
          </Text>
          <Stack gap="xs">
            <Group justify="space-between">
              <Text size="sm">Grid Lines</Text>
              <Switch
                size="sm"
                checked={indicators.grid}
                onChange={(e) => onIndicatorChange('grid', e.currentTarget.checked)}
              />
            </Group>

            <Group justify="space-between">
              <Text size="sm">Crosshair</Text>
              <Switch
                size="sm"
                checked={indicators.crosshair}
                onChange={(e) => onIndicatorChange('crosshair', e.currentTarget.checked)}
              />
            </Group>
          </Stack>
        </div>
      </Stack>
    </Card>
  );
}
