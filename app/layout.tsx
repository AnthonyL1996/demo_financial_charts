import '@mantine/core/styles.css';
import '@mantine/dates/styles.css';
import '@mantine/charts/styles.css';
import '@mantine/notifications/styles.css';
import './globals.css';

import { ColorSchemeScript } from '@mantine/core';
import { Providers } from '@/components/providers/Providers';

export const metadata = {
  title: 'JDB Trading System',
  description: 'Quantitative trading signal system based on JDB Trading methodology',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <ColorSchemeScript defaultColorScheme="dark" />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
