package com.jdb.trading.repository

import com.jdb.trading.domain.entity.Stock
import com.jdb.trading.domain.entity.StockPrice
import com.jdb.trading.domain.entity.StockPriceId
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.stereotype.Repository
import java.time.LocalDateTime

/**
 * Repository for StockPrice entity
 */
@Repository
interface StockPriceRepository : JpaRepository<StockPrice, StockPriceId> {

    /**
     * Find all prices for a stock, ordered by date descending
     */
    fun findByStockOrderByDateDesc(stock: Stock): List<StockPrice>

    /**
     * Find prices for a stock within a date range
     */
    fun findByStockAndDateBetweenOrderByDateAsc(
        stock: Stock,
        startDate: LocalDateTime,
        endDate: LocalDateTime
    ): List<StockPrice>

    /**
     * Find latest N prices for a stock
     */
    @Query("SELECT sp FROM StockPrice sp WHERE sp.stock = :stock ORDER BY sp.date DESC LIMIT :limit")
    fun findLatestPrices(stock: Stock, limit: Int): List<StockPrice>

    /**
     * Get the latest price for a stock
     */
    fun findFirstByStockOrderByDateDesc(stock: Stock): StockPrice?

    /**
     * Delete all prices for a stock
     */
    fun deleteByStock(stock: Stock)

    /**
     * Count prices for a stock
     */
    fun countByStock(stock: Stock): Long
}
