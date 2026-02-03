# TrailEquip - Getting Started Guide

## Prerequisites

Ensure you have the following installed:

- **Java 21** - Required for Spring Boot 3.2.0
- **PostgreSQL 14** - Database
- **Node.js 20+** - For React UI
- **npm** - Node package manager
- **Gradle** - Build system (wrapper included)
- **Git** - Version control

## Initial Setup

### 1. Clone Repository

```bash
git clone https://gitlab.com/your-account/trail-equip.git
cd TrailEquip
```

### 2. Setup PostgreSQL Database

#### Create Database User
```bash
psql -d template1 -c "CREATE ROLE trailequip WITH LOGIN PASSWORD 'trailequip_dev' CREATEDB;"
```

#### Create Database
```bash
createdb -O trailequip trailequip
```

#### Load Schema (Without PostGIS)
```bash
psql trailequip < infra/db/init-no-postgis.sql
```

If you have PostGIS installed:
```bash
psql trailequip < infra/db/init.sql
```

#### Verify Setup
```bash
psql trailequip -U trailequip -c "SELECT COUNT(*) FROM trails;"
```

Should return: 3 (the seed trails)

### 3. Configure Java Path

Update your shell configuration (`~/.zshrc` or `~/.bash_profile`):

```bash
export PATH="/opt/homebrew/opt/openjdk@21/bin:$PATH"
export JAVA_HOME="/opt/homebrew/opt/openjdk@21"
```

Reload shell:
```bash
source ~/.zshrc
```

Verify Java:
```bash
java -version
```

### 4. Install Node Dependencies

```bash
cd ui
npm install
cd ..
```

---

## Running the Application

### Option 1: Single Terminal (Recommended)

```bash
./run-all.sh
```

This script:
- Starts all 5 microservices
- Starts React UI
- Displays service URLs
- Shows log file locations

Output:
```
════════════════════════════════════════════════════════════
       TrailEquip - Starting All Services
════════════════════════════════════════════════════════════

✓ Prerequisites OK
✓ All ports available

Starting Trail Service (8081)...
✓ Trail Service started (PID: 12345)
...
✓ All services started!

📍 Services Available:
  UI:                    http://localhost:3000
  API Gateway:           http://localhost:8080
  API Docs (Swagger):    http://localhost:8080/swagger-ui.html
  Health Check:          http://localhost:8080/api/v1/health
```

### Option 2: Individual Terminal Windows

Terminal 1 - Trail Service:
```bash
export JAVA_HOME="/opt/homebrew/opt/openjdk@21"
./gradlew :trail-service:bootRun
```

Terminal 2 - Weather Service:
```bash
export JAVA_HOME="/opt/homebrew/opt/openjdk@21"
./gradlew :weather-service:bootRun
```

Terminal 3 - Recommendation Service:
```bash
export JAVA_HOME="/opt/homebrew/opt/openjdk@21"
./gradlew :recommendation-service:bootRun
```

Terminal 4 - API Gateway:
```bash
export JAVA_HOME="/opt/homebrew/opt/openjdk@21"
./gradlew :api-gateway:bootRun
```

Terminal 5 - React UI:
```bash
cd ui && npm run dev
```

---

## Accessing the Application

### User Interface
Open browser: http://localhost:3000

Features:
- Browse available trails
- Filter by difficulty, distance, terrain
- View weather forecasts
- Get equipment recommendations

### API Gateway
Base URL: http://localhost:8080

Health Check:
```bash
curl http://localhost:8080/api/v1/health
```

API Documentation:
http://localhost:8080/swagger-ui.html

### Individual Services

| Service | URL | Health Endpoint |
|---------|-----|-----------------|
| Trail Service | http://localhost:8081 | /actuator/health |
| Weather Service | http://localhost:8082 | /actuator/health |
| Recommendation Service | http://localhost:8083 | /actuator/health |

---

## Testing the APIs

### Get All Trails
```bash
curl http://localhost:8080/api/v1/trails | jq
```

### Filter by Difficulty
```bash
curl "http://localhost:8080/api/v1/trails?difficulty=EASY" | jq
```

### Create New Trail
```bash
curl -X POST http://localhost:8080/api/v1/trails \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Trail",
    "description": "A new hiking trail",
    "distance": 8.5,
    "elevationGain": 400,
    "elevationLoss": 400,
    "durationMinutes": 180,
    "maxSlope": 25.0,
    "avgSlope": 10.0,
    "terrain": ["forest", "mountain"],
    "difficulty": "MEDIUM",
    "hazards": ["exposure"],
    "source": "user-submitted"
  }' | jq
```

### Get Weather Forecast
```bash
curl "http://localhost:8080/api/v1/weather/forecast?latitude=45.5&longitude=25.3" | jq
```

### Get Equipment Recommendations
```bash
curl -X POST http://localhost:8080/api/v1/recommendations/equipment \
  -H "Content-Type: application/json" \
  -d '{
    "trailDifficulty": "MEDIUM",
    "temperature": 15,
    "rainProbability": 30,
    "windSpeed": 20
  }' | jq
```

---

## Running Tests

### All Tests
```bash
gradle clean test
```

### Specific Service Tests
```bash
gradle :trail-service:test
gradle :weather-service:test
gradle :recommendation-service:test
```

### Generate Coverage Report
```bash
gradle test jacocoTestReport
```

Report location: `build/reports/jacoco/test/html/index.html`

---

## Monitoring Services

### View Logs

Individual service logs:
```bash
tail -f .logs/trail-service.log
tail -f .logs/weather-service.log
tail -f .logs/recommendation-service.log
tail -f .logs/api-gateway.log
tail -f .logs/ui.log
```

### Check Service Health
```bash
curl http://localhost:8081/actuator/health  # Trail Service
curl http://localhost:8082/actuator/health  # Weather Service
curl http://localhost:8083/actuator/health  # Recommendation Service
curl http://localhost:8080/actuator/health  # API Gateway
```

---

## Troubleshooting

### Issue: Port already in use

**Error:** `Address already in use`

**Solution:** Find and kill process using port
```bash
lsof -i :8080  # Check port
kill -9 <PID>  # Kill process
```

### Issue: PostgreSQL connection refused

**Error:** `FATAL: role "trailequip" does not exist`

**Solution:** Create user and database (see Setup section)
```bash
psql -d template1 -c "CREATE ROLE trailequip WITH LOGIN PASSWORD 'trailequip_dev' CREATEDB;"
createdb -O trailequip trailequip
```

### Issue: Java not found

**Error:** `java: command not found`

**Solution:** Set JAVA_HOME
```bash
export JAVA_HOME="/opt/homebrew/opt/openjdk@21"
export PATH="$JAVA_HOME/bin:$PATH"
```

### Issue: npm modules not installed

**Error:** `Cannot find module '@vitejs/plugin-react'`

**Solution:** Install dependencies
```bash
cd ui && npm install && cd ..
```

### Issue: API Gateway can't reach services

**Error:** `Connection refused` to trail-service:8081

**Solution:** Ensure all services are running. Check `run-all.sh` log output.

### Issue: React UI won't build

**Error:** `TypeScript compilation error`

**Solution:**
```bash
cd ui
npm install
npm run build
npm run dev
```

---

## Building for Production

### Build Docker Images

```bash
# Individual services
docker build -t trail-equip/trail-service services/trail-service
docker build -t trail-equip/weather-service services/weather-service
docker build -t trail-equip/recommendation-service services/recommendation-service
docker build -t trail-equip/api-gateway services/api-gateway
docker build -t trail-equip/ui ui
```

### Run with Docker Compose

```bash
docker-compose -f infra/docker-compose.yml up
```

### Deploy to Kubernetes

```bash
kubectl apply -f infra/k8s/
```

---

## Development Workflow

1. **Start services** (terminal 1)
   ```bash
   ./run-all.sh
   ```

2. **Code changes** - Make changes in your IDE

3. **Auto-reload** - Services restart automatically on code changes (via Spring DevTools)

4. **Test** - Run tests in another terminal
   ```bash
   gradle test
   ```

5. **Verify** - Test API endpoints with curl or Swagger UI

6. **Commit** - When ready, commit changes
   ```bash
   git add .
   git commit -m "Feature: Add new trail filters"
   ```

7. **Push** - Push to GitLab
   ```bash
   git push origin main
   ```

---

## IDE Setup

### IntelliJ IDEA

1. **Open Project**
   - File → Open
   - Select TrailEquip directory

2. **Configure SDK**
   - File → Project Structure
   - SDK: openjdk-21

3. **Enable Gradle**
   - View → Tool Windows → Gradle
   - Should auto-detect build files

4. **Run Configurations**
   - Add new Run Configuration for each service
   - Use Gradle tasks: `:service-name:bootRun`

### VSCode

1. **Install Extensions**
   - Extension Pack for Java
   - Spring Boot Extension Pack
   - Gradle for Java

2. **Open Workspace**
   - Open folder: TrailEquip

3. **Debug Configuration**
   - Create `.vscode/launch.json` for debugging

---

## Next Steps

1. ✅ Setup database
2. ✅ Install dependencies
3. ✅ Run all services
4. ✅ Access UI at http://localhost:3000
5. ⬜ Test APIs with provided examples
6. ⬜ Review code and architecture
7. ⬜ Make code changes
8. ⬜ Run tests
9. ⬜ Commit and push changes

---

## Support

- **Architecture:** See [ARCHITECTURE.md](./ARCHITECTURE.md)
- **API Documentation:** http://localhost:8080/swagger-ui.html
- **Tests:** See [CRUD_TESTS.md](./CRUD_TESTS.md)
- **Database:** See [Database Schema](../infra/db/init-no-postgis.sql)

---

**Last Updated:** January 29, 2026
**Version:** 1.0
