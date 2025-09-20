const bcrypt = require('bcryptjs')
const jwt = require('jsonwebtoken')
const { v4: uuidv4 } = require('uuid')
const { db } = require('../database/connection')
const { validateEmail, validatePassword } = require('../utils/validation')

class AuthController {
  // User registration
  async register(req, res) {
    try {
      const { email, password, username, organization } = req.body

      // Validate input
      if (!validateEmail(email)) {
        return res.status(400).json({ error: 'Invalid email format' })
      }

      if (!validatePassword(password)) {
        return res.status(400).json({ 
          error: 'Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character' 
        })
      }

      if (!username || username.length < 3) {
        return res.status(400).json({ error: 'Username must be at least 3 characters long' })
      }

      // Check if user already exists
      const existingUser = await db.query(
        'SELECT id FROM users WHERE email = $1 OR username = $2',
        [email, username]
      )

      if (existingUser.rows.length > 0) {
        return res.status(409).json({ error: 'User with this email or username already exists' })
      }

      // Hash password
      const saltRounds = 12
      const passwordHash = await bcrypt.hash(password, saltRounds)

      // Generate API key
      const apiKey = `sb_${uuidv4().replace(/-/g, '')}`

      // Insert new user
      const result = await db.query(
        `INSERT INTO users (email, password_hash, username, organization, api_key) 
         VALUES ($1, $2, $3, $4, $5) 
         RETURNING id, email, username, organization, api_key, created_at`,
        [email, passwordHash, username, organization || null, apiKey]
      )

      const user = result.rows[0]

      // Generate JWT token
      const token = jwt.sign(
        { userId: user.id, email: user.email },
        process.env.JWT_SECRET,
        { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
      )

      res.status(201).json({
        message: 'User registered successfully',
        user: {
          id: user.id,
          email: user.email,
          username: user.username,
          organization: user.organization,
          apiKey: user.api_key,
          createdAt: user.created_at
        },
        token
      })

    } catch (error) {
      console.error('Registration error:', error)
      res.status(500).json({ error: 'Internal server error' })
    }
  }

  // User login
  async login(req, res) {
    try {
      const { email, password } = req.body

      if (!email || !password) {
        return res.status(400).json({ error: 'Email and password are required' })
      }

      // Find user by email
      const result = await db.query(
        'SELECT id, email, password_hash, username, organization, api_key, is_active FROM users WHERE email = $1',
        [email]
      )

      if (result.rows.length === 0) {
        return res.status(401).json({ error: 'Invalid email or password' })
      }

      const user = result.rows[0]

      if (!user.is_active) {
        return res.status(401).json({ error: 'Account is deactivated' })
      }

      // Verify password
      const isValidPassword = await bcrypt.compare(password, user.password_hash)

      if (!isValidPassword) {
        return res.status(401).json({ error: 'Invalid email or password' })
      }

      // Generate JWT token
      const token = jwt.sign(
        { userId: user.id, email: user.email },
        process.env.JWT_SECRET,
        { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
      )

      res.json({
        message: 'Login successful',
        user: {
          id: user.id,
          email: user.email,
          username: user.username,
          organization: user.organization,
          apiKey: user.api_key
        },
        token
      })

    } catch (error) {
      console.error('Login error:', error)
      res.status(500).json({ error: 'Internal server error' })
    }
  }

  // Get current user profile
  async getProfile(req, res) {
    try {
      const result = await db.query(
        'SELECT id, email, username, organization, api_key, is_verified, role, created_at FROM users WHERE id = $1',
        [req.user.id]
      )

      if (result.rows.length === 0) {
        return res.status(404).json({ error: 'User not found' })
      }

      res.json({ user: result.rows[0] })

    } catch (error) {
      console.error('Get profile error:', error)
      res.status(500).json({ error: 'Internal server error' })
    }
  }

  // Update user profile
  async updateProfile(req, res) {
    try {
      const { username, organization } = req.body
      const userId = req.user.id

      const updateFields = []
      const updateValues = []
      let paramCount = 1

      if (username && username.length >= 3) {
        updateFields.push(`username = $${paramCount}`)
        updateValues.push(username)
        paramCount++
      }

      if (organization !== undefined) {
        updateFields.push(`organization = $${paramCount}`)
        updateValues.push(organization)
        paramCount++
      }

      if (updateFields.length === 0) {
        return res.status(400).json({ error: 'No valid fields to update' })
      }

      updateFields.push(`updated_at = CURRENT_TIMESTAMP`)
      updateValues.push(userId)

      const query = `
        UPDATE users 
        SET ${updateFields.join(', ')} 
        WHERE id = $${paramCount} 
        RETURNING id, email, username, organization, updated_at
      `

      const result = await db.query(query, updateValues)

      res.json({
        message: 'Profile updated successfully',
        user: result.rows[0]
      })

    } catch (error) {
      console.error('Update profile error:', error)
      if (error.code === '23505') { // Unique constraint violation
        return res.status(409).json({ error: 'Username already exists' })
      }
      res.status(500).json({ error: 'Internal server error' })
    }
  }

  // Generate new API key
  async regenerateApiKey(req, res) {
    try {
      const newApiKey = `sb_${uuidv4().replace(/-/g, '')}`

      const result = await db.query(
        'UPDATE users SET api_key = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2 RETURNING api_key',
        [newApiKey, req.user.id]
      )

      res.json({
        message: 'API key regenerated successfully',
        apiKey: result.rows[0].api_key
      })

    } catch (error) {
      console.error('Regenerate API key error:', error)
      res.status(500).json({ error: 'Internal server error' })
    }
  }
}

module.exports = new AuthController()