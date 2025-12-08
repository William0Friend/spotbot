# SpotBot Infrastructure

This directory contains Infrastructure as Code (IaC) for deploying SpotBot.

## Tools Used

- **OpenTofu**: Open-source Terraform alternative for infrastructure provisioning
- **Ansible**: Configuration management and application deployment

## Structure

```
infra/
├── tofu/                    # OpenTofu configuration files
│   ├── environments/        # Environment-specific configs
│   │   ├── dev/
│   │   ├── staging/
│   │   └── production/
│   ├── modules/             # Reusable Tofu modules
│   │   ├── compute/         # VM/container instances
│   │   ├── database/        # PostgreSQL setup
│   │   ├── networking/      # VPC, subnets, security groups
│   │   └── storage/         # Object storage for media
│   └── main.tf              # Root configuration
├── ansible/                 # Ansible playbooks
│   ├── inventories/         # Host inventories per environment
│   ├── playbooks/           # Main playbooks
│   │   ├── setup.yml        # Initial server setup
│   │   ├── deploy.yml       # Application deployment
│   │   └── update.yml       # Rolling updates
│   ├── roles/               # Ansible roles
│   │   ├── common/          # Base system config
│   │   ├── docker/          # Docker installation
│   │   ├── spotbot/         # SpotBot application
│   │   └── monitoring/      # Prometheus, Grafana
│   └── group_vars/          # Variables per environment
└── scripts/                 # Helper deployment scripts
    ├── deploy.sh
    └── rollback.sh
```

## Supported Platforms

- **DigitalOcean**: Droplets + Managed PostgreSQL
- **AWS**: EC2 + RDS
- **Hetzner Cloud**: Cost-effective alternative
- **Azure**: VMs + Azure Database for PostgreSQL
- **On-premise**: Any server with Ubuntu 22.04+

## Quick Start

### 1. Initialize Infrastructure

```bash
cd infra/tofu
tofu init
tofu plan -var-file=environments/dev/terraform.tfvars
tofu apply -var-file=environments/dev/terraform.tfvars
```

### 2. Configure Servers

```bash
cd infra/ansible
ansible-playbook -i inventories/dev playbooks/setup.yml
```

### 3. Deploy Application

```bash
ansible-playbook -i inventories/dev playbooks/deploy.yml
```

## CI/CD Integration

See `.github/workflows/` for GitHub Actions pipelines that:
- Run on push to `main` branch
- Execute Tofu plan
- Deploy with Ansible
- Run smoke tests

## Environment Variables

Required secrets (set in CI/CD or `.env`):
- `DB_PASSWORD`
- `JWT_SECRET`
- `REDIS_PASSWORD`
- `OPENAI_API_KEY` (if using GPT-based detection)
