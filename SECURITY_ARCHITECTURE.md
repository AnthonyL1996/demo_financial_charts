# Security Architecture Design

## Phase 2: Security Hardening

### 1. JWT Authentication Architecture

#### Overview
- **Token Type**: JWT (JSON Web Tokens) with RS256 (asymmetric encryption)
- **Storage**: httpOnly cookies (XSS protection) + SameSite=Strict (CSRF protection)
- **Refresh Strategy**: Refresh tokens with rotation
- **Token Lifetime**:
  - Access Token: 15 minutes
  - Refresh Token: 7 days

#### Components

##### Backend (Spring Security)
```
┌─────────────────────────────────────────────────────────┐
│                    Spring Security Filter Chain          │
├─────────────────────────────────────────────────────────┤
│  1. JWT Authentication Filter                           │
│     - Extract JWT from cookie                            │
│     - Validate signature & expiration                    │
│     - Set SecurityContext                                │
│  2. Authorization Filter                                 │
│     - Check user roles/permissions                       │
│  3. Exception Handling Filter                            │
│     - Handle auth failures gracefully                    │
└─────────────────────────────────────────────────────────┘
```

**Endpoints**:
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT in httpOnly cookie)
- `POST /api/auth/logout` - Invalidate tokens
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info

**Security Configuration**:
- CORS: Whitelist specific origins (localhost:3000, production domain)
- CSRF: Disabled for stateless JWT (but protected by SameSite cookie attribute)
- Password: BCrypt with strength 12
- Rate Limiting: 5 login attempts per IP per 15 minutes

##### Frontend (Next.js)
```
┌─────────────────────────────────────────────────────────┐
│                    Authentication Flow                    │
├─────────────────────────────────────────────────────────┤
│  1. Login Form → POST /api/auth/login                   │
│  2. Server sets httpOnly cookie with JWT                │
│  3. Subsequent requests include cookie automatically    │
│  4. API client intercepts 401 → refresh token           │
│  5. On refresh failure → redirect to login              │
└─────────────────────────────────────────────────────────┘
```

**Pages**:
- `/login` - Login form
- `/register` - Registration form
- `/logout` - Logout (clear cookies + redirect)

**Protection**:
- Protected routes wrapped in AuthGuard
- Auto-redirect to login if not authenticated
- Token refresh on API 401 errors

#### Database Schema

**users table**:
```sql
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
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

**refresh_tokens table**:
```sql
CREATE TABLE refresh_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    revoked BOOLEAN NOT NULL DEFAULT false,
    replaced_by_token VARCHAR(255),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
```

#### JWT Payload Structure

**Access Token**:
```json
{
  "sub": "user@example.com",
  "userId": 123,
  "role": "USER",
  "iat": 1699123456,
  "exp": 1699124356,
  "type": "access"
}
```

**Refresh Token**:
```json
{
  "sub": "user@example.com",
  "userId": 123,
  "tokenId": "uuid-v4",
  "iat": 1699123456,
  "exp": 1699728256,
  "type": "refresh"
}
```

### 2. Rate Limiting Architecture

#### Implementation: Bucket4j (Token Bucket Algorithm)

**Configuration**:
```yaml
rate-limiting:
  enabled: true
  configs:
    default:
      capacity: 100          # tokens
      refill-rate: 10        # tokens/second
      refill-period: 1s
    auth-login:
      capacity: 5            # 5 attempts
      refill-rate: 1         # 1 token
      refill-period: 15m     # per 15 minutes
    api-general:
      capacity: 50
      refill-rate: 5
      refill-period: 1s
```

**Endpoints with Custom Limits**:
- `/api/auth/login` - 5 requests per 15 minutes per IP
- `/api/auth/register` - 3 requests per hour per IP
- `/api/stocks/**` - 50 requests per second per user
- `/api/signals/**` - 20 requests per minute per user

#### Storage: Redis (for distributed rate limiting)
```
Key Pattern: rate_limit:{endpoint}:{identifier}:{window}
Value: token_bucket_state
TTL: window_duration
```

### 3. Input Validation Architecture

#### Backend (Bean Validation / JSR-380)

**DTOs with Validation**:
```kotlin
data class RegisterRequest(
    @field:Email(message = "Invalid email format")
    @field:NotBlank(message = "Email is required")
    val email: String,

    @field:Size(min = 8, max = 128, message = "Password must be 8-128 characters")
    @field:Pattern(
        regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$",
        message = "Password must contain uppercase, lowercase, number, and special character"
    )
    val password: String,

    @field:Size(min = 2, max = 100, message = "Name must be 2-100 characters")
    val fullName: String
)

data class StockDataRequest(
    @field:Pattern(regexp = "^[A-Z]{1,5}$", message = "Invalid ticker format")
    val ticker: String,

    @field:Pattern(regexp = "^(1D|1W|1M)$", message = "Invalid timeframe")
    val timeframe: String = "1D",

    @field:PastOrPresent(message = "Start date cannot be in future")
    val start: LocalDate?,

    @field:PastOrPresent(message = "End date cannot be in future")
    val end: LocalDate?
)
```

**Controller Validation**:
```kotlin
@PostMapping("/register")
fun register(@Valid @RequestBody request: RegisterRequest): ResponseEntity<ApiResponse<UserDto>> {
    // Validation happens automatically before method execution
    // MethodArgumentNotValidException thrown if invalid
}
```

**Global Exception Handler**:
```kotlin
@RestControllerAdvice
class GlobalExceptionHandler {
    @ExceptionHandler(MethodArgumentNotValidException::class)
    fun handleValidationErrors(ex: MethodArgumentNotValidException): ResponseEntity<ApiResponse<Map<String, String>>> {
        val errors = ex.bindingResult.fieldErrors.associate {
            it.field to (it.defaultMessage ?: "Invalid value")
        }
        return ResponseEntity.badRequest().body(ApiResponse.error("Validation failed", errors))
    }
}
```

#### ML Service (Pydantic)

**Models with Validation**:
```python
from pydantic import BaseModel, Field, validator

class SignalGenerationRequest(BaseModel):
    ticker: str = Field(..., regex="^[A-Z]{1,5}$", description="Stock ticker")
    timeframe: str = Field(default="daily", regex="^(daily|weekly|monthly)$")

    @validator('ticker')
    def validate_ticker(cls, v):
        if not v.isupper():
            raise ValueError('Ticker must be uppercase')
        return v

class MultiTimeframeRequest(BaseModel):
    ticker: str = Field(..., regex="^[A-Z]{1,5}$")
    model_ticker: str = Field(default="spy", regex="^[a-z]{1,5}$")
```

**Flask Integration**:
```python
from pydantic import ValidationError

@app.route('/api/signals/generate', methods=['POST'])
def generate_signal():
    try:
        request_data = SignalGenerationRequest(**request.json)
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.errors()}), 400

    # Process validated data
    signal = predictor.generate_signal(request_data.ticker, request_data.timeframe)
    return jsonify(signal)
```

### 4. CORS Configuration

#### Backend (Spring)
```kotlin
@Configuration
class SecurityConfig {
    @Bean
    fun corsConfigurationSource(): CorsConfigurationSource {
        val configuration = CorsConfiguration().apply {
            // PRODUCTION: Whitelist specific origins
            allowedOrigins = listOf(
                "https://yourdomain.com",
                "https://app.yourdomain.com"
            )

            // DEVELOPMENT: Localhost only
            if (environment == "development") {
                allowedOrigins = listOf("http://localhost:3000")
            }

            allowedMethods = listOf("GET", "POST", "PUT", "DELETE", "OPTIONS")
            allowedHeaders = listOf("Authorization", "Content-Type", "X-Requested-With")
            allowCredentials = true
            maxAge = 3600
        }

        return UrlBasedCorsConfigurationSource().apply {
            registerCorsConfiguration("/**", configuration)
        }
    }
}
```

#### ML Service (Flask-CORS)
```python
from flask_cors import CORS

app = Flask(__name__)

# PRODUCTION
if os.getenv('ENVIRONMENT') == 'production':
    CORS(app, origins=[
        "https://yourdomain.com",
        "https://api.yourdomain.com"
    ], supports_credentials=True)

# DEVELOPMENT
else:
    CORS(app, origins=["http://localhost:3000", "http://localhost:8080"],
         supports_credentials=True)
```

### 5. Environment Variable Validation

#### Backend (Spring Boot)
```kotlin
@Configuration
@ConfigurationProperties(prefix = "app")
@Validated
data class AppConfig(
    @field:NotBlank(message = "JWT secret is required")
    @field:Size(min = 32, message = "JWT secret must be at least 32 characters")
    val jwtSecret: String,

    @field:NotBlank(message = "ML service URL is required")
    @field:Pattern(regexp = "^https?://.*", message = "ML service URL must be valid")
    val mlServiceUrl: String,

    @field:NotBlank(message = "Database URL is required")
    val databaseUrl: String,

    @field:Min(value = 1, message = "JWT expiration must be positive")
    val jwtExpirationMinutes: Int = 15
)

@Component
class ConfigValidator(private val appConfig: AppConfig) : CommandLineRunner {
    override fun run(vararg args: String?) {
        logger.info("Configuration validated successfully")
        logger.info("ML Service URL: ${appConfig.mlServiceUrl}")
        logger.info("JWT Expiration: ${appConfig.jwtExpirationMinutes} minutes")
    }
}
```

#### ML Service (Python)
```python
from pydantic import BaseSettings, Field, validator
import sys

class Settings(BaseSettings):
    # Required settings
    database_url: str = Field(..., env='DATABASE_URL')
    flask_secret_key: str = Field(..., min_length=32, env='FLASK_SECRET_KEY')

    # Optional with defaults
    model_path: str = Field(default='./models', env='MODEL_PATH')
    log_level: str = Field(default='INFO', env='LOG_LEVEL')

    # Validation
    @validator('database_url')
    def validate_database_url(cls, v):
        if not v.startswith('postgresql://'):
            raise ValueError('DATABASE_URL must be a PostgreSQL connection string')
        return v

    @validator('log_level')
    def validate_log_level(cls, v):
        if v not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            raise ValueError('Invalid log level')
        return v

    class Config:
        env_file = '.env'

# Validate on startup
try:
    settings = Settings()
except Exception as e:
    print(f"Configuration validation failed: {e}")
    sys.exit(1)
```

### 6. Security Audit Checklist (OWASP Top 10 2021)

#### A01:2021 – Broken Access Control
- [ ] Implement role-based access control (RBAC)
- [ ] Validate user permissions on every request
- [ ] Prevent parameter tampering (user ID in URL)
- [ ] Implement proper session management

#### A02:2021 – Cryptographic Failures
- [ ] Use BCrypt for password hashing (strength 12+)
- [ ] Use HTTPS everywhere (TLS 1.3)
- [ ] Encrypt sensitive data at rest
- [ ] Use secure random number generators

#### A03:2021 – Injection
- [ ] Use parameterized queries (JPA/SQLAlchemy)
- [ ] Validate and sanitize all inputs
- [ ] Use ORMs to prevent SQL injection
- [ ] Escape special characters in queries

#### A04:2021 – Insecure Design
- [ ] Implement defense in depth
- [ ] Use threat modeling for critical flows
- [ ] Separate admin and user flows
- [ ] Implement rate limiting

#### A05:2021 – Security Misconfiguration
- [ ] Remove default credentials
- [ ] Disable directory listing
- [ ] Remove unnecessary features
- [ ] Configure security headers properly

#### A06:2021 – Vulnerable and Outdated Components
- [ ] Keep dependencies up to date
- [ ] Use Dependabot/Renovate for alerts
- [ ] Audit dependencies regularly
- [ ] Remove unused dependencies

#### A07:2021 – Identification and Authentication Failures
- [ ] Implement multi-factor authentication (future)
- [ ] Use secure session management
- [ ] Implement account lockout
- [ ] Log authentication attempts

#### A08:2021 – Software and Data Integrity Failures
- [ ] Verify dependencies (checksums)
- [ ] Use signed containers
- [ ] Implement CI/CD pipeline security
- [ ] Code review for security

#### A09:2021 – Security Logging and Monitoring Failures
- [ ] Log all authentication events
- [ ] Log authorization failures
- [ ] Monitor for suspicious patterns
- [ ] Set up alerts for security events

#### A10:2021 – Server-Side Request Forgery (SSRF)
- [ ] Validate all URLs
- [ ] Use allowlist for external requests
- [ ] Disable HTTP redirects
- [ ] Sanitize user-supplied URLs

### 7. Implementation Priority

1. **Week 1**: JWT Authentication
   - User entity + repository
   - JWT service
   - Authentication endpoints
   - Frontend login/register

2. **Week 2**: Security Hardening
   - Rate limiting (Bucket4j)
   - Input validation (all endpoints)
   - CORS configuration
   - Environment validation

3. **Week 3**: Testing & Audit
   - Security tests
   - OWASP Top 10 audit
   - Penetration testing
   - Security documentation
