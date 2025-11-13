# Technical Debt & Future Improvements

This document tracks technical debt, known issues, and planned improvements for the JDB Trading System frontend.

**Last Updated:** 2025-11-13

---

## 🔴 High Priority

### 1. Type Safety Issues

**Location:** `lib/api/endpoints.ts`
- **Lines 75, 131:** Using `any` type instead of specific types
- **Impact:** Reduces type safety for technical indicators and portfolio history
- **Fix:** Create proper TypeScript interfaces for these return types
```typescript
// TODO: Create types for these
getTechnicals: async (ticker: string): Promise<StockTechnicals>
getPortfolioHistory: async (params?: {...}): Promise<PortfolioHistoryPoint[]>
```

### 2. Unused Type Import

**Location:** `lib/api/endpoints.ts:9`
- **Issue:** `PaginatedResponse` is imported but never used
- **Impact:** Minimal, but should be removed or used for pagination
- **Fix:** Either remove the import or implement pagination for list endpoints

### 3. Mock Data Hardcoded

**Location:** `app/page.tsx`
- **Issue:** Using mock data directly instead of API hooks
- **Impact:** Won't work with real backend without changes
- **Fix:** Replace with React Query hooks once backend is ready
```typescript
// Current (temporary):
const activeSignals = mockSignals.filter(...)

// Should be:
const { data: activeSignals } = useSignals({ status: 'ACTIVE' })
```

---

## 🟡 Medium Priority

### 4. Unused Dependencies

**Location:** `package.json`

Several dependencies are installed but not yet used:

| Dependency | Purpose | Status | Should Keep? |
|------------|---------|--------|--------------|
| `@mantine/dates` | Date pickers for filtering | Not used | ✅ Yes - needed for date filters |
| `@mantine/charts` | Basic charts | Not used | ⚠️ Maybe - we use lightweight-charts |
| `@tanstack/react-table` | Data tables | Not used | ✅ Yes - needed for trade lists |
| `react-hook-form` | Form management | Not used | ✅ Yes - needed for backtest config |
| `zod` | Schema validation | Not used | ✅ Yes - needed for form validation |
| `zustand` | State management | Not used | ✅ Yes - needed for user preferences |
| `dayjs` | Date utilities | Not used | ✅ Yes - used in formatters |

**Action Items:**
- Remove `@mantine/charts` if not planning to use (40KB)
- Keep others as they'll be needed for upcoming features
- Document where each will be used

### 5. Error Boundaries Missing

**Location:** Throughout app
- **Issue:** No error boundaries to catch rendering errors
- **Impact:** App could crash completely on component errors
- **Fix:** Add error boundary components
```typescript
// TODO: Create components/common/ErrorBoundary.tsx
// Wrap in app/layout.tsx
```

### 6. Loading States Not Implemented

**Location:** `app/page.tsx`
- **Issue:** No loading skeletons while data fetches
- **Impact:** Poor UX when switching to real API
- **Fix:** Add Mantine Skeleton components
```typescript
// TODO: Add loading states
if (isLoading) return <DashboardSkeleton />
```

---

## 🟢 Low Priority

### 7. Chart Performance Not Optimized

**Location:** `components/charts/CandlestickChart.tsx`
- **Issue:** Recalculating MA on every render
- **Impact:** Minor performance hit with large datasets
- **Fix:** Memoize calculations or calculate on backend
```typescript
// TODO: Memoize MA calculations
const ma20Data = useMemo(() => calculateMA(data, 20), [data])
```

### 8. No Test Coverage

**Location:** Everywhere
- **Issue:** Zero tests written
- **Impact:** No safety net for refactoring
- **Fix:** Add tests for critical paths
  - API client (JWT handling)
  - Chart rendering
  - Signal card display
  - Utility functions

**Recommended Testing Stack:**
```json
{
  "vitest": "^1.0.0",
  "@testing-library/react": "^14.0.0",
  "@testing-library/jest-dom": "^6.0.0",
  "@testing-library/user-event": "^14.0.0"
}
```

### 9. Accessibility Not Audited

**Location:** Throughout
- **Issue:** No ARIA labels, keyboard navigation not tested
- **Impact:** Poor accessibility for screen readers
- **Fix:**
  - Add ARIA labels to charts
  - Test keyboard navigation
  - Add focus indicators
  - Ensure color contrast meets WCAG AA

### 10. No Internationalization (i18n)

**Location:** Hardcoded strings everywhere
- **Issue:** All text is English only
- **Impact:** Can't support other languages
- **Fix:** Consider `next-intl` or `react-i18next` if needed
- **Decision:** May not be needed for MVP

---

## 📋 Future Features (Documented for Planning)

### 11. Missing Pages/Routes

These routes were planned but not implemented:

**Signals Pages:**
- `/signals` - All signals list with filters
- `/signals/[id]` - Signal detail page

**Stocks Pages:**
- `/stocks` - Stock screener/search
- `/stocks/[ticker]` - Individual stock page with full chart

**Backtests Pages:**
- `/backtests` - Backtest results list
- `/backtests/[id]` - Detailed backtest report
- `/backtests/new` - Create new backtest

**Portfolio Pages:**
- `/portfolio` - Full portfolio view
- `/portfolio/history` - Historical performance

**Action:** Create these pages as needed, using existing components

### 12. Missing Components

Planned but not built:

**Charts:**
- `VolumeChart.tsx` - Standalone volume chart
- `RSIChart.tsx` - RSI indicator chart
- `EquityCurve.tsx` - Backtest equity curve

**Signals:**
- `SignalTable.tsx` - Table view of signals
- `SignalFilters.tsx` - Filter component
- `SignalExplanation.tsx` - Detailed reasoning modal

**Backtests:**
- `BacktestMetrics.tsx` - Performance metrics cards
- `TradeList.tsx` - List of trades
- `MonthlyReturns.tsx` - Returns heatmap

**Common:**
- `LoadingState.tsx` - Skeleton loaders
- `EmptyState.tsx` - No data states
- `ErrorState.tsx` - Error displays

**Action:** Build these as features are developed

### 13. State Management Not Utilized

**Location:** `lib/store/` (removed - was empty)
- **Issue:** Zustand installed but no stores created
- **Impact:** Using props drilling in some places
- **Fix:** Create stores for:
  - User preferences (theme, chart settings)
  - App state (selected ticker, timeframe)
  - Filter state (signal filters, stock filters)

Example:
```typescript
// lib/store/userPreferences.ts
export const usePreferencesStore = create((set) => ({
  theme: 'dark',
  chartTimeframe: '1W',
  setChartTimeframe: (tf) => set({ chartTimeframe: tf }),
}))
```

### 14. API Error Handling Incomplete

**Location:** `lib/api/client.ts`
- **Issue:** Basic error handling, no retry logic
- **Impact:** Poor UX on network errors
- **Fix:** Add:
  - Exponential backoff retry
  - Offline detection
  - Better error messages
  - Error tracking (Sentry?)

### 15. No Authentication UI

**Location:** Missing `/login`, `/register` pages
- **Issue:** Auth API exists but no UI
- **Impact:** Can't actually log in
- **Fix:** Create auth pages when backend is ready
  - `/login` - Login form
  - `/register` - Registration form
  - Protected route middleware

---

## 🔧 Code Quality Issues

### 16. Magic Numbers

**Location:** Various files
```typescript
// app/page.tsx - hardcoded chart height
height={500}

// lib/api/client.ts - timeout
timeout: 30000

// lib/hooks - stale time
staleTime: 1000 * 60 * 5
```

**Fix:** Move to constants file
```typescript
// lib/constants/chart.ts
export const CHART_DEFAULT_HEIGHT = 500

// lib/constants/api.ts
export const API_TIMEOUT = 30_000
export const CACHE_STALE_TIME = 5 * 60 * 1000
```

### 17. Commented Code / TODOs

Search for any TODO comments in code:
```bash
# None found currently - good!
```

### 18. Large Component Files

**Location:** `app/page.tsx` (175+ lines)
- **Issue:** Dashboard page is getting large
- **Impact:** Harder to maintain
- **Fix:** Split into smaller components:
  - `DashboardStats.tsx`
  - `DashboardChart.tsx`
  - `DashboardSignals.tsx`
  - `DashboardPositions.tsx`

---

## 📊 Performance Considerations

### 19. Bundle Size Not Optimized

**Current:** 165 KB first load
- **Goal:** < 150 KB
- **Actions:**
  - Remove unused `@mantine/charts` (~40KB savings)
  - Consider dynamic imports for heavy components
  - Analyze with `@next/bundle-analyzer`

### 20. No Code Splitting Beyond Next.js Defaults

**Location:** Throughout
- **Issue:** All components loaded upfront
- **Fix:** Use dynamic imports for modals, heavy charts
```typescript
const SignalDetail = dynamic(() => import('./SignalDetail'), {
  loading: () => <Skeleton />
})
```

### 21. No Caching Strategy for Charts

**Location:** `components/charts/CandlestickChart.tsx`
- **Issue:** Chart data not cached, recalculated on every render
- **Impact:** Sluggish performance with large datasets
- **Fix:**
  - Implement data caching with React Query
  - Use Web Workers for heavy calculations
  - Virtualize data for very large datasets

---

## 🔒 Security Considerations

### 22. JWT Token Storage

**Location:** `lib/api/client.ts:48`
- **Issue:** Token stored in localStorage (XSS vulnerable)
- **Impact:** Tokens can be stolen via XSS attacks
- **Fix:** Consider:
  - HttpOnly cookies (requires backend support)
  - Memory-only storage (lost on refresh)
  - Short-lived tokens with refresh tokens

**Current Implementation:**
```typescript
// SECURITY NOTE: localStorage is vulnerable to XSS
localStorage.setItem(TOKEN_KEY, token)
```

### 23. No CSRF Protection

**Location:** API client
- **Issue:** No CSRF tokens for state-changing requests
- **Impact:** Vulnerable to CSRF attacks
- **Fix:** Implement CSRF tokens when authentication is added

### 24. API Keys in Environment

**Location:** `.env.local` (not committed - good!)
- **Status:** ✅ Properly using environment variables
- **Note:** Make sure never to commit `.env.local`
- **Production:** Use proper secrets management (Vercel env vars, AWS Secrets Manager, etc.)

---

## 📱 Mobile/Responsive Issues

### 25. Charts Not Fully Responsive

**Location:** `components/charts/CandlestickChart.tsx`
- **Issue:** Chart may not resize properly on mobile
- **Impact:** Poor mobile experience
- **Fix:**
  - Test on various screen sizes
  - Add touch gestures for zoom/pan
  - Consider simplified mobile view

### 26. Large Tables on Mobile

**Location:** Future table components
- **Issue:** Trade lists, signal tables will be wide
- **Fix:**
  - Implement horizontal scroll
  - Or card view on mobile
  - Or column visibility toggle

---

## 🎨 UI/UX Debt

### 27. No Empty States

**Location:** All list components
- **Issue:** No "No data" messages
- **Impact:** Confusing when no data exists
- **Fix:** Add EmptyState component
```typescript
{signals.length === 0 && (
  <EmptyState
    title="No signals found"
    description="There are no trading signals at the moment"
    icon={<IconChartLine />}
  />
)}
```

### 28. No Toast Notifications for Actions

**Location:** Throughout
- **Issue:** No feedback when actions complete
- **Impact:** User unsure if action succeeded
- **Fix:** Use Mantine notifications
```typescript
notifications.show({
  title: 'Success',
  message: 'Signal created successfully',
  color: 'teal'
})
```

### 29. Inconsistent Spacing/Styling

**Location:** Various components
- **Issue:** Mix of `padding="lg"` and manual px values
- **Impact:** Slightly inconsistent UI
- **Fix:** Standardize on Mantine's spacing system

---

## 🚀 Deployment Considerations

### 30. No Environment Validation

**Location:** Missing
- **Issue:** No check that required env vars are set
- **Impact:** Cryptic errors if API URL missing
- **Fix:** Add validation in `next.config.js`
```typescript
if (!process.env.NEXT_PUBLIC_API_BASE_URL) {
  throw new Error('NEXT_PUBLIC_API_BASE_URL is required')
}
```

### 31. No Health Check Endpoint

**Location:** Missing
- **Issue:** Can't verify app is running
- **Fix:** Add `/api/health` route
```typescript
// app/api/health/route.ts
export async function GET() {
  return Response.json({ status: 'ok' })
}
```

### 32. No Monitoring/Analytics

**Location:** Missing
- **Issue:** No visibility into production errors
- **Fix:** Add error tracking (Sentry, LogRocket)
- **Also Consider:** Analytics (PostHog, Mixpanel)

---

## 📚 Documentation Debt

### 33. Component Documentation

**Location:** Throughout
- **Issue:** No JSDoc comments on components
- **Impact:** Harder for new developers
- **Fix:** Add JSDoc to all exported components
```typescript
/**
 * Displays a trading signal card with JDB methodology reasoning
 * @param signal - The signal to display
 * @param onClick - Optional click handler
 */
export function SignalCard({ signal, onClick }: SignalCardProps) {
```

### 34. API Documentation

**Location:** README.md
- **Status:** ✅ Good high-level docs
- **Missing:**
  - API response examples
  - Error response formats
  - Authentication flow diagrams

---

## ✅ Not Issues (Intentional Decisions)

### Documented for Clarity:

1. **Mock Data** - Intentional for development, will be replaced
2. **Empty Directories Removed** - Were placeholders, cleaned up
3. **No Tests Yet** - MVP phase, will add later
4. **Simple Error Handling** - Will improve with production experience
5. **Single Page Initially** - Feature pages will be added iteratively

---

## 🔄 Refactoring Opportunities

### 35. Extract Chart Logic

**Current:** Chart has too many responsibilities
**Proposed:**
```
components/charts/
├── CandlestickChart.tsx (presentation)
├── useChartData.ts (data fetching)
├── useChartIndicators.ts (MA calculations)
└── chartUtils.ts (helpers)
```

### 36. Create Custom Hooks

Extract repeated logic:
- `useSignalReasoning()` - Format signal reasoning badges
- `usePortfolioMetrics()` - Calculate portfolio stats
- `useChartSettings()` - Persist chart preferences

### 37. Standardize Error Handling

Create consistent error handling pattern:
```typescript
// lib/hooks/useErrorHandler.ts
export function useErrorHandler() {
  return (error: Error) => {
    console.error(error)
    notifications.show({
      title: 'Error',
      message: error.message,
      color: 'red'
    })
  }
}
```

---

## 📈 Metrics to Track

When addressing technical debt:

1. **Bundle Size:** Currently 165 KB → Target < 150 KB
2. **TypeScript Coverage:** Currently ~95% → Target 100%
3. **Test Coverage:** Currently 0% → Target 80%+
4. **Lighthouse Score:** Not measured → Target 90+
5. **Accessibility Score:** Not measured → Target 95+

---

## 🎯 Recommended Priority Order

1. **Before Backend Integration:**
   - Fix `any` types (#1)
   - Add loading states (#6)
   - Add error boundaries (#5)

2. **Before Production:**
   - Add tests for critical paths (#8)
   - Implement error tracking (#32)
   - Add environment validation (#30)
   - Improve JWT storage (#22)

3. **Before Scale:**
   - Optimize bundle size (#19)
   - Add code splitting (#20)
   - Implement proper state management (#13)

4. **Nice to Have:**
   - i18n support (#10)
   - Accessibility audit (#9)
   - Component documentation (#33)

---

**Notes:**
- This is a living document - update as debt is addressed
- Don't let perfect be the enemy of good - the current code is solid for MVP
- Focus on high-impact items first
- Some "debt" may become obsolete as requirements change
