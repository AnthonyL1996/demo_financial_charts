package com.jdb.trading.security

import com.jdb.trading.security.ratelimit.RateLimitFilter
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.http.HttpMethod
import org.springframework.security.authentication.AuthenticationManager
import org.springframework.security.authentication.AuthenticationProvider
import org.springframework.security.authentication.dao.DaoAuthenticationProvider
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity
import org.springframework.security.config.annotation.web.builders.HttpSecurity
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity
import org.springframework.security.config.http.SessionCreationPolicy
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder
import org.springframework.security.crypto.password.PasswordEncoder
import org.springframework.security.web.SecurityFilterChain
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter
import org.springframework.web.cors.CorsConfiguration
import org.springframework.web.cors.CorsConfigurationSource
import org.springframework.web.cors.UrlBasedCorsConfigurationSource

/**
 * Spring Security configuration
 * Configures JWT authentication, CORS, rate limiting, and authorization rules
 */
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
class SecurityConfiguration(
    private val jwtAuthenticationFilter: JwtAuthenticationFilter,
    private val rateLimitFilter: RateLimitFilter,
    private val customUserDetailsService: CustomUserDetailsService
) {

    /**
     * Security filter chain configuration
     */
    @Bean
    fun securityFilterChain(http: HttpSecurity): SecurityFilterChain {
        http
            // Disable CSRF (using JWT tokens in httpOnly cookies with SameSite)
            .csrf { it.disable() }

            // CORS configuration
            .cors { it.configurationSource(corsConfigurationSource()) }

            // Session management (stateless - no sessions, using JWT)
            .sessionManagement { it.sessionCreationPolicy(SessionCreationPolicy.STATELESS) }

            // Authorization rules
            .authorizeHttpRequests { auth ->
                auth
                    // Public endpoints (no authentication required)
                    .requestMatchers(
                        "/api/auth/register",
                        "/api/auth/login",
                        "/api/auth/refresh",
                        "/actuator/health",
                        "/actuator/info"
                    ).permitAll()

                    // Public read-only stock endpoints
                    .requestMatchers(HttpMethod.GET, "/api/stocks/**").permitAll()
                    .requestMatchers(HttpMethod.GET, "/api/health").permitAll()

                    // Admin-only endpoints (future use)
                    .requestMatchers("/api/admin/**").hasRole("ADMIN")

                    // All other endpoints require authentication
                    .anyRequest().authenticated()
            }

            // Authentication provider
            .authenticationProvider(authenticationProvider())

            // Add rate limit filter first (before any authentication)
            .addFilterBefore(rateLimitFilter, UsernamePasswordAuthenticationFilter::class.java)

            // Add JWT filter after rate limiting
            .addFilterAfter(jwtAuthenticationFilter, RateLimitFilter::class.java)

        return http.build()
    }

    /**
     * CORS configuration
     * Whitelists specific origins and allows credentials (cookies)
     */
    @Bean
    fun corsConfigurationSource(): CorsConfigurationSource {
        val configuration = CorsConfiguration().apply {
            // Allowed origins (update for production)
            allowedOrigins = listOf(
                "http://localhost:3000",      // Next.js dev
                "http://localhost:3001",      // Alternative port
                "https://yourdomain.com",     // Production domain (update this!)
                "https://app.yourdomain.com"  // Production app (update this!)
            )

            // Allowed methods
            allowedMethods = listOf("GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH")

            // Allowed headers
            allowedHeaders = listOf(
                "Authorization",
                "Content-Type",
                "X-Requested-With",
                "Accept",
                "Origin",
                "Access-Control-Request-Method",
                "Access-Control-Request-Headers"
            )

            // Exposed headers (client can read these)
            exposedHeaders = listOf(
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Credentials"
            )

            // Allow credentials (cookies)
            allowCredentials = true

            // Max age for preflight requests (1 hour)
            maxAge = 3600L
        }

        val source = UrlBasedCorsConfigurationSource()
        source.registerCorsConfiguration("/**", configuration)
        return source
    }

    /**
     * Password encoder bean (BCrypt with strength 12)
     */
    @Bean
    fun passwordEncoder(): PasswordEncoder {
        return BCryptPasswordEncoder(12)
    }

    /**
     * Authentication provider
     */
    @Bean
    fun authenticationProvider(): AuthenticationProvider {
        val provider = DaoAuthenticationProvider()
        provider.setUserDetailsService(customUserDetailsService)
        provider.setPasswordEncoder(passwordEncoder())
        return provider
    }

    /**
     * Authentication manager bean
     */
    @Bean
    fun authenticationManager(config: AuthenticationConfiguration): AuthenticationManager {
        return config.authenticationManager
    }
}
