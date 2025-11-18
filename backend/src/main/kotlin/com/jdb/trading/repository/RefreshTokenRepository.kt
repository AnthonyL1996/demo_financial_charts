package com.jdb.trading.repository

import com.jdb.trading.domain.entity.RefreshToken
import com.jdb.trading.domain.entity.User
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Modifying
import org.springframework.data.jpa.repository.Query
import org.springframework.stereotype.Repository
import java.time.LocalDateTime
import java.util.*

/**
 * Repository for RefreshToken entity
 */
@Repository
interface RefreshTokenRepository : JpaRepository<RefreshToken, Long> {

    /**
     * Find refresh token by token hash
     */
    fun findByTokenHash(tokenHash: String): Optional<RefreshToken>

    /**
     * Find all valid (non-revoked, non-expired) tokens for a user
     */
    @Query(
        """
        SELECT rt FROM RefreshToken rt
        WHERE rt.user = :user
        AND rt.revoked = false
        AND rt.expiresAt > :now
        """
    )
    fun findValidTokensByUser(user: User, now: LocalDateTime = LocalDateTime.now()): List<RefreshToken>

    /**
     * Revoke all tokens for a user (logout from all devices)
     */
    @Modifying
    @Query("UPDATE RefreshToken rt SET rt.revoked = true WHERE rt.user = :user")
    fun revokeAllTokensForUser(user: User)

    /**
     * Delete expired tokens (cleanup job)
     */
    @Modifying
    @Query("DELETE FROM RefreshToken rt WHERE rt.expiresAt < :now")
    fun deleteExpiredTokens(now: LocalDateTime = LocalDateTime.now())

    /**
     * Count valid tokens for a user
     */
    @Query(
        """
        SELECT COUNT(rt) FROM RefreshToken rt
        WHERE rt.user = :user
        AND rt.revoked = false
        AND rt.expiresAt > :now
        """
    )
    fun countValidTokensByUser(user: User, now: LocalDateTime = LocalDateTime.now()): Long
}
