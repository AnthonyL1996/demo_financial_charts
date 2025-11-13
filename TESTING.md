# Testing Guide

This document provides information about testing the JDB Trading System frontend application.

---

## 📋 Table of Contents

- [Test Stack](#test-stack)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [Mock Backend API](#mock-backend-api)
- [API Testing](#api-testing)

---

## 🧪 Test Stack

### Testing Framework
- **Vitest** - Fast unit test framework (compatible with Jest)
- **React Testing Library** - Component testing utilities
- **@testing-library/jest-dom** - Custom Jest matchers
- **@testing-library/user-event** - User interaction simulation
- **jsdom** - DOM implementation for Node.js

### Current Test Coverage
```
Test Files: 4
- lib/utils/formatters.test.ts
- lib/mock/mockData.test.ts
- components/signals/SignalCard.test.tsx
- components/charts/ChartControls.test.tsx

Total Tests: 53 passing ✅
```

---

## 🚀 Running Tests

### Run All Tests
```bash
npm test
```

### Run Tests in Watch Mode
```bash
npm test -- --watch
```

### Run Tests with UI
```bash
npm run test:ui
```
Opens an interactive UI in your browser to view and run tests.

### Run Tests with Coverage
```bash
npm run test:coverage
```
Generates a coverage report in `coverage/` directory.

### Run Specific Test File
```bash
npm test formatters.test
```

### Run Tests Matching Pattern
```bash
npm test -- --grep="SignalCard"
```

---

## 📊 Test Coverage

### Coverage Reports

After running `npm run test:coverage`, open `coverage/index.html` in your browser to see detailed coverage reports.

### Coverage Goals
- **Utilities**: 90%+ coverage ✅
- **Components**: 70%+ coverage ✅
- **API Client**: 80%+ coverage (TODO)
- **Overall**: 75%+ coverage

---

## ✍️ Writing Tests

### Test File Naming Convention
- Component tests: `ComponentName.test.tsx`
- Utility tests: `utilityName.test.ts`
- Hook tests: `useHookName.test.ts`
- API tests: `apiName.test.ts`

### Example: Component Test

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MantineProvider } from '@mantine/core';
import { MyComponent } from './MyComponent';

// Wrapper for Mantine components
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <MantineProvider>{children}</MantineProvider>
);

describe('MyComponent', () => {
  it('should render correctly', () => {
    render(<MyComponent />, { wrapper });

    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
});
```

### Example: Utility Function Test

```typescript
import { describe, it, expect } from 'vitest';
import { myUtilityFunction } from './myUtility';

describe('myUtilityFunction', () => {
  it('should return correct result', () => {
    const result = myUtilityFunction('input');
    expect(result).toBe('expectedOutput');
  });

  it('should handle edge cases', () => {
    expect(myUtilityFunction(null)).toBe(null);
  });
});
```

### Example: Testing User Interactions

```typescript
import userEvent from '@testing-library/user-event';

it('should handle button click', async () => {
  const user = userEvent.setup();
  const mockFn = vi.fn();

  render(<Button onClick={mockFn}>Click Me</Button>);

  await user.click(screen.getByText('Click Me'));

  expect(mockFn).toHaveBeenCalled();
});
```

---

## 🔌 Mock Backend API

The application includes a **mock REST API** built with Next.js API routes for development and testing.

### Starting the Development Server

```bash
npm run dev
```

The mock API will be available at `http://localhost:3000/api/`

### API Endpoints

#### Health Check
```
GET /api/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2025-11-13T10:00:00.000Z",
  "version": "0.1.0"
}
```

#### Get All Signals
```
GET /api/signals
```

Query Parameters:
- `status` - Filter by status (ACTIVE, CLOSED, EXPIRED)
- `type` - Filter by type (LONG, SHORT)
- `ticker` - Filter by ticker symbol
- `minConfidence` - Minimum confidence level (0-100)
- `limit` - Limit number of results

Example:
```bash
curl http://localhost:3000/api/signals?status=ACTIVE&type=LONG
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "id": "1",
      "ticker": "AAPL",
      "type": "LONG",
      "status": "ACTIVE",
      "confidence": 78,
      ...
    }
  ],
  "timestamp": "2025-11-13T10:00:00.000Z"
}
```

#### Get Signal by ID
```
GET /api/signals/:id
```

Example:
```bash
curl http://localhost:3000/api/signals/1
```

#### Get All Stocks
```
GET /api/stocks
```

Query Parameters:
- `search` - Search by ticker or company name
- `limit` - Limit number of results

Example:
```bash
curl http://localhost:3000/api/stocks?search=apple
```

#### Get Stock by Ticker
```
GET /api/stocks/:ticker
```

Example:
```bash
curl http://localhost:3000/api/stocks/AAPL
```

#### Get Stock OHLCV Data
```
GET /api/stocks/:ticker/data
```

Query Parameters:
- `timeframe` - Time frame (1D, 1W, 1M) - default: 1D
- `start` - Start date (ISO format)
- `end` - End date (ISO format)

Example:
```bash
curl http://localhost:3000/api/stocks/AAPL/data?timeframe=1W
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "time": "2025-01-01",
      "open": 175.23,
      "high": 178.45,
      "low": 174.12,
      "close": 177.89,
      "volume": 52341567
    },
    ...
  ],
  "meta": {
    "ticker": "AAPL",
    "timeframe": "1W",
    "count": 180
  },
  "timestamp": "2025-11-13T10:00:00.000Z"
}
```

#### Get Portfolio
```
GET /api/portfolio
```

Example:
```bash
curl http://localhost:3000/api/portfolio
```

#### Get Backtests
```
GET /api/backtests
```

Example:
```bash
curl http://localhost:3000/api/backtests
```

---

## 🔍 API Testing

### Testing with cURL

```bash
# Test health endpoint
curl http://localhost:3000/api/health

# Get active signals
curl http://localhost:3000/api/signals?status=ACTIVE

# Get AAPL data
curl http://localhost:3000/api/stocks/AAPL

# Get AAPL chart data (weekly)
curl http://localhost:3000/api/stocks/AAPL/data?timeframe=1W
```

### Testing with Browser

Open your browser and visit:
- http://localhost:3000/api/health
- http://localhost:3000/api/signals
- http://localhost:3000/api/stocks
- http://localhost:3000/api/portfolio

You'll see JSON responses directly in the browser.

### Testing with Postman/Insomnia

Import these endpoints into your API testing tool:

**Collection: JDB Trading System**

1. Health Check - GET `{{baseUrl}}/api/health`
2. Get Signals - GET `{{baseUrl}}/api/signals`
3. Get Signal by ID - GET `{{baseUrl}}/api/signals/:id`
4. Get Stocks - GET `{{baseUrl}}/api/stocks`
5. Get Stock Data - GET `{{baseUrl}}/api/stocks/:ticker/data`
6. Get Portfolio - GET `{{baseUrl}}/api/portfolio`
7. Get Backtests - GET `{{baseUrl}}/api/backtests`

Where `baseUrl = http://localhost:3000`

### Testing API from Frontend

Update `.env.local` to use the mock API:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:3000/api
```

Then the React Query hooks will automatically use the mock API:

```typescript
// This will call http://localhost:3000/api/signals
const { data: signals } = useSignals({ status: 'ACTIVE' });
```

---

## 🏗️ Test Architecture

### Directory Structure

```
.
├── vitest.config.ts           # Vitest configuration
├── vitest.setup.ts            # Test setup (mocks, globals)
├── app/api/                   # Mock API routes
│   ├── health/route.ts
│   ├── signals/route.ts
│   ├── stocks/route.ts
│   └── portfolio/route.ts
├── lib/
│   ├── mock/
│   │   ├── mockData.ts
│   │   └── mockData.test.ts   # Mock data tests
│   └── utils/
│       ├── formatters.ts
│       └── formatters.test.ts # Utility tests
└── components/
    ├── signals/
    │   ├── SignalCard.tsx
    │   └── SignalCard.test.tsx # Component tests
    └── charts/
        ├── ChartControls.tsx
        └── ChartControls.test.tsx
```

### Test Categories

1. **Unit Tests** - Test individual functions and utilities
   - `lib/utils/*.test.ts`
   - Fast, isolated tests

2. **Component Tests** - Test React components
   - `components/**/*.test.tsx`
   - Use React Testing Library
   - Test user interactions

3. **Integration Tests** - Test API routes (TODO)
   - `app/api/**/*.test.ts`
   - Test endpoint logic

4. **E2E Tests** - Test full user flows (TODO)
   - Use Playwright or Cypress
   - Test in real browser

---

## 📝 Best Practices

### Do's ✅

1. **Write tests for critical paths**
   - User-facing features
   - Business logic
   - Data transformations

2. **Test behavior, not implementation**
   - Test what users see and do
   - Avoid testing internal state

3. **Use descriptive test names**
   - Good: `should format positive numbers with + sign`
   - Bad: `test1`

4. **Keep tests simple and focused**
   - One assertion per test (when possible)
   - Clear arrange-act-assert pattern

5. **Use mock data consistently**
   - Import from `lib/mock/mockData.ts`
   - Don't create inline mock data

### Don'ts ❌

1. **Don't test third-party libraries**
   - Trust that Mantine, React Query work
   - Test your usage of them

2. **Don't test implementation details**
   - Don't test component state directly
   - Test what users interact with

3. **Don't create brittle tests**
   - Avoid testing exact class names
   - Use accessible roles and labels

4. **Don't ignore failing tests**
   - Fix or remove them
   - Failing tests reduce trust

---

## 🐛 Debugging Tests

### Run Single Test in Debug Mode

```bash
npm test -- --inspect-brk formatters.test
```

Then open `chrome://inspect` in Chrome.

### View Test Output

```bash
npm test -- --reporter=verbose
```

### Check What's Rendered

```typescript
import { screen } from '@testing-library/react';

render(<MyComponent />);
screen.debug(); // Prints HTML to console
```

### Use Testing Playground

```typescript
import { screen } from '@testing-library/react';

render(<MyComponent />);
screen.logTestingPlaygroundURL();
```

Visit the URL to get query suggestions.

---

## 🎯 Next Steps

### TODO: Add More Tests

1. **API Client Tests**
   - Test JWT token management
   - Test error handling
   - Test retry logic

2. **Hook Tests**
   - Test `useSignals`
   - Test `useStocks`
   - Test `usePortfolio`

3. **Integration Tests**
   - Test API routes with supertest
   - Test database operations

4. **E2E Tests**
   - Test full user flows
   - Test chart interactions
   - Test signal creation

### Improving Coverage

Run coverage report and focus on:
1. Low-coverage files
2. Critical business logic
3. Error handling paths

---

## 📚 Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Next.js Testing](https://nextjs.org/docs/testing)

---

**Current Test Status:**
- ✅ 53 tests passing
- ✅ 0 tests failing
- ✅ Utilities: Fully tested
- ✅ Components: Partially tested
- ⚠️ API Client: Not yet tested
- ⚠️ E2E: Not yet implemented

**Keep your tests green! 🟢**
