const express = require('express')
const router = express.Router()
const authController = require('../controllers/authController')
const { authenticateToken } = require('../middleware/auth')

// Public routes
router.post('/register', authController.register)
router.post('/login', authController.login)

// Protected routes (require authentication)
router.get('/profile', authenticateToken, authController.getProfile)
router.put('/profile', authenticateToken, authController.updateProfile)
router.post('/regenerate-api-key', authenticateToken, authController.regenerateApiKey)

module.exports = router