import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChartControls, type IndicatorSettings } from './ChartControls';
import { MantineProvider } from '@mantine/core';

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <MantineProvider>{children}</MantineProvider>
);

const defaultIndicators: IndicatorSettings = {
  ma20: true,
  ma50: true,
  ma200: true,
  bollingerBands: false,
  volume: true,
  ema12: false,
  ema26: false,
  grid: true,
  crosshair: true,
};

describe('ChartControls', () => {
  it('should render all indicator labels', () => {
    const mockOnChange = vi.fn();
    render(<ChartControls indicators={defaultIndicators} onIndicatorChange={mockOnChange} />, {
      wrapper,
    });

    expect(screen.getByText('MA 20')).toBeInTheDocument();
    expect(screen.getByText('MA 50')).toBeInTheDocument();
    expect(screen.getByText('MA 200')).toBeInTheDocument();
    expect(screen.getByText('EMA 12')).toBeInTheDocument();
    expect(screen.getByText('EMA 26')).toBeInTheDocument();
    expect(screen.getByText('Bollinger Bands')).toBeInTheDocument();
    expect(screen.getByText('Volume Histogram')).toBeInTheDocument();
    expect(screen.getByText('Grid Lines')).toBeInTheDocument();
    expect(screen.getByText('Crosshair')).toBeInTheDocument();
  });

  it('should have correct initial switch states', () => {
    const mockOnChange = vi.fn();
    render(<ChartControls indicators={defaultIndicators} onIndicatorChange={mockOnChange} />, {
      wrapper,
    });

    // Get all switches (Mantine uses role="switch" not "checkbox")
    const switches = screen.getAllByRole('switch');

    // MA20, MA50, MA200, Volume, Grid, Crosshair should be checked (6 total)
    const checkedSwitches = switches.filter((s) => s.getAttribute('data-checked') === 'true');
    expect(checkedSwitches.length).toBe(6);
  });

  it('should call onIndicatorChange when a switch is toggled', async () => {
    const user = userEvent.setup();
    const mockOnChange = vi.fn();

    render(<ChartControls indicators={defaultIndicators} onIndicatorChange={mockOnChange} />, {
      wrapper,
    });

    // Get any switch and click it
    const switches = screen.getAllByRole('switch');
    // Click the first unchecked switch (EMA12, which is the 4th one)
    const uncheckedSwitch = switches.find((s) => s.getAttribute('data-checked') !== 'true');

    if (uncheckedSwitch) {
      await user.click(uncheckedSwitch);
      // Just verify the callback was called, we don't care about exact args in this test
      expect(mockOnChange).toHaveBeenCalled();
      expect(mockOnChange.mock.calls[0][1]).toBe(true); // Second arg should be true
    }
  });

  it('should display category headers', () => {
    const mockOnChange = vi.fn();
    render(<ChartControls indicators={defaultIndicators} onIndicatorChange={mockOnChange} />, {
      wrapper,
    });

    expect(screen.getByText('Moving Averages (SMA)')).toBeInTheDocument();
    expect(screen.getByText('Exponential Moving Averages (EMA)')).toBeInTheDocument();
    expect(screen.getByText('Volatility')).toBeInTheDocument();
    expect(screen.getByText('Volume')).toBeInTheDocument();
    expect(screen.getByText('Display Options')).toBeInTheDocument();
  });
});
