# SpotBot Deployment on Hostinger VPS

## Overview

This guide walks through deploying SpotBot on a Hostinger VPS. Hostinger offers affordable VPS hosting starting at ~$4/month, making it perfect for initial deployment before scaling to DigitalOcean.

## Prerequisites

- Hostinger VPS account (KVM 1 or higher recommended)
- Domain name (can use Hostinger's domain services)
- SSH access to your VPS
- Local machine with Git and SSH client

## Hostinger VPS Specs Recommendation

| Plan | vCPU | RAM | Storage | Monthly Cost | Best For |
|------|------|-----|---------|--------------|----------|
| KVM 1 | 1 | 2GB | 20GB SSD | ~$4 | Testing only |
| KVM 2 | 2 | 4GB | 40GB SSD | ~$8 | Development |
| **KVM 4** | **4** | **8GB** | **80GB SSD** | **~$15** | **Production** |

## Step-by-Step Deployment

### 1. Initial Server Setup

```bash
# SSH into your Hostinger VPS
ssh root@your-vps-ip

# Update system packages
apt update && apt upgrade -y

# Install essential tools
apt install -y curl wget git ufw fail2ban

# Create non-root user for security
adduser spotbot
usermod -aG sudo spotbot

# Setup SSH key authentication (recommended)
mkdir -p /home/spotbot/.ssh
cp /root/.ssh/authorized_keys /home/spotbot/.ssh/
chown -R spotbot:spotbot /home/spotbot/.ssh
chmod 700 /home/spotbot/.ssh
chmod 600 /home/spotbot/.ssh/authorized_keys

# Configure firewall
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable

# Exit and reconnect as spotbot user
exit
ssh spotbot@your-vps-ip
```

### 2. Install Docker & Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add current user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version

# Log out and back in for group changes to take effect
exit
ssh spotbot@your-vps-ip
```

### 3. Clone SpotBot Repository

```bash
# Clone the repository
cd ~
git clone https://github.com/William0Friend/spotbot.git
cd spotbot

# Or if using private repository
git clone git@github.com:William0Friend/spotbot.git
```

### 4. Configure Environment Variables

```bash
# Create production .env file
cat > .env << 'EOF'
# === Database Configuration ===
POSTGRES_USER=spotbot_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_DB=spotbot_db

# === Redis Configuration ===
REDIS_PASSWORD=$(openssl rand -base64 32)

# === Backend Configuration ===
SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database connection (internal Docker network)
DATABASE_URL=postgresql://spotbot_user:${POSTGRES_PASSWORD}@postgres:5432/spotbot_db

# Redis connection (internal Docker network)
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# CORS origins (replace with your domain)
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com,http://your-vps-ip:3000

# === Frontend Configuration ===
# Use your domain or VPS IP
VITE_API_URL=https://your-domain.com/api
# Or for testing: VITE_API_URL=http://your-vps-ip:8000

# === Optional: AI API Keys (for future ML features) ===
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here

# === Optional: Monitoring ===
# SENTRY_DSN=your_sentry_dsn
EOF

# Generate secure random passwords
POSTGRES_PASS=$(openssl rand -base64 32)
REDIS_PASS=$(openssl rand -base64 32)
SECRET=$(openssl rand -base64 32)
JWT=$(openssl rand -base64 32)

# Update .env with generated passwords
sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$POSTGRES_PASS|" .env
sed -i "s|REDIS_PASSWORD=.*|REDIS_PASSWORD=$REDIS_PASS|" .env
sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET|" .env
sed -i "s|JWT_SECRET=.*|JWT_SECRET=$JWT|" .env

# Update DATABASE_URL with generated password
sed -i "s|spotbot_user:.*@postgres|spotbot_user:$POSTGRES_PASS@postgres|" .env

# Update REDIS_URL with generated password
sed -i "s|redis://:\(.*\)@redis|redis://:$REDIS_PASS@redis|" .env

# Secure the .env file
chmod 600 .env

echo "✅ Environment configured with secure random passwords"
```

### 5. Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up --build -d

# Wait for services to start (about 30 seconds)
sleep 30

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 6. Verify Deployment

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend (if running on port 3000)
curl http://localhost:3000

# Test API detection endpoint
curl -X POST http://localhost:8000/api/v1/detect/ \
  -H "Content-Type: application/json" \
  -d '{"content_type": "text", "content_text": "Certainly! It'\''s worth noting that this is a test."}'
```

### 7. Setup Nginx Reverse Proxy (Recommended)

```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/spotbot << 'EOF'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
    }

    # API docs
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/spotbot /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 8. Setup SSL with Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Certbot will automatically configure Nginx for HTTPS
# Certificates auto-renew, but you can test renewal with:
sudo certbot renew --dry-run
```

### 9. Setup Systemd Service (Auto-start on boot)

```bash
# Create systemd service file
sudo tee /etc/systemd/system/spotbot.service << 'EOF'
[Unit]
Description=SpotBot Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
User=spotbot
Group=spotbot
WorkingDirectory=/home/spotbot/spotbot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable spotbot

# Start service
sudo systemctl start spotbot

# Check status
sudo systemctl status spotbot
```

### 10. Database Backup Setup

```bash
# Create backup script
cat > ~/backup-spotbot.sh << 'EOF'
#!/bin/bash

# Configuration
BACKUP_DIR="/home/spotbot/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="spotbot_db_${TIMESTAMP}.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Run pg_dump inside the postgres container
docker-compose exec -T postgres pg_dump -U spotbot_user spotbot_db > $BACKUP_DIR/$BACKUP_FILE

# Compress the backup
gzip $BACKUP_DIR/$BACKUP_FILE

# Delete backups older than 7 days
find $BACKUP_DIR -name "spotbot_db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
EOF

chmod +x ~/backup-spotbot.sh

# Setup daily backup cron job
(crontab -l 2>/dev/null; echo "0 2 * * * /home/spotbot/backup-spotbot.sh") | crontab -

# Test backup
~/backup-spotbot.sh
```

## Monitoring & Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f ai-detector

# Last 100 lines
docker-compose logs --tail=100
```

### Check Resource Usage

```bash
# Docker stats
docker stats

# System resources
htop
# or
top
```

### Update Application

```bash
cd ~/spotbot

# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose up --build -d

# Check logs
docker-compose logs -f
```

### Troubleshooting

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend

# Full rebuild (if dependencies changed)
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Clear Docker cache (if disk space low)
docker system prune -a
```

## Performance Optimization for Hostinger

### 1. Enable Swap (if RAM < 8GB)

```bash
# Create 2GB swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Optimize swap usage
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

### 2. Docker Resource Limits

Edit `docker-compose.yml` to add resource limits:

```yaml
services:
  backend:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          memory: 512M
```

### 3. Enable Docker Logging Rotation

```bash
# Create Docker daemon config
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# Restart Docker
sudo systemctl restart docker
```

## Security Hardening

### 1. Setup Fail2Ban

```bash
# Create Nginx jail
sudo tee /etc/fail2ban/jail.d/nginx.conf << 'EOF'
[nginx-http-auth]
enabled = true

[nginx-botsearch]
enabled = true

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
EOF

# Restart fail2ban
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban
```

### 2. Disable Root Login

```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Set:
# PermitRootLogin no
# PasswordAuthentication no

# Restart SSH
sudo systemctl restart sshd
```

### 3. Setup Automatic Security Updates

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Cost Optimization

| Service | Hostinger VPS | DigitalOcean Equivalent |
|---------|---------------|-------------------------|
| VPS (4 vCPU, 8GB) | $15/month | $48/month (Droplet) |
| PostgreSQL | $0 (self-hosted) | $15/month (Managed) |
| Redis | $0 (self-hosted) | $15/month (Managed) |
| **Total** | **$15/month** | **$78/month** |

**Savings**: $63/month (~80% cheaper) while learning and growing!

**When to migrate to DigitalOcean:**
- Traffic exceeds 10,000 requests/day
- Need managed databases (automatic backups, scaling)
- Want multiple regions/CDN
- Team needs production-grade infrastructure

## Migration to DigitalOcean Later

When ready to scale:

1. **Export data from Hostinger:**
   ```bash
   ~/backup-spotbot.sh
   ```

2. **Use the OpenTofu config we created:**
   ```bash
   cd infra/tofu
   tofu apply
   ```

3. **Deploy with Ansible:**
   ```bash
   cd infra/ansible
   ansible-playbook playbooks/deploy.yml
   ```

4. **Import database:**
   ```bash
   gunzip -c backup.sql.gz | psql postgresql://user:pass@do-db-host:25060/spotbot_db
   ```

## Support & Resources

- **Hostinger Support**: https://www.hostinger.com/tutorials/vps
- **Docker Docs**: https://docs.docker.com/
- **SpotBot Docs**: See DEPLOYMENT.md and DEBUGGING.md

---

**Note**: This is a production-ready setup for Hostinger VPS. All passwords are randomly generated, services auto-start on boot, and backups run daily. You're ready to go! 🚀
