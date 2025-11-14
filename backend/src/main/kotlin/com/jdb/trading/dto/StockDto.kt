package com.jdb.trading.dto

/**
 * Stock data transfer object matching frontend Stock interface
 */
data class StockDto(
    val ticker: String,
    val companyName: String,
    val sector: String? = null,
    val industry: String? = null,
    val currentPrice: Double,
    val priceChange: Double,  // Percentage
    val volume: Long,
    val marketCap: Long? = null,
    val technicals: StockTechnicalsDto,
    val activeSignals: List<SignalDto> = emptyList(),
    val mlSignals: MultiTimeframeSignalsDto? = null  // ML predictions (optional)
)

/**
 * Technical indicators matching frontend StockTechnicals interface
 */
data class StockTechnicalsDto(
    val ma20: Double,
    val ma50: Double,
    val ma200: Double,
    val rsi: Double,
    val bollingerUpper: Double,
    val bollingerMiddle: Double,
    val bollingerLower: Double,
    val atr: Double,
    val volume: Long,
    val volumeMA: Long
)
