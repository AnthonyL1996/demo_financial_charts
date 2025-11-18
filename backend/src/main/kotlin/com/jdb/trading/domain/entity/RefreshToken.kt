package com.jdb.trading.domain.entity

import jakarta.persistence.*
import java.time.LocalDateTime
import java.util.*

/**
 * Refresh token entity for JWT token rotation
 */
@Entity
@Table(name = "refresh_tokens")
data class RefreshToken(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    val user: User,

    @Column(name = "token_hash", unique = true, nullable = false)
    val tokenHash: String,

    @Column(name = "expires_at", nullable = false)
    val expiresAt: LocalDateTime,

    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(nullable = false)
    var revoked: Boolean = false,

    @Column(name = "replaced_by_token")
    var replacedByToken: String? = null
) {
    /**
     * Check if token is expired
     */
    fun isExpired(): Boolean {
        return LocalDateTime.now().isAfter(expiresAt)
    }

    /**
     * Check if token is valid (not expired and not revoked)
     */
    fun isValid(): Boolean {
        return !isExpired() && !revoked
    }

    /**
     * Revoke this token (used during logout or token rotation)
     */
    fun revoke(replacementToken: String? = null) {
        revoked = true
        replacedByToken = replacementToken
    }

    companion object {
        /**
         * Create a new refresh token
         */
        fun create(
            user: User,
            tokenHash: String,
            expiresAt: LocalDateTime
        ): RefreshToken {
            return RefreshToken(
                user = user,
                tokenHash = tokenHash,
                expiresAt = expiresAt,
                createdAt = LocalDateTime.now(),
                revoked = false
            )
        }
    }
}
