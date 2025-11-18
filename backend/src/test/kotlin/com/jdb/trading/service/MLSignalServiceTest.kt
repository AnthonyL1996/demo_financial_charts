package com.jdb.trading.service

import com.jdb.trading.dto.MLSignalDto
import com.jdb.trading.dto.MultiTimeframeSignalsDto
import com.jdb.trading.dto.ConsensusDto
import io.mockk.*
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.springframework.http.HttpEntity
import org.springframework.http.HttpStatus
import org.springframework.web.client.HttpClientErrorException
import org.springframework.web.client.ResourceAccessException
import org.springframework.web.client.RestTemplate

class MLSignalServiceTest {

    private lateinit var restTemplate: RestTemplate
    private lateinit var service: MLSignalService

    @BeforeEach
    fun setup() {
        restTemplate = mockk()
        service = MLSignalService(
            mlServiceUrl = "http://localhost:5000",
            mlServiceEnabled = true,
            restTemplate = restTemplate
        )
    }

    @AfterEach
    fun tearDown() {
        unmockkAll()
    }

    @Test
    fun `generateSignal should return ML signal successfully`() {
        // Given
        val ticker = "AAPL"
        val timeframe = "daily"
        val expectedSignal = MLSignalDto(
            ticker = "AAPL",
            timeframe = "daily",
            signal = "BUY",
            confidence = 0.85,
            prediction = 160.0,
            currentPrice = 150.0,
            reasoning = "Strong bullish indicators"
        )

        every {
            restTemplate.postForObject(
                "http://localhost:5000/api/signals/generate",
                any<HttpEntity<*>>(),
                MLSignalDto::class.java
            )
        } returns expectedSignal

        // When
        val result = service.generateSignal(ticker, timeframe)

        // Then
        assertNotNull(result)
        assertEquals("AAPL", result?.ticker)
        assertEquals("BUY", result?.signal)
        assertEquals(0.85, result?.confidence)
        assertEquals(160.0, result?.prediction)

        verify {
            restTemplate.postForObject(
                "http://localhost:5000/api/signals/generate",
                any<HttpEntity<*>>(),
                MLSignalDto::class.java
            )
        }
    }

    @Test
    fun `generateSignal should handle weekly timeframe`() {
        // Given
        val ticker = "TSLA"
        val timeframe = "weekly"
        val expectedSignal = MLSignalDto(
            ticker = "TSLA",
            timeframe = "weekly",
            signal = "HOLD",
            confidence = 0.65,
            prediction = 210.0,
            currentPrice = 205.0,
            reasoning = "Mixed signals"
        )

        every {
            restTemplate.postForObject(
                "http://localhost:5000/api/signals/generate",
                any<HttpEntity<*>>(),
                MLSignalDto::class.java
            )
        } returns expectedSignal

        // When
        val result = service.generateSignal(ticker, timeframe)

        // Then
        assertNotNull(result)
        assertEquals("TSLA", result?.ticker)
        assertEquals("HOLD", result?.signal)
    }

    @Test
    fun `generateSignal should return null when ML service disabled`() {
        // Given
        val disabledService = MLSignalService(
            mlServiceUrl = "http://localhost:5000",
            mlServiceEnabled = false,
            restTemplate = restTemplate
        )

        // When
        val result = disabledService.generateSignal("AAPL")

        // Then
        assertNull(result)
        verify(exactly = 0) { restTemplate.postForObject(any<String>(), any(), any<Class<*>>()) }
    }

    @Test
    fun `generateSignal should return null on HttpClientErrorException`() {
        // Given
        val ticker = "INVALID"
        every {
            restTemplate.postForObject(any<String>(), any<HttpEntity<*>>(), MLSignalDto::class.java)
        } throws HttpClientErrorException(HttpStatus.BAD_REQUEST, "Invalid ticker")

        // When
        val result = service.generateSignal(ticker)

        // Then
        assertNull(result)
    }

    @Test
    fun `generateSignal should return null on ResourceAccessException`() {
        // Given
        val ticker = "AAPL"
        every {
            restTemplate.postForObject(any<String>(), any<HttpEntity<*>>(), MLSignalDto::class.java)
        } throws ResourceAccessException("Connection refused")

        // When
        val result = service.generateSignal(ticker)

        // Then
        assertNull(result)
    }

    @Test
    fun `generateSignal should return null on generic Exception`() {
        // Given
        val ticker = "AAPL"
        every {
            restTemplate.postForObject(any<String>(), any<HttpEntity<*>>(), MLSignalDto::class.java)
        } throws RuntimeException("Unexpected error")

        // When
        val result = service.generateSignal(ticker)

        // Then
        assertNull(result)
    }

    @Test
    fun `generateMultiTimeframeSignals should return signals successfully`() {
        // Given
        val ticker = "AAPL"
        val expectedSignals = MultiTimeframeSignalsDto(
            ticker = "AAPL",
            daily = MLSignalDto("AAPL", "daily", "BUY", 0.85, 160.0, 150.0, "Bullish"),
            weekly = MLSignalDto("AAPL", "weekly", "BUY", 0.75, 165.0, 150.0, "Uptrend"),
            monthly = MLSignalDto("AAPL", "monthly", "HOLD", 0.60, 155.0, 150.0, "Neutral"),
            consensus = ConsensusDto("BUY", 0.73, "Majority bullish signals")
        )

        every {
            restTemplate.postForObject(
                "http://localhost:5000/api/signals/multi-timeframe",
                any<HttpEntity<*>>(),
                MultiTimeframeSignalsDto::class.java
            )
        } returns expectedSignals

        // When
        val result = service.generateMultiTimeframeSignals(ticker)

        // Then
        assertNotNull(result)
        assertEquals("AAPL", result?.ticker)
        assertEquals("BUY", result?.daily?.signal)
        assertEquals("BUY", result?.weekly?.signal)
        assertEquals("HOLD", result?.monthly?.signal)
        assertEquals("BUY", result?.consensus?.recommendation)
        assertEquals(0.73, result?.consensus?.confidence)
    }

    @Test
    fun `generateMultiTimeframeSignals should return null when disabled`() {
        // Given
        val disabledService = MLSignalService(
            mlServiceUrl = "http://localhost:5000",
            mlServiceEnabled = false,
            restTemplate = restTemplate
        )

        // When
        val result = disabledService.generateMultiTimeframeSignals("AAPL")

        // Then
        assertNull(result)
    }

    @Test
    fun `generateMultiTimeframeSignals should return null on error`() {
        // Given
        val ticker = "AAPL"
        every {
            restTemplate.postForObject(
                any<String>(),
                any<HttpEntity<*>>(),
                MultiTimeframeSignalsDto::class.java
            )
        } throws ResourceAccessException("Service unavailable")

        // When
        val result = service.generateMultiTimeframeSignals(ticker)

        // Then
        assertNull(result)
    }

    @Test
    fun `isHealthy should return true when service is UP`() {
        // Given
        val healthResponse = mapOf("status" to "UP")
        every {
            restTemplate.getForObject("http://localhost:5000/health", Map::class.java)
        } returns healthResponse

        // When
        val result = service.isHealthy()

        // Then
        assertTrue(result)
    }

    @Test
    fun `isHealthy should return false when service is DOWN`() {
        // Given
        val healthResponse = mapOf("status" to "DOWN")
        every {
            restTemplate.getForObject("http://localhost:5000/health", Map::class.java)
        } returns healthResponse

        // When
        val result = service.isHealthy()

        // Then
        assertFalse(result)
    }

    @Test
    fun `isHealthy should return false when service disabled`() {
        // Given
        val disabledService = MLSignalService(
            mlServiceUrl = "http://localhost:5000",
            mlServiceEnabled = false,
            restTemplate = restTemplate
        )

        // When
        val result = disabledService.isHealthy()

        // Then
        assertFalse(result)
        verify(exactly = 0) { restTemplate.getForObject(any<String>(), any<Class<*>>()) }
    }

    @Test
    fun `isHealthy should return false on exception`() {
        // Given
        every {
            restTemplate.getForObject("http://localhost:5000/health", Map::class.java)
        } throws ResourceAccessException("Connection refused")

        // When
        val result = service.isHealthy()

        // Then
        assertFalse(result)
    }

    @Test
    fun `getModelInfo should return model information`() {
        // Given
        val modelInfo = mapOf(
            "model_type" to "XGBoost",
            "version" to "2.0.3",
            "features" to 30,
            "trained_on" to "2024-01-01"
        )
        every {
            restTemplate.getForObject("http://localhost:5000/api/model/info", Map::class.java)
        } returns modelInfo

        // When
        val result = service.getModelInfo()

        // Then
        assertNotNull(result)
        assertEquals("XGBoost", result?.get("model_type"))
        assertEquals("2.0.3", result?.get("version"))
        assertEquals(30, result?.get("features"))
    }

    @Test
    fun `getModelInfo should return null when disabled`() {
        // Given
        val disabledService = MLSignalService(
            mlServiceUrl = "http://localhost:5000",
            mlServiceEnabled = false,
            restTemplate = restTemplate
        )

        // When
        val result = disabledService.getModelInfo()

        // Then
        assertNull(result)
    }

    @Test
    fun `getModelInfo should return null on exception`() {
        // Given
        every {
            restTemplate.getForObject("http://localhost:5000/api/model/info", Map::class.java)
        } throws ResourceAccessException("Service unavailable")

        // When
        val result = service.getModelInfo()

        // Then
        assertNull(result)
    }

    @Test
    fun `generateSignal should uppercase ticker`() {
        // Given
        val ticker = "aapl"
        val expectedSignal = MLSignalDto(
            ticker = "AAPL",
            timeframe = "daily",
            signal = "BUY",
            confidence = 0.85,
            prediction = 160.0,
            currentPrice = 150.0,
            reasoning = "Strong bullish indicators"
        )

        every {
            restTemplate.postForObject(
                any<String>(),
                any<HttpEntity<*>>(),
                MLSignalDto::class.java
            )
        } returns expectedSignal

        // When
        val result = service.generateSignal(ticker)

        // Then
        assertNotNull(result)
        verify {
            restTemplate.postForObject(
                any<String>(),
                match<HttpEntity<*>> { entity ->
                    @Suppress("UNCHECKED_CAST")
                    val body = entity.body as Map<String, String>
                    body["ticker"] == "AAPL"
                },
                MLSignalDto::class.java
            )
        }
    }

    @Test
    fun `generateSignal should lowercase timeframe`() {
        // Given
        val ticker = "AAPL"
        val timeframe = "DAILY"
        val expectedSignal = MLSignalDto(
            ticker = "AAPL",
            timeframe = "daily",
            signal = "BUY",
            confidence = 0.85,
            prediction = 160.0,
            currentPrice = 150.0,
            reasoning = "Strong bullish indicators"
        )

        every {
            restTemplate.postForObject(
                any<String>(),
                any<HttpEntity<*>>(),
                MLSignalDto::class.java
            )
        } returns expectedSignal

        // When
        val result = service.generateSignal(ticker, timeframe)

        // Then
        assertNotNull(result)
        verify {
            restTemplate.postForObject(
                any<String>(),
                match<HttpEntity<*>> { entity ->
                    @Suppress("UNCHECKED_CAST")
                    val body = entity.body as Map<String, String>
                    body["timeframe"] == "daily"
                },
                MLSignalDto::class.java
            )
        }
    }
}
