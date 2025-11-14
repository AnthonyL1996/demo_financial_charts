package com.jdb.trading.dto

/**
 * Signal data transfer object matching frontend Signal interface
 */
data class SignalDto(
    val id: String,
    val ticker: String,
    val companyName: String,
    val type: String,  // LONG, SHORT, NEUTRAL
    val status: String,  // ACTIVE, CLOSED, EXPIRED
    val confidence: Int,  // 0-100
    val expectedReturn: Double,
    val entryPrice: Double,
    val targetPrice: Double,
    val stopLoss: Double,
    val riskRewardRatio: Double,
    val generatedAt: String,  // ISO date string
    val expiresAt: String,
    val closedAt: String? = null,
    val timeframe: String,  // 1D, 1W, 1M, 3M
    val reasoning: SignalReasoningDto,
    val actualReturn: Double? = null,
    val exitPrice: Double? = null
)

/**
 * Signal reasoning matching frontend SignalReasoning interface
 */
data class SignalReasoningDto(
    val dominantMA: DominantMADto,
    val bollingerBands: BollingerBandsDto,
    val fibonacci: FibonacciDto,
    val rsiDivergence: RSIDivergenceDto,
    val volumeConfirmation: Boolean,
    val trendStrength: String  // STRONG, MODERATE, WEAK
)

data class DominantMADto(
    val period: Int,  // 20, 50, or 200
    val respected: Boolean,
    val distance: Double  // Percentage from MA
)

data class BollingerBandsDto(
    val position: String,  // LOWER, MIDDLE, UPPER, BELOW, ABOVE
    val bandwidth: Double
)

data class FibonacciDto(
    val level: Double,  // 0, 0.236, 0.382, 0.5, 0.618, 0.786, 1
    val inRetracementZone: Boolean
)

data class RSIDivergenceDto(
    val detected: Boolean,
    val type: String? = null,  // BULLISH, BEARISH
    val strength: Double? = null
)
