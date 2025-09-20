const express = require('express')
const router = express.Router()
const botController = require('../controllers/botController')
const { authenticateApiKey, optionalAuth } = require('../middleware/auth')

// Report a bot (requires API key or token authentication)
router.post('/report', authenticateApiKey, botController.reportBot)

// Check if IP is a known bot (public endpoint with optional auth for enhanced features)
router.get('/check/:ip', optionalAuth, botController.checkBot)

// Get bot statistics (public endpoint with optional auth)
router.get('/stats', optionalAuth, botController.getBotStats)

module.exports = router