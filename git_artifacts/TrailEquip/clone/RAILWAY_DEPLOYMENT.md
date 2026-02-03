# TrailEquip Deployment on Railway

## ✅ Why Railway?

| Feature | Render | Railway | GitHub |
|---------|--------|---------|--------|
| Free Tier Minutes | 500/month | ∞ | ∞ |
| Pipeline Charges | $5/1000 min | No | No |
| Free Credit | None | $5/month | N/A |
| Auto-Deploy | Webhook | Native | Webhook |
| Cost (Hobby) | Paid after free | $0-2/month | Free |
| **Verdict** | ❌ Charges | ✅ Best | ✅ CI only |

---

## 🚀 Quick Start (5 minutes)

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Authorize Railway to access your repositories

### Step 2: Create Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Search for: `vionascu/TrailEquip`
4. Click to import

### Step 3: Configure Environment
Railway automatically:
- ✅ Creates PostgreSQL database
- ✅ Sets DATABASE_URL environment variable
- ✅ Builds Docker image from Dockerfile
- ✅ Sets PORT to 10000
- ✅ Configures entrypoint.sh

### Step 4: Deploy
1. Click "Deploy"
2. Wait 3-5 minutes
3. Application is live! 🎉

---

## 🔧 How It Works

### Build Process
```
GitHub Push
    ↓
Railway detects webhook
    ↓
Railway pulls Dockerfile
    ↓
Railway builds Docker image
    ↓
Railway starts container
    ↓
entrypoint.sh converts DATABASE_URL
    ↓
Java starts with correct config
    ↓
Application connects to PostgreSQL
    ↓
Health check returns UP ✅
```

### Key Configuration
- **Dockerfile**: Multi-stage build (Node 20 → Gradle 8.6 → JRE 21)
- **entrypoint.sh**: Converts Render/Railway DATABASE_URL to JDBC format
- **railway.json**: Tells Railway how to build and deploy
- **application-render.yml**: Spring Boot config for Railway environment

---

## ✅ Verify Deployment

### Health Check
```bash
curl https://trail-equip-production.up.railway.app/actuator/health

# Expected response:
{
  "status": "UP",
  "components": {
    "db": { "status": "UP" },
    ...
  }
}
```

### API Endpoint
```bash
curl https://trail-equip-production.up.railway.app/api/v1/trails

# Returns trail data
```

---

## 📊 Cost Breakdown

### GitHub Actions (CI/CD)
- Build: Free (unlimited minutes)
- Tests: Free (unlimited)
- Total: **$0/month**

### Railway (Deployment)
- Free credit: $5/month
- Typical hobby usage: $2-4/month
- Database: Included in free tier
- Total: **$0-2/month** (covered by free credit)

### Monthly Cost: ~$0 (within free tier)

---

## 🔄 Update Process

Every time you push to GitHub:
1. GitHub Actions builds and tests ✅
2. Tests pass (unlimited CI/CD minutes)
3. Railway webhook triggered (free)
4. Railway builds new Docker image
5. Railway deploys new version
6. Application live in ~3-5 minutes

**Zero manual steps. Zero charges.**

---

## 🐛 If Deployment Fails

Check Railway logs:
1. Go to Railway dashboard
2. Select TrailEquip project
3. View deployment logs
4. Common issues:
   - DATABASE_URL not set → Railway should auto-create
   - Port conflicts → Railway manages this
   - Java heap → Railway has sufficient memory

---

## 💰 Estimated Monthly Costs

| Component | Estimate | Free Tier |
|-----------|----------|-----------|
| PostgreSQL | $3-5 | ✅ Included |
| Java app | $2-3 | ✅ Included |
| Bandwidth | <$1 | ✅ Included |
| **Total** | **$5-9** | **$5 credit ✅** |

**Result: Usually $0/month (stays within free credit)**

---

## 📋 Troubleshooting

### Application not starting
- Check Railway logs for Java errors
- Verify DATABASE_URL is set
- Verify PORT is set to 10000

### Database connection fails
- Railway auto-creates PostgreSQL
- Verify DATABASE_URL format in logs
- Check if entrypoint.sh is converting correctly

### Slow deployments
- First deploy: 3-5 minutes (normal)
- Subsequent deploys: 1-2 minutes
- Cold start: Railway free tier may have slight delay

---

## 🎯 Summary

**Render → Railway Migration:**
- ✅ Render disconnected from GitHub Actions
- ✅ GitHub Actions remains unlimited and free
- ✅ Railway configuration added (railway.json)
- ✅ Application already compatible
- ✅ One-click deployment ready

**Next action:** Go to https://railway.app and deploy! 🚀

