const { db } = require('../database/connection')
const geoip = require('geoip-lite')
const { 
  validateIP, 
  validateBotType, 
  validateConfidenceScore,
  validateURL,
  validateHttpMethod,
  sanitizeString,
  validateEvidenceData 
} = require('../utils/validation')

class BotController {
  // Report a bot
  async reportBot(req, res) {
    try {
      const {
        ipAddress,
        userAgent,
        requestUrl,
        requestMethod = 'GET',
        requestHeaders = {},
        botType,
        confidenceScore,
        evidenceData = {}
      } = req.body

      // Validate required fields
      if (!ipAddress || !validateIP(ipAddress)) {
        return res.status(400).json({ error: 'Valid IP address is required' })
      }

      if (botType && !validateBotType(botType)) {
        return res.status(400).json({ error: 'Invalid bot type' })
      }

      if (confidenceScore !== undefined && !validateConfidenceScore(confidenceScore)) {
        return res.status(400).json({ error: 'Confidence score must be between 0 and 100' })
      }

      if (requestUrl && !validateURL(requestUrl)) {
        return res.status(400).json({ error: 'Invalid request URL format' })
      }

      if (!validateHttpMethod(requestMethod)) {
        return res.status(400).json({ error: 'Invalid HTTP method' })
      }

      if (!validateEvidenceData(evidenceData)) {
        return res.status(400).json({ error: 'Invalid evidence data structure' })
      }

      // Get geolocation data
      const geoData = geoip.lookup(ipAddress)
      const countryCode = geoData ? geoData.country : null

      // Insert bot report
      const result = await db.query(
        `INSERT INTO bot_reports 
         (reporter_id, ip_address, user_agent, request_url, request_method, 
          request_headers, bot_type, confidence_score, evidence_data, country_code)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
         RETURNING id, ip_address, bot_type, confidence_score, reported_at`,
        [
          req.user ? req.user.id : null,
          ipAddress,
          sanitizeString(userAgent, 500),
          sanitizeString(requestUrl, 1000),
          requestMethod.toUpperCase(),
          JSON.stringify(requestHeaders),
          botType || 'other',
          confidenceScore || 50,
          JSON.stringify(evidenceData),
          countryCode
        ]
      )

      // Log bot activity
      await this.logBotActivity(ipAddress, userAgent, evidenceData)

      res.status(201).json({
        message: 'Bot reported successfully',
        report: result.rows[0]
      })

    } catch (error) {
      console.error('Report bot error:', error)
      res.status(500).json({ error: 'Internal server error' })
    }
  }

  // Check if IP is a known bot
  async checkBot(req, res) {
    try {
      const { ip } = req.params

      if (!validateIP(ip)) {
        return res.status(400).json({ error: 'Invalid IP address format' })
      }

      // Check if IP is whitelisted
      const whitelistCheck = await db.query(
        `SELECT id, organization, description FROM bot_whitelist 
         WHERE is_active = true AND (ip_address = $1 OR $1 << ip_range)`,
        [ip]
      )

      if (whitelistCheck.rows.length > 0) {
        return res.json({
          ip,
          isBot: false,
          isWhitelisted: true,
          whitelistInfo: whitelistCheck.rows[0],
          confidence: 0,
          reports: []
        })
      }

      // Get bot reports for this IP
      const reports = await db.query(
        `SELECT id, bot_type, confidence_score, reported_at, status, 
                request_method, user_agent, country_code
         FROM bot_reports 
         WHERE ip_address = $1 
         ORDER BY reported_at DESC 
         LIMIT 50`,
        [ip]
      )

      // Calculate overall confidence score
      const validReports = reports.rows.filter(r => r.status !== 'rejected')
      let overallConfidence = 0
      
      if (validReports.length > 0) {
        const avgConfidence = validReports.reduce((sum, r) => sum + r.confidence_score, 0) / validReports.length
        const reportBonus = Math.min(validReports.length * 2, 20) // Bonus for multiple reports
        overallConfidence = Math.min(avgConfidence + reportBonus, 100)
      }

      // Get recent activity
      const activityData = await db.query(
        `SELECT request_count, behavior_score, detected_at 
         FROM bot_activity_logs 
         WHERE ip_address = $1 AND detected_at > NOW() - INTERVAL '24 hours'
         ORDER BY detected_at DESC LIMIT 10`,
        [ip]
      )

      res.json({
        ip,
        isBot: overallConfidence > 30,
        confidence: Math.round(overallConfidence),
        reportCount: validReports.length,
        lastSeen: reports.rows.length > 0 ? reports.rows[0].reported_at : null,
        commonBotTypes: this.getCommonBotTypes(validReports),
        recentActivity: activityData.rows,
        isWhitelisted: false
      })

    } catch (error) {
      console.error('Check bot error:', error)
      res.status(500).json({ error: 'Internal server error' })
    }
  }

  // Get bot statistics
  async getBotStats(req, res) {
    try {
      const { period = '24h' } = req.query

      let timeInterval
      switch (period) {
        case '1h': timeInterval = '1 hour'; break
        case '24h': timeInterval = '24 hours'; break
        case '7d': timeInterval = '7 days'; break
        case '30d': timeInterval = '30 days'; break
        default: timeInterval = '24 hours'
      }

      const stats = await db.query(
        `SELECT 
           COUNT(*) as total_reports,
           COUNT(DISTINCT ip_address) as unique_ips,
           COUNT(DISTINCT bot_type) as bot_types,
           AVG(confidence_score) as avg_confidence,
           bot_type,
           COUNT(*) as type_count
         FROM bot_reports 
         WHERE reported_at > NOW() - INTERVAL '${timeInterval}'
         GROUP BY bot_type
         ORDER BY type_count DESC`,
        []
      )

      const countryStats = await db.query(
        `SELECT country_code, COUNT(*) as report_count
         FROM bot_reports 
         WHERE reported_at > NOW() - INTERVAL '${timeInterval}' 
           AND country_code IS NOT NULL
         GROUP BY country_code 
         ORDER BY report_count DESC 
         LIMIT 10`,
        []
      )

      res.json({
        period,
        totalReports: parseInt(stats.rows.reduce((sum, r) => sum + parseInt(r.type_count), 0)),
        uniqueIPs: stats.rows.length > 0 ? parseInt(stats.rows[0].unique_ips) : 0,
        averageConfidence: stats.rows.length > 0 ? Math.round(parseFloat(stats.rows[0].avg_confidence)) : 0,
        botTypeDistribution: stats.rows.map(r => ({
          type: r.bot_type,
          count: parseInt(r.type_count)
        })),
        topCountries: countryStats.rows.map(r => ({
          country: r.country_code,
          count: parseInt(r.report_count)
        }))
      })

    } catch (error) {
      console.error('Get bot stats error:', error)
      res.status(500).json({ error: 'Internal server error' })
    }
  }

  // Helper method to log bot activity
  async logBotActivity(ipAddress, userAgent, evidenceData) {
    try {
      const requestCount = evidenceData.requestFrequency || 1
      const behaviorScore = this.calculateBehaviorScore(evidenceData)

      await db.query(
        `INSERT INTO bot_activity_logs (ip_address, user_agent, request_count, behavior_score, activity_data)
         VALUES ($1, $2, $3, $4, $5)
         ON CONFLICT (ip_address) DO UPDATE SET
           request_count = bot_activity_logs.request_count + $3,
           behavior_score = GREATEST(bot_activity_logs.behavior_score, $4),
           activity_data = $5,
           detected_at = CURRENT_TIMESTAMP`,
        [ipAddress, userAgent, requestCount, behaviorScore, JSON.stringify(evidenceData)]
      )
    } catch (error) {
      console.error('Log bot activity error:', error)
    }
  }

  // Helper method to calculate behavior score
  calculateBehaviorScore(evidenceData) {
    let score = 0

    if (evidenceData.requestFrequency > 10) score += 20
    if (evidenceData.uniqueUserAgents > 5) score += 15
    if (evidenceData.httpErrors > 0.3) score += 25
    if (evidenceData.suspiciousHeaders) score += 10
    if (evidenceData.requestPattern === 'sequential') score += 15

    return Math.min(score, 100)
  }

  // Helper method to get common bot types from reports
  getCommonBotTypes(reports) {
    const typeCounts = {}
    reports.forEach(report => {
      typeCounts[report.bot_type] = (typeCounts[report.bot_type] || 0) + 1
    })

    return Object.entries(typeCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([type, count]) => ({ type, count }))
  }
}

module.exports = new BotController()