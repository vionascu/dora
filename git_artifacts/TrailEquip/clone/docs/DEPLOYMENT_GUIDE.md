# TrailEquip Deployment Guide

## Overview

After GitLab CI/CD pipeline completes successfully, the application is automatically containerized and made accessible from anywhere. This guide covers all deployment options.

---

## 🚀 **Option 1: Docker Compose (Easiest - Local/Self-Hosted)**

### Local Testing
```bash
# Clone the repository
git clone https://gitlab.com/vic.ionascu/trail-equip.git
cd trail-equip

# Start the entire stack (database + backend + frontend)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop the stack
docker-compose down
```

### Access the Application
- **Frontend:** http://localhost:8081 (backend serves frontend static files)
- **API:** http://localhost:8081/api/v1/trails
- **API Docs:** http://localhost:8081/swagger-ui.html
- **Health:** http://localhost:8081/actuator/health

### Database
- PostgreSQL runs in container with PostGIS
- Credentials: `trailequip` / `trailequip_dev`
- Data persists in `postgres_data` volume

---

## 🐳 **Option 2: GitLab Container Registry**

### Automatic Pipeline
After each push to `main`:

1. ✅ **Build Stage** - Backend and Frontend built
2. ✅ **Test Stage** - Unit tests and code quality checks
3. ✅ **Package Stage** - Docker image built and pushed to GitLab Container Registry
4. 🔄 **Deploy Stage** - (Manual trigger) Image pushed to registry

### Access Built Images
```bash
# Login to GitLab Container Registry
docker login registry.gitlab.com
# Username: <your-gitlab-username>
# Password: <personal-access-token>

# Pull the image
docker pull registry.gitlab.com/vic.ionascu/trail-equip:latest

# Run the container
docker run -e SPRING_DATASOURCE_URL=jdbc:postgresql://host.docker.internal:5432/trailequip \
           -e SPRING_DATASOURCE_USERNAME=trailequip \
           -e SPRING_DATASOURCE_PASSWORD=trailequip_dev \
           -p 8081:8081 \
           registry.gitlab.com/vic.ionascu/trail-equip:latest
```

**View Available Images:** https://gitlab.com/vic.ionascu/trail-equip/-/packages

---

## ☁️ **Option 3: Deploy to Cloud Platforms**

### 3a. Heroku (Free Tier Available)
```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create trail-equip

# Add PostgreSQL with PostGIS
heroku addons:create heroku-postgresql:essential-0 --app trail-equip
heroku run "psql \$DATABASE_URL -c 'CREATE EXTENSION IF NOT EXISTS postgis;'" --app trail-equip

# Deploy
git push heroku main
```

**Access:** `https://trail-equip.herokuapp.com`

---

### 3b. AWS (EC2 + RDS)
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker tag trail-equip:latest $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/trail-equip:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/trail-equip:latest

# Deploy on EC2 using docker-compose
# 1. Upload docker-compose.yml to EC2
# 2. SSH into instance and run: docker-compose up -d
```

---

### 3c. DigitalOcean (Simple & Affordable)
```bash
# 1. Create a Droplet (Ubuntu 22.04)
# 2. SSH into droplet and install Docker:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Clone and deploy
git clone https://gitlab.com/vic.ionascu/trail-equip.git
cd trail-equip
docker-compose up -d
```

**Access:** `http://<your-droplet-ip>:8081`

---

### 3d. Google Cloud Run (Serverless)
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/trail-equip

# Deploy
gcloud run deploy trail-equip \
  --image gcr.io/PROJECT_ID/trail-equip \
  --platform managed \
  --region us-central1 \
  --set-env-vars SPRING_DATASOURCE_URL=... \
  --set-env-vars SPRING_DATASOURCE_USERNAME=trailequip \
  --set-env-vars SPRING_DATASOURCE_PASSWORD=trailequip_dev
```

---

### 3e. Azure Container Instances
```bash
# Push to Azure Container Registry
az acr build --registry myregistry --image trail-equip:latest .

# Deploy
az container create \
  --resource-group myResourceGroup \
  --name trail-equip \
  --image myregistry.azurecr.io/trail-equip:latest \
  --dns-name-label trail-equip \
  --environment-variables \
    SPRING_DATASOURCE_URL="jdbc:postgresql://..." \
    SPRING_DATASOURCE_USERNAME="trailequip" \
    SPRING_DATASOURCE_PASSWORD="trailequip_dev"
```

---

## 🔄 **Option 4: Kubernetes (Advanced)**

### Deploy to Any Kubernetes Cluster
```bash
# 1. Create namespace
kubectl create namespace trail-equip

# 2. Create secrets
kubectl create secret generic db-credentials \
  --from-literal=username=trailequip \
  --from-literal=password=trailequip_dev \
  -n trail-equip

# 3. Create ConfigMap
kubectl create configmap app-config \
  --from-literal=DB_URL=postgresql://postgres:5432/trailequip \
  -n trail-equip

# 4. Deploy using provided manifests
kubectl apply -f k8s/postgres-deployment.yaml -n trail-equip
kubectl apply -f k8s/app-deployment.yaml -n trail-equip
kubectl apply -f k8s/service.yaml -n trail-equip
```

---

## 📊 **Comparison Table**

| Platform | Cost | Ease | Scalability | Persistence |
|----------|------|------|-------------|------------|
| Docker Compose | Free | ⭐⭐⭐⭐⭐ | Low | Local |
| Heroku | $7-50/mo | ⭐⭐⭐⭐⭐ | Medium | Included |
| DigitalOcean | $4-12/mo | ⭐⭐⭐⭐ | Medium | Droplet |
| AWS EC2 + RDS | $10-50/mo | ⭐⭐⭐ | High | AWS RDS |
| Google Cloud Run | $0.15/mo* | ⭐⭐⭐ | Very High | Cloud SQL |
| Azure | $5-30/mo | ⭐⭐⭐ | High | Azure DB |
| Kubernetes | $0-500/mo | ⭐⭐ | Very High | Configurable |

*Pay per request, very affordable for low traffic

---

## 🔐 **Environment Variables**

Create a `.env` file or configure in your deployment platform:

```env
# Database
SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/trailequip
SPRING_DATASOURCE_USERNAME=trailequip
SPRING_DATASOURCE_PASSWORD=trailequip_dev

# JPA/Hibernate
SPRING_JPA_HIBERNATE_DDL_AUTO=update
SPRING_JPA_DATABASE_PLATFORM=org.hibernate.spatial.dialect.postgis.PostgisPG10Dialect

# Java
JAVA_OPTS=-Xmx512m -Xms256m

# Server
SERVER_PORT=8081
SERVER_SERVLET_CONTEXT_PATH=/
```

---

## 🧪 **Verification Checklist**

After deployment, verify:

- [ ] Backend is running: `curl http://<app-url>:8081/actuator/health`
- [ ] Frontend loads: Visit `http://<app-url>:8081` in browser
- [ ] API responds: `curl http://<app-url>:8081/api/v1/trails`
- [ ] Database connected: Check logs for connection messages
- [ ] PostGIS enabled: Check database logs
- [ ] CORS configured: Can frontend reach backend API

---

## 📈 **Scaling Considerations**

### Horizontal Scaling
- Run multiple backend instances behind a load balancer
- Use managed database services (RDS, Cloud SQL, Azure DB)
- Configure sticky sessions or external session store

### Vertical Scaling
- Increase JVM heap: `-Xmx2g -Xms1g` for more memory
- Use faster CPU instances
- Optimize database indexes

### Caching
- Enable Redis for weather forecast caching
- Cache API responses at CDN level
- Implement browser caching for static assets

---

## 🚨 **Monitoring & Logging**

### Metrics
- Monitor CPU, Memory, Disk usage
- Track database connections
- Monitor API response times

### Health Checks
```bash
# Backend health
curl http://<app-url>:8081/actuator/health

# Detailed metrics
curl http://<app-url>:8081/actuator/metrics
```

### Logs
```bash
# Docker Compose
docker-compose logs -f app

# Kubernetes
kubectl logs -f deployment/trail-equip -n trail-equip

# Cloud platforms
# Check provider's logging dashboard (CloudWatch, Stackdriver, etc.)
```

---

## 🎯 **Next Steps**

1. **Choose your deployment platform** based on your needs and budget
2. **Set up environment variables** for your chosen platform
3. **Configure database** with PostGIS extension
4. **Enable monitoring** for your deployment
5. **Share the public URL** with others to access the application

---

## ✅ **Success Criteria**

After deployment, you can:
- ✅ Access the application from any browser globally
- ✅ Share the URL with team members/users
- ✅ Application runs independently of your local machine
- ✅ Database persists data across restarts
- ✅ Automatic updates on each GitLab push (if CI/CD is automated)

