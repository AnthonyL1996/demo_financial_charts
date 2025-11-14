package com.jdb.trading.service

import com.jdb.trading.dto.MLSignalDto
import com.jdb.trading.dto.MultiTimeframeSignalsDto
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.MediaType
import org.springframework.stereotype.Service
import org.springframework.web.client.RestTemplate
import org.springframework.web.client.HttpClientErrorException
import org.springframework.web.client.ResourceAccessException

/**
 * Service for calling Python ML microservice
 */
@Service
class MLSignalService(
    @Value("\${ml-service.url:http://localhost:5000}")
    private val mlServiceUrl: String,

    @Value("\${ml-service.enabled:true}")
    private val mlServiceEnabled: Boolean,

    private val restTemplate: RestTemplate
) {
    private val logger = LoggerFactory.getLogger(MLSignalService::class.java)

    /**
     * Generate ML signal for a ticker and timeframe
     *
     * @param ticker Stock ticker symbol
     * @param timeframe Timeframe ("daily", "weekly", "monthly")
     * @return ML signal or null if service unavailable
     */
    fun generateSignal(ticker: String, timeframe: String = "daily"): MLSignalDto? {
        if (!mlServiceEnabled) {
            logger.debug("ML service disabled via configuration")
            return null
        }

        return try {
            logger.debug("Requesting ML signal for $ticker ($timeframe)")

            val headers = HttpHeaders().apply {
                contentType = MediaType.APPLICATION_JSON
            }

            val requestBody = mapOf(
                "ticker" to ticker.uppercase(),
                "timeframe" to timeframe.lowercase()
            )

            val request = HttpEntity(requestBody, headers)
            val url = "$mlServiceUrl/api/signals/generate"

            val response = restTemplate.postForObject(
                url,
                request,
                MLSignalDto::class.java
            )

            logger.debug("ML signal received for $ticker: ${response?.signal}")
            response

        } catch (e: HttpClientErrorException) {
            logger.warn("ML service returned error for $ticker: ${e.message}")
            null

        } catch (e: ResourceAccessException) {
            logger.warn("ML service unavailable: ${e.message}")
            null

        } catch (e: Exception) {
            logger.error("Error calling ML service for $ticker", e)
            null
        }
    }

    /**
     * Generate signals for all timeframes
     *
     * @param ticker Stock ticker symbol
     * @return Multi-timeframe signals or null if service unavailable
     */
    fun generateMultiTimeframeSignals(ticker: String): MultiTimeframeSignalsDto? {
        if (!mlServiceEnabled) {
            logger.debug("ML service disabled via configuration")
            return null
        }

        return try {
            logger.debug("Requesting multi-timeframe signals for $ticker")

            val headers = HttpHeaders().apply {
                contentType = MediaType.APPLICATION_JSON
            }

            val requestBody = mapOf("ticker" to ticker.uppercase())
            val request = HttpEntity(requestBody, headers)
            val url = "$mlServiceUrl/api/signals/multi-timeframe"

            val response = restTemplate.postForObject(
                url,
                request,
                MultiTimeframeSignalsDto::class.java
            )

            logger.debug(
                "Multi-timeframe signals received for $ticker: " +
                "${response?.consensus?.recommendation}"
            )
            response

        } catch (e: HttpClientErrorException) {
            logger.warn("ML service returned error for $ticker: ${e.message}")
            null

        } catch (e: ResourceAccessException) {
            logger.warn("ML service unavailable: ${e.message}")
            null

        } catch (e: Exception) {
            logger.error("Error calling ML service for $ticker", e)
            null
        }
    }

    /**
     * Check if ML service is healthy
     *
     * @return true if service is responding, false otherwise
     */
    fun isHealthy(): Boolean {
        if (!mlServiceEnabled) {
            return false
        }

        return try {
            val url = "$mlServiceUrl/health"
            val response = restTemplate.getForObject(url, Map::class.java)
            response?.get("status") == "UP"

        } catch (e: Exception) {
            logger.debug("ML service health check failed: ${e.message}")
            false
        }
    }

    /**
     * Get ML service model information
     *
     * @return Model info map or null if unavailable
     */
    fun getModelInfo(): Map<String, Any>? {
        if (!mlServiceEnabled) {
            return null
        }

        return try {
            val url = "$mlServiceUrl/api/model/info"
            restTemplate.getForObject(url, Map::class.java)

        } catch (e: Exception) {
            logger.debug("Failed to get model info: ${e.message}")
            null
        }
    }
}
