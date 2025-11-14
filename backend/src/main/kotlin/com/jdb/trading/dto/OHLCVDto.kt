package com.jdb.trading.dto

/**
 * OHLCV data transfer object matching frontend OHLCVData interface
 */
data class OHLCVDto(
    val time: String,  // ISO date string
    val open: Double,
    val high: Double,
    val low: Double,
    val close: Double,
    val volume: Long
)
