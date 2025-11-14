package com.jdb.trading.service

import com.jdb.trading.domain.entity.StockPrice
import com.jdb.trading.dto.StockTechnicalsDto
import mu.KotlinLogging
import org.springframework.stereotype.Service
import org.ta4j.core.BarSeries
import org.ta4j.core.BaseBarSeriesBuilder
import org.ta4j.core.indicators.ATRIndicator
import org.ta4j.core.indicators.RSIIndicator
import org.ta4j.core.indicators.SMAIndicator
import org.ta4j.core.indicators.bollinger.BollingerBandsLowerIndicator
import org.ta4j.core.indicators.bollinger.BollingerBandsMiddleIndicator
import org.ta4j.core.indicators.bollinger.BollingerBandsUpperIndicator
import org.ta4j.core.indicators.helpers.ClosePriceIndicator
import org.ta4j.core.indicators.helpers.VolumeIndicator
import org.ta4j.core.indicators.statistics.StandardDeviationIndicator
import org.ta4j.core.num.DecimalNum
import java.time.ZoneId
import java.time.ZonedDateTime

private val logger = KotlinLogging.logger {}

/**
 * Service for calculating technical indicators using ta4j library
 */
@Service
class TechnicalAnalysisService {

    /**
     * Calculate all technical indicators for a stock
     *
     * @param prices List of stock prices (should be sorted by date ascending)
     * @return StockTechnicalsDto with all calculated indicators
     */
    fun calculateTechnicals(prices: List<StockPrice>): StockTechnicalsDto {
        if (prices.isEmpty()) {
            logger.warn { "No price data provided for technical analysis" }
            return getDefaultTechnicals()
        }

        if (prices.size < 200) {
            logger.warn { "Only ${prices.size} price records available, need 200+ for accurate MA200" }
        }

        try {
            // Convert to ta4j BarSeries
            val series = createBarSeries(prices)

            // Close price indicator (base for most calculations)
            val closePrice = ClosePriceIndicator(series)

            // Moving Averages
            val ma20 = SMAIndicator(closePrice, 20)
            val ma50 = SMAIndicator(closePrice, 50)
            val ma200 = SMAIndicator(closePrice, 200)

            // RSI (14-period)
            val rsi = RSIIndicator(closePrice, 14)

            // Bollinger Bands (20-period, 2 std dev)
            val bbMiddle = BollingerBandsMiddleIndicator(SMAIndicator(closePrice, 20))
            val stdDev = StandardDeviationIndicator(closePrice, 20)
            val bbUpper = BollingerBandsUpperIndicator(bbMiddle, stdDev, DecimalNum.valueOf(2))
            val bbLower = BollingerBandsLowerIndicator(bbMiddle, stdDev, DecimalNum.valueOf(2))

            // ATR (14-period)
            val atr = ATRIndicator(series, 14)

            // Volume indicators
            val volume = VolumeIndicator(series)
            val volumeMA = SMAIndicator(volume, 20)

            // Get the latest (most recent) values
            val endIndex = series.endIndex

            // Current volume (from last price record)
            val currentVolume = prices.last().volume

            return StockTechnicalsDto(
                ma20 = ma20.getValue(endIndex).doubleValue(),
                ma50 = ma50.getValue(endIndex).doubleValue(),
                ma200 = if (prices.size >= 200) ma200.getValue(endIndex).doubleValue() else 0.0,
                rsi = rsi.getValue(endIndex).doubleValue(),
                bollingerUpper = bbUpper.getValue(endIndex).doubleValue(),
                bollingerMiddle = bbMiddle.getValue(endIndex).doubleValue(),
                bollingerLower = bbLower.getValue(endIndex).doubleValue(),
                atr = atr.getValue(endIndex).doubleValue(),
                volume = currentVolume,
                volumeMA = volumeMA.getValue(endIndex).longValueExact()
            )
        } catch (e: Exception) {
            logger.error(e) { "Error calculating technical indicators" }
            return getDefaultTechnicals()
        }
    }

    /**
     * Convert StockPrice list to ta4j BarSeries
     */
    private fun createBarSeries(prices: List<StockPrice>): BarSeries {
        val series = BaseBarSeriesBuilder()
            .withName(prices.firstOrNull()?.stock?.ticker ?: "UNKNOWN")
            .build()

        prices.forEach { price ->
            val zonedDateTime = ZonedDateTime.of(price.date, ZoneId.systemDefault())

            series.addBar(
                zonedDateTime,
                price.open,
                price.high,
                price.low,
                price.close,
                price.volume
            )
        }

        return series
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

    /**
     * Calculate a single indicator (for testing/debugging)
     */
    fun calculateSMA(prices: List<StockPrice>, period: Int): Double {
        if (prices.size < period) {
            return 0.0
        }

        val series = createBarSeries(prices)
        val closePrice = ClosePriceIndicator(series)
        val sma = SMAIndicator(closePrice, period)

        return sma.getValue(series.endIndex).doubleValue()
    }

    /**
     * Calculate RSI (for testing/debugging)
     */
    fun calculateRSI(prices: List<StockPrice>, period: Int = 14): Double {
        if (prices.size < period + 1) {
            return 50.0  // Neutral RSI
        }

        val series = createBarSeries(prices)
        val closePrice = ClosePriceIndicator(series)
        val rsi = RSIIndicator(closePrice, period)

        return rsi.getValue(series.endIndex).doubleValue()
    }
}
