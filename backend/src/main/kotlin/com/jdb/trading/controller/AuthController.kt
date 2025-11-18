package com.jdb.trading.controller

import com.jdb.trading.domain.entity.User
import com.jdb.trading.dto.ApiResponse
import com.jdb.trading.dto.auth.*
import com.jdb.trading.security.JwtProperties
import com.jdb.trading.service.AuthenticationService
import jakarta.servlet.http.Cookie
import jakarta.servlet.http.HttpServletResponse
import jakarta.validation.Valid
import mu.KotlinLogging
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.security.core.annotation.AuthenticationPrincipal
import org.springframework.web.bind.annotation.*

private val logger = KotlinLogging.logger {}

/**
 * Authentication controller
 * Handles user registration, login, logout, and token refresh
 */
@RestController
@RequestMapping("/api/auth")
class AuthController(
    private val authenticationService: AuthenticationService,
    private val jwtProperties: JwtProperties
) {

    /**
     * POST /api/auth/register
     * Register a new user account
     */
    @PostMapping("/register")
    fun register(
        @Valid @RequestBody request: RegisterRequest
    ): ResponseEntity<ApiResponse<AuthResponse>> {
        logger.info { "Registration request for: ${request.email}" }

        return try {
            val response = authenticationService.register(request)
            ResponseEntity
                .status(HttpStatus.CREATED)
                .body(ApiResponse.success(response, "User registered successfully"))
        } catch (e: IllegalArgumentException) {
            logger.warn { "Registration failed: ${e.message}" }
            ResponseEntity
                .badRequest()
                .body(ApiResponse.error(e.message ?: "Registration failed"))
        }
    }

    /**
     * POST /api/auth/login
     * Authenticate user and return tokens in httpOnly cookies
     */
    @PostMapping("/login")
    fun login(
        @Valid @RequestBody request: LoginRequest,
        response: HttpServletResponse
    ): ResponseEntity<ApiResponse<AuthResponse>> {
        logger.info { "Login request for: ${request.email}" }

        return try {
            val (authResponse, tokens) = authenticationService.login(request)

            // Set tokens in httpOnly cookies
            setTokenCookies(response, tokens.accessToken, tokens.refreshToken)

            ResponseEntity.ok(ApiResponse.success(authResponse, "Login successful"))
        } catch (e: Exception) {
            logger.warn(e) { "Login failed for: ${request.email}" }
            ResponseEntity
                .status(HttpStatus.UNAUTHORIZED)
                .body(ApiResponse.error("Invalid email or password"))
        }
    }

    /**
     * POST /api/auth/refresh
     * Refresh access token using refresh token from cookie
     */
    @PostMapping("/refresh")
    fun refreshToken(
        @CookieValue(name = "refresh_token", required = false) refreshToken: String?,
        response: HttpServletResponse
    ): ResponseEntity<ApiResponse<Map<String, String>>> {
        logger.debug { "Token refresh request" }

        if (refreshToken == null) {
            return ResponseEntity
                .status(HttpStatus.UNAUTHORIZED)
                .body(ApiResponse.error("Refresh token not found"))
        }

        return try {
            val tokens = authenticationService.refreshToken(refreshToken)

            // Set new tokens in cookies
            setTokenCookies(response, tokens.accessToken, tokens.refreshToken)

            ResponseEntity.ok(
                ApiResponse.success(
                    mapOf("message" to "Tokens refreshed successfully"),
                    "Tokens refreshed"
                )
            )
        } catch (e: Exception) {
            logger.warn(e) { "Token refresh failed" }
            ResponseEntity
                .status(HttpStatus.UNAUTHORIZED)
                .body(ApiResponse.error("Invalid or expired refresh token"))
        }
    }

    /**
     * POST /api/auth/logout
     * Logout user and revoke refresh token
     */
    @PostMapping("/logout")
    fun logout(
        @AuthenticationPrincipal user: User,
        @RequestBody(required = false) request: LogoutRequest?,
        @CookieValue(name = "refresh_token", required = false) refreshToken: String?,
        response: HttpServletResponse
    ): ResponseEntity<ApiResponse<Map<String, String>>> {
        logger.info { "Logout request for user: ${user.email}" }

        val logoutFromAllDevices = request?.logoutFromAllDevices ?: false

        authenticationService.logout(user, refreshToken, logoutFromAllDevices)

        // Clear cookies
        clearTokenCookies(response)

        val message = if (logoutFromAllDevices) {
            "Logged out from all devices"
        } else {
            "Logged out successfully"
        }

        return ResponseEntity.ok(
            ApiResponse.success(
                mapOf("message" to message),
                message
            )
        )
    }

    /**
     * GET /api/auth/me
     * Get current authenticated user info
     */
    @GetMapping("/me")
    fun getCurrentUser(
        @AuthenticationPrincipal user: User
    ): ResponseEntity<ApiResponse<UserDto>> {
        logger.debug { "Get current user request: ${user.email}" }

        val userDto = authenticationService.getCurrentUser(user)
        return ResponseEntity.ok(ApiResponse.success(userDto))
    }

    /**
     * Helper: Set JWT tokens in httpOnly cookies
     */
    private fun setTokenCookies(
        response: HttpServletResponse,
        accessToken: String,
        refreshToken: String
    ) {
        // Access token cookie (15 minutes)
        val accessTokenCookie = Cookie(jwtProperties.accessTokenCookieName, accessToken).apply {
            isHttpOnly = true
            secure = true  // Set to true in production (requires HTTPS)
            path = "/"
            maxAge = (jwtProperties.accessTokenExpirationMinutes * 60).toInt()
            setAttribute("SameSite", "Strict")
        }

        // Refresh token cookie (7 days)
        val refreshTokenCookie = Cookie(jwtProperties.refreshTokenCookieName, refreshToken).apply {
            isHttpOnly = true
            secure = true  // Set to true in production (requires HTTPS)
            path = "/api/auth"  // Only send to auth endpoints
            maxAge = (jwtProperties.refreshTokenExpirationDays * 24 * 60 * 60).toInt()
            setAttribute("SameSite", "Strict")
        }

        response.addCookie(accessTokenCookie)
        response.addCookie(refreshTokenCookie)

        logger.debug { "Tokens set in httpOnly cookies" }
    }

    /**
     * Helper: Clear JWT cookies
     */
    private fun clearTokenCookies(response: HttpServletResponse) {
        val accessTokenCookie = Cookie(jwtProperties.accessTokenCookieName, "").apply {
            isHttpOnly = true
            secure = true
            path = "/"
            maxAge = 0
        }

        val refreshTokenCookie = Cookie(jwtProperties.refreshTokenCookieName, "").apply {
            isHttpOnly = true
            secure = true
            path = "/api/auth"
            maxAge = 0
        }

        response.addCookie(accessTokenCookie)
        response.addCookie(refreshTokenCookie)

        logger.debug { "Token cookies cleared" }
    }
}
