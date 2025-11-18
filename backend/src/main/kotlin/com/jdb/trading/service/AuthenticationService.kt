package com.jdb.trading.service

import com.jdb.trading.domain.entity.RefreshToken
import com.jdb.trading.domain.entity.User
import com.jdb.trading.domain.entity.UserRole
import com.jdb.trading.dto.auth.*
import com.jdb.trading.repository.RefreshTokenRepository
import com.jdb.trading.repository.UserRepository
import com.jdb.trading.security.JwtService
import mu.KotlinLogging
import org.springframework.security.authentication.AuthenticationManager
import org.springframework.security.authentication.BadCredentialsException
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.security.core.Authentication
import org.springframework.security.core.userdetails.UsernameNotFoundException
import org.springframework.security.crypto.password.PasswordEncoder
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

private val logger = KotlinLogging.logger {}

/**
 * Authentication service handling registration, login, and token management
 */
@Service
class AuthenticationService(
    private val userRepository: UserRepository,
    private val refreshTokenRepository: RefreshTokenRepository,
    private val passwordEncoder: PasswordEncoder,
    private val jwtService: JwtService,
    private val authenticationManager: AuthenticationManager
) {

    private val dateFormatter = DateTimeFormatter.ISO_DATE_TIME

    /**
     * Register a new user
     */
    @Transactional
    fun register(request: RegisterRequest): AuthResponse {
        logger.info { "Registering new user: ${request.email}" }

        // Check if user already exists
        if (userRepository.existsByEmail(request.email.lowercase().trim())) {
            throw IllegalArgumentException("Email already registered: ${request.email}")
        }

        // Create new user
        val user = User.create(
            email = request.email,
            passwordHash = passwordEncoder.encode(request.password),
            fullName = request.fullName,
            role = UserRole.USER
        )

        val savedUser = userRepository.save(user)
        logger.info { "User registered successfully: ${savedUser.email} (ID: ${savedUser.id})" }

        return AuthResponse(
            user = savedUser.toDto(),
            message = "Registration successful"
        )
    }

    /**
     * Authenticate user and generate tokens
     */
    @Transactional
    fun login(request: LoginRequest): Pair<AuthResponse, TokenPair> {
        logger.info { "Login attempt for user: ${request.email}" }

        try {
            // Authenticate with Spring Security
            val authentication: Authentication = authenticationManager.authenticate(
                UsernamePasswordAuthenticationToken(
                    request.email.lowercase().trim(),
                    request.password
                )
            )

            val user = authentication.principal as User

            // Update last login
            user.updateLastLogin()
            userRepository.save(user)

            // Generate tokens
            val accessToken = jwtService.generateAccessToken(user)
            val refreshToken = jwtService.generateRefreshToken(user)

            // Store refresh token in database
            val refreshTokenEntity = RefreshToken.create(
                user = user,
                tokenHash = jwtService.hashToken(refreshToken),
                expiresAt = LocalDateTime.from(jwtService.getRefreshTokenExpiration())
            )
            refreshTokenRepository.save(refreshTokenEntity)

            logger.info { "User logged in successfully: ${user.email}" }

            return Pair(
                AuthResponse(
                    user = user.toDto(),
                    message = "Login successful"
                ),
                TokenPair(accessToken, refreshToken)
            )

        } catch (e: BadCredentialsException) {
            logger.warn { "Failed login attempt for: ${request.email}" }
            throw BadCredentialsException("Invalid email or password")
        }
    }

    /**
     * Refresh access token using refresh token
     */
    @Transactional
    fun refreshToken(refreshToken: String): TokenPair {
        logger.debug { "Refreshing access token" }

        // Validate refresh token
        val email = jwtService.extractEmail(refreshToken)
            ?: throw BadCredentialsException("Invalid refresh token")

        val user = userRepository.findByEmail(email)
            .orElseThrow { UsernameNotFoundException("User not found: $email") }

        // Verify token is valid and not expired
        if (!jwtService.isTokenValid(refreshToken, user)) {
            throw BadCredentialsException("Invalid or expired refresh token")
        }

        // Check if token exists in database and is not revoked
        val tokenHash = jwtService.hashToken(refreshToken)
        val storedToken = refreshTokenRepository.findByTokenHash(tokenHash)
            .orElseThrow { BadCredentialsException("Refresh token not found") }

        if (!storedToken.isValid()) {
            throw BadCredentialsException("Refresh token has been revoked or expired")
        }

        // Generate new tokens
        val newAccessToken = jwtService.generateAccessToken(user)
        val newRefreshToken = jwtService.generateRefreshToken(user)

        // Revoke old refresh token and store new one
        storedToken.revoke(jwtService.hashToken(newRefreshToken))
        refreshTokenRepository.save(storedToken)

        val newRefreshTokenEntity = RefreshToken.create(
            user = user,
            tokenHash = jwtService.hashToken(newRefreshToken),
            expiresAt = LocalDateTime.from(jwtService.getRefreshTokenExpiration())
        )
        refreshTokenRepository.save(newRefreshTokenEntity)

        logger.info { "Tokens refreshed for user: ${user.email}" }

        return TokenPair(newAccessToken, newRefreshToken)
    }

    /**
     * Logout user (revoke refresh token)
     */
    @Transactional
    fun logout(user: User, refreshToken: String?, logoutFromAllDevices: Boolean = false) {
        logger.info { "Logout request for user: ${user.email} (all devices: $logoutFromAllDevices)" }

        if (logoutFromAllDevices) {
            // Revoke all refresh tokens for this user
            refreshTokenRepository.revokeAllTokensForUser(user)
            logger.info { "All tokens revoked for user: ${user.email}" }
        } else if (refreshToken != null) {
            // Revoke specific refresh token
            val tokenHash = jwtService.hashToken(refreshToken)
            refreshTokenRepository.findByTokenHash(tokenHash).ifPresent { token ->
                token.revoke()
                refreshTokenRepository.save(token)
                logger.info { "Token revoked for user: ${user.email}" }
            }
        }
    }

    /**
     * Get current user info
     */
    fun getCurrentUser(user: User): UserDto {
        return user.toDto()
    }

    /**
     * Convert User entity to DTO
     */
    private fun User.toDto(): UserDto {
        return UserDto(
            id = this.id,
            email = this.email,
            fullName = this.fullName,
            role = this.role.name,
            isActive = this.isActive,
            emailVerified = this.emailVerified,
            createdAt = this.createdAt.format(dateFormatter),
            lastLogin = this.lastLogin?.format(dateFormatter)
        )
    }
}

/**
 * Token pair (access + refresh)
 */
data class TokenPair(
    val accessToken: String,
    val refreshToken: String
)
