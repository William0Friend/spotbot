# Architecture Decision Records

## SpotBot System Architecture

### Technology Stack

#### Backend: FastAPI
**Why FastAPI over Django/Flask?**
- **Performance**: FastAPI is built on ASDF (Starlette + Pydantic), making it one of the fastest Python frameworks
- **Modern Python**: Native async/await support, type hints throughout
- **Automatic API Docs**: Built-in Swagger UI and ReDoc
- **Less Boilerplate**: Compared to Django, FastAPI requires less code for APIs
- **Growing Ecosystem**: Excellent for microservices and API-first applications

**When to use Django instead:**
- Need full-featured admin panel
- Building traditional web application with server-side rendering
- Need Django ORM's advanced features
- Large monolithic application

**When to use Flask instead:**
- Extremely simple APIs
- Need maximum flexibility/minimalism
- Legacy codebase compatibility

#### Architecture: Hybrid Monolith + Microservice

**Decision**: Monolithic backend + Separate AI Detector service

**Rationale:**
1. **Start Simple**: Monolith is easier to develop, deploy, and debug initially
2. **Selective Microservices**: Only split what needs it:
   - AI Detector is separate because:
     - Heavy computational requirements
     - Different resource scaling needs
     - Can upgrade ML models independently
     - May need GPU access
3. **Future-Ready**: Architecture allows adding services as needed

**Microservices to add later (Phase 2+):**
- Bot Tracking Service
- Crowdsource Reporting Service
- Analytics Service
- Notification Service

#### Database: PostgreSQL
- **JSONB support** for flexible detection result storage
- **UUID support** for distributed systems
- **Strong ACID guarantees**
- **Excellent performance** for analytical queries

#### Cache: Redis
- **Session management**
- **Rate limiting** (future)
- **Real-time features** (future)
- **Job queue** (future with Celery)

#### Frontend: React + Vite
- **Fast development** with hot reload
- **Modern tooling** with Vite
- **Component-based** architecture
- **Easy to extend** to mobile (React Native)

### Scalability Plan

#### Phase 1 (Current): Single Server
```
┌─────────────┐
│   Docker    │
│  Compose    │
├─────────────┤
│  Frontend   │
│   Backend   │
│ AI Detector │
│  Postgres   │
│   Redis     │
└─────────────┘
```

#### Phase 2: Horizontal Scaling
```
┌─────────────┐
│Load Balancer│
└──────┬──────┘
       │
   ┌───┴───┬───────┬────────┐
   │       │       │        │
┌──▼──┐ ┌──▼──┐ ┌──▼──┐  ┌──▼──────┐
│Front│ │Back │ │Back │  │AI Detect│
│ end │ │ end │ │ end │  │ Service │
└─────┘ └──┬──┘ └──┬──┘  └────┬────┘
          │       │           │
        ┌─▼───────▼───┬───────▼─┐
        │  Postgres   │  Redis  │
        └─────────────┴─────────┘
```

#### Phase 3: Full Microservices
```
┌─────────────┐
│   API GW    │
└──────┬──────┘
       │
   ┌───┴───┬───────┬────────┬─────────┐
   │       │       │        │         │
┌──▼──┐ ┌──▼──┐ ┌──▼──┐  ┌──▼──┐  ┌──▼──┐
│Auth │ │Detect│ │ Bot │  │Report│  │ AI  │
│ Svc │ │ Svc  │ │Track│  │ Svc  │  │Svc  │
└──┬──┘ └──┬───┘ └──┬──┘  └──┬───┘  └──┬──┘
   │       │        │        │         │
   └───┬───┴────┬───┴────┬───┴─────────┘
       │        │        │
    ┌──▼────┐┌──▼───┐┌───▼───┐
    │ DB 1  ││ DB 2 ││ Cache │
    └───────┘└──────┘└───────┘
```

### Data Flow

#### Detection Request Flow
```
User → Frontend → Backend API → AI Detector Service
                      ↓                 ↓
                   Postgres ←───── Results
                      ↓
                  Response → Frontend → User
```

#### Bot Reporting Flow (Phase 2)
```
User → Report Bot → Backend → Bot Tracking Service
                                      ↓
                              Pattern Analysis
                                      ↓
                         Network Identification
                                      ↓
                        Broadcast to All Clients
```

### Security Considerations

1. **Authentication**: JWT tokens
2. **Rate Limiting**: Redis-based (Phase 2)
3. **Input Validation**: Pydantic schemas
4. **SQL Injection**: SQLAlchemy ORM
5. **XSS**: React auto-escaping
6. **CORS**: Configured properly

### Deployment Strategy

#### Development: Docker Compose
- Easy onboarding
- Consistent environments
- All services in one command

#### Production: Kubernetes + Terraform/OpenTofu
- **Why not Ansible?**
  - Ansible is better for configuration management
  - Terraform/OpenTofu better for infrastructure provisioning
  - We'll use both: Terraform for infra, Ansible for config

```
Terraform/OpenTofu → Provision cloud resources
        ↓
    Kubernetes → Container orchestration
        ↓
     Helm Charts → Application deployment
        ↓
     Ansible → Configuration management
```

### Monitoring & Observability (Phase 2+)

```
┌─────────────┐
│ Prometheus  │ ← Metrics collection
└──────┬──────┘
       │
┌──────▼──────┐
│  Grafana    │ ← Visualization
└─────────────┘

┌─────────────┐
│    ELK      │ ← Log aggregation
│  Stack      │
└─────────────┘
```

### Cost Optimization

1. **Start Small**: Single DigitalOcean/Hetzner VPS ($20/month)
2. **Scale Smart**: Add services only when needed
3. **Cache Aggressively**: Redis for repeated queries
4. **Optimize ML Models**: Use quantized models, batch processing
5. **CDN**: CloudFlare for static assets

### Future Enhancements

#### Phase 2: Crowdsourcing
- User reports database
- Confidence aggregation
- Bot network graphing
- Real-time alerts

#### Phase 3: Enterprise SaaS
- Multi-tenancy
- Organization management
- Advanced analytics
- Custom integrations
- SDK/Client libraries

#### Phase 4: Platform
- API marketplace
- Third-party detectors
- Plugin system
- White-label solution
