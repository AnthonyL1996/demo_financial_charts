package com.jdb.trading.security

import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import mu.KotlinLogging
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.security.core.userdetails.UserDetails
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource
import org.springframework.stereotype.Component
import org.springframework.web.filter.OncePerRequestFilter

private val logger = KotlinLogging.logger {}

/**
 * JWT Authentication Filter
 * Extracts JWT from cookies/headers and validates it
 * Runs once per request before Spring Security's authentication
 */
@Component
class JwtAuthenticationFilter(
    private val jwtService: JwtService,
    private val userDetailsService: CustomUserDetailsService,
    private val jwtProperties: JwtProperties
) : OncePerRequestFilter() {

    override fun doFilterInternal(
        request: HttpServletRequest,
        response: HttpServletResponse,
        filterChain: FilterChain
    ) {
        try {
            // Extract JWT from request
            val jwt = extractJwtFromRequest(request)

            if (jwt != null) {
                // Extract email from token
                val email = jwtService.extractEmail(jwt)

                // If email exists and no authentication in context
                if (email != null && SecurityContextHolder.getContext().authentication == null) {
                    // Load user details
                    val userDetails: UserDetails = userDetailsService.loadUserByUsername(email)

                    // Validate token
                    if (jwtService.isTokenValid(jwt, userDetails)) {
                        // Create authentication token
                        val authToken = UsernamePasswordAuthenticationToken(
                            userDetails,
                            null,
                            userDetails.authorities
                        )

                        // Set authentication details
                        authToken.details = WebAuthenticationDetailsSource().buildDetails(request)

                        // Set authentication in security context
                        SecurityContextHolder.getContext().authentication = authToken

                        logger.debug { "JWT authentication successful for user: $email" }
                    } else {
                        logger.debug { "Invalid JWT token for user: $email" }
                    }
                }
            }
        } catch (e: Exception) {
            logger.warn(e) { "JWT authentication failed: ${e.message}" }
            // Don't block the filter chain, just log the error
            // Spring Security will handle authentication failure
        }

        // Continue filter chain
        filterChain.doFilter(request, response)
    }

    /**
     * Extract JWT from request (cookies first, then Authorization header)
     */
    private fun extractJwtFromRequest(request: HttpServletRequest): String? {
        // First, try to get token from httpOnly cookie
        request.cookies?.forEach { cookie ->
            if (cookie.name == jwtProperties.accessTokenCookieName) {
                logger.debug { "JWT found in cookie" }
                return cookie.value
            }
        }

        // Fallback: Try Authorization header (for API clients that can't use cookies)
        val authHeader = request.getHeader("Authorization")
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            logger.debug { "JWT found in Authorization header" }
            return authHeader.substring(7)
        }

        return null
    }
}
