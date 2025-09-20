const express = require('express')
const router = express.Router()

// Placeholder for reports routes - will contain detailed report management
router.get('/', (req, res) => {
  res.json({ 
    message: 'Reports endpoint - coming soon',
    availableEndpoints: [
      'GET /api/v1/reports - List all reports',
      'GET /api/v1/reports/:id - Get specific report',
      'PUT /api/v1/reports/:id - Update report status',
      'DELETE /api/v1/reports/:id - Delete report'
    ]
  })
})

module.exports = router