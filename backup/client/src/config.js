/**
 * Configuration management for Client Application
 */

require('dotenv').config();

const config = {
  // Server Configuration
  server: {
    port: parseInt(process.env.PORT) || 3000,
    host: process.env.HOST || '0.0.0.0',
    nodeEnv: process.env.NODE_ENV || 'development',
    trustProxy: process.env.TRUST_PROXY === 'true'
  },

  // External Services
  services: {
    authServer: process.env.AUTH_SERVER_URL || 'http://localhost:8001',
    backendApi: process.env.BACKEND_API_URL || 'http://localhost:8000'
  },

  // Session Configuration
  session: {
    secret: process.env.SESSION_SECRET || 'your-super-secret-session-key-change-this-in-production',
    maxAge: parseInt(process.env.SESSION_MAX_AGE) || 86400000, // 24 hours in milliseconds
    secure: process.env.SECURE_COOKIES === 'true',
    sameSite: process.env.SAME_SITE || 'lax'
  },

  // Redis Configuration
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379/1'
  },

  // Logging Configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    file: process.env.LOG_FILE || 'client.log'
  },

  // CORS Configuration
  cors: {
    allowedOrigins: process.env.ALLOWED_ORIGINS ? 
      process.env.ALLOWED_ORIGINS.split(',').map(origin => origin.trim()) : 
      ['http://localhost:3000']
  },

  // Rate Limiting Configuration
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 900000, // 15 minutes
    maxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100
  },

  // Security Configuration
  security: {
    helmetOptions: {
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          styleSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
          scriptSrc: ["'self'", "https://cdn.jsdelivr.net"],
          imgSrc: ["'self'", "data:", "https:"],
          connectSrc: ["'self'", process.env.AUTH_SERVER_URL, process.env.BACKEND_API_URL],
          fontSrc: ["'self'", "https://cdn.jsdelivr.net"],
          objectSrc: ["'none'"],
          mediaSrc: ["'self'"],
          frameSrc: ["'none'"]
        }
      },
      crossOriginEmbedderPolicy: false
    }
  },

  // API Endpoints
  endpoints: {
    auth: {
      login: '/auth/login',
      refresh: '/auth/refresh',
      logout: '/auth/logout'
    },
    api: {
      protectedData: '/api/protected-data',
      userProfile: '/api/user-profile',
      adminOnly: '/api/admin-only',
      itDepartment: '/api/it-department'
    }
  },

  // Development mode check
  isDevelopment: () => config.server.nodeEnv === 'development',
  isProduction: () => config.server.nodeEnv === 'production'
};

// Validation
if (!config.session.secret || config.session.secret.includes('change-this')) {
  console.warn('WARNING: Using default session secret. Please set SESSION_SECRET in production!');
}

if (config.isProduction() && !config.session.secure) {
  console.warn('WARNING: Secure cookies disabled in production. Set SECURE_COOKIES=true');
}

module.exports = config; 