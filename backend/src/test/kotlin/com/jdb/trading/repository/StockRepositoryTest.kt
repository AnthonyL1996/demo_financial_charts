package com.jdb.trading.repository

import com.jdb.trading.domain.entity.Stock
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager
import org.springframework.test.context.ActiveProfiles

@DataJpaTest
@ActiveProfiles("test")
class StockRepositoryTest {

    @Autowired
    private lateinit var entityManager: TestEntityManager

    @Autowired
    private lateinit var stockRepository: StockRepository

    @Test
    fun `findByTicker should return stock when exists`() {
        // Given
        val stock = Stock(
            ticker = "AAPL",
            companyName = "Apple Inc.",
            sector = "Technology",
            industry = "Consumer Electronics",
            isActive = true
        )
        entityManager.persist(stock)
        entityManager.flush()

        // When
        val found = stockRepository.findByTicker("AAPL")

        // Then
        assertNotNull(found)
        assertEquals("AAPL", found?.ticker)
        assertEquals("Apple Inc.", found?.companyName)
        assertEquals("Technology", found?.sector)
        assertTrue(found?.isActive ?: false)
    }

    @Test
    fun `findByTicker should return null when not exists`() {
        // When
        val found = stockRepository.findByTicker("NOTFOUND")

        // Then
        assertNull(found)
    }

    @Test
    fun `findByIsActiveTrue should return only active stocks`() {
        // Given
        val activeStock = Stock(
            ticker = "AAPL",
            companyName = "Apple Inc.",
            isActive = true
        )
        val inactiveStock = Stock(
            ticker = "INACTIVE",
            companyName = "Inactive Corp.",
            isActive = false
        )
        entityManager.persist(activeStock)
        entityManager.persist(inactiveStock)
        entityManager.flush()

        // When
        val activeStocks = stockRepository.findByIsActiveTrue()

        // Then
        assertEquals(1, activeStocks.size)
        assertEquals("AAPL", activeStocks[0].ticker)
        assertTrue(activeStocks[0].isActive)
    }

    @Test
    fun `save should persist stock to database`() {
        // Given
        val stock = Stock(
            ticker = "TSLA",
            companyName = "Tesla Inc.",
            sector = "Automotive",
            industry = "Electric Vehicles",
            marketCap = 600_000_000_000L,
            isActive = true
        )

        // When
        val saved = stockRepository.save(stock)
        entityManager.flush()
        entityManager.clear()

        // Then
        val found = stockRepository.findById(saved.id)
        assertTrue(found.isPresent)
        assertEquals("TSLA", found.get().ticker)
        assertEquals("Tesla Inc.", found.get().companyName)
        assertEquals(600_000_000_000L, found.get().marketCap)
    }

    @Test
    fun `findAll should return all stocks`() {
        // Given
        val stock1 = Stock(ticker = "AAPL", companyName = "Apple Inc.", isActive = true)
        val stock2 = Stock(ticker = "TSLA", companyName = "Tesla Inc.", isActive = true)
        val stock3 = Stock(ticker = "MSFT", companyName = "Microsoft Corp.", isActive = true)

        entityManager.persist(stock1)
        entityManager.persist(stock2)
        entityManager.persist(stock3)
        entityManager.flush()

        // When
        val allStocks = stockRepository.findAll()

        // Then
        assertEquals(3, allStocks.size)
        assertTrue(allStocks.any { it.ticker == "AAPL" })
        assertTrue(allStocks.any { it.ticker == "TSLA" })
        assertTrue(allStocks.any { it.ticker == "MSFT" })
    }

    @Test
    fun `ticker should be unique`() {
        // Given
        val stock1 = Stock(ticker = "AAPL", companyName = "Apple Inc.", isActive = true)
        entityManager.persist(stock1)
        entityManager.flush()

        // When/Then - Attempting to save duplicate ticker should fail
        val stock2 = Stock(ticker = "AAPL", companyName = "Apple Copy", isActive = true)
        assertThrows(Exception::class.java) {
            entityManager.persist(stock2)
            entityManager.flush()
        }
    }
}
