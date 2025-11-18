package com.jdb.trading.domain.entity

import jakarta.persistence.*
import org.springframework.security.core.GrantedAuthority
import org.springframework.security.core.authority.SimpleGrantedAuthority
import org.springframework.security.core.userdetails.UserDetails
import java.time.LocalDateTime

/**
 * User entity for authentication and authorization
 */
@Entity
@Table(name = "users")
data class User(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(unique = true, nullable = false)
    val email: String,

    @Column(name = "password_hash", nullable = false)
    private val passwordHash: String,

    @Column(name = "full_name")
    val fullName: String? = null,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val role: UserRole = UserRole.USER,

    @Column(name = "is_active", nullable = false)
    val isActive: Boolean = true,

    @Column(name = "email_verified", nullable = false)
    val emailVerified: Boolean = false,

    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(name = "updated_at", nullable = false)
    var updatedAt: LocalDateTime = LocalDateTime.now(),

    @Column(name = "last_login")
    var lastLogin: LocalDateTime? = null,

    // Relationships
    @OneToMany(mappedBy = "user", cascade = [CascadeType.ALL], orphanRemoval = true)
    val refreshTokens: MutableList<RefreshToken> = mutableListOf()
) : UserDetails {

    /**
     * Returns the authorities granted to the user
     */
    override fun getAuthorities(): Collection<GrantedAuthority> {
        return listOf(SimpleGrantedAuthority("ROLE_${role.name}"))
    }

    /**
     * Returns the password used to authenticate the user
     */
    override fun getPassword(): String = passwordHash

    /**
     * Returns the username used to authenticate the user (email in our case)
     */
    override fun getUsername(): String = email

    /**
     * Indicates whether the user's account has expired
     */
    override fun isAccountNonExpired(): Boolean = true

    /**
     * Indicates whether the user is locked or unlocked
     */
    override fun isAccountNonLocked(): Boolean = isActive

    /**
     * Indicates whether the user's credentials (password) has expired
     */
    override fun isCredentialsNonExpired(): Boolean = true

    /**
     * Indicates whether the user is enabled or disabled
     */
    override fun isEnabled(): Boolean = isActive

    /**
     * Update last login timestamp
     */
    fun updateLastLogin() {
        lastLogin = LocalDateTime.now()
    }

    companion object {
        /**
         * Create a new user with hashed password
         */
        fun create(
            email: String,
            passwordHash: String,
            fullName: String?,
            role: UserRole = UserRole.USER
        ): User {
            return User(
                email = email.lowercase().trim(),
                passwordHash = passwordHash,
                fullName = fullName?.trim(),
                role = role,
                isActive = true,
                emailVerified = false,
                createdAt = LocalDateTime.now(),
                updatedAt = LocalDateTime.now()
            )
        }
    }
}

/**
 * User roles
 */
enum class UserRole {
    USER,       // Regular user
    PREMIUM,    // Premium subscriber
    ADMIN       // Administrator
}
