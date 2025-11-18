package com.jdb.trading.security

import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.context.annotation.Configuration
import org.springframework.validation.annotation.Validated
import jakarta.validation.constraints.Min
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Size

/**
 * JWT configuration properties
 *
 * Configure in application.yml:
 * ```yaml
 * jwt:
 *   secret: your-secret-key-min-32-characters
 *   access-token-expiration-minutes: 15
 *   refresh-token-expiration-days: 7
 * ```
 */
@Configuration
@ConfigurationProperties(prefix = "jwt")
@Validated
data class JwtProperties(
    /**
     * JWT secret key (minimum 32 characters for security)
     * In production, use a strong randomly generated key
     */
    @field:NotBlank(message = "JWT secret is required")
    @field:Size(min = 32, message = "JWT secret must be at least 32 characters")
    var secret: String = "",

    /**
     * Access token expiration in minutes (default: 15 minutes)
     */
    @field:Min(value = 1, message = "Access token expiration must be at least 1 minute")
    var accessTokenExpirationMinutes: Long = 15,

    /**
     * Refresh token expiration in days (default: 7 days)
     */
    @field:Min(value = 1, message = "Refresh token expiration must be at least 1 day")
    var refreshTokenExpirationDays: Long = 7,

    /**
     * JWT issuer
     */
    var issuer: String = "jdb-trading-api",

    /**
     * Cookie name for access token (httpOnly)
     */
    var accessTokenCookieName: String = "access_token",

    /**
     * Cookie name for refresh token (httpOnly)
     */
    var refreshTokenCookieName: String = "refresh_token"
)
