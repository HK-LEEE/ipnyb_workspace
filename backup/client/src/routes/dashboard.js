/**
 * Dashboard and protected routes
 */

const express = require('express');
const apiClient = require('../services/apiClient');
const { requireAuth } = require('../middleware/auth');

const router = express.Router();

/**
 * GET /dashboard - Main dashboard page
 */
router.get('/dashboard', requireAuth, async (req, res) => {
  try {
    const user = req.session.user || {};
    
    res.send(`
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard - Auth System</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
          .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
          .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee; }
          .user-info { display: flex; align-items: center; gap: 15px; }
          .user-avatar { width: 40px; height: 40px; background: #007bff; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; }
          .btn { padding: 8px 16px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; margin: 5px; }
          .btn:hover { background: #0056b3; }
          .btn.danger { background: #dc3545; }
          .btn.danger:hover { background: #c82333; }
          .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
          .card { background: white; padding: 20px; border-radius: 8px; border: 1px solid #ddd; }
          .card h3 { margin-top: 0; color: #333; }
          .status { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
          .status.success { background: #d4edda; color: #155724; }
          .status.warning { background: #fff3cd; color: #856404; }
          .result { margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 4px; border-left: 4px solid #007bff; }
          .error { color: red; background: #ffe6e6; border-left-color: #dc3545; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>Dashboard</h1>
            <div class="user-info">
              <div class="user-avatar">${user.username ? user.username.charAt(0).toUpperCase() : 'U'}</div>
              <div>
                <div><strong>${user.username || 'Unknown'}</strong></div>
                <div style="font-size: 12px; color: #666;">${user.group || 'No group'} - ${user.department || 'No department'}</div>
              </div>
              <form method="POST" action="/logout" style="margin: 0;">
                <button type="submit" class="btn danger">Logout</button>
              </form>
            </div>
          </div>

          <div class="grid">
            <div class="card">
              <h3>Protected Data</h3>
              <p>Access protected information from the backend API.</p>
              <button class="btn" onclick="getProtectedData()">Load Protected Data</button>
              <div id="protected-result" class="result" style="display: none;"></div>
            </div>

            <div class="card">
              <h3>User Profile</h3>
              <p>View your user profile information.</p>
              <button class="btn" onclick="getUserProfile()">Load Profile</button>
              <div id="profile-result" class="result" style="display: none;"></div>
            </div>

            <div class="card">
              <h3>Admin Only</h3>
              <p>Access admin-only content (requires admin group).</p>
              <button class="btn" onclick="getAdminData()">Load Admin Data</button>
              <div id="admin-result" class="result" style="display: none;"></div>
            </div>

            <div class="card">
              <h3>IT Department</h3>
              <p>Access IT department content (requires IT department).</p>
              <button class="btn" onclick="getItData()">Load IT Data</button>
              <div id="it-result" class="result" style="display: none;"></div>
            </div>
          </div>
        </div>

        <script>
          async function makeApiCall(endpoint, resultElementId) {
            const resultElement = document.getElementById(resultElementId);
            resultElement.style.display = 'block';
            resultElement.innerHTML = 'Loading...';
            resultElement.className = 'result';

            try {
              const response = await fetch(endpoint);
              const data = await response.json();
              
              if (response.ok) {
                resultElement.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
              } else {
                resultElement.innerHTML = 'Error: ' + (data.detail || 'Request failed');
                resultElement.className = 'result error';
              }
            } catch (error) {
              resultElement.innerHTML = 'Error: ' + error.message;
              resultElement.className = 'result error';
            }
          }

          function getProtectedData() {
            makeApiCall('/api/protected-data', 'protected-result');
          }

          function getUserProfile() {
            makeApiCall('/api/user-profile', 'profile-result');
          }

          function getAdminData() {
            makeApiCall('/api/admin-data', 'admin-result');
          }

          function getItData() {
            makeApiCall('/api/it-data', 'it-result');
          }
        </script>
      </body>
      </html>
    `);
  } catch (error) {
    console.error('[DASHBOARD] Error loading dashboard:', error.message);
    res.status(500).send('Error loading dashboard');
  }
});

module.exports = router; 