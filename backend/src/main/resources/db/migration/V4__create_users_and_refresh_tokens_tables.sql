-- V4: Create users and refresh_tokens tables for authentication
-- Phase 2: Security Hardening - JWT Authentication

-- Create users table
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'USER',
    is_active BOOLEAN NOT NULL DEFAULT true,
    email_verified BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP,

    -- Constraints
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_role CHECK (role IN ('USER', 'PREMIUM', 'ADMIN'))
);

-- Create refresh_tokens table
CREATE TABLE refresh_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    revoked BOOLEAN NOT NULL DEFAULT false,
    replaced_by_token VARCHAR(255),

    -- Foreign key
    CONSTRAINT fk_refresh_token_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_email_verified ON users(email_verified);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
CREATE INDEX idx_refresh_tokens_revoked ON refresh_tokens(revoked);

-- Create composite index for finding valid tokens
CREATE INDEX idx_refresh_tokens_user_valid ON refresh_tokens(user_id, revoked, expires_at)
    WHERE revoked = false;

-- Add comments for documentation
COMMENT ON TABLE users IS 'User accounts for authentication and authorization';
COMMENT ON COLUMN users.email IS 'User email address (unique identifier for login)';
COMMENT ON COLUMN users.password_hash IS 'BCrypt hashed password (strength 12)';
COMMENT ON COLUMN users.role IS 'User role: USER, PREMIUM, or ADMIN';
COMMENT ON COLUMN users.is_active IS 'Whether the user account is active (false = locked)';
COMMENT ON COLUMN users.email_verified IS 'Whether the user has verified their email address';
COMMENT ON COLUMN users.last_login IS 'Timestamp of last successful login';

COMMENT ON TABLE refresh_tokens IS 'Refresh tokens for JWT token rotation';
COMMENT ON COLUMN refresh_tokens.token_hash IS 'SHA-256 hash of the refresh token';
COMMENT ON COLUMN refresh_tokens.expires_at IS 'Token expiration timestamp (7 days from creation)';
COMMENT ON COLUMN refresh_tokens.revoked IS 'Whether token has been revoked (logout)';
COMMENT ON COLUMN refresh_tokens.replaced_by_token IS 'Token hash that replaced this token (rotation)';

-- Insert default admin user (password: Admin123!)
-- Password hash for "Admin123!" with BCrypt strength 12
INSERT INTO users (email, password_hash, full_name, role, is_active, email_verified, created_at, updated_at)
VALUES (
    'admin@trading.local',
    '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYCZ4KV1vni',
    'System Administrator',
    'ADMIN',
    true,
    true,
    NOW(),
    NOW()
);

-- Insert test user (password: User123!)
INSERT INTO users (email, password_hash, full_name, role, is_active, email_verified, created_at, updated_at)
VALUES (
    'user@trading.local',
    '$2a$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
    'Test User',
    'USER',
    true,
    true,
    NOW(),
    NOW()
);
