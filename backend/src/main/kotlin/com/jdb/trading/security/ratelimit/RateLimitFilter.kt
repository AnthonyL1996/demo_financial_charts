package com.jdb.trading.security.ratelimit

import com.fasterxml.jackson.databind.ObjectMapper
import com.jdb.trading.dto.ApiResponse
import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import mu.KotlinLogging
import org.springframework.http.HttpStatus
import org.springframework.http.MediaType
import org.springframework.stereotype.Component
import org.springframework.web.filter.OncePerRequestFilter

private val logger = KotlinLogging.logger {}

/**
 * Rate limiting filter
 * Applies rate limits to HTTP requests based on endpoint and client IP
 */
@Component
class RateLimitFilter(
    private val rateLimitService: RateLimitService,
    private val rateLimitProperties: RateLimitProperties,
    private val objectMapper: ObjectMapper
) : OncePerRequestFilter() {

    override fun doFilterInternal(
        request: HttpServletRequest,
        response: HttpServletResponse,
        filterChain: FilterChain
    ) {
        // Skip rate limiting if disabled
        if (!rateLimitProperties.enabled) {
            filterChain.doFilter(request, response)
            return
        }

        val requestUri = request.requestURI
        val clientId = getClientIdentifier(request)

        // Determine if this endpoint should be rate limited
        val rateLimitResult = checkRateLimit(requestUri, request.method, clientId)

        if (!rateLimitResult.allowed) {
            // Rate limit exceeded - return 429 Too Many Requests
            handleRateLimitExceeded(response, rateLimitResult)
            return
        }

        // Add rate limit headers to response
        addRateLimitHeaders(response, rateLimitResult)

        // Continue filter chain
        filterChain.doFilter(request, response)
    }

    /**
     * Check rate limit for the request
     */
    private fun checkRateLimit(
        requestUri: String,
        method: String,
        clientId: String
    ): RateLimitResult {
        return when {
            // Login endpoint - strict rate limit
            requestUri.endsWith("/api/auth/login") && method == "POST" -> {
                val allowed = rateLimitService.allowLoginRequest(clientId)
                RateLimitResult(
                    allowed = allowed,
                    remaining = rateLimitService.getRemainingTokens("login", clientId),
                    retryAfter = rateLimitService.getSecondsUntilRefill("login", clientId),
                    endpoint = "login"
                )
            }

            // Register endpoint - very strict rate limit
            requestUri.endsWith("/api/auth/register") && method == "POST" -> {
                val allowed = rateLimitService.allowRegisterRequest(clientId)
                RateLimitResult(
                    allowed = allowed,
                    remaining = rateLimitService.getRemainingTokens("register", clientId),
                    retryAfter = rateLimitService.getSecondsUntilRefill("register", clientId),
                    endpoint = "register"
                )
            }

            // Refresh endpoint - moderate rate limit
            requestUri.endsWith("/api/auth/refresh") && method == "POST" -> {
                val allowed = rateLimitService.allowRefreshRequest(clientId)
                RateLimitResult(
                    allowed = allowed,
                    remaining = rateLimitService.getRemainingTokens("refresh", clientId),
                    retryAfter = rateLimitService.getSecondsUntilRefill("refresh", clientId),
                    endpoint = "refresh"
                )
            }

            // General API endpoints - lenient rate limit
            requestUri.startsWith("/api/") -> {
                val allowed = rateLimitService.allowApiRequest(clientId)
                RateLimitResult(
                    allowed = allowed,
                    remaining = rateLimitService.getRemainingTokens("api", clientId),
                    retryAfter = rateLimitService.getSecondsUntilRefill("api", clientId),
                    endpoint = "api"
                )
            }

            // No rate limit for other endpoints
            else -> RateLimitResult(allowed = true, remaining = Long.MAX_VALUE, retryAfter = 0)
        }
    }

    /**
     * Get client identifier (IP address)
     * Checks X-Forwarded-For header for proxy/load balancer scenarios
     */
    private fun getClientIdentifier(request: HttpServletRequest): String {
        // Check for X-Forwarded-For header (proxy/load balancer)
        val forwardedFor = request.getHeader("X-Forwarded-For")
        if (!forwardedFor.isNullOrBlank()) {
            // Take the first IP in the chain
            return forwardedFor.split(",").first().trim()
        }

        // Check for X-Real-IP header
        val realIp = request.getHeader("X-Real-IP")
        if (!realIp.isNullOrBlank()) {
            return realIp.trim()
        }

        // Fallback to remote address
        return request.remoteAddr ?: "unknown"
    }

    /**
     * Handle rate limit exceeded
     */
    private fun handleRateLimitExceeded(
        response: HttpServletResponse,
        result: RateLimitResult
    ) {
        logger.warn {
            "Rate limit exceeded for ${result.endpoint} endpoint. " +
                    "Retry after ${result.retryAfter} seconds"
        }

        response.status = HttpStatus.TOO_MANY_REQUESTS.value()
        response.contentType = MediaType.APPLICATION_JSON_VALUE

        // Add standard rate limit headers
        response.setHeader("X-RateLimit-Limit", getRateLimit(result.endpoint).toString())
        response.setHeader("X-RateLimit-Remaining", "0")
        response.setHeader("X-RateLimit-Reset", result.retryAfter.toString())
        response.setHeader("Retry-After", result.retryAfter.toString())

        // Write error response
        val errorResponse = ApiResponse.error<Any>(
            "Rate limit exceeded. Too many requests. Please try again later.",
            mapOf(
                "retryAfter" to result.retryAfter,
                "endpoint" to result.endpoint
            )
        )

        response.writer.write(objectMapper.writeValueAsString(errorResponse))
        response.writer.flush()
    }

    /**
     * Add rate limit headers to response
     */
    private fun addRateLimitHeaders(
        response: HttpServletResponse,
        result: RateLimitResult
    ) {
        if (result.allowed && result.remaining != Long.MAX_VALUE) {
            response.setHeader("X-RateLimit-Limit", getRateLimit(result.endpoint).toString())
            response.setHeader("X-RateLimit-Remaining", result.remaining.toString())
            response.setHeader("X-RateLimit-Reset", result.retryAfter.toString())
        }
    }

    /**
     * Get rate limit capacity for endpoint
     */
    private fun getRateLimit(endpoint: String): Long {
        return when (endpoint) {
            "login" -> rateLimitProperties.login.capacity
            "register" -> rateLimitProperties.register.capacity
            "refresh" -> rateLimitProperties.refresh.capacity
            "api" -> rateLimitProperties.api.capacity
            else -> 0
        }
    }
}

/**
 * Rate limit check result
 */
private data class RateLimitResult(
    val allowed: Boolean,
    val remaining: Long,
    val retryAfter: Long,
    val endpoint: String = "unknown"
)
