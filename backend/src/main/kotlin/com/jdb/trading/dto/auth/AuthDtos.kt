package com.jdb.trading.dto.auth

import jakarta.validation.constraints.Email
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Pattern
import jakarta.validation.constraints.Size

/**
 * Login request DTO
 */
data class LoginRequest(
    @field:Email(message = "Invalid email format")
    @field:NotBlank(message = "Email is required")
    val email: String,

    @field:NotBlank(message = "Password is required")
    @field:Size(min = 8, max = 128, message = "Password must be 8-128 characters")
    val password: String
)

/**
 * Register request DTO
 */
data class RegisterRequest(
    @field:Email(message = "Invalid email format")
    @field:NotBlank(message = "Email is required")
    val email: String,

    @field:NotBlank(message = "Password is required")
    @field:Size(min = 8, max = 128, message = "Password must be 8-128 characters")
    @field:Pattern(
        regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$",
        message = "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character"
    )
    val password: String,

    @field:Size(min = 2, max = 100, message = "Full name must be 2-100 characters")
    val fullName: String?
)

/**
 * Authentication response DTO
 */
data class AuthResponse(
    val user: UserDto,
    val message: String = "Authentication successful"
)

/**
 * User DTO (safe for client consumption)
 */
data class UserDto(
    val id: Long,
    val email: String,
    val fullName: String?,
    val role: String,
    val isActive: Boolean,
    val emailVerified: Boolean,
    val createdAt: String,
    val lastLogin: String?
)

/**
 * Refresh token request DTO
 */
data class RefreshTokenRequest(
    @field:NotBlank(message = "Refresh token is required")
    val refreshToken: String
)

/**
 * Logout request DTO
 */
data class LogoutRequest(
    val logoutFromAllDevices: Boolean = false
)
