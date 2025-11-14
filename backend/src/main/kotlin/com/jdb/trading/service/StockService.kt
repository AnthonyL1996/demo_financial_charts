package com.jdb.trading.service

import com.jdb.trading.dto.OHLCVDto
import com.jdb.trading.dto.StockDto
import com.jdb.trading.dto.StockTechnicalsDto
import com.jdb.trading.repository.StockRepository
import mu.KotlinLogging
import org.springframework.cache.annotation.Cacheable
import org.springframework.stereotype.Service
import java.time.LocalDate

private val logger = KotlinLogging.logger {}

/**
 * Main service for stock-related operations
 * Coordinates between YahooFinanceService, StockPriceService, and TechnicalAnalysisService
 */
@Service
class StockService(
    private val yahooFinanceService: YahooFinanceService,
    private val stockPriceService: StockPriceService,
    private val technicalAnalysisService: TechnicalAnalysisService,
    private val stockRepository: StockRepository
) {

    /**
     * Get stock with current quote and technical indicators
     */
    @Cacheable(value = ["stockDetails"], key = "#ticker")
    fun getStock(ticker: String): StockDto {
        logger.info { "Getting stock details for $ticker" }

        // Fetch current quote from Yahoo Finance
        val quote = yahooFinanceService.fetchCurrentQuote(ticker)

        // Get price history and calculate technicals
        val technicals = try {
            val prices = stockPriceService.getLatestPrices(ticker, 200)
            if (prices.isNotEmpty()) {
                technicalAnalysisService.calculateTechnicals(prices)
            } else {
                getDefaultTechnicals()
            }
        } catch (e: Exception) {
            logger.warn(e) { "Failed to calculate technicals for $ticker" }
            getDefaultTechnicals()
        }

        return StockDto(
            ticker = quote.ticker,
            companyName = quote.companyName,
            currentPrice = quote.currentPrice,
            priceChange = quote.priceChange,
            volume = quote.volume,
            marketCap = quote.marketCap,
            technicals = technicals,
            activeSignals = emptyList()  // TODO: Implement in Phase 3
        )
    }

    /**
     * Get multiple stocks
     */
    fun getStocks(search: String?, limit: Int?): List<StockDto> {
        val popularTickers = listOf("AAPL", "TSLA", "MSFT", "NVDA", "GOOGL", "AMZN", "META")

        val tickers = if (search != null) {
            listOf(search.uppercase())
        } else {
            popularTickers.take(limit ?: 10)
        }

        return tickers.mapNotNull { ticker ->
            try {
                getStock(ticker)
            } catch (e: Exception) {
                logger.warn(e) { "Failed to fetch stock data for $ticker" }
                null
            }
        }
    }

    /**
     * Get OHLCV data for a stock
     */
    fun getStockData(
        ticker: String,
        timeframe: String,
        start: LocalDate?,
        end: LocalDate?
    ): List<OHLCVDto> {
        logger.info { "Getting OHLCV data for $ticker (timeframe: $timeframe)" }

        // Get from database or fetch from Yahoo Finance
        val prices = stockPriceService.getStockPriceData(ticker, timeframe, start, end)

        // Convert to DTO
        return stockPriceService.toOHLCVDto(prices)
    }

    /**
     * Get technical indicators for a stock
     */
    @Cacheable(value = ["technicals"], key = "#ticker")
    fun getTechnicals(ticker: String): StockTechnicalsDto {
        logger.info { "Getting technical indicators for $ticker" }

        return try {
            val prices = stockPriceService.getLatestPrices(ticker, 200)
            if (prices.isNotEmpty()) {
                technicalAnalysisService.calculateTechnicals(prices)
            } else {
                logger.warn { "No price data available for $ticker" }
                getDefaultTechnicals()
            }
        } catch (e: Exception) {
            logger.error(e) { "Error calculating technicals for $ticker" }
            getDefaultTechnicals()
        }
    }

    /**
     * Default/placeholder technical indicators
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
