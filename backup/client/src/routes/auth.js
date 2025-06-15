/**
 * Authentication routes
 */

const express = require('express');
const apiClient = require('../services/apiClient');
const { redirectIfAuthenticated } = require('../middleware/auth');

const router = express.Router();

/**
 * GET /login - Display login page
 */
router.get('/login', redirectIfAuthenticated, (req, res) => {
  const error = req.query.error;
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Login - Auth System</title>
      <style>
        body { font-family: Arial, sans-serif; max-width: 400px; margin: 100px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .error { color: red; margin-bottom: 15px; padding: 10px; border: 1px solid red; border-radius: 4px; background: #ffe6e6; }
        .title { text-align: center; color: #333; margin-bottom: 30px; }
      </style>
    </head>
    <body>
      <h1 class="title">Central Authentication System</h1>
      <h2>Login</h2>
      
      ${error ? `<div class="error">${error}</div>` : ''}
      
      <form method="POST" action="/login">
        <div class="form-group">
          <label for="username">Username:</label>
          <input type="text" id="username" name="username" required>
        </div>
        
        <div class="form-group">
          <label for="password">Password:</label>
          <input type="password" id="password" name="password" required>
        </div>
        
        <button type="submit">Login</button>
      </form>
      
      <p style="margin-top: 20px; text-align: center; color: #666;">
        Test credentials: admin/password or user1/password
      </p>
    </body>
    </html>
  `);
});

/**
 * POST /login - Handle login form submission
 */
router.post('/login', redirectIfAuthenticated, async (req, res) => {
  const { username, password } = req.body;
  
  if (!username || !password) {
    return res.redirect('/login?error=Username and password are required');
  }
  
  try {
    console.log(`[AUTH ROUTE] Login attempt for user: ${username}`);
    
    const result = await apiClient.login(username, password);
    
    console.log(`[AUTH ROUTE] Login successful for user: ${username}`);
    
    // Store user info in session
    req.session.user = result.user;
    
    res.redirect('/dashboard');
    
  } catch (error) {
    console.error(`[AUTH ROUTE] Login failed for user: ${username}`, error.message);
    res.redirect(`/login?error=${encodeURIComponent(error.message)}`);
  }
});

/**
 * POST /logout - Handle logout
 */
router.post('/logout', async (req, res) => {
  try {
    console.log('[AUTH ROUTE] Logout attempt');
    
    await apiClient.logout();
    
    // Clear session
    req.session.destroy((err) => {
      if (err) {
        console.error('[AUTH ROUTE] Session destroy error:', err);
      }
    });
    
    console.log('[AUTH ROUTE] Logout successful');
    res.redirect('/login');
    
  } catch (error) {
    console.error('[AUTH ROUTE] Logout error:', error.message);
    // Redirect to login anyway
    res.redirect('/login');
  }
});

module.exports = router; 