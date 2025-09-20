# SpotBot - Bot Detection Platform

A comprehensive bot detection and reporting platform similar to AbuseIPDB, designed specifically for identifying and tracking malicious bot activity across websites. SpotBot provides a community-driven database for bot intelligence sharing with powerful APIs and a user-friendly interface.

## 🚀 Features

- **Bot Reporting**: Report suspicious IP addresses and bot behavior
- **Real-time Detection**: Check if an IP address is a known bot
- **Community Database**: Shared intelligence across all participating websites
- **Pattern Recognition**: Advanced bot behavior analysis and pattern detection
- **API Access**: RESTful API for easy integration
- **Web Interface**: Clean, responsive web dashboard
- **Network Analysis**: Track bot networks and coordinated attacks
- **Geo-location Tracking**: Country-based bot activity analysis
- **Confidence Scoring**: Intelligent scoring system based on multiple reports

## 🏗️ Architecture

- **Backend**: Node.js with Express.js
- **Database**: PostgreSQL for data storage
- **Cache**: Redis (optional, for performance)
- **Frontend**: HTML5 with Tailwind CSS
- **Authentication**: JWT tokens and API keys
- **Validation**: Comprehensive input validation and sanitization

## 📋 Prerequisites

- Node.js 16.0+
- PostgreSQL 12+
- Redis (optional, for caching)
- NPM or Yarn

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/William0Friend/spotbot.git
   cd spotbot
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb spotbot
   
   # Run the schema
   psql -d spotbot -f src/database/schema.sql
   ```

5. **Start the server**
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:3000`

## 🔧 Configuration

Key environment variables in `.env`:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=spotbot
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# Server
PORT=3000
JWT_SECRET=your_jwt_secret_key

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 📖 API Documentation

### Authentication

Most API endpoints require authentication via API key:

```bash
curl -H "X-API-Key: your_api_key" https://api.spotbot.com/v1/bots/check/1.2.3.4
```

### Core Endpoints

#### Check IP Address
```http
GET /api/v1/bots/check/{ip}
```
Returns bot detection information for an IP address.

#### Report Bot Activity
```http
POST /api/v1/bots/report
Content-Type: application/json
X-API-Key: your_api_key

{
  "ipAddress": "1.2.3.4",
  "botType": "scraper",
  "userAgent": "BadBot/1.0",
  "confidenceScore": 85,
  "evidenceData": {
    "requestFrequency": 100,
    "suspiciousHeaders": true
  }
}
```

#### Get Platform Statistics
```http
GET /api/v1/bots/stats?period=24h
```

#### User Registration
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "username": "myusername",
  "organization": "My Company"
}
```

## 🎯 Use Cases

### Website Protection
```javascript
// Check if incoming request is from a bot
const response = await fetch(`https://your-spotbot.com/api/v1/bots/check/${userIP}`, {
  headers: { 'X-API-Key': 'your_api_key' }
});
const data = await response.json();

if (data.isBot && data.confidence > 70) {
  // Block or limit the request
  return res.status(429).json({ error: 'Bot traffic detected' });
}
```

### Bot Activity Reporting
```javascript
// Report suspicious activity
await fetch('https://your-spotbot.com/api/v1/bots/report', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your_api_key'
  },
  body: JSON.stringify({
    ipAddress: suspiciousIP,
    botType: 'scraper',
    confidenceScore: 90,
    evidenceData: {
      requestFrequency: 500,
      uniqueUserAgents: 1,
      httpErrors: 0.1
    }
  })
});
```

## 🛡️ Security Features

- Rate limiting on all API endpoints
- Input validation and sanitization
- SQL injection protection
- JWT token authentication
- API key authentication
- CORS protection
- Helmet.js security headers

## 📊 Bot Types Supported

- **Scraper**: Web scraping bots
- **Spam**: Comment and form spam bots  
- **Malicious**: Generally malicious bot activity
- **Scanner**: Security/vulnerability scanners
- **DDoS**: Distributed denial of service bots
- **Credential Stuffing**: Login attempt bots
- **Fake Account**: Account creation bots

## 🚀 Development

```bash
# Development with auto-reload
npm run dev

# Run tests
npm test

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix
```

## 🤝 Contributing

We welcome contributions! The SpotBot platform thrives on community participation.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the API documentation at `/api`
- **Issues**: Report bugs on GitHub Issues
- **Community**: Join our community discussions

## 🎯 Roadmap

- [ ] Machine learning-based bot detection
- [ ] Real-time dashboard with WebSocket updates
- [ ] Advanced analytics and reporting
- [ ] Integration with popular web frameworks
- [ ] Mobile app for on-the-go monitoring
- [ ] Automated threat intelligence feeds
- [ ] Enterprise features and SSO integration

---

**SpotBot** - Protecting websites from malicious bots through community intelligence. 🛡️