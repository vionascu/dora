# Free Deployment Options for TrailEquip

This guide provides multiple options to deploy TrailEquip completely free without needing to install anything locally.

## Option 1: Railway.app (Recommended - Easiest)

**Cost**: Free tier with $5 monthly credit (effectively free for development)
**Setup time**: ~10 minutes
**Features**: PostgreSQL included, easy GitHub/GitLab integration

### Steps:

1. **Sign up at** https://railway.app (no credit card required)

2. **Connect your GitLab project**:
   - Go to Dashboard → New Project
   - Select "Deploy from GitHub" or "Deploy from GitLab"
   - Authorize and select `TrailEquip` repository

3. **Add PostgreSQL Plugin**:
   - Click "Add Service" → "Database" → "PostgreSQL"
   - Default config is fine

4. **Configure Environment Variables**:
   - `SPRING_DATASOURCE_URL`: `jdbc:postgresql://localhost:5432/railway`
   - `SPRING_JPA_HIBERNATE_DDL_AUTO`: `update`
   - `PORT`: `3000` (Railway will set this automatically)

5. **Deploy**:
   - Railway auto-detects `Dockerfile`
   - Builds and deploys automatically
   - Your app will be available at: `https://trailequip-production.up.railway.app`

**Free tier includes**:
- 500 GB-hours per month
- PostgreSQL database
- Unlimited deployments

---

## Option 2: Render.com (Also Very Easy)

**Cost**: Free tier with hibernation
**Setup time**: ~10 minutes
**Features**: Excellent for side projects, simple UI

### Steps:

1. **Sign up at** https://render.com (no credit card required)

2. **Create New Service**:
   - Dashboard → Create → Web Service
   - Connect GitLab repository
   - Select `TrailEquip` repo

3. **Configure Service**:
   - **Name**: `trailequip`
   - **Environment**: Docker
   - **Region**: Any
   - **Branch**: `main`

4. **Add PostgreSQL Database**:
   - Dashboard → Create → PostgreSQL
   - Use default settings

5. **Link Database to Service**:
   - Edit service environment variables:
   ```
   DATABASE_URL: (Render auto-fills from PostgreSQL service)
   SPRING_JPA_HIBERNATE_DDL_AUTO: update
   ```

6. **Deploy**:
   - Click "Create Web Service"
   - Render builds from Dockerfile
   - App available at: `https://trailequip.onrender.com`

**Free tier limitations**:
- Services spin down after 15 minutes of inactivity
- Restart takes ~30 seconds
- Perfect for development/testing

---

## Option 3: Fly.io (Fast & Reliable)

**Cost**: Generous free tier (up to 3 shared-cpu-1x 256MB VMs)
**Setup time**: ~15 minutes
**Features**: Very fast, excellent performance

### Steps:

1. **Sign up at** https://fly.io (no credit card required)

2. **Install Fly CLI**:
   ```bash
   # macOS
   brew install flyctl

   # Or visit: https://fly.io/docs/hands-on/install-flyctl/
   ```

3. **Launch App**:
   ```bash
   cd /Users/viionascu/Projects/TrailEquip
   flyctl launch --name trailequip
   ```

4. **Configure**:
   - Select "Dockerfile" for build strategy
   - Choose region closest to you
   - Agree to .dockerignore creation

5. **Create PostgreSQL Database**:
   ```bash
   flyctl postgres create --name trailequip-db

   # When prompted, select:
   # - Organization: personal
   # - VM Size: shared-cpu-1x (free)
   # - Volume: skip (optional)
   ```

6. **Attach Database**:
   ```bash
   flyctl postgres attach trailequip-db --app trailequip
   ```

7. **Deploy**:
   ```bash
   flyctl deploy
   ```

8. **Get URL**:
   ```bash
   flyctl open
   ```

**Free tier includes**:
- 3 shared CPU VMs with 256MB RAM each
- 3GB storage per VM
- 160GB/month bandwidth
- No hibernation - always running!

---

## Option 4: Heroku (Legacy but Still Works)

**Cost**: $7/month minimum (Eco tier)
**Setup time**: ~10 minutes
**Note**: Free tier was discontinued in Nov 2022, now requires payment

### If budget allows:

1. Sign up at https://heroku.com
2. Create new app: `heroku create trailequip`
3. Add PostgreSQL: `heroku addons:create heroku-postgresql:basic`
4. Deploy: `git push heroku main`

---

## Option 5: Netlify + External Backend (Frontend Only)

**Cost**: Completely free for frontend
**Setup time**: ~5 minutes
**Architecture**: Netlify hosts frontend, backend on Railway/Render

### Steps:

1. **Deploy Frontend to Netlify**:
   - Visit https://netlify.com
   - Sign in with GitHub/GitLab
   - Select `TrailEquip` repo
   - Build command: `cd ui && npm run build`
   - Publish directory: `ui/dist`
   - Deploy!

2. **Set Backend API URL**:
   - Add environment variable: `VITE_API_URL=https://your-railway-app.com`
   - Netlify automatically redeploys

**Free tier includes**:
- Unlimited deployments
- Custom domain support
- HTTPS by default
- Edge functions (extra features)

---

## Option 6: GitHub Pages + Backend (Frontend Only)

**Cost**: Completely free
**Limitation**: Only works if you use GitHub (you're on GitLab)

### Alternative: Fork to GitHub
1. Create GitHub account (free)
2. Mirror repository from GitLab to GitHub
3. Enable GitHub Pages in repository settings
4. Deploy frontend to GitHub Pages

---

## Recommended Setup for You: Railway + GitHub Pages

This is the easiest free option:

### Architecture
```
┌─────────────────────────────────────────────┐
│         GitHub Pages (Free)                 │
│     Frontend: React + Vite Build            │
│  https://yourusername.github.io/trailequip  │
└──────────────────┬──────────────────────────┘
                   │ API calls to
                   ▼
┌─────────────────────────────────────────────┐
│      Railway.app (Free tier)                │
│  Backend: Spring Boot + PostgreSQL 15       │
│  https://trailequip.up.railway.app          │
└─────────────────────────────────────────────┘
```

### Steps:

1. **Setup Railway Backend** (see Option 1 above)
   - Note the deployed URL

2. **Fork to GitHub**:
   ```bash
   # Create new GitHub repo called "trailequip"
   # Then:
   git remote add github https://github.com/yourusername/trailequip.git
   git push github main
   ```

3. **Deploy Frontend to GitHub Pages**:
   ```bash
   # In GitHub repo settings:
   # - Go to Pages
   # - Set source to "GitHub Actions"
   # - Create .github/workflows/deploy.yml
   ```

4. **Update CORS in Backend**:
   - Edit [TrailController.java](../services/trail-service/src/main/java/com/trailequip/trail/adapter/rest/TrailController.java)
   - Change CORS origin to your GitHub Pages URL
   - Push to GitLab, Railway auto-redeploys

---

## Comparison Table

| Platform | Cost | Setup | Performance | Database | Hibernation | Best For |
|----------|------|-------|-------------|----------|-------------|----------|
| **Railway** | $5 credit/mo | 10 min | ⭐⭐⭐⭐ | ✅ Included | ❌ No | Production-ready |
| **Render** | Free | 10 min | ⭐⭐⭐ | ✅ Included | ✅ Yes (slow) | Development |
| **Fly.io** | Free | 15 min | ⭐⭐⭐⭐⭐ | ⚠️ Extra setup | ❌ No | Performance |
| **GitHub Pages** | Free | 5 min | ⭐⭐⭐⭐⭐ | ❌ Frontend only | ❌ No | Frontend only |
| **Netlify** | Free | 5 min | ⭐⭐⭐⭐⭐ | ❌ Frontend only | ❌ No | Frontend only |
| **Cloud Run** | $6.50/mo | 30 min | ⭐⭐⭐⭐⭐ | ✅ Included | ❌ No | Enterprise |

---

## Getting Started Now: Step-by-Step

### Fastest Path (Railway - 10 minutes)

1. Visit https://railway.app
2. Sign in (GitHub / Email)
3. Create new project → Connect GitHub/GitLab
4. Select TrailEquip repository
5. Add PostgreSQL service
6. Wait 2-3 minutes for build
7. Click service URL to open app
8. **Done! Share the URL with anyone**

### URL Format
Your app will be available at:
```
https://trailequip-production.up.railway.app
```

Share this link - anyone can access it without installing anything!

---

## After Deployment

### Monitor Logs
Most platforms provide built-in log viewing:
- **Railway**: Dashboard → Service → Logs
- **Render**: Dashboard → Service → Logs
- **Fly.io**: `flyctl logs -a trailequip`

### Update Deployment
Every push to `main` auto-triggers new deployment

### Custom Domain
- Railway: Settings → Domains → Add custom domain
- Render: Settings → Custom Domain
- Fly.io: `flyctl certs add yourdomain.com`

---

## Troubleshooting

### "Build failed"
Check the platform's build logs:
- Rails/Django scripts must match platform expectations
- Java projects need correct build system (Gradle ✓)

### "Database connection failed"
Ensure DATABASE_URL environment variable is set:
- Railway/Render auto-set this for you
- Check environment variables in service settings

### "Port not working"
Application must listen on PORT environment variable:
- Our Dockerfile already does this ✓
- Spring Boot configured with `-Dserver.port=${PORT}`

### "Out of free tier quota"
Upgrade to paid tier or create new free account on different platform

---

## My Recommendation

**Use Railway for the best balance of:**
- ✅ Simple setup (literally 3 clicks)
- ✅ PostgreSQL included
- ✅ Always running (no hibernation)
- ✅ Auto-deploys from GitLab push
- ✅ $5/month ($0 free tier credit)
- ✅ Easy to scale when needed

Go to https://railway.app now and follow Option 1 above!

---

## Need More Help?

Check platform documentation:
- Railway: https://docs.railway.app/
- Render: https://render.com/docs
- Fly.io: https://fly.io/docs/
- Google Cloud Run: https://cloud.google.com/run/docs

**Questions?** Each platform has excellent support/docs. Start with Railway - it's the easiest!
