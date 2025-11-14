package com.jdb.trading.domain.entity

import jakarta.persistence.*
import java.time.LocalDateTime

/**
 * Stock entity representing a tradable security
 */
@Entity
@Table(name = "stocks")
data class Stock(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(unique = true, nullable = false, length = 20)
    val ticker: String,

    @Column(name = "company_name", nullable = false)
    val companyName: String,

    @Column(length = 100)
    val sector: String? = null,

    @Column(length = 100)
    val industry: String? = null,

    @Column(name = "market_cap")
    val marketCap: Long? = null,

    @Column(name = "is_active", nullable = false)
    val isActive: Boolean = true,

    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(name = "updated_at", nullable = false)
    var updatedAt: LocalDateTime = LocalDateTime.now(),

    // Relationships
    @OneToMany(mappedBy = "stock", cascade = [CascadeType.ALL], orphanRemoval = true)
    val prices: MutableList<StockPrice> = mutableListOf()
)
