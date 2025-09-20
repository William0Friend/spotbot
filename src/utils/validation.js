// Email validation
const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// Password validation - at least 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
const validatePassword = (password) => {
  if (!password || password.length < 8) return false
  
  const hasUppercase = /[A-Z]/.test(password)
  const hasLowercase = /[a-z]/.test(password)
  const hasNumber = /\d/.test(password)
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password)
  
  return hasUppercase && hasLowercase && hasNumber && hasSpecialChar
}

// IP address validation
const validateIP = (ip) => {
  const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
  const ipv6Regex = /^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$/
  
  return ipv4Regex.test(ip) || ipv6Regex.test(ip)
}

// Bot type validation
const validateBotType = (botType) => {
  const validBotTypes = [
    'scraper', 'crawler', 'spam', 'malicious', 'scanner', 
    'ddos', 'comment_spam', 'form_spam', 'brute_force', 
    'credential_stuffing', 'fake_account', 'other'
  ]
  
  return validBotTypes.includes(botType)
}

// Confidence score validation
const validateConfidenceScore = (score) => {
  return Number.isInteger(score) && score >= 0 && score <= 100
}

// URL validation
const validateURL = (url) => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

// HTTP method validation
const validateHttpMethod = (method) => {
  const validMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
  return validMethods.includes(method.toUpperCase())
}

// Sanitize user input
const sanitizeString = (str, maxLength = 1000) => {
  if (typeof str !== 'string') return ''
  return str.trim().slice(0, maxLength)
}

// Validate evidence data structure
const validateEvidenceData = (evidence) => {
  if (!evidence || typeof evidence !== 'object') return false
  
  // Allow reasonable evidence fields
  const allowedFields = [
    'requestFrequency', 'uniqueUserAgents', 'requestPattern', 
    'responseTime', 'httpErrors', 'suspiciousHeaders', 
    'geoLocation', 'timeOfDay', 'referrer', 'sessionInfo'
  ]
  
  const evidenceKeys = Object.keys(evidence)
  return evidenceKeys.every(key => allowedFields.includes(key))
}

module.exports = {
  validateEmail,
  validatePassword,
  validateIP,
  validateBotType,
  validateConfidenceScore,
  validateURL,
  validateHttpMethod,
  sanitizeString,
  validateEvidenceData
}