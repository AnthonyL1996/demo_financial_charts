package com.jdb.trading.service

import com.jdb.trading.domain.entity.Stock
import com.jdb.trading.domain.entity.StockPrice
import com.jdb.trading.dto.MLSignalDto
import com.jdb.trading.dto.MultiTimeframeSignalsDto
import com.jdb.trading.dto.ConsensusDto
import com.jdb.trading.dto.OHLCVDto
import com.jdb.trading.dto.StockTechnicalsDto
import com.jdb.trading.repository.StockRepository
import io.mockk.*
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime

class StockServiceTest {

    private lateinit var yahooFinanceService: YahooFinanceService
    private lateinit var stockPriceService: StockPriceService
    private lateinit var technicalAnalysisService: TechnicalAnalysisService
    private lateinit var stockRepository: StockRepository
    private lateinit var mlSignalService: MLSignalService
    private lateinit var service: StockService

    @BeforeEach
    fun setup() {
        yahooFinanceService = mockk()
        stockPriceService = mockk()
        technicalAnalysisService = mockk()
        stockRepository = mockk()
        mlSignalService = mockk()

        service = StockService(
            yahooFinanceService,
            stockPriceService,
            technicalAnalysisService,
            stockRepository,
            mlSignalService
        )
    }

    @AfterEach
    fun tearDown() {
        unmockkAll()
    }

    @Test
    fun `getStock should return complete stock data`() {
        // Given
        val ticker = "AAPL"
        val mockQuote = CurrentQuoteData(
            ticker = "AAPL",
            companyName = "Apple Inc.",
            currentPrice = 150.50,
            priceChange = 2.5,
            volume = 10_000_000L,
            marketCap = 2_500_000_000_000L
        )
        val mockPrices = createMockPrices(50)
        val mockTechnicals = createMockTechnicals()
        val mockMLSignals = createMockMLSignals()

        every { yahooFinanceService.fetchCurrentQuote(ticker) } returns mockQuote
        every { stockPriceService.getLatestPrices(ticker, 200) } returns mockPrices
        every { technicalAnalysisService.calculateTechnicals(mockPrices) } returns mockTechnicals
        every { mlSignalService.generateMultiTimeframeSignals(ticker) } returns mockMLSignals

        // When
        val result = service.getStock(ticker)

        // Then
        assertEquals("AAPL", result.ticker)
        assertEquals("Apple Inc.", result.companyName)
        assertEquals(150.50, result.currentPrice)
        assertEquals(2.5, result.priceChange)
        assertEquals(10_000_000L, result.volume)
        assertEquals(2_500_000_000_000L, result.marketCap)
        assertNotNull(result.technicals)
        assertNotNull(result.mlSignals)
        assertTrue(result.activeSignals.isEmpty())

        verify { yahooFinanceService.fetchCurrentQuote(ticker) }
        verify { stockPriceService.getLatestPrices(ticker, 200) }
        verify { technicalAnalysisService.calculateTechnicals(mockPrices) }
        verify { mlSignalService.generateMultiTimeframeSignals(ticker) }
    }

    @Test
    fun `getStock should handle missing price data with default technicals`() {
        // Given
        val ticker = "AAPL"
        val mockQuote = CurrentQuoteData(
            ticker = "AAPL",
            companyName = "Apple Inc.",
            currentPrice = 150.50,
            priceChange = 2.5,
            volume = 10_000_000L,
            marketCap = 2_500_000_000_000L
        )

        every { yahooFinanceService.fetchCurrentQuote(ticker) } returns mockQuote
        every { stockPriceService.getLatestPrices(ticker, 200) } returns emptyList()
        every { mlSignalService.generateMultiTimeframeSignals(ticker) } returns null

        // When
        val result = service.getStock(ticker)

        // Then
        assertEquals("AAPL", result.ticker)
        assertNotNull(result.technicals)
        assertEquals(0.0, result.technicals.ma20)
        assertEquals(50.0, result.technicals.rsi)
        assertNull(result.mlSignals)
    }

    @Test
    fun `getStock should handle technical analysis failure gracefully`() {
        // Given
        val ticker = "AAPL"
        val mockQuote = CurrentQuoteData(
            ticker = "AAPL",
            companyName = "Apple Inc.",
            currentPrice = 150.50,
            priceChange = 2.5,
            volume = 10_000_000L,
            marketCap = 2_500_000_000_000L
        )

        every { yahooFinanceService.fetchCurrentQuote(ticker) } returns mockQuote
        every { stockPriceService.getLatestPrices(ticker, 200) } throws RuntimeException("Database error")
        every { mlSignalService.generateMultiTimeframeSignals(ticker) } returns null

        // When
        val result = service.getStock(ticker)

        // Then
        assertEquals("AAPL", result.ticker)
        assertNotNull(result.technicals)
        assertEquals(0.0, result.technicals.ma20)
    }

    @Test
    fun `getStock should handle ML service failure gracefully`() {
        // Given
        val ticker = "AAPL"
        val mockQuote = CurrentQuoteData(
            ticker = "AAPL",
            companyName = "Apple Inc.",
            currentPrice = 150.50,
            priceChange = 2.5,
            volume = 10_000_000L,
            marketCap = 2_500_000_000_000L
        )
        val mockPrices = createMockPrices(50)
        val mockTechnicals = createMockTechnicals()

        every { yahooFinanceService.fetchCurrentQuote(ticker) } returns mockQuote
        every { stockPriceService.getLatestPrices(ticker, 200) } returns mockPrices
        every { technicalAnalysisService.calculateTechnicals(mockPrices) } returns mockTechnicals
        every { mlSignalService.generateMultiTimeframeSignals(ticker) } throws RuntimeException("ML service down")

        // When
        val result = service.getStock(ticker)

        // Then
        assertEquals("AAPL", result.ticker)
        assertNotNull(result.technicals)
        assertNull(result.mlSignals)
    }

    @Test
    fun `getStocks should return multiple stocks without search`() {
        // Given
        val limit = 3
        val mockQuote1 = CurrentQuoteData("AAPL", "Apple Inc.", 150.0, 2.5, 10_000_000L, 2_500_000_000_000L)
        val mockQuote2 = CurrentQuoteData("TSLA", "Tesla Inc.", 200.0, 3.0, 15_000_000L, 600_000_000_000L)
        val mockQuote3 = CurrentQuoteData("MSFT", "Microsoft Corp.", 300.0, 1.5, 8_000_000L, 2_200_000_000_000L)
        val mockPrices = createMockPrices(50)
        val mockTechnicals = createMockTechnicals()

        every { yahooFinanceService.fetchCurrentQuote("AAPL") } returns mockQuote1
        every { yahooFinanceService.fetchCurrentQuote("TSLA") } returns mockQuote2
        every { yahooFinanceService.fetchCurrentQuote("MSFT") } returns mockQuote3
        every { stockPriceService.getLatestPrices(any(), 200) } returns mockPrices
        every { technicalAnalysisService.calculateTechnicals(mockPrices) } returns mockTechnicals
        every { mlSignalService.generateMultiTimeframeSignals(any()) } returns null

        // When
        val result = service.getStocks(search = null, limit = limit)

        // Then
        assertEquals(3, result.size)
        assertEquals("AAPL", result[0].ticker)
        assertEquals("TSLA", result[1].ticker)
        assertEquals("MSFT", result[2].ticker)
    }

    @Test
    fun `getStocks should return single stock with search parameter`() {
        // Given
        val search = "GOOGL"
        val mockQuote = CurrentQuoteData("GOOGL", "Alphabet Inc.", 140.0, 1.8, 5_000_000L, 1_800_000_000_000L)
        val mockPrices = createMockPrices(50)
        val mockTechnicals = createMockTechnicals()

        every { yahooFinanceService.fetchCurrentQuote("GOOGL") } returns mockQuote
        every { stockPriceService.getLatestPrices("GOOGL", 200) } returns mockPrices
        every { technicalAnalysisService.calculateTechnicals(mockPrices) } returns mockTechnicals
        every { mlSignalService.generateMultiTimeframeSignals("GOOGL") } returns null

        // When
        val result = service.getStocks(search = search, limit = null)

        // Then
        assertEquals(1, result.size)
        assertEquals("GOOGL", result[0].ticker)
    }

    @Test
    fun `getStocks should skip failed tickers`() {
        // Given
        val limit = 3
        val mockQuote1 = CurrentQuoteData("AAPL", "Apple Inc.", 150.0, 2.5, 10_000_000L, 2_500_000_000_000L)
        val mockQuote3 = CurrentQuoteData("MSFT", "Microsoft Corp.", 300.0, 1.5, 8_000_000L, 2_200_000_000_000L)
        val mockPrices = createMockPrices(50)
        val mockTechnicals = createMockTechnicals()

        every { yahooFinanceService.fetchCurrentQuote("AAPL") } returns mockQuote1
        every { yahooFinanceService.fetchCurrentQuote("TSLA") } throws RuntimeException("Stock not found")
        every { yahooFinanceService.fetchCurrentQuote("MSFT") } returns mockQuote3
        every { stockPriceService.getLatestPrices(any(), 200) } returns mockPrices
        every { technicalAnalysisService.calculateTechnicals(mockPrices) } returns mockTechnicals
        every { mlSignalService.generateMultiTimeframeSignals(any()) } returns null

        // When
        val result = service.getStocks(search = null, limit = limit)

        // Then
        assertEquals(2, result.size)
        assertEquals("AAPL", result[0].ticker)
        assertEquals("MSFT", result[1].ticker)
    }

    @Test
    fun `getStockData should return OHLCV data`() {
        // Given
        val ticker = "AAPL"
        val timeframe = "1D"
        val start = LocalDate.of(2024, 1, 1)
        val end = LocalDate.of(2024, 1, 31)
        val mockPrices = createMockPrices(30)
        val mockOHLCV = listOf(
            OHLCVDto("2024-01-01T00:00:00Z", 150.0, 155.0, 149.0, 154.0, 1_000_000L),
            OHLCVDto("2024-01-02T00:00:00Z", 154.0, 158.0, 153.0, 157.0, 1_200_000L)
        )

        every { stockPriceService.getStockPriceData(ticker, timeframe, start, end) } returns mockPrices
        every { stockPriceService.toOHLCVDto(mockPrices) } returns mockOHLCV

        // When
        val result = service.getStockData(ticker, timeframe, start, end)

        // Then
        assertEquals(2, result.size)
        assertEquals(150.0, result[0].open)
        assertEquals(154.0, result[1].open)

        verify { stockPriceService.getStockPriceData(ticker, timeframe, start, end) }
        verify { stockPriceService.toOHLCVDto(mockPrices) }
    }

    @Test
    fun `getTechnicals should return calculated technicals`() {
        // Given
        val ticker = "AAPL"
        val mockPrices = createMockPrices(200)
        val mockTechnicals = createMockTechnicals()

        every { stockPriceService.getLatestPrices(ticker, 200) } returns mockPrices
        every { technicalAnalysisService.calculateTechnicals(mockPrices) } returns mockTechnicals

        // When
        val result = service.getTechnicals(ticker)

        // Then
        assertNotNull(result)
        assertEquals(150.5, result.ma20)
        assertEquals(148.0, result.ma50)
        assertEquals(145.0, result.ma200)
        assertEquals(65.5, result.rsi)

        verify { stockPriceService.getLatestPrices(ticker, 200) }
        verify { technicalAnalysisService.calculateTechnicals(mockPrices) }
    }

    @Test
    fun `getTechnicals should return default values when no price data`() {
        // Given
        val ticker = "AAPL"

        every { stockPriceService.getLatestPrices(ticker, 200) } returns emptyList()

        // When
        val result = service.getTechnicals(ticker)

        // Then
        assertNotNull(result)
        assertEquals(0.0, result.ma20)
        assertEquals(0.0, result.ma50)
        assertEquals(0.0, result.ma200)
        assertEquals(50.0, result.rsi)
    }

    @Test
    fun `getTechnicals should return default values on error`() {
        // Given
        val ticker = "AAPL"

        every { stockPriceService.getLatestPrices(ticker, 200) } throws RuntimeException("Database error")

        // When
        val result = service.getTechnicals(ticker)

        // Then
        assertNotNull(result)
        assertEquals(0.0, result.ma20)
        assertEquals(50.0, result.rsi)
    }

    // Helper functions
    private fun createMockPrices(count: Int): List<StockPrice> {
        val stock = Stock(
            id = 1L,
            ticker = "AAPL",
            companyName = "Apple Inc.",
            isActive = true
        )

        return (0 until count).map { i ->
            StockPrice(
                stock = stock,
                date = LocalDateTime.now().minusDays(i.toLong()),
                open = BigDecimal.valueOf(150.0),
                high = BigDecimal.valueOf(155.0),
                low = BigDecimal.valueOf(149.0),
                close = BigDecimal.valueOf(154.0),
                volume = 1_000_000L
            )
        }
    }

    private fun createMockTechnicals(): StockTechnicalsDto {
        return StockTechnicalsDto(
            ma20 = 150.5,
            ma50 = 148.0,
            ma200 = 145.0,
            rsi = 65.5,
            bollingerUpper = 155.0,
            bollingerMiddle = 150.0,
            bollingerLower = 145.0,
            atr = 2.5,
            volume = 1_000_000L,
            volumeMA = 1_200_000L
        )
    }

    private fun createMockMLSignals(): MultiTimeframeSignalsDto {
        return MultiTimeframeSignalsDto(
            ticker = "AAPL",
            daily = MLSignalDto("AAPL", "daily", "BUY", 0.85, 160.0, 150.0, "Bullish"),
            weekly = MLSignalDto("AAPL", "weekly", "BUY", 0.75, 165.0, 150.0, "Uptrend"),
            monthly = MLSignalDto("AAPL", "monthly", "HOLD", 0.60, 155.0, 150.0, "Neutral"),
            consensus = ConsensusDto("BUY", 0.73, "Majority bullish signals")
        )
    }
}
