package com.jdb.trading.repository

import com.jdb.trading.domain.entity.Stock
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.*

/**
 * Repository for Stock entity
 */
@Repository
interface StockRepository : JpaRepository<Stock, Long> {

    /**
     * Find stock by ticker symbol
     */
    fun findByTicker(ticker: String): Optional<Stock>

    /**
     * Find stock by ticker, case-insensitive
     */
    fun findByTickerIgnoreCase(ticker: String): Optional<Stock>

    /**
     * Find all active stocks
     */
    fun findAllByIsActive(isActive: Boolean): List<Stock>

    /**
     * Check if stock exists by ticker
     */
    fun existsByTickerIgnoreCase(ticker: String): Boolean
}
