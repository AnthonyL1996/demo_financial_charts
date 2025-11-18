package com.jdb.trading.security

import com.jdb.trading.domain.entity.User
import io.jsonwebtoken.*
import io.jsonwebtoken.security.Keys
import io.jsonwebtoken.security.SignatureException
import mu.KotlinLogging
import org.springframework.security.core.userdetails.UserDetails
import org.springframework.stereotype.Service
import java.time.Instant
import java.time.temporal.ChronoUnit
import java.util.*
import javax.crypto.SecretKey

private val logger = KotlinLogging.logger {}

/**
 * JWT token generation and validation service
 */
@Service
class JwtService(
    private val jwtProperties: JwtProperties
) {
    private val secretKey: SecretKey = Keys.hmacShaKeyFor(jwtProperties.secret.toByteArray())

    /**
     * Generate access token (short-lived)
     */
    fun generateAccessToken(user: User): String {
        val now = Instant.now()
        val expiration = now.plus(jwtProperties.accessTokenExpirationMinutes, ChronoUnit.MINUTES)

        return Jwts.builder()
            .subject(user.email)
            .claim("userId", user.id)
            .claim("role", user.role.name)
            .claim("type", "access")
            .issuer(jwtProperties.issuer)
            .issuedAt(Date.from(now))
            .expiration(Date.from(expiration))
            .signWith(secretKey)
            .compact()
    }

    /**
     * Generate refresh token (long-lived)
     */
    fun generateRefreshToken(user: User, tokenId: String = UUID.randomUUID().toString()): String {
        val now = Instant.now()
        val expiration = now.plus(jwtProperties.refreshTokenExpirationDays, ChronoUnit.DAYS)

        return Jwts.builder()
            .subject(user.email)
            .claim("userId", user.id)
            .claim("tokenId", tokenId)
            .claim("type", "refresh")
            .issuer(jwtProperties.issuer)
            .issuedAt(Date.from(now))
            .expiration(Date.from(expiration))
            .signWith(secretKey)
            .compact()
    }

    /**
     * Extract email from token
     */
    fun extractEmail(token: String): String? {
        return try {
            extractClaims(token).subject
        } catch (e: Exception) {
            logger.debug(e) { "Failed to extract email from token" }
            null
        }
    }

    /**
     * Extract user ID from token
     */
    fun extractUserId(token: String): Long? {
        return try {
            extractClaims(token).get("userId", java.lang.Long::class.java)?.toLong()
        } catch (e: Exception) {
            logger.debug(e) { "Failed to extract user ID from token" }
            null
        }
    }

    /**
     * Extract token ID (for refresh tokens)
     */
    fun extractTokenId(token: String): String? {
        return try {
            extractClaims(token).get("tokenId", String::class.java)
        } catch (e: Exception) {
            logger.debug(e) { "Failed to extract token ID" }
            null
        }
    }

    /**
     * Extract token type (access or refresh)
     */
    fun extractTokenType(token: String): String? {
        return try {
            extractClaims(token).get("type", String::class.java)
        } catch (e: Exception) {
            logger.debug(e) { "Failed to extract token type" }
            null
        }
    }

    /**
     * Extract expiration date from token
     */
    fun extractExpiration(token: String): Date? {
        return try {
            extractClaims(token).expiration
        } catch (e: Exception) {
            logger.debug(e) { "Failed to extract expiration from token" }
            null
        }
    }

    /**
     * Validate token
     */
    fun isTokenValid(token: String, userDetails: UserDetails): Boolean {
        try {
            val email = extractEmail(token)
            val isEmailMatch = email == userDetails.username
            val isNotExpired = !isTokenExpired(token)

            return isEmailMatch && isNotExpired
        } catch (e: Exception) {
            logger.debug(e) { "Token validation failed" }
            return false
        }
    }

    /**
     * Check if token is expired
     */
    fun isTokenExpired(token: String): Boolean {
        return try {
            val expiration = extractExpiration(token) ?: return true
            expiration.before(Date())
        } catch (e: Exception) {
            true
        }
    }

    /**
     * Extract all claims from token
     */
    private fun extractClaims(token: String): Claims {
        return try {
            Jwts.parser()
                .verifyWith(secretKey)
                .build()
                .parseSignedClaims(token)
                .payload
        } catch (e: ExpiredJwtException) {
            logger.debug("Token expired")
            throw e
        } catch (e: UnsupportedJwtException) {
            logger.warn("Unsupported JWT token")
            throw e
        } catch (e: MalformedJwtException) {
            logger.warn("Malformed JWT token")
            throw e
        } catch (e: SignatureException) {
            logger.warn("Invalid JWT signature")
            throw e
        } catch (e: IllegalArgumentException) {
            logger.warn("JWT claims string is empty")
            throw e
        }
    }

    /**
     * Generate SHA-256 hash of token (for database storage)
     */
    fun hashToken(token: String): String {
        val digest = java.security.MessageDigest.getInstance("SHA-256")
        val hashBytes = digest.digest(token.toByteArray())
        return hashBytes.joinToString("") { "%02x".format(it) }
    }

    /**
     * Calculate refresh token expiration time
     */
    fun getRefreshTokenExpiration(): Instant {
        return Instant.now().plus(jwtProperties.refreshTokenExpirationDays, ChronoUnit.DAYS)
    }
}
