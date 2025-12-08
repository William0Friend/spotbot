# SpotBot Deployment Guide

## Local Development

### Prerequisites
- Docker & Docker Compose
- Git

### Quick Start
```bash
# Clone repository
git clone https://github.com/William0Friend/spotbot.git
cd spotbot

# Deploy locally
./deploy-local.sh

# Access application
open http://localhost:3000
```

### Manual Setup
```bash
# Create .env file
cp .env.example .env
nano .env  # Edit passwords and secrets

# Start services
docker-compose up --build -d

# View logs
docker-compose logs -f
```

## Cloud Deployment (Production)

### Step 1: Provision Infrastructure with OpenTofu

```bash
cd infra/tofu

# Initialize Tofu
tofu init

# Set your DigitalOcean token
export DIGITALOCEAN_TOKEN="your_token_here"

# Plan infrastructure
tofu plan -var-file=environments/production/terraform.tfvars

# Apply (create resources)
tofu apply -var-file=environments/production/terraform.tfvars

# Note the outputs (server IPs, database URIs, etc.)
tofu output
```

### Step 2: Configure Ansible Inventory

```bash
cd ../ansible

# Edit inventory with server IPs from Tofu output
nano inventories/production/hosts.ini

# Update with:
# - Server IP addresses
# - Database connection strings
# - Redis URIs
# - Secret keys (generate random ones!)
```

### Step 3: Deploy Application with Ansible

```bash
# Test connection
ansible -i inventories/production all -m ping

# Run initial server setup
ansible-playbook -i inventories/production playbooks/setup.yml

# Deploy application
ansible-playbook -i inventories/production playbooks/deploy.yml
```

### Step 4: Configure DNS

Point your domain to the load balancer IP (from Tofu output):

```
A     spotbot.com          -> <load_balancer_ip>
A     www.spotbot.com      -> <load_balancer_ip>
A     api.spotbot.com      -> <load_balancer_ip>
```

### Step 5: SSL Certificates

DigitalOcean will automatically provision Let's Encrypt certificates for your domain.

## Deployment Options

### Option 1: DigitalOcean (Recommended)
- **Cost**: ~$40/month (2 droplets + managed DB + Redis)
- **Pros**: Managed services, easy setup, good support
- **Cons**: Slightly more expensive than bare metal

### Option 2: AWS
- **Cost**: ~$50-100/month (EC2 + RDS + ElastiCache)
- **Pros**: Most features, global infrastructure
- **Cons**: Complex pricing, steeper learning curve

### Option 3: Hetzner Cloud
- **Cost**: ~$20/month (VPS + separate DB instance)
- **Pros**: Very affordable, EU-based
- **Cons**: Manual database setup, fewer managed services

### Option 4: On-Premise / VPS
- **Cost**: Variable (your own hardware)
- **Pros**: Full control, no cloud vendor lock-in
- **Cons**: Manual everything, no managed services

## CI/CD Pipeline (Future)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: ./run-e2e-tests.sh
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy with Ansible
        env:
          ANSIBLE_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
        run: |
          cd infra/ansible
          ansible-playbook -i inventories/production playbooks/deploy.yml
```

## Monitoring & Maintenance

### Health Checks
```bash
# Check backend
curl https://api.spotbot.com/health

# Check frontend
curl https://spotbot.com

# View application logs
ssh user@server "cd /opt/spotbot && docker-compose logs"
```

### Database Backups

DigitalOcean Managed Database automatically creates daily backups. To create manual backup:

```bash
# From DigitalOcean console or CLI
doctl databases backup create <database-id>
```

### Updates

```bash
# Deploy new version
cd infra/ansible
ansible-playbook -i inventories/production playbooks/update.yml

# Rollback if needed
ansible-playbook -i inventories/production playbooks/rollback.yml
```

## Scaling

### Horizontal Scaling
```bash
# Edit Tofu config to increase droplet count
nano infra/tofu/environments/production/terraform.tfvars
# Change: droplet_count = 3

# Apply changes
cd infra/tofu
tofu apply -var-file=environments/production/terraform.tfvars

# Ansible will automatically configure load balancer
```

### Vertical Scaling
```bash
# Upgrade droplet size
# Change: droplet_size = "s-4vcpu-8gb"

# Apply
tofu apply
```

## Cost Estimates

### Development
- **Local**: Free (runs on your machine)

### Production (DigitalOcean)
| Service | Size | Cost/Month |
|---------|------|------------|
| App Droplets (2x) | 2 vCPU, 4GB RAM | $24 |
| PostgreSQL | 1 vCPU, 1GB RAM | $15 |
| Redis | 1 vCPU, 1GB RAM | $15 |
| Load Balancer | - | $12 |
| Backups | - | $3 |
| **Total** | | **~$70/month** |

### Production (Hetzner - Budget)
| Service | Size | Cost/Month |
|---------|------|------------|
| VPS (2x) | 2 vCPU, 4GB RAM | $10 |
| Separate DB instance | 2 vCPU, 4GB RAM | $5 |
| Redis (on app server) | - | $0 |
| **Total** | | **~$15/month** |

## Security Checklist

- [ ] Change all default passwords in `.env`
- [ ] Generate random SECRET_KEY and JWT_SECRET
- [ ] Restrict firewall to specific IPs for SSH (not 0.0.0.0/0)
- [ ] Enable 2FA for cloud provider account
- [ ] Set up log monitoring (Sentry, Datadog, etc.)
- [ ] Configure automated backups
- [ ] Enable SSL/TLS (Let's Encrypt)
- [ ] Set up rate limiting (already in code)
- [ ] Regular security updates (`apt update && apt upgrade`)

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

### Database connection errors
- Check DATABASE_URL in .env
- Verify PostgreSQL is running: `docker-compose ps postgres`
- Check database logs: `docker-compose logs postgres`

### Frontend can't connect to backend
- Check CORS_ORIGINS in backend .env
- Verify VITE_API_URL in frontend .env
- Check network connectivity

## Support

- **Documentation**: See `/docs` directory
- **Issues**: GitHub Issues
- **Community**: Discord / Slack (TBD)
