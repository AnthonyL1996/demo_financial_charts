#!/bin/bash

# JDB Trading Backend API Test Script
# Tests all API endpoints and validates responses

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="${API_URL:-http://localhost:8080/api}"
VERBOSE="${VERBOSE:-0}"

echo "==========================================="
echo "JDB Trading Backend API Test Suite"
echo "==========================================="
echo "API URL: $API_URL"
echo "==========================================="
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to print test results
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"

    echo -n "Testing: $name ... "

    if [ "$VERBOSE" = "1" ]; then
        echo ""
        echo "URL: $url"
    fi

    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        ((TESTS_PASSED++))

        if [ "$VERBOSE" = "1" ]; then
            echo "Response: $body" | jq '.' 2>/dev/null || echo "$body"
            echo ""
        fi

        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code, expected $expected_status)"
        ((TESTS_FAILED++))

        echo "Response: $body"
        echo ""

        return 1
    fi
}

# Helper function to check JSON field exists
check_json_field() {
    local json="$1"
    local field="$2"

    echo "$json" | jq -e "$field" > /dev/null 2>&1
    return $?
}

echo "=== Health Check ==="
test_endpoint "Health endpoint" "$API_URL/health"
echo ""

echo "=== Stock List Endpoints ==="
test_endpoint "Get all stocks" "$API_URL/stocks"
test_endpoint "Search for AAPL" "$API_URL/stocks?search=AAPL"
test_endpoint "Limit results" "$API_URL/stocks?limit=3"
echo ""

echo "=== Individual Stock Endpoints ==="
for ticker in AAPL TSLA MSFT; do
    test_endpoint "Get $ticker stock" "$API_URL/stocks/$ticker"
done
echo ""

echo "=== OHLCV Data Endpoints ==="
test_endpoint "Get AAPL daily data" "$API_URL/stocks/AAPL/data?timeframe=1D"
test_endpoint "Get TSLA weekly data" "$API_URL/stocks/TSLA/data?timeframe=1W"
test_endpoint "Get MSFT monthly data" "$API_URL/stocks/MSFT/data?timeframe=1M"
echo ""

echo "=== Date Range Filtering ==="
test_endpoint "Get data for date range" "$API_URL/stocks/AAPL/data?start=2025-01-01&end=2025-11-14"
echo ""

echo "=== Technical Indicators ==="
test_endpoint "Get AAPL technicals" "$API_URL/stocks/AAPL/technicals"
echo ""

echo "=== Error Handling ==="
test_endpoint "Invalid ticker (should fail gracefully)" "$API_URL/stocks/INVALIDTICKER" "500" || true
echo ""

echo "=== Performance Test (Caching) ==="
echo "First request (should hit Yahoo Finance)..."
time_start=$(date +%s%N)
curl -s "$API_URL/stocks/NVDA/data?timeframe=1D" > /dev/null
time_end=$(date +%s%N)
time_first=$((($time_end - $time_start) / 1000000))
echo "  Time: ${time_first}ms"

echo "Second request (should use cache)..."
time_start=$(date +%s%N)
curl -s "$API_URL/stocks/NVDA/data?timeframe=1D" > /dev/null
time_end=$(date +%s%N)
time_second=$((($time_end - $time_start) / 1000000))
echo "  Time: ${time_second}ms"

if [ $time_second -lt $time_first ]; then
    echo -e "${GREEN}✓ Cache is working!${NC} (${time_second}ms < ${time_first}ms)"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠ Cache might not be working${NC} (${time_second}ms >= ${time_first}ms)"
fi
echo ""

echo "==========================================="
echo "Test Summary"
echo "==========================================="
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo "Total:  $((TESTS_PASSED + TESTS_FAILED))"
echo "==========================================="

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! 🎉${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Check the output above.${NC}"
    exit 1
fi
