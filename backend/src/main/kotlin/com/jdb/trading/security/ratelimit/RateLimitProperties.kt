package com.jdb.trading.security.ratelimit

import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.context.annotation.Configuration
import org.springframework.validation.annotation.Validated
import jakarta.validation.constraints.Min

/**
 * Rate limiting configuration properties
 *
 * Configure in application.yml:
 * ```yaml
 * rate-limit:
 *   enabled: true
 *   login:
 *     capacity: 5
 *     refill-tokens: 5
 *     refill-duration-minutes: 15
 *   register:
 *     capacity: 3
 *     refill-tokens: 3
 *     refill-duration-minutes: 60
 *   api:
 *     capacity: 100
 *     refill-tokens: 20
 *     refill-duration-seconds: 1
 * ```
 */
@Configuration
@ConfigurationProperties(prefix = "rate-limit")
@Validated
data class RateLimitProperties(
    /**
     * Enable or disable rate limiting globally
     */
    var enabled: Boolean = true,

    /**
     * Login endpoint rate limit
     * Default: 5 attempts per 15 minutes per IP
     */
    var login: RateLimitConfig = RateLimitConfig(
        capacity = 5,
        refillTokens = 5,
        refillDurationMinutes = 15
    ),

    /**
     * Register endpoint rate limit
     * Default: 3 attempts per hour per IP
     */
    var register: RateLimitConfig = RateLimitConfig(
        capacity = 3,
        refillTokens = 3,
        refillDurationMinutes = 60
    ),

    /**
     * General API rate limit
     * Default: 100 requests with 20 tokens/second refill
     */
    var api: RateLimitConfig = RateLimitConfig(
        capacity = 100,
        refillTokens = 20,
        refillDurationSeconds = 1
    ),

    /**
     * Refresh token endpoint rate limit
     * Default: 10 attempts per 5 minutes per IP
     */
    var refresh: RateLimitConfig = RateLimitConfig(
        capacity = 10,
        refillTokens = 10,
        refillDurationMinutes = 5
    )
)

/**
 * Rate limit configuration for a specific endpoint or group
 */
data class RateLimitConfig(
    /**
     * Maximum number of tokens (requests) in the bucket
     */
    @field:Min(1)
    var capacity: Long = 100,

    /**
     * Number of tokens to add during each refill
     */
    @field:Min(1)
    var refillTokens: Long = 10,

    /**
     * Refill duration in seconds (takes precedence if set)
     */
    var refillDurationSeconds: Long? = null,

    /**
     * Refill duration in minutes (used if refillDurationSeconds is null)
     */
    var refillDurationMinutes: Long? = null
) {
    /**
     * Get refill duration in seconds
     */
    fun getRefillDurationInSeconds(): Long {
        return refillDurationSeconds ?: (refillDurationMinutes?.times(60) ?: 60)
    }
}
