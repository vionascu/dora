# Deploy TrailEquip Locally with Docker Compose

Test the complete application stack locally before deploying to cloud.

## Prerequisites

- **Docker Desktop** installed: https://www.docker.com/products/docker-desktop
- **Docker Compose** (included with Docker Desktop)
- ~2 GB disk space

## Quick Start (One Command)

```bash
cd /Users/viionascu/Projects/TrailEquip
docker-compose up -d
```

Wait ~2 minutes for services to start, then:
- **Frontend**: http://localhost:3001
- **Backend**: http://localhost:8081/api/v1/trails
- **Database**: PostgreSQL at localhost:5432

To stop:
```bash
docker-compose down
```

---

## Manual Setup (Step by Step)

### Step 1: Build Docker Image

```bash
cd /Users/viionascu/Projects/TrailEquip

# Build the image (takes 5-10 minutes first time)
docker build -t trailequip:latest .

# Verify image was created
docker images | grep trailequip
```

### Step 2: Start PostgreSQL with PostGIS

```bash
# Start database container
docker run -d \
  --name trailequip-db \
  -e POSTGRES_USER=trailequip \
  -e POSTGRES_PASSWORD=trailequip-secure \
  -e POSTGRES_DB=trailequip \
  -p 5432:5432 \
  -v trailequip-db-data:/var/lib/postgresql/data \
  postgis/postgis:15-3.3

# Wait for database to be ready (30 seconds)
sleep 30

# Verify connection
docker exec trailequip-db psql -U trailequip -d trailequip -c "SELECT postgis_version();"
```

### Step 3: Start Application

```bash
# Run the application
docker run -d \
  --name trailequip-app \
  -e SPRING_DATASOURCE_URL=jdbc:postgresql://trailequip-db:5432/trailequip \
  -e SPRING_DATASOURCE_USERNAME=trailequip \
  -e SPRING_DATASOURCE_PASSWORD=trailequip-secure \
  -e SPRING_JPA_HIBERNATE_DDL_AUTO=update \
  -p 8081:8081 \
  --link trailequip-db:trailequip-db \
  trailequip:latest

# Wait for app startup (30 seconds)
sleep 30

# Check logs
docker logs trailequip-app | tail -20
```

### Step 4: Access Application

```bash
# Test backend
curl http://localhost:8081/api/v1/trails

# Open frontend in browser
open http://localhost:3001
```

---

## Using docker-compose.yml

The `docker-compose.yml` file orchestrates everything. View it:

```bash
cat docker-compose.yml
```

### Services defined:
- `db`: PostgreSQL 15 with PostGIS 15-3.3
- `app`: Spring Boot application with frontend

### Environment variables:
```yaml
SPRING_DATASOURCE_URL: jdbc:postgresql://db:5432/trailequip
SPRING_DATASOURCE_USERNAME: trailequip
SPRING_DATASOURCE_PASSWORD: trailequip-secure
SPRING_JPA_HIBERNATE_DDL_AUTO: update
```

---

## Useful Commands

### View all containers
```bash
docker ps -a
```

### View logs
```bash
# Application logs (real-time)
docker logs -f trailequip-app

# Database logs
docker logs -f trailequip-db
```

### Stop services
```bash
# Stop all
docker-compose down

# Stop single container
docker stop trailequip-app
docker stop trailequip-db
```

### Clean up everything
```bash
# Remove containers and volumes
docker-compose down -v

# Or manually
docker rm trailequip-app trailequip-db
docker volume rm trailequip-db-data
```

### Rebuild without cache
```bash
docker build --no-cache -t trailequip:latest .
```

### Run with custom environment
```bash
docker run -d \
  --name trailequip-app \
  -e PORT=3000 \
  -e SPRING_DATASOURCE_URL=jdbc:postgresql://db:5432/custom_db \
  -p 3000:3000 \
  trailequip:latest
```

---

## Troubleshooting

### Port already in use
```bash
# Kill process on port 8081
lsof -ti:8081 | xargs kill -9

# Or use different port
docker run -p 9000:8081 trailequip:latest
# Then access at http://localhost:9000
```

### Database connection failed
```bash
# Check if database is running
docker ps | grep trailequip-db

# Check database logs
docker logs trailequip-db

# Restart database
docker restart trailequip-db
```

### Out of memory
Increase Docker's memory allocation:
- Docker Desktop → Settings → Resources → Memory: increase to 4GB+

### Container crashes immediately
```bash
# Check logs for error
docker logs trailequip-app

# Run in foreground to see output
docker run --rm \
  -e SPRING_DATASOURCE_URL=jdbc:postgresql://db:5432/trailequip \
  trailequip:latest
```

### Build fails: Gradle memory
```bash
# Rebuild with more memory
docker build --build-arg GRADLE_OPTS="-Xmx2g" -t trailequip:latest .
```

---

## Health Checks

### Backend health
```bash
curl http://localhost:8081/actuator/health
# Should return: {"status":"UP"}
```

### Database health
```bash
docker exec trailequip-db pg_isready -U trailequip
# Should return: accepting connections
```

### Frontend health
```bash
curl http://localhost:3001
# Should return HTML content
```

---

## Performance Optimization

### For faster builds:
1. Use BuildKit:
   ```bash
   DOCKER_BUILDKIT=1 docker build -t trailequip:latest .
   ```

2. Multi-stage build (already in Dockerfile):
   - Frontend built once
   - Backend compiled once
   - Runtime image smaller than build context

### For faster startup:
```bash
# Add to environment
-e SPRING_JPA_SHOW_SQL=false
-e SPRING_PROFILES_ACTIVE=prod
```

### Reduce image size:
```bash
# Current size check
docker images trailequip:latest

# Build without development dependencies
docker build --target backend-builder -t trailequip:slim .
```

---

## Next Steps

After testing locally:

1. **Push to GitLab**:
   ```bash
   git add .
   git commit -m "Verified local Docker deployment"
   git push gitlab main
   ```

2. **Deploy to cloud** (see docs/FREE_DEPLOYMENT_OPTIONS.md):
   - Choose Railway, Render, or Fly.io
   - Follow setup steps
   - Share public URL with anyone

3. **Monitor in production**:
   - Platform-specific logging
   - Set up alerts
   - Track performance

---

## Docker Compose Cheat Sheet

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild services
docker-compose up --build

# View services
docker-compose ps

# View logs
docker-compose logs -f [service-name]

# Execute command in container
docker-compose exec app sh

# Scale service (if applicable)
docker-compose up -d --scale app=3
```

---

## What's Inside the Container

### Frontend Build
- Node 20 Alpine
- React 18 + TypeScript
- Vite build tool
- Output: `/app/static` (served by Spring Boot)

### Backend Build
- Gradle 8.6
- Java 21
- Spring Boot 3.2
- JAR file: `app.jar`

### Runtime
- Eclipse Temurin JRE 21 (official Java runtime)
- PostgreSQL client tools
- Health check curl
- User: `appuser` (non-root for security)

### Startup
1. Hibernate auto-creates schema
2. PostGIS extensions enabled
3. Spring Boot starts on port 8080 (or $PORT)
4. Health endpoint: `/actuator/health`

---

## Production Considerations

When deploying to cloud platforms:

1. ✅ Use managed databases (don't run DB in container)
2. ✅ Set read-only replicas for scaling
3. ✅ Configure backups
4. ✅ Enable monitoring/logging
5. ✅ Use environment variables for secrets
6. ⚠️ Never commit secrets to repository
7. ✅ Enable HTTPS everywhere
8. ✅ Set up CI/CD for auto-deployment

All of this is handled by Railway, Render, or Fly.io - they're production-ready!

---

Need help? Check Docker documentation: https://docs.docker.com/
