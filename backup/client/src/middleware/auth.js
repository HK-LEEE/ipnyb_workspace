/**
 * Authentication middleware for client application
 */

const apiClient = require('../services/apiClient');

/**
 * Middleware to check if user is authenticated
 */
function requireAuth(req, res, next) {
  if (!apiClient.isAuthenticated()) {
    console.log('[AUTH MIDDLEWARE] User not authenticated, redirecting to login');
    return res.redirect('/login');
  }
  
  console.log('[AUTH MIDDLEWARE] User authenticated, proceeding');
  next();
}

/**
 * Middleware to redirect authenticated users away from login page
 */
function redirectIfAuthenticated(req, res, next) {
  if (apiClient.isAuthenticated()) {
    console.log('[AUTH MIDDLEWARE] User already authenticated, redirecting to dashboard');
    return res.redirect('/dashboard');
  }
  
  next();
}

/**
 * Middleware to add authentication status to all responses
 */
function addAuthStatus(req, res, next) {
  res.locals.isAuthenticated = apiClient.isAuthenticated();
  next();
}

module.exports = {
  requireAuth,
  redirectIfAuthenticated,
  addAuthStatus
}; 