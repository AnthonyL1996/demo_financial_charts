package com.jdb.trading.controller

import com.jdb.trading.dto.OHLCVDto
import com.jdb.trading.dto.StockDto
import com.jdb.trading.dto.StockTechnicalsDto
import com.jdb.trading.service.StockService
import com.ninjasquad.springmockk.MockkBean
import io.mockk.every
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest
import org.springframework.http.MediaType
import org.springframework.test.context.ActiveProfiles
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.*
import java.time.LocalDate

@WebMvcTest(StockController::class)
@ActiveProfiles("test")
class StockControllerTest {

    @Autowired
    private lateinit var mockMvc: MockMvc

    @MockkBean
    private lateinit var stockService: StockService

    @Test
    fun `GET stocks should return list of stocks`() {
        // Given
        val mockStocks = listOf(
            createMockStockDto("AAPL", "Apple Inc.", 150.50),
            createMockStockDto("TSLA", "Tesla Inc.", 200.00),
            createMockStockDto("MSFT", "Microsoft Corp.", 300.00)
        )
        every { stockService.getStocks(null, null) } returns mockStocks

        // When/Then
        mockMvc.perform(get("/api/stocks"))
            .andExpect(status().isOk)
            .andExpect(content().contentType(MediaType.APPLICATION_JSON))
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data").isArray)
            .andExpect(jsonPath("$.data.length()").value(3))
            .andExpect(jsonPath("$.data[0].ticker").value("AAPL"))
            .andExpect(jsonPath("$.data[0].companyName").value("Apple Inc."))
            .andExpect(jsonPath("$.data[0].currentPrice").value(150.50))
            .andExpect(jsonPath("$.data[1].ticker").value("TSLA"))
            .andExpect(jsonPath("$.data[2].ticker").value("MSFT"))
    }

    @Test
    fun `GET stocks with search parameter should return filtered stocks`() {
        // Given
        val mockStocks = listOf(
            createMockStockDto("GOOGL", "Alphabet Inc.", 140.00)
        )
        every { stockService.getStocks("GOOGL", null) } returns mockStocks

        // When/Then
        mockMvc.perform(get("/api/stocks").param("search", "GOOGL"))
            .andExpect(status().isOk)
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data.length()").value(1))
            .andExpect(jsonPath("$.data[0].ticker").value("GOOGL"))
            .andExpect(jsonPath("$.data[0].companyName").value("Alphabet Inc."))
    }

    @Test
    fun `GET stocks with limit parameter should return limited stocks`() {
        // Given
        val mockStocks = listOf(
            createMockStockDto("AAPL", "Apple Inc.", 150.50),
            createMockStockDto("TSLA", "Tesla Inc.", 200.00)
        )
        every { stockService.getStocks(null, 2) } returns mockStocks

        // When/Then
        mockMvc.perform(get("/api/stocks").param("limit", "2"))
            .andExpect(status().isOk)
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data.length()").value(2))
    }

    @Test
    fun `GET stocks ticker should return single stock`() {
        // Given
        val ticker = "AAPL"
        val mockStock = createMockStockDto(ticker, "Apple Inc.", 150.50)
        every { stockService.getStock(ticker) } returns mockStock

        // When/Then
        mockMvc.perform(get("/api/stocks/$ticker"))
            .andExpect(status().isOk)
            .andExpect(content().contentType(MediaType.APPLICATION_JSON))
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data.ticker").value("AAPL"))
            .andExpect(jsonPath("$.data.companyName").value("Apple Inc."))
            .andExpect(jsonPath("$.data.currentPrice").value(150.50))
            .andExpect(jsonPath("$.data.priceChange").value(2.5))
            .andExpect(jsonPath("$.data.volume").value(10000000))
    }

    @Test
    fun `GET stocks ticker data should return OHLCV data`() {
        // Given
        val ticker = "AAPL"
        val mockData = listOf(
            OHLCVDto("2024-01-01T00:00:00Z", 150.0, 155.0, 149.0, 154.0, 1_000_000L),
            OHLCVDto("2024-01-02T00:00:00Z", 154.0, 158.0, 153.0, 157.0, 1_200_000L)
        )
        every { stockService.getStockData(ticker, "1D", null, null) } returns mockData

        // When/Then
        mockMvc.perform(get("/api/stocks/$ticker/data"))
            .andExpect(status().isOk)
            .andExpect(content().contentType(MediaType.APPLICATION_JSON))
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data").isArray)
            .andExpect(jsonPath("$.data.length()").value(2))
            .andExpect(jsonPath("$.data[0].time").value("2024-01-01T00:00:00Z"))
            .andExpect(jsonPath("$.data[0].open").value(150.0))
            .andExpect(jsonPath("$.data[0].high").value(155.0))
            .andExpect(jsonPath("$.data[0].low").value(149.0))
            .andExpect(jsonPath("$.data[0].close").value(154.0))
            .andExpect(jsonPath("$.data[0].volume").value(1000000))
    }

    @Test
    fun `GET stocks ticker data with timeframe should return data for timeframe`() {
        // Given
        val ticker = "AAPL"
        val mockData = listOf(
            OHLCVDto("2024-01-01T00:00:00Z", 150.0, 160.0, 148.0, 158.0, 5_000_000L)
        )
        every { stockService.getStockData(ticker, "1W", null, null) } returns mockData

        // When/Then
        mockMvc.perform(get("/api/stocks/$ticker/data").param("timeframe", "1W"))
            .andExpect(status().isOk)
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data.length()").value(1))
    }

    @Test
    fun `GET stocks ticker data with date range should return data for range`() {
        // Given
        val ticker = "AAPL"
        val start = "2024-01-01"
        val end = "2024-01-31"
        val startDate = LocalDate.parse(start)
        val endDate = LocalDate.parse(end)
        val mockData = listOf(
            OHLCVDto("2024-01-15T00:00:00Z", 150.0, 155.0, 149.0, 154.0, 1_000_000L)
        )
        every { stockService.getStockData(ticker, "1D", startDate, endDate) } returns mockData

        // When/Then
        mockMvc.perform(
            get("/api/stocks/$ticker/data")
                .param("start", start)
                .param("end", end)
        )
            .andExpect(status().isOk)
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data").isArray)
    }

    @Test
    fun `GET stocks ticker technicals should return technical indicators`() {
        // Given
        val ticker = "AAPL"
        val mockTechnicals = StockTechnicalsDto(
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
        every { stockService.getTechnicals(ticker) } returns mockTechnicals

        // When/Then
        mockMvc.perform(get("/api/stocks/$ticker/technicals"))
            .andExpect(status().isOk)
            .andExpect(content().contentType(MediaType.APPLICATION_JSON))
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data.ma20").value(150.5))
            .andExpect(jsonPath("$.data.ma50").value(148.0))
            .andExpect(jsonPath("$.data.ma200").value(145.0))
            .andExpect(jsonPath("$.data.rsi").value(65.5))
            .andExpect(jsonPath("$.data.bollingerUpper").value(155.0))
            .andExpect(jsonPath("$.data.bollingerMiddle").value(150.0))
            .andExpect(jsonPath("$.data.bollingerLower").value(145.0))
            .andExpect(jsonPath("$.data.atr").value(2.5))
            .andExpect(jsonPath("$.data.volume").value(1000000))
            .andExpect(jsonPath("$.data.volumeMA").value(1200000))
    }

    @Test
    fun `GET stocks with invalid ticker should handle exception`() {
        // Given
        val ticker = "INVALID"
        every { stockService.getStock(ticker) } throws IllegalArgumentException("Stock not found")

        // When/Then
        mockMvc.perform(get("/api/stocks/$ticker"))
            .andExpect(status().isInternalServerError)
    }

    // Helper functions
    private fun createMockStockDto(ticker: String, companyName: String, price: Double): StockDto {
        return StockDto(
            ticker = ticker,
            companyName = companyName,
            currentPrice = price,
            priceChange = 2.5,
            volume = 10_000_000L,
            marketCap = 2_500_000_000_000L,
            technicals = StockTechnicalsDto(
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
            ),
            activeSignals = emptyList(),
            mlSignals = null
        )
    }
}
