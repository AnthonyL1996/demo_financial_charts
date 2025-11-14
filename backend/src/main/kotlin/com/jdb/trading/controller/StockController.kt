package com.jdb.trading.controller

import com.jdb.trading.dto.ApiResponse
import com.jdb.trading.dto.OHLCVDto
import com.jdb.trading.dto.StockDto
import com.jdb.trading.dto.StockTechnicalsDto
import com.jdb.trading.service.StockService
import mu.KotlinLogging
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*
import java.time.LocalDate

private val logger = KotlinLogging.logger {}

/**
 * REST controller for stock-related endpoints
 * Matches frontend API expectations from lib/api/endpoints.ts
 *
 * Phase 2: Now includes real technical analysis calculations
 */
@RestController
@RequestMapping("/api/stocks")
class StockController(
    private val stockService: StockService
) {

    /**
     * GET /api/stocks
     * Get list of stocks with real-time data and technical indicators
     * Matches: stocksApi.getStocks()
     */
    @GetMapping
    fun getStocks(
        @RequestParam(required = false) search: String?,
        @RequestParam(required = false) limit: Int?
    ): ResponseEntity<ApiResponse<List<StockDto>>> {
        logger.info { "GET /api/stocks - search: $search, limit: $limit" }

        val stocks = stockService.getStocks(search, limit)
        return ResponseEntity.ok(ApiResponse.success(stocks))
    }

    /**
     * GET /api/stocks/{ticker}
     * Get detailed stock information with technical indicators
     * Matches: stocksApi.getStock(ticker)
     */
    @GetMapping("/{ticker}")
    fun getStock(@PathVariable ticker: String): ResponseEntity<ApiResponse<StockDto>> {
        logger.info { "GET /api/stocks/$ticker" }

        val stock = stockService.getStock(ticker)
        return ResponseEntity.ok(ApiResponse.success(stock))
    }

    /**
     * GET /api/stocks/{ticker}/data
     * Get OHLCV historical price data (with database caching)
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

        val data = stockService.getStockData(
            ticker = ticker,
            timeframe = timeframe ?: "1D",
            start = startDate,
            end = endDate
        )

        return ResponseEntity.ok(ApiResponse.success(data))
    }

    /**
     * GET /api/stocks/{ticker}/technicals
     * Get technical indicators for a stock (calculated with ta4j)
     * Matches: stocksApi.getTechnicals(ticker)
     *
     * Returns: MA20, MA50, MA200, RSI, Bollinger Bands, ATR, Volume MA
     */
    @GetMapping("/{ticker}/technicals")
    fun getTechnicals(@PathVariable ticker: String): ResponseEntity<ApiResponse<StockTechnicalsDto>> {
        logger.info { "GET /api/stocks/$ticker/technicals" }

        val technicals = stockService.getTechnicals(ticker)
        return ResponseEntity.ok(ApiResponse.success(technicals))
    }
}
