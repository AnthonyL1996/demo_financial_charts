package com.jdb.trading.security

import com.jdb.trading.repository.UserRepository
import mu.KotlinLogging
import org.springframework.security.core.userdetails.UserDetails
import org.springframework.security.core.userdetails.UserDetailsService
import org.springframework.security.core.userdetails.UsernameNotFoundException
import org.springframework.stereotype.Service

private val logger = KotlinLogging.logger {}

/**
 * Custom UserDetailsService implementation for Spring Security
 * Loads users from database by email
 */
@Service
class CustomUserDetailsService(
    private val userRepository: UserRepository
) : UserDetailsService {

    /**
     * Load user by username (email in our case)
     * Required by Spring Security for authentication
     */
    override fun loadUserByUsername(email: String): UserDetails {
        logger.debug { "Loading user by email: $email" }

        return userRepository.findByEmail(email.lowercase().trim())
            .orElseThrow {
                logger.warn { "User not found with email: $email" }
                UsernameNotFoundException("User not found with email: $email")
            }
    }

    /**
     * Load user by ID (for token-based authentication)
     */
    fun loadUserById(userId: Long): UserDetails {
        logger.debug { "Loading user by ID: $userId" }

        return userRepository.findById(userId)
            .orElseThrow {
                logger.warn { "User not found with ID: $userId" }
                UsernameNotFoundException("User not found with ID: $userId")
            }
    }
}
