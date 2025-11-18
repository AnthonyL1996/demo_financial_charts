package com.jdb.trading.repository

import com.jdb.trading.domain.entity.User
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.*

/**
 * Repository for User entity
 */
@Repository
interface UserRepository : JpaRepository<User, Long> {

    /**
     * Find user by email
     */
    fun findByEmail(email: String): Optional<User>

    /**
     * Check if email exists
     */
    fun existsByEmail(email: String): Boolean

    /**
     * Find all active users
     */
    fun findByIsActiveTrue(): List<User>

    /**
     * Find all verified users
     */
    fun findByEmailVerifiedTrue(): List<User>
}
