package com.jdb.trading.controller

import com.jdb.trading.dto.ApiResponse
import com.jdb.trading.dto.OHLCVDto
import com.jdb.trading.dto.StockDto
import com.jdb.trading.dto.StockTechnicalsDto
import com.jdb.trading.service.YahooFinanceService
import mu.KotlinLogging
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*
import java.time.LocalDate

private val logger = KotlinLogging.logger {}

/**
 * REST controller for stock-related endpoints
 * Matches frontend API expectations from lib/api/endpoints.ts
 */
@RestController
@RequestMapping("/api/stocks")
class StockController(
    private val yahooFinanceService: YahooFinanceService
) {

    /**
     * GET /api/stocks
     * Get list of stocks (currently returns mock data - will be enhanced later)
     * Matches: stocksApi.getStocks()
     */
    @GetMapping
    fun getStocks(
        @RequestParam(required = false) search: String?,
        @RequestParam(required = false) limit: Int?
    ): ResponseEntity<ApiResponse<List<StockDto>>> {
        logger.info { "GET /api/stocks - search: $search, limit: $limit" }

        // For now, return a predefined list of popular stocks
        val popularTickers = listOf("AAPL", "TSLA", "MSFT", "NVDA", "GOOGL", "AMZN", "META")
        val tickers = if (search != null) {
            listOf(search.uppercase())
        } else {
            popularTickers.take(limit ?: 10)
        }

        val stocks = tickers.mapNotNull { ticker ->
            try {
                val quote = yahooFinanceService.fetchCurrentQuote(ticker)
                StockDto(
                    ticker = quote.ticker,
                    companyName = quote.companyName,
                    currentPrice = quote.currentPrice,
                    priceChange = quote.priceChange,
                    volume = quote.volume,
                    marketCap = quote.marketCap,
                    technicals = getDefaultTechnicals(),  // Will be calculated later
                    activeSignals = emptyList()  // Will be populated later
                )
            } catch (e: Exception) {
                logger.warn(e) { "Failed to fetch stock data for $ticker" }
                null
            }
        }

        return ResponseEntity.ok(ApiResponse.success(stocks))
    }

    /**
     * GET /api/stocks/{ticker}
     * Get detailed stock information
     * Matches: stocksApi.getStock(ticker)
     */
    @GetMapping("/{ticker}")
    fun getStock(@PathVariable ticker: String): ResponseEntity<ApiResponse<StockDto>> {
        logger.info { "GET /api/stocks/$ticker" }

        val quote = yahooFinanceService.fetchCurrentQuote(ticker)

        val stock = StockDto(
            ticker = quote.ticker,
            companyName = quote.companyName,
            currentPrice = quote.currentPrice,
            priceChange = quote.priceChange,
            volume = quote.volume,
            marketCap = quote.marketCap,
            technicals = getDefaultTechnicals(),  // Will be calculated later
            activeSignals = emptyList()  // Will be populated later
        )

        return ResponseEntity.ok(ApiResponse.success(stock))
    }

    /**
     * GET /api/stocks/{ticker}/data
     * Get OHLCV historical price data
     * Matches: stocksApi.getStockData(ticker, params)
     *
     * Query params:
     * - timeframe: 1D, 1W, 1M (default: 1D)
     * - start: Start date in ISO format (YYYY-MM-DD)
     * - end: End date in ISO format (YYYY-MM-DD)
     */
    @GetMapping("/{ticker}/data")
    fun getStockData(
        @PathVariable ticker: String,
        @RequestParam(required = false) timeframe: String?,
        @RequestParam(required = false) start: String?,
        @RequestParam(required = false) end: String?
    ): ResponseEntity<ApiResponse<List<OHLCVDto>>> {
        logger.info { "GET /api/stocks/$ticker/data - timeframe: $timeframe, start: $start, end: $end" }

        val startDate = start?.let { LocalDate.parse(it) }
        val endDate = end?.let { LocalDate.parse(it) }

        val data = yahooFinanceService.fetchStockData(
            ticker = ticker,
            timeframe = timeframe ?: "1D",
            start = startDate,
            end = endDate
        )

        return ResponseEntity.ok(ApiResponse.success(data))
    }

    /**
     * GET /api/stocks/{ticker}/technicals
     * Get technical indicators for a stock
     * Matches: stocksApi.getTechnicals(ticker)
     */
    @GetMapping("/{ticker}/technicals")
    fun getTechnicals(@PathVariable ticker: String): ResponseEntity<ApiResponse<StockTechnicalsDto>> {
        logger.info { "GET /api/stocks/$ticker/technicals" }

        // For now, return default technicals
        // Will be calculated from actual price data in Phase 2
        val technicals = getDefaultTechnicals()

        return ResponseEntity.ok(ApiResponse.success(technicals))
    }

    /**
     * Default/placeholder technical indicators
     * Will be replaced with actual calculations in Phase 2
     */
    private fun getDefaultTechnicals(): StockTechnicalsDto {
        return StockTechnicalsDto(
            ma20 = 0.0,
            ma50 = 0.0,
            ma200 = 0.0,
            rsi = 50.0,
            bollingerUpper = 0.0,
            bollingerMiddle = 0.0,
            bollingerLower = 0.0,
            atr = 0.0,
            volume = 0L,
            volumeMA = 0L
        )
    }
}
