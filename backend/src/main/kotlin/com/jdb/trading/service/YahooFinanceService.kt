package com.jdb.trading.service

import com.jdb.trading.dto.OHLCVDto
import mu.KotlinLogging
import org.springframework.beans.factory.annotation.Value
import org.springframework.cache.annotation.Cacheable
import org.springframework.stereotype.Service
import yahoofinance.YahooFinance
import yahoofinance.histquotes.HistoricalQuote
import yahoofinance.histquotes.Interval
import java.math.BigDecimal
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.util.*

private val logger = KotlinLogging.logger {}

/**
 * Service for fetching stock data from Yahoo Finance API
 */
@Service
class YahooFinanceService(
    @Value("\${yahoo-finance.cache-duration-seconds:300}")
    private val cacheDuration: Long,

    @Value("\${yahoo-finance.retry-attempts:3}")
    private val retryAttempts: Int,

    @Value("\${yahoo-finance.retry-delay-ms:1000}")
    private val retryDelay: Long
) {

    /**
     * Fetch OHLCV data from Yahoo Finance
     * Matches frontend API: GET /stocks/{ticker}/data
     *
     * @param ticker Stock ticker symbol (e.g., AAPL, TSLA)
     * @param timeframe Time interval: 1D (daily), 1W (weekly), 1M (monthly)
     * @param start Start date (optional, defaults to 6 months ago)
     * @param end End date (optional, defaults to today)
     * @return List of OHLCV data points
     */
    @Cacheable(value = ["stockData"], key = "#ticker + '-' + #timeframe + '-' + #start + '-' + #end")
    fun fetchStockData(
        ticker: String,
        timeframe: String = "1D",
        start: LocalDate? = null,
        end: LocalDate? = null
    ): List<OHLCVDto> {
        logger.info { "Fetching stock data for $ticker with timeframe $timeframe" }

        return retryOperation {
            val stock = YahooFinance.get(ticker.uppercase())
                ?: throw IllegalArgumentException("Stock not found: $ticker")

            val interval = when (timeframe) {
                "1W" -> Interval.WEEKLY
                "1M" -> Interval.MONTHLY
                else -> Interval.DAILY
            }

            val calendar = Calendar.getInstance()
            val fromCalendar = start?.let {
                Calendar.getInstance().apply {
                    time = Date.from(it.atStartOfDay(ZoneId.systemDefault()).toInstant())
                }
            } ?: Calendar.getInstance().apply {
                add(Calendar.MONTH, -6)  // Default: 6 months of data
            }

            val toCalendar = end?.let {
                Calendar.getInstance().apply {
                    time = Date.from(it.atStartOfDay(ZoneId.systemDefault()).toInstant())
                }
            } ?: Calendar.getInstance()

            val history = stock.getHistory(fromCalendar, toCalendar, interval)
                ?: throw IllegalStateException("No historical data available for $ticker")

            history.map { quote -> quote.toOHLCVDto() }
                .sortedBy { it.time }  // Ensure chronological order
        }
    }

    /**
     * Fetch current stock quote
     *
     * @param ticker Stock ticker symbol
     * @return Current price, volume, and market cap
     */
    @Cacheable(value = ["currentQuote"], key = "#ticker")
    fun fetchCurrentQuote(ticker: String): CurrentQuoteData {
        logger.info { "Fetching current quote for $ticker" }

        return retryOperation {
            val stock = YahooFinance.get(ticker.uppercase())
                ?: throw IllegalArgumentException("Stock not found: $ticker")

            stock.quote.refresh()  // Ensure latest data

            val quote = stock.quote
            val stats = stock.stats

            CurrentQuoteData(
                ticker = ticker.uppercase(),
                companyName = stock.name ?: ticker.uppercase(),
                currentPrice = quote.price?.toDouble() ?: 0.0,
                priceChange = quote.changeInPercent?.toDouble() ?: 0.0,
                volume = quote.volume ?: 0L,
                marketCap = stats?.marketCap?.toLong()
            )
        }
    }

    /**
     * Fetch multiple stock quotes at once (batch operation)
     */
    fun fetchMultipleQuotes(tickers: List<String>): Map<String, CurrentQuoteData> {
        logger.info { "Fetching quotes for ${tickers.size} stocks" }

        return tickers.associateWith { ticker ->
            try {
                fetchCurrentQuote(ticker)
            } catch (e: Exception) {
                logger.warn(e) { "Failed to fetch quote for $ticker" }
                null
            }
        }.filterValues { it != null }
            .mapValues { it.value!! }
    }

    /**
     * Retry operation with exponential backoff
     */
    private fun <T> retryOperation(operation: () -> T): T {
        var lastException: Exception? = null
        var delay = retryDelay

        repeat(retryAttempts) { attempt ->
            try {
                return operation()
            } catch (e: Exception) {
                lastException = e
                logger.warn(e) { "Attempt ${attempt + 1} failed, retrying after ${delay}ms..." }

                if (attempt < retryAttempts - 1) {
                    Thread.sleep(delay)
                    delay *= 2  // Exponential backoff
                }
            }
        }

        throw lastException ?: IllegalStateException("All retry attempts failed")
    }

    /**
     * Convert Yahoo Finance HistoricalQuote to OHLCVDto
     */
    private fun HistoricalQuote.toOHLCVDto(): OHLCVDto {
        return OHLCVDto(
            time = this.date.toInstant().toString(),  // ISO 8601 format
            open = this.open?.toDouble() ?: 0.0,
            high = this.high?.toDouble() ?: 0.0,
            low = this.low?.toDouble() ?: 0.0,
            close = this.close?.toDouble() ?: 0.0,
            volume = this.volume ?: 0L
        )
    }
}

/**
 * Data class for current stock quote information
 */
data class CurrentQuoteData(
    val ticker: String,
    val companyName: String,
    val currentPrice: Double,
    val priceChange: Double,  // Percentage
    val volume: Long,
    val marketCap: Long? = null
)
