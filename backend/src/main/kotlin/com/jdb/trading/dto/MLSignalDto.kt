package com.jdb.trading.dto

import com.fasterxml.jackson.annotation.JsonProperty

/**
 * ML Signal response from Python ML service
 */
data class MLSignalDto(
    val ticker: String,
    val timeframe: String,
    val signal: String,  // "BUY" or "NONE"
    val confidence: Double,

    @JsonProperty("prediction_date")
    val predictionDate: String,

    @JsonProperty("current_price")
    val currentPrice: Double,

    val target: MLTargetDto,
    val technicals: Map<String, Any>,
    val model: MLModelInfoDto
)

data class MLTargetDto(
    @JsonProperty("horizon_days")
    val horizonDays: Int,

    @JsonProperty("expected_return")
    val expectedReturn: Double,  // Percentage

    @JsonProperty("target_price")
    val targetPrice: Double?,

    val threshold: Double
)

data class MLModelInfoDto(
    val name: String,

    @JsonProperty("trained_on")
    val trainedOn: String
)

/**
 * Multi-timeframe signals response
 */
data class MultiTimeframeSignalsDto(
    val ticker: String,
    val signals: Map<String, MLSignalDto>,
    val consensus: ConsensusDto
)

data class ConsensusDto(
    val recommendation: String,  // "STRONG_BUY", "BUY", "WEAK_BUY", "NONE"
    val strength: String,  // "STRONG", "MODERATE", "WEAK", "NONE"

    @JsonProperty("bullish_timeframes")
    val bullishTimeframes: Int,

    @JsonProperty("avg_confidence")
    val avgConfidence: Double,

    @JsonProperty("suggested_position_size")
    val suggestedPositionSize: Double,

    val notes: String
)
