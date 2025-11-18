package com.jdb.trading.security.ratelimit

import io.github.bucket4j.Bandwidth
import io.github.bucket4j.Bucket
import io.github.bucket4j.Refill
import mu.KotlinLogging
import org.springframework.stereotype.Service
import java.time.Duration
import java.util.concurrent.ConcurrentHashMap

private val logger = KotlinLogging.logger {}

/**
 * Rate limiting service using Bucket4j (Token Bucket algorithm)
 * Manages rate limit buckets for different endpoints and clients
 */
@Service
class RateLimitService(
    private val rateLimitProperties: RateLimitProperties
) {
    // In-memory cache of buckets per client (IP address or user ID)
    // Key format: "endpoint:identifier" (e.g., "login:192.168.1.1" or "api:user123")
    private val buckets = ConcurrentHashMap<String, Bucket>()

    /**
     * Check if request is allowed for login endpoint
     * @param clientId Client identifier (usually IP address)
     * @return true if request is allowed, false if rate limit exceeded
     */
    fun allowLoginRequest(clientId: String): Boolean {
        if (!rateLimitProperties.enabled) {
            return true
        }

        val bucket = resolveBucket("login:$clientId", rateLimitProperties.login)
        return consumeToken(bucket, "login", clientId)
    }

    /**
     * Check if request is allowed for register endpoint
     * @param clientId Client identifier (usually IP address)
     * @return true if request is allowed, false if rate limit exceeded
     */
    fun allowRegisterRequest(clientId: String): Boolean {
        if (!rateLimitProperties.enabled) {
            return true
        }

        val bucket = resolveBucket("register:$clientId", rateLimitProperties.register)
        return consumeToken(bucket, "register", clientId)
    }

    /**
     * Check if request is allowed for refresh endpoint
     * @param clientId Client identifier (usually IP address)
     * @return true if request is allowed, false if rate limit exceeded
     */
    fun allowRefreshRequest(clientId: String): Boolean {
        if (!rateLimitProperties.enabled) {
            return true
        }

        val bucket = resolveBucket("refresh:$clientId", rateLimitProperties.refresh)
        return consumeToken(bucket, "refresh", clientId)
    }

    /**
     * Check if request is allowed for general API endpoints
     * @param clientId Client identifier (user ID or IP address)
     * @return true if request is allowed, false if rate limit exceeded
     */
    fun allowApiRequest(clientId: String): Boolean {
        if (!rateLimitProperties.enabled) {
            return true
        }

        val bucket = resolveBucket("api:$clientId", rateLimitProperties.api)
        return consumeToken(bucket, "api", clientId)
    }

    /**
     * Get remaining tokens for a specific endpoint and client
     */
    fun getRemainingTokens(endpoint: String, clientId: String): Long {
        val key = "$endpoint:$clientId"
        val bucket = buckets[key] ?: return 0
        return bucket.availableTokens
    }

    /**
     * Get time until next refill (in seconds)
     */
    fun getSecondsUntilRefill(endpoint: String, clientId: String): Long {
        val config = when (endpoint) {
            "login" -> rateLimitProperties.login
            "register" -> rateLimitProperties.register
            "refresh" -> rateLimitProperties.refresh
            else -> rateLimitProperties.api
        }
        return config.getRefillDurationInSeconds()
    }

    /**
     * Resolve or create a bucket for the given key
     */
    private fun resolveBucket(key: String, config: RateLimitConfig): Bucket {
        return buckets.computeIfAbsent(key) {
            createBucket(config)
        }
    }

    /**
     * Create a new bucket with the specified configuration
     */
    private fun createBucket(config: RateLimitConfig): Bucket {
        val refillDuration = Duration.ofSeconds(config.getRefillDurationInSeconds())

        // Create bandwidth limit (capacity and refill strategy)
        val bandwidth = Bandwidth.classic(
            config.capacity,
            Refill.intervally(config.refillTokens, refillDuration)
        )

        // Build and return bucket
        return Bucket.builder()
            .addLimit(bandwidth)
            .build()
    }

    /**
     * Try to consume a token from the bucket
     * @return true if token consumed successfully, false if rate limit exceeded
     */
    private fun consumeToken(bucket: Bucket, endpoint: String, clientId: String): Boolean {
        val allowed = bucket.tryConsume(1)

        if (!allowed) {
            logger.warn { "Rate limit exceeded for $endpoint by client: $clientId" }
        } else {
            logger.debug { "Rate limit check passed for $endpoint by client: $clientId (remaining: ${bucket.availableTokens})" }
        }

        return allowed
    }

    /**
     * Clear all buckets (useful for testing or administrative purposes)
     */
    fun clearAllBuckets() {
        buckets.clear()
        logger.info { "All rate limit buckets cleared" }
    }

    /**
     * Clear bucket for specific endpoint and client
     */
    fun clearBucket(endpoint: String, clientId: String) {
        val key = "$endpoint:$clientId"
        buckets.remove(key)
        logger.debug { "Bucket cleared for $key" }
    }
}
