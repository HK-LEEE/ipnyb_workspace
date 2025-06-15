/**
 * API proxy routes - forwards requests to backend API
 */

const express = require('express');
const apiClient = require('../services/apiClient');
const { requireAuth } = require('../middleware/auth');

const router = express.Router();

/**
 * GET /api/protected-data - Proxy to backend protected data
 */
router.get('/api/protected-data', requireAuth, async (req, res) => {
  try {
    console.log('[API PROXY] Fetching protected data');
    const data = await apiClient.getProtectedData();
    res.json(data);
  } catch (error) {
    console.error('[API PROXY] Protected data error:', error.message);
    res.status(error.response?.status || 500).json({
      detail: error.message,
      error_code: 'PROXY_ERROR'
    });
  }
});

/**
 * GET /api/user-profile - Proxy to backend user profile
 */
router.get('/api/user-profile', requireAuth, async (req, res) => {
  try {
    console.log('[API PROXY] Fetching user profile');
    const data = await apiClient.getUserProfile();
    res.json(data);
  } catch (error) {
    console.error('[API PROXY] User profile error:', error.message);
    res.status(error.response?.status || 500).json({
      detail: error.message,
      error_code: 'PROXY_ERROR'
    });
  }
});

/**
 * GET /api/admin-data - Proxy to backend admin data
 */
router.get('/api/admin-data', requireAuth, async (req, res) => {
  try {
    console.log('[API PROXY] Fetching admin data');
    const data = await apiClient.getAdminData();
    res.json(data);
  } catch (error) {
    console.error('[API PROXY] Admin data error:', error.message);
    res.status(error.response?.status || 500).json({
      detail: error.message,
      error_code: 'PROXY_ERROR'
    });
  }
});

/**
 * GET /api/it-data - Proxy to backend IT department data
 */
router.get('/api/it-data', requireAuth, async (req, res) => {
  try {
    console.log('[API PROXY] Fetching IT department data');
    // This is just a placeholder - you can implement the actual method in apiClient
    const response = await apiClient.apiClient.get('/api/it-department');
    res.json(response.data);
  } catch (error) {
    console.error('[API PROXY] IT data error:', error.message);
    res.status(error.response?.status || 500).json({
      detail: error.message,
      error_code: 'PROXY_ERROR'
    });
  }
});

/**
 * POST /api/secure-action - Proxy to backend secure action
 */
router.post('/api/secure-action', requireAuth, async (req, res) => {
  try {
    console.log('[API PROXY] Performing secure action');
    const response = await apiClient.apiClient.post('/api/secure-action', req.body);
    res.json(response.data);
  } catch (error) {
    console.error('[API PROXY] Secure action error:', error.message);
    res.status(error.response?.status || 500).json({
      detail: error.message,
      error_code: 'PROXY_ERROR'
    });
  }
});

module.exports = router; 