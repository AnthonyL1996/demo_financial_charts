package com.jdb.trading.service

import com.jdb.trading.domain.entity.Stock
import com.jdb.trading.domain.entity.StockPrice
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import java.math.BigDecimal
import java.time.LocalDateTime

class TechnicalAnalysisServiceTest {

    private lateinit var service: TechnicalAnalysisService
    private lateinit var testStock: Stock

    @BeforeEach
    fun setup() {
        service = TechnicalAnalysisService()
        testStock = Stock(
            id = 1L,
            ticker = "AAPL",
            companyName = "Apple Inc.",
            isActive = true
        )
    }

    @Test
    fun `calculateTechnicals should return default values for empty list`() {
        // When
        val result = service.calculateTechnicals(emptyList())

        // Then
        assertEquals(0.0, result.ma20)
        assertEquals(0.0, result.ma50)
        assertEquals(0.0, result.ma200)
        assertEquals(50.0, result.rsi)
        assertEquals(0.0, result.bollingerUpper)
        assertEquals(0.0, result.bollingerMiddle)
        assertEquals(0.0, result.bollingerLower)
        assertEquals(0.0, result.atr)
        assertEquals(0L, result.volume)
        assertEquals(0L, result.volumeMA)
    }

    @Test
    fun `calculateTechnicals should calculate indicators for sufficient data`() {
        // Given - Create 50 days of trending price data
        val prices = createTrendingPriceData(50, startPrice = 100.0, trend = 0.5)

        // When
        val result = service.calculateTechnicals(prices)

        // Then - All indicators should be calculated
        assertTrue(result.ma20 > 0.0, "MA20 should be calculated")
        assertTrue(result.ma50 > 0.0, "MA50 should be calculated")
        assertTrue(result.rsi > 0.0 && result.rsi < 100.0, "RSI should be between 0 and 100")
        assertTrue(result.bollingerUpper > result.bollingerMiddle, "Upper band should be above middle")
        assertTrue(result.bollingerMiddle > result.bollingerLower, "Middle should be above lower band")
        assertTrue(result.atr > 0.0, "ATR should be positive")
        assertTrue(result.volume > 0L, "Volume should be positive")
        assertTrue(result.volumeMA > 0L, "Volume MA should be positive")

        // MA20 should be greater than MA50 for uptrending data
        assertTrue(result.ma20 > result.ma50, "MA20 should be above MA50 in uptrend")
    }

    @Test
    fun `calculateTechnicals should set MA200 to 0 for insufficient data`() {
        // Given - Only 100 days of data (need 200 for MA200)
        val prices = createTrendingPriceData(100, startPrice = 150.0, trend = 0.3)

        // When
        val result = service.calculateTechnicals(prices)

        // Then
        assertEquals(0.0, result.ma200, "MA200 should be 0 with less than 200 data points")
        assertTrue(result.ma20 > 0.0, "MA20 should still be calculated")
        assertTrue(result.ma50 > 0.0, "MA50 should still be calculated")
    }

    @Test
    fun `calculateTechnicals should calculate MA200 with 200+ data points`() {
        // Given - 250 days of data
        val prices = createTrendingPriceData(250, startPrice = 120.0, trend = 0.2)

        // When
        val result = service.calculateTechnicals(prices)

        // Then
        assertTrue(result.ma200 > 0.0, "MA200 should be calculated with 200+ data points")
        assertTrue(result.ma20 > 0.0, "MA20 should be calculated")
        assertTrue(result.ma50 > 0.0, "MA50 should be calculated")
    }

    @Test
    fun `calculateTechnicals should handle volatile price data`() {
        // Given - Volatile prices (alternating high/low)
        val prices = mutableListOf<StockPrice>()
        for (i in 0 until 50) {
            val basePrice = if (i % 2 == 0) 100.0 else 110.0
            prices.add(createStockPrice(i, basePrice, volatility = 5.0))
        }

        // When
        val result = service.calculateTechnicals(prices)

        // Then
        assertTrue(result.atr > 0.0, "ATR should be positive for volatile data")
        assertTrue(result.bollingerUpper - result.bollingerLower > 0, "Bollinger bands should be wide")
        assertTrue(result.rsi > 0.0 && result.rsi < 100.0, "RSI should be valid")
    }

    @Test
    fun `calculateTechnicals should handle uptrending data with high RSI`() {
        // Given - Strong uptrend
        val prices = createTrendingPriceData(50, startPrice = 100.0, trend = 2.0)

        // When
        val result = service.calculateTechnicals(prices)

        // Then
        assertTrue(result.rsi > 50.0, "RSI should be above 50 in strong uptrend")
        assertTrue(result.ma20 > result.ma50, "MA20 should be above MA50 in uptrend")
    }

    @Test
    fun `calculateTechnicals should handle downtrending data with low RSI`() {
        // Given - Downtrend
        val prices = createTrendingPriceData(50, startPrice = 100.0, trend = -1.0)

        // When
        val result = service.calculateTechnicals(prices)

        // Then
        assertTrue(result.rsi < 50.0, "RSI should be below 50 in downtrend")
        assertTrue(result.ma20 < result.ma50, "MA20 should be below MA50 in downtrend")
    }

    @Test
    fun `calculateSMA should calculate simple moving average`() {
        // Given
        val prices = createTrendingPriceData(30, startPrice = 100.0, trend = 0.0)

        // When
        val sma20 = service.calculateSMA(prices, 20)

        // Then
        assertTrue(sma20 > 0.0, "SMA should be calculated")
        assertTrue(sma20 >= 95.0 && sma20 <= 105.0, "SMA should be close to base price")
    }

    @Test
    fun `calculateSMA should return 0 for insufficient data`() {
        // Given
        val prices = createTrendingPriceData(10, startPrice = 100.0, trend = 0.0)

        // When
        val sma20 = service.calculateSMA(prices, 20)

        // Then
        assertEquals(0.0, sma20, "SMA should be 0 with insufficient data")
    }

    @Test
    fun `calculateRSI should calculate relative strength index`() {
        // Given
        val prices = createTrendingPriceData(30, startPrice = 100.0, trend = 0.5)

        // When
        val rsi = service.calculateRSI(prices, 14)

        // Then
        assertTrue(rsi > 0.0 && rsi <= 100.0, "RSI should be between 0 and 100")
        assertTrue(rsi > 50.0, "RSI should be above 50 for uptrending data")
    }

    @Test
    fun `calculateRSI should return neutral 50 for insufficient data`() {
        // Given
        val prices = createTrendingPriceData(10, startPrice = 100.0, trend = 0.0)

        // When
        val rsi = service.calculateRSI(prices, 14)

        // Then
        assertEquals(50.0, rsi, "RSI should be 50 (neutral) with insufficient data")
    }

    @Test
    fun `calculateTechnicals should handle exception gracefully`() {
        // Given - Create invalid data that might cause calculation errors
        val prices = listOf(
            createStockPrice(0, 0.0, volatility = 0.0)  // Zero prices might cause issues
        )

        // When
        val result = service.calculateTechnicals(prices)

        // Then - Should return default values instead of throwing
        assertEquals(0.0, result.ma20)
        assertEquals(50.0, result.rsi)
    }

    @Test
    fun `calculateTechnicals should use latest price for current volume`() {
        // Given
        val prices = createTrendingPriceData(50, startPrice = 100.0, trend = 0.0)
        val latestVolume = prices.last().volume

        // When
        val result = service.calculateTechnicals(prices)

        // Then
        assertEquals(latestVolume, result.volume, "Should return the latest price's volume")
    }

    @Test
    fun `calculateTechnicals should calculate Bollinger Bands correctly`() {
        // Given - Stable prices should result in narrow bands
        val prices = createTrendingPriceData(50, startPrice = 100.0, trend = 0.0)

        // When
        val result = service.calculateTechnicals(prices)

        // Then
        assertTrue(result.bollingerUpper > result.bollingerMiddle, "Upper band > middle")
        assertTrue(result.bollingerMiddle > result.bollingerLower, "Middle > lower band")
        assertTrue(result.bollingerMiddle >= 95.0 && result.bollingerMiddle <= 105.0,
                   "Middle band should be near price")

        // Band width should be reasonable (not too wide or too narrow)
        val bandWidth = result.bollingerUpper - result.bollingerLower
        assertTrue(bandWidth > 0.0 && bandWidth < 50.0, "Band width should be reasonable")
    }

    @Test
    fun `calculateTechnicals should calculate volume MA`() {
        // Given
        val prices = mutableListOf<StockPrice>()
        for (i in 0 until 50) {
            prices.add(createStockPrice(i, 100.0, volatility = 2.0, volume = 1_000_000L + i * 10_000L))
        }

        // When
        val result = service.calculateTechnicals(prices)

        // Then
        assertTrue(result.volumeMA > 0L, "Volume MA should be calculated")
        assertTrue(result.volumeMA >= 1_000_000L, "Volume MA should be reasonable")
    }

    // Helper functions
    private fun createTrendingPriceData(
        days: Int,
        startPrice: Double,
        trend: Double
    ): List<StockPrice> {
        val prices = mutableListOf<StockPrice>()
        var currentPrice = startPrice

        for (i in 0 until days) {
            prices.add(createStockPrice(i, currentPrice, volatility = 2.0))
            currentPrice += trend
        }

        return prices
    }

    private fun createStockPrice(
        daysAgo: Int,
        basePrice: Double,
        volatility: Double = 2.0,
        volume: Long = 1_000_000L
    ): StockPrice {
        val date = LocalDateTime.now().minusDays(daysAgo.toLong())
        val open = basePrice
        val high = basePrice + volatility
        val low = basePrice - volatility
        val close = basePrice + (Math.random() * volatility * 2 - volatility) * 0.5

        return StockPrice(
            stock = testStock,
            date = date,
            open = BigDecimal.valueOf(open),
            high = BigDecimal.valueOf(high),
            low = BigDecimal.valueOf(low),
            close = BigDecimal.valueOf(close),
            volume = volume
        )
    }
}
