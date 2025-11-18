package com.jdb.trading.service

import io.mockk.*
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import yahoofinance.Stock
import yahoofinance.YahooFinance
import yahoofinance.histquotes.HistoricalQuote
import yahoofinance.histquotes.Interval
import yahoofinance.quotes.stock.StockQuote
import yahoofinance.quotes.stock.StockStats
import java.math.BigDecimal
import java.time.LocalDate
import java.util.*

class YahooFinanceServiceTest {

    private lateinit var service: YahooFinanceService

    @BeforeEach
    fun setup() {
        mockkStatic(YahooFinance::class)
        service = YahooFinanceService(
            cacheDuration = 300L,
            retryAttempts = 3,
            retryDelay = 100L
        )
    }

    @AfterEach
    fun tearDown() {
        unmockkAll()
    }

    @Test
    fun `fetchStockData should return OHLCV data successfully`() {
        // Given
        val ticker = "AAPL"
        val mockStock = mockk<Stock>()
        val mockQuote1 = createMockHistoricalQuote(
            date = Calendar.getInstance().apply { add(Calendar.DAY_OF_YEAR, -2) },
            open = 150.0,
            high = 155.0,
            low = 149.0,
            close = 154.0,
            volume = 1000000L
        )
        val mockQuote2 = createMockHistoricalQuote(
            date = Calendar.getInstance().apply { add(Calendar.DAY_OF_YEAR, -1) },
            open = 154.0,
            high = 158.0,
            low = 153.0,
            close = 157.0,
            volume = 1200000L
        )

        every { YahooFinance.get(ticker) } returns mockStock
        every { mockStock.getHistory(any(), any(), Interval.DAILY) } returns listOf(mockQuote1, mockQuote2)

        // When
        val result = service.fetchStockData(ticker)

        // Then
        assertEquals(2, result.size)
        assertEquals(150.0, result[0].open)
        assertEquals(155.0, result[0].high)
        assertEquals(149.0, result[0].low)
        assertEquals(154.0, result[0].close)
        assertEquals(1000000L, result[0].volume)

        // Verify chronological order
        assertTrue(result[0].time < result[1].time)
    }

    @Test
    fun `fetchStockData should handle weekly timeframe`() {
        // Given
        val ticker = "TSLA"
        val mockStock = mockk<Stock>()
        val mockQuote = createMockHistoricalQuote(
            date = Calendar.getInstance(),
            open = 200.0,
            high = 210.0,
            low = 195.0,
            close = 205.0,
            volume = 5000000L
        )

        every { YahooFinance.get(ticker) } returns mockStock
        every { mockStock.getHistory(any(), any(), Interval.WEEKLY) } returns listOf(mockQuote)

        // When
        val result = service.fetchStockData(ticker, timeframe = "1W")

        // Then
        assertEquals(1, result.size)
        assertEquals(200.0, result[0].open)
        verify { mockStock.getHistory(any(), any(), Interval.WEEKLY) }
    }

    @Test
    fun `fetchStockData should handle monthly timeframe`() {
        // Given
        val ticker = "MSFT"
        val mockStock = mockk<Stock>()
        val mockQuote = createMockHistoricalQuote(
            date = Calendar.getInstance(),
            open = 300.0,
            high = 320.0,
            low = 295.0,
            close = 315.0,
            volume = 10000000L
        )

        every { YahooFinance.get(ticker) } returns mockStock
        every { mockStock.getHistory(any(), any(), Interval.MONTHLY) } returns listOf(mockQuote)

        // When
        val result = service.fetchStockData(ticker, timeframe = "1M")

        // Then
        assertEquals(1, result.size)
        verify { mockStock.getHistory(any(), any(), Interval.MONTHLY) }
    }

    @Test
    fun `fetchStockData should handle custom date range`() {
        // Given
        val ticker = "GOOGL"
        val start = LocalDate.of(2024, 1, 1)
        val end = LocalDate.of(2024, 1, 31)
        val mockStock = mockk<Stock>()
        val mockQuote = createMockHistoricalQuote(
            date = Calendar.getInstance(),
            open = 140.0,
            high = 145.0,
            low = 138.0,
            close = 143.0,
            volume = 2000000L
        )

        every { YahooFinance.get(ticker) } returns mockStock
        every { mockStock.getHistory(any(), any(), any()) } returns listOf(mockQuote)

        // When
        val result = service.fetchStockData(ticker, start = start, end = end)

        // Then
        assertEquals(1, result.size)
        verify { mockStock.getHistory(any(), any(), Interval.DAILY) }
    }

    @Test
    fun `fetchStockData should throw exception when stock not found`() {
        // Given
        val ticker = "INVALID"
        every { YahooFinance.get(ticker) } returns null

        // When/Then
        val exception = assertThrows<IllegalArgumentException> {
            service.fetchStockData(ticker)
        }
        assertTrue(exception.message!!.contains("Stock not found"))
    }

    @Test
    fun `fetchStockData should throw exception when no historical data`() {
        // Given
        val ticker = "AAPL"
        val mockStock = mockk<Stock>()

        every { YahooFinance.get(ticker) } returns mockStock
        every { mockStock.getHistory(any(), any(), any()) } returns null

        // When/Then
        val exception = assertThrows<IllegalStateException> {
            service.fetchStockData(ticker)
        }
        assertTrue(exception.message!!.contains("No historical data available"))
    }

    @Test
    fun `fetchStockData should retry on failure`() {
        // Given
        val ticker = "AAPL"
        val mockStock = mockk<Stock>()
        val mockQuote = createMockHistoricalQuote(
            date = Calendar.getInstance(),
            open = 150.0,
            high = 155.0,
            low = 149.0,
            close = 154.0,
            volume = 1000000L
        )

        every { YahooFinance.get(ticker) } throws RuntimeException("Network error") andThen mockStock
        every { mockStock.getHistory(any(), any(), any()) } returns listOf(mockQuote)

        // When
        val result = service.fetchStockData(ticker)

        // Then
        assertEquals(1, result.size)
        verify(exactly = 2) { YahooFinance.get(ticker) }
    }

    @Test
    fun `fetchStockData should fail after max retries`() {
        // Given
        val ticker = "AAPL"
        every { YahooFinance.get(ticker) } throws RuntimeException("Network error")

        // When/Then
        assertThrows<RuntimeException> {
            service.fetchStockData(ticker)
        }
        verify(exactly = 3) { YahooFinance.get(ticker) }
    }

    @Test
    fun `fetchCurrentQuote should return current quote data`() {
        // Given
        val ticker = "AAPL"
        val mockStock = mockk<Stock>()
        val mockQuote = mockk<StockQuote>()
        val mockStats = mockk<StockStats>()

        every { YahooFinance.get(ticker) } returns mockStock
        every { mockStock.name } returns "Apple Inc."
        every { mockStock.quote } returns mockQuote
        every { mockStock.stats } returns mockStats
        every { mockQuote.refresh() } just Runs
        every { mockQuote.price } returns BigDecimal("150.50")
        every { mockQuote.changeInPercent } returns BigDecimal("2.5")
        every { mockQuote.volume } returns 10000000L
        every { mockStats.marketCap } returns BigDecimal("2500000000000")

        // When
        val result = service.fetchCurrentQuote(ticker)

        // Then
        assertEquals("AAPL", result.ticker)
        assertEquals("Apple Inc.", result.companyName)
        assertEquals(150.50, result.currentPrice)
        assertEquals(2.5, result.priceChange)
        assertEquals(10000000L, result.volume)
        assertEquals(2500000000000L, result.marketCap)
        verify { mockQuote.refresh() }
    }

    @Test
    fun `fetchCurrentQuote should handle missing optional fields`() {
        // Given
        val ticker = "UNKNOWN"
        val mockStock = mockk<Stock>()
        val mockQuote = mockk<StockQuote>()
        val mockStats = mockk<StockStats>()

        every { YahooFinance.get(ticker) } returns mockStock
        every { mockStock.name } returns null
        every { mockStock.quote } returns mockQuote
        every { mockStock.stats } returns mockStats
        every { mockQuote.refresh() } just Runs
        every { mockQuote.price } returns null
        every { mockQuote.changeInPercent } returns null
        every { mockQuote.volume } returns null
        every { mockStats.marketCap } returns null

        // When
        val result = service.fetchCurrentQuote(ticker)

        // Then
        assertEquals("UNKNOWN", result.ticker)
        assertEquals("UNKNOWN", result.companyName)
        assertEquals(0.0, result.currentPrice)
        assertEquals(0.0, result.priceChange)
        assertEquals(0L, result.volume)
        assertNull(result.marketCap)
    }

    @Test
    fun `fetchMultipleQuotes should return map of quotes`() {
        // Given
        val tickers = listOf("AAPL", "TSLA", "MSFT")
        val mockStock1 = createMockStockWithQuote("AAPL", "Apple Inc.", 150.0)
        val mockStock2 = createMockStockWithQuote("TSLA", "Tesla Inc.", 200.0)
        val mockStock3 = createMockStockWithQuote("MSFT", "Microsoft Corp.", 300.0)

        every { YahooFinance.get("AAPL") } returns mockStock1
        every { YahooFinance.get("TSLA") } returns mockStock2
        every { YahooFinance.get("MSFT") } returns mockStock3

        // When
        val result = service.fetchMultipleQuotes(tickers)

        // Then
        assertEquals(3, result.size)
        assertTrue(result.containsKey("AAPL"))
        assertTrue(result.containsKey("TSLA"))
        assertTrue(result.containsKey("MSFT"))
        assertEquals(150.0, result["AAPL"]?.currentPrice)
    }

    @Test
    fun `fetchMultipleQuotes should skip failed tickers`() {
        // Given
        val tickers = listOf("AAPL", "INVALID", "MSFT")
        val mockStock1 = createMockStockWithQuote("AAPL", "Apple Inc.", 150.0)
        val mockStock3 = createMockStockWithQuote("MSFT", "Microsoft Corp.", 300.0)

        every { YahooFinance.get("AAPL") } returns mockStock1
        every { YahooFinance.get("INVALID") } throws RuntimeException("Stock not found")
        every { YahooFinance.get("MSFT") } returns mockStock3

        // When
        val result = service.fetchMultipleQuotes(tickers)

        // Then
        assertEquals(2, result.size)
        assertTrue(result.containsKey("AAPL"))
        assertFalse(result.containsKey("INVALID"))
        assertTrue(result.containsKey("MSFT"))
    }

    // Helper functions
    private fun createMockHistoricalQuote(
        date: Calendar,
        open: Double,
        high: Double,
        low: Double,
        close: Double,
        volume: Long
    ): HistoricalQuote {
        val quote = mockk<HistoricalQuote>()
        every { quote.date } returns date
        every { quote.open } returns BigDecimal(open)
        every { quote.high } returns BigDecimal(high)
        every { quote.low } returns BigDecimal(low)
        every { quote.close } returns BigDecimal(close)
        every { quote.volume } returns volume
        return quote
    }

    private fun createMockStockWithQuote(ticker: String, name: String, price: Double): Stock {
        val stock = mockk<Stock>()
        val quote = mockk<StockQuote>()
        val stats = mockk<StockStats>()

        every { stock.name } returns name
        every { stock.quote } returns quote
        every { stock.stats } returns stats
        every { quote.refresh() } just Runs
        every { quote.price } returns BigDecimal(price)
        every { quote.changeInPercent } returns BigDecimal("1.0")
        every { quote.volume } returns 1000000L
        every { stats.marketCap } returns BigDecimal("1000000000")

        return stock
    }
}
