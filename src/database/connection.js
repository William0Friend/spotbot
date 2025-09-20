const { Pool } = require('pg')
const redis = require('redis')
require('dotenv').config()

// PostgreSQL connection
const pgPool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'spotbot',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || '',
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
})

// Redis connection (optional - the app will work without Redis)
let redisClient = null
try {
  redisClient = redis.createClient({
    url: `redis://${process.env.REDIS_HOST || 'localhost'}:${process.env.REDIS_PORT || 6379}`,
    password: process.env.REDIS_PASSWORD || undefined
  })

  redisClient.on('error', (err) => {
    console.log('Redis connection error (optional service):', err.message)
    redisClient = null
  })

  redisClient.on('connect', () => {
    console.log('Connected to Redis')
  })

  // Try to connect
  redisClient.connect().catch(err => {
    console.log('Redis not available, continuing without cache')
    redisClient = null
  })
} catch (err) {
  console.log('Redis not configured, continuing without cache')
}

// Test database connection
pgPool.connect((err, client, release) => {
  if (err) {
    console.error('Error connecting to PostgreSQL database:', err.stack)
    return
  }
  console.log('Connected to PostgreSQL database')
  release()
})

module.exports = {
  db: pgPool,
  redis: redisClient
}