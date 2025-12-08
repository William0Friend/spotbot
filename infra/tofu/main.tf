# SpotBot Infrastructure - OpenTofu Configuration
# Provisions cloud infrastructure for SpotBot deployment

terraform {
  required_version = ">= 1.6"
  
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
  
  # Backend for state management (uncomment and configure)
  # backend "s3" {
  #   bucket = "spotbot-terraform-state"
  #   key    = "prod/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

# Variables
variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "dev"
}

variable "region" {
  description = "Cloud provider region"
  type        = string
  default     = "nyc3"
}

variable "droplet_size" {
  description = "Droplet size for application servers"
  type        = string
  default     = "s-2vcpu-4gb"
}

variable "db_size" {
  description = "Database cluster size"
  type        = string
  default     = "db-s-1vcpu-1gb"
}

variable "domain" {
  description = "Domain name for the application"
  type        = string
  default     = "spotbot.example.com"
}

# Provider configuration
provider "digitalocean" {
  # Set DIGITALOCEAN_TOKEN environment variable
}

# Data sources
data "digitalocean_ssh_key" "terraform" {
  name = "terraform-key"
}

# VPC for network isolation
resource "digitalocean_vpc" "spotbot" {
  name     = "spotbot-${var.environment}-vpc"
  region   = var.region
  ip_range = "10.10.0.0/16"
  
  description = "VPC for SpotBot ${var.environment} environment"
}

# Application droplet
resource "digitalocean_droplet" "app" {
  count  = var.environment == "production" ? 2 : 1
  image  = "ubuntu-22-04-x64"
  name   = "spotbot-app-${var.environment}-${count.index + 1}"
  region = var.region
  size   = var.droplet_size
  vpc_uuid = digitalocean_vpc.spotbot.id
  
  ssh_keys = [data.digitalocean_ssh_key.terraform.id]
  
  tags = [
    "environment:${var.environment}",
    "service:spotbot",
    "role:application"
  ]
  
  user_data = file("${path.module}/cloud-init/app-server.yml")
}

# Managed PostgreSQL database
resource "digitalocean_database_cluster" "postgres" {
  name       = "spotbot-${var.environment}-db"
  engine     = "pg"
  version    = "15"
  size       = var.db_size
  region     = var.region
  node_count = 1
  
  tags = [
    "environment:${var.environment}",
    "service:spotbot"
  ]
}

# Database
resource "digitalocean_database_db" "spotbot" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "spotbot_${var.environment}"
}

# Database user
resource "digitalocean_database_user" "spotbot" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "spotbot_user"
}

# Redis cluster (for caching and rate limiting)
resource "digitalocean_database_cluster" "redis" {
  name       = "spotbot-${var.environment}-redis"
  engine     = "redis"
  version    = "7"
  size       = "db-s-1vcpu-1gb"
  region     = var.region
  node_count = 1
  
  tags = [
    "environment:${var.environment}",
    "service:spotbot"
  ]
}

# Load balancer for production
resource "digitalocean_loadbalancer" "app" {
  count  = var.environment == "production" ? 1 : 0
  name   = "spotbot-${var.environment}-lb"
  region = var.region
  vpc_uuid = digitalocean_vpc.spotbot.id
  
  forwarding_rule {
    entry_port     = 443
    entry_protocol = "https"
    
    target_port     = 80
    target_protocol = "http"
    
    certificate_name = digitalocean_certificate.app[0].name
  }
  
  forwarding_rule {
    entry_port     = 80
    entry_protocol = "http"
    
    target_port     = 80
    target_protocol = "http"
  }
  
  healthcheck {
    port     = 8000
    protocol = "http"
    path     = "/health"
  }
  
  droplet_ids = digitalocean_droplet.app[*].id
}

# SSL Certificate (Let's Encrypt)
resource "digitalocean_certificate" "app" {
  count  = var.environment == "production" ? 1 : 0
  name   = "spotbot-${var.environment}-cert"
  type   = "lets_encrypt"
  domains = [var.domain, "www.${var.domain}", "api.${var.domain}"]
}

# Firewall rules
resource "digitalocean_firewall" "app" {
  name = "spotbot-${var.environment}-firewall"
  
  droplet_ids = digitalocean_droplet.app[*].id
  
  # Inbound rules
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]  # Restrict in production!
  }
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "8000"
    source_addresses = [digitalocean_vpc.spotbot.ip_range]
  }
  
  # Outbound rules (allow all)
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# Outputs
output "app_server_ips" {
  value       = digitalocean_droplet.app[*].ipv4_address
  description = "Public IP addresses of application servers"
}

output "database_uri" {
  value       = digitalocean_database_cluster.postgres.uri
  sensitive   = true
  description = "PostgreSQL connection URI"
}

output "redis_uri" {
  value       = digitalocean_database_cluster.redis.uri
  sensitive   = true
  description = "Redis connection URI"
}

output "loadbalancer_ip" {
  value       = try(digitalocean_loadbalancer.app[0].ip, "N/A")
  description = "Load balancer IP address"
}
