/**
 * Main Express application for Client
 */

const express = require('express');
const session = require('express-session');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const path = require('path');

const config = require('./config');
const { addAuthStatus } = require('./middleware/auth');

// Import routes
const authRoutes = require('./routes/auth');
const dashboardRoutes = require('./routes/dashboard');
const apiRoutes = require('./routes/api');

const app = express();

// Trust proxy if configured
if (config.server.trustProxy) {
  app.set('trust proxy', 1);
}

// Security middleware
app.use(helmet(config.security.helmetOptions));

// Logging middleware
app.use(morgan(config.isDevelopment() ? 'dev' : 'combined'));

// CORS configuration
app.use(cors({
  origin: config.cors.allowedOrigins,
  credentials: true
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: config.rateLimit.windowMs,
  max: config.rateLimit.maxRequests,
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false
});
app.use(limiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(cookieParser());

// Session configuration
app.use(session({
  secret: config.session.secret,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: config.session.secure,
    httpOnly: true,
    maxAge: config.session.maxAge,
    sameSite: config.session.sameSite
  }
}));

// Global middleware
app.use(addAuthStatus);

// Static files
app.use('/public', express.static(path.join(__dirname, '../public')));

// Routes
app.use('/', authRoutes);
app.use('/', dashboardRoutes);
app.use('/', apiRoutes);

// Root route
app.get('/', (req, res) => {
  if (res.locals.isAuthenticated) {
    res.redirect('/dashboard');
  } else {
    res.redirect('/login');
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'Client Application',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>404 - Page Not Found</title>
      <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; }
        .container { max-width: 500px; margin: 0 auto; }
        h1 { color: #333; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>404 - Page Not Found</h1>
        <p>The page you are looking for does not exist.</p>
        <p><a href="/">Go back to home</a></p>
      </div>
    </body>
    </html>
  `);
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('[APP] Unhandled error:', err);
  
  res.status(500).send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>500 - Internal Server Error</title>
      <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; }
        .container { max-width: 500px; margin: 0 auto; }
        h1 { color: #dc3545; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>500 - Internal Server Error</h1>
        <p>Something went wrong on our end.</p>
        <p><a href="/">Go back to home</a></p>
        ${config.isDevelopment() ? `<pre style="text-align: left; background: #f8f9fa; padding: 15px; border-radius: 4px;">${err.stack}</pre>` : ''}
      </div>
    </body>
    </html>
  `);
});

// Start server
const PORT = config.server.port;
const HOST = config.server.host;

app.listen(PORT, HOST, () => {
  console.log(`[CLIENT] Server running on http://${HOST}:${PORT}`);
  console.log(`[CLIENT] Environment: ${config.server.nodeEnv}`);
  console.log(`[CLIENT] Auth Server: ${config.services.authServer}`);
  console.log(`[CLIENT] Backend API: ${config.services.backendApi}`);
});

module.exports = app; 