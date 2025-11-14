package com.jdb.trading.service

import com.jdb.trading.domain.entity.Stock
import com.jdb.trading.domain.entity.StockPrice
import com.jdb.trading.dto.OHLCVDto
import com.jdb.trading.repository.StockPriceRepository
import com.jdb.trading.repository.StockRepository
import mu.KotlinLogging
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneId

private val logger = KotlinLogging.logger {}

/**
 * Service for managing stock price data
 */
@Service
@Transactional
class StockPriceService(
    private val stockRepository: StockRepository,
    private val stockPriceRepository: StockPriceRepository,
    private val yahooFinanceService: YahooFinanceService
) {

    /**
     * Get or fetch stock price data
     * First checks database, then fetches from Yahoo Finance if needed
     */
    fun getStockPriceData(
        ticker: String,
        timeframe: String = "1D",
        start: LocalDate? = null,
        end: LocalDate? = null
    ): List<StockPrice> {
        val stock = getOrCreateStock(ticker)

        // Check if we have data in database
        val existingData = if (start != null && end != null) {
            stockPriceRepository.findByStockAndDateBetweenOrderByDateAsc(
                stock,
                start.atStartOfDay(),
                end.atTime(23, 59, 59)
            )
        } else {
            stockPriceRepository.findByStockOrderByDateDesc(stock).take(500)
        }

        // If we have sufficient data, return it
        if (existingData.isNotEmpty() && existingData.size >= 50) {
            logger.debug { "Retrieved ${existingData.size} price records from database for $ticker" }
            return existingData.sortedBy { it.date }
        }

        // Otherwise, fetch from Yahoo Finance and store
        logger.info { "Fetching fresh data from Yahoo Finance for $ticker" }
        val ohlcvData = yahooFinanceService.fetchStockData(ticker, timeframe, start, end)

        // Store in database
        val stockPrices = ohlcvData.map { ohlcv ->
            StockPrice(
                stock = stock,
                date = LocalDateTime.ofInstant(Instant.parse(ohlcv.time), ZoneId.systemDefault()),
                open = BigDecimal.valueOf(ohlcv.open),
                high = BigDecimal.valueOf(ohlcv.high),
                low = BigDecimal.valueOf(ohlcv.low),
                close = BigDecimal.valueOf(ohlcv.close),
                volume = ohlcv.volume
            )
        }

        // Save to database (batch insert)
        stockPriceRepository.saveAll(stockPrices)
        logger.info { "Stored ${stockPrices.size} price records for $ticker" }

        return stockPrices
    }

    /**
     * Get latest N prices for technical analysis
     */
    fun getLatestPrices(ticker: String, limit: Int = 200): List<StockPrice> {
        val stock = stockRepository.findByTickerIgnoreCase(ticker)
            .orElseGet {
                logger.info { "Stock $ticker not in database, fetching from Yahoo Finance" }
                getOrCreateStock(ticker)
            }

        val prices = stockPriceRepository.findLatestPrices(stock, limit)

        // If we don't have enough data, fetch from Yahoo Finance
        if (prices.size < limit) {
            logger.info { "Only ${prices.size} records found, fetching from Yahoo Finance" }
            return getStockPriceData(ticker, "1D")
        }

        return prices.sortedBy { it.date }
    }

    /**
     * Convert StockPrice entities to OHLCVDto
     */
    fun toOHLCVDto(prices: List<StockPrice>): List<OHLCVDto> {
        return prices.map { price ->
            OHLCVDto(
                time = price.date.atZone(ZoneId.systemDefault()).toInstant().toString(),
                open = price.open.toDouble(),
                high = price.high.toDouble(),
                low = price.low.toDouble(),
                close = price.close.toDouble(),
                volume = price.volume
            )
        }
    }

    /**
     * Get or create a stock entity
     */
    private fun getOrCreateStock(ticker: String): Stock {
        return stockRepository.findByTickerIgnoreCase(ticker).orElseGet {
            // Fetch company info from Yahoo Finance
            val quote = yahooFinanceService.fetchCurrentQuote(ticker)

            val newStock = Stock(
                ticker = ticker.uppercase(),
                companyName = quote.companyName,
                marketCap = quote.marketCap
            )

            stockRepository.save(newStock)
            logger.info { "Created new stock record for $ticker" }
            newStock
        }
    }

    /**
     * Clear old price data for a stock
     */
    fun clearStockPrices(ticker: String) {
        stockRepository.findByTickerIgnoreCase(ticker).ifPresent { stock ->
            stockPriceRepository.deleteByStock(stock)
            logger.info { "Cleared all price data for $ticker" }
        }
    }
}
