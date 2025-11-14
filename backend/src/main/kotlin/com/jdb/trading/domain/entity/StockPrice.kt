package com.jdb.trading.domain.entity

import jakarta.persistence.*
import java.io.Serializable
import java.math.BigDecimal
import java.time.LocalDateTime

/**
 * Stock price entity for OHLCV historical data
 */
@Entity
@Table(name = "stock_prices")
@IdClass(StockPriceId::class)
data class StockPrice(
    @Id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "stock_id", nullable = false)
    val stock: Stock,

    @Id
    @Column(nullable = false)
    val date: LocalDateTime,

    @Column(nullable = false, precision = 12, scale = 4)
    val open: BigDecimal,

    @Column(nullable = false, precision = 12, scale = 4)
    val high: BigDecimal,

    @Column(nullable = false, precision = 12, scale = 4)
    val low: BigDecimal,

    @Column(nullable = false, precision = 12, scale = 4)
    val close: BigDecimal,

    @Column(nullable = false)
    val volume: Long,

    @Column(name = "adj_close", precision = 12, scale = 4)
    val adjClose: BigDecimal? = null
)

/**
 * Composite primary key for StockPrice
 */
data class StockPriceId(
    val stock: Long = 0,
    val date: LocalDateTime = LocalDateTime.now()
) : Serializable
