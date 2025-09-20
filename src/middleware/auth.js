const jwt = require('jsonwebtoken')
const { db } = require('../database/connection')

// Authentication middleware
const authenticateToken = async (req, res, next) => {
  const authHeader = req.headers['authorization']
  const token = authHeader && authHeader.split(' ')[1]

  if (!token) {
    return res.status(401).json({ error: 'Access token required' })
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET)
    
    // Get user from database to ensure they still exist and are active
    const result = await db.query(
      'SELECT id, email, username, role, is_active FROM users WHERE id = $1',
      [decoded.userId]
    )

    if (result.rows.length === 0 || !result.rows[0].is_active) {
      return res.status(401).json({ error: 'Invalid or inactive user' })
    }

    req.user = result.rows[0]
    next()
  } catch (error) {
    return res.status(403).json({ error: 'Invalid or expired token' })
  }
}

// API Key authentication middleware
const authenticateApiKey = async (req, res, next) => {
  const apiKey = req.headers['x-api-key']

  if (!apiKey) {
    return res.status(401).json({ error: 'API key required' })
  }

  try {
    const result = await db.query(
      'SELECT id, email, username, role, is_active FROM users WHERE api_key = $1',
      [apiKey]
    )

    if (result.rows.length === 0 || !result.rows[0].is_active) {
      return res.status(401).json({ error: 'Invalid or inactive API key' })
    }

    req.user = result.rows[0]
    next()
  } catch (error) {
    console.error('API key authentication error:', error)
    return res.status(500).json({ error: 'Authentication error' })
  }
}

// Authorization middleware
const requireRole = (roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' })
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' })
    }

    next()
  }
}

// Optional authentication - allows both authenticated and unauthenticated requests
const optionalAuth = async (req, res, next) => {
  const authHeader = req.headers['authorization']
  const apiKey = req.headers['x-api-key']
  
  if (authHeader) {
    const token = authHeader.split(' ')[1]
    if (token) {
      try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET)
        const result = await db.query(
          'SELECT id, email, username, role, is_active FROM users WHERE id = $1',
          [decoded.userId]
        )
        
        if (result.rows.length > 0 && result.rows[0].is_active) {
          req.user = result.rows[0]
        }
      } catch (error) {
        // Ignore token errors for optional auth
      }
    }
  } else if (apiKey) {
    try {
      const result = await db.query(
        'SELECT id, email, username, role, is_active FROM users WHERE api_key = $1',
        [apiKey]
      )
      
      if (result.rows.length > 0 && result.rows[0].is_active) {
        req.user = result.rows[0]
      }
    } catch (error) {
      // Ignore API key errors for optional auth
    }
  }
  
  next()
}

module.exports = {
  authenticateToken,
  authenticateApiKey,
  requireRole,
  optionalAuth
}