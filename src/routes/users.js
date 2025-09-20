const express = require('express')
const router = express.Router()

// Placeholder for user management routes
router.get('/', (req, res) => {
  res.json({ 
    message: 'Users endpoint - coming soon',
    availableEndpoints: [
      'GET /api/v1/users - List users (admin)',
      'GET /api/v1/users/:id - Get user details',
      'PUT /api/v1/users/:id - Update user',
      'DELETE /api/v1/users/:id - Delete user'
    ]
  })
})

module.exports = router