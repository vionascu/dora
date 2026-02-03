# TrailEquip – Bucegi Mountains Hiking Guide

A production-quality web application for discovering, planning, and outfitting hiking trails in the Bucegi Mountains, Romania.

## Quick Start (5 minutes)

```bash
cd ~/Projects/TrailEquip/infra
docker-compose up -d
sleep 30
curl http://localhost:8080/api/v1/health
open http://localhost:3000
```

**Expected Output:**
- Services running on ports 8080–8083, 3000, 5432
- Web UI displays 3 sample Bucegi trails
- Health check returns `"status": "UP"`

## Architecture

- **Microservices:** Trail, Weather, Recommendation services
- **Backend:** Java 21, Spring Boot 3.x, PostgreSQL + PostGIS
- **Frontend:** React 18, TypeScript, Leaflet map
- **Infrastructure:** Docker Compose, GitLab CI/CD

## Testing

```bash
./gradlew test integrationTest              # Java tests
cd ui && npm run test:ui                    # UI tests
```

## Development

```bash
./gradlew build                             # Build
cd ui && npm run dev                        # Dev server with hot reload
docker-compose restart trail-service        # Restart after code changes
```

## Deploy to Cloud (Free - No Installation Required)

**🚀 Share your app with anyone via public URL!**

### Easiest Option: Railway.app (Recommended)
**Cost:** Free tier with $5 monthly credit (effectively free)
**Setup:** 10 minutes | **Runs:** Always on (no hibernation)

```bash
1. Visit https://railway.app
2. Connect your GitLab repository
3. Add PostgreSQL service
4. Done! Public URL generated automatically
```

→ See [FREE_DEPLOYMENT_OPTIONS.md](./docs/FREE_DEPLOYMENT_OPTIONS.md) for Railway + Render + Fly.io

### Other Free Options
- **Render.com**: Free tier with 15-min hibernation (perfect for testing)
- **Fly.io**: Generous free tier, very fast performance
- **Google Cloud Run**: Free tier with $300 credit
- **GitHub Pages**: Free frontend-only deployment

→ Full guide: [docs/FREE_DEPLOYMENT_OPTIONS.md](./docs/FREE_DEPLOYMENT_OPTIONS.md)

## Documentation

**📚 ALL DOCUMENTATION IN `/docs` FOLDER**

- [📖 Documentation Index](./docs/README.md)
- [🚀 Startup Guide](./docs/STARTUP.md)
- [⚙️ Configuration](./docs/CONFIGURATION.md)
- [🏗️ Architecture](./docs/ARCHITECTURE.md)
- [📡 API Reference](./docs/API_REFERENCE.md)
- [🧪 Testing Strategy](./docs/TESTING_STRATEGY.md)
- [☁️ Free Cloud Deployment](./docs/FREE_DEPLOYMENT_OPTIONS.md) ⭐ NEW
- [🐳 Local Docker Deployment](./docs/LOCAL_DOCKER_DEPLOYMENT.md) ⭐ NEW
- [⚡ Google Cloud Run Deployment](./docs/CLOUD_RUN_DEPLOYMENT.md) ⭐ NEW

## Key Features (v1)

✅ Interactive map with Bucegi trails
✅ Trail discovery and filtering by difficulty
✅ Weather forecast integration
✅ Equipment recommendations based on conditions
✅ REST APIs with Swagger documentation
✅ Unit + integration tests
✅ Docker-based local development
✅ GitLab CI/CD pipelines

## Next Steps

### Option A: Run Locally (5 min)
```bash
cd ~/Projects/TrailEquip
docker-compose up -d          # Start all services
sleep 30                       # Wait for startup
open http://localhost:3001    # Open web UI
```

### Option B: Deploy to Cloud (10 min) - Most Popular!
```bash
# Push to GitLab (auto-triggers CI/CD)
git push gitlab main

# Then deploy to Railway:
1. Visit https://railway.app
2. Connect your GitLab repo
3. Add PostgreSQL
4. Share public URL with anyone!

See: docs/FREE_DEPLOYMENT_OPTIONS.md
```

### Then:
1. View API docs: http://localhost:8081/swagger-ui.html
2. Explore trails and generate recommendations
3. Share the public URL (if deployed to cloud)

## License

MIT

---

**Version:** 0.1.0 | **Status:** MVP Ready
