# GitLab Pages Deployment - In Progress

**Date:** February 3, 2026
**Status:** 🚀 **DEPLOYMENT INITIATED**

---

## Deployment Timeline

### ✅ Step 1: Repository Created
```
[COMPLETE] GitLab project created at:
https://git.ecd.axway.org/viionascu/dora
```

### ✅ Step 2: Code Pushed to GitLab
```
[COMPLETE] Pushed main branch with:
- All source code
- .gitlab-ci.yml pipeline
- Dashboard and documentation
- 7,182 commits from aisportal (calculated metrics)
```

### ⏳ Step 3: GitLab CI/CD Pipeline Running
```
[IN PROGRESS] Monitor at:
https://git.ecd.axway.org/viionascu/dora/-/pipelines
```

Pipeline stages:
1. **collect_git** - Cloning aisportal, extracting metrics
2. **calculate_metrics** - Computing DORA calculations
3. **pages** - Deploying to GitLab Pages

Estimated time: **5-10 minutes**

### ⏳ Step 4: Dashboard Deployment
```
[WAITING FOR PIPELINE]
Will be available at:
https://git.ecd.axway.org/viionascu/dora/-/pages
```

---

## How to Monitor

### Check Pipeline Status
Visit: `https://git.ecd.axway.org/viionascu/dora/-/pipelines`

You'll see three jobs:
1. **collect_git** (Stage: collect)
   - Clones aisportal repository
   - Extracts git metrics
   - Status: Running/Passed

2. **calculate_metrics** (Stage: calculate)
   - Computes all DORA metrics
   - Calculates test metrics and evolution metrics
   - Status: Running/Passed

3. **pages** (Stage: deploy)
   - Builds GitLab Pages deployment
   - Publishes dashboard to GitLab Pages
   - Status: Running/Passed

### Watch Live Logs
Click on each job to see real-time output:
- See commits being collected
- Watch metrics calculations
- Verify page deployment

### Expected Output

#### collect_git job log:
```
✓ Cloned successfully
✓ Extracted 7182 commits, 33 authors
✓ Artifacts saved
```

#### calculate_metrics job log:
```
✓ Saved global metrics for 1 repos
✓ Global test metrics saved
✓ Velocity trends: 381 weeks active
✓ Contributor growth: 48 contributors
```

#### pages job log:
```
✓ Dashboard ready for deployment
✓ GitLab Pages published
```

---

## What Happens During Deployment

### Stage 1: Collect Git Data (2-5 minutes)
```
1. Authenticate to aisportal repository using GITLAB_TOKEN
2. Clone aisportal.git repository
3. Extract git history (7182 commits)
4. Process commit data
5. Save to git_artifacts/aisportal/
```

### Stage 2: Calculate Metrics (1-2 minutes)
```
1. Parse git artifacts from Stage 1
2. Calculate DORA metrics:
   - Commits & velocity
   - Contributors
   - Lead time
   - Test metrics
   - Evolution indicators
3. Save to calculations/per_repo/aisportal/
4. Calculate global metrics
5. Save to calculations/global/
```

### Stage 3: Deploy to GitLab Pages (1 minute)
```
1. Copy dashboard files (public/)
2. Copy metrics data (calculations/)
3. Copy documentation (docs/)
4. Move to public/ folder (GitLab Pages requirement)
5. Publish to:
   https://git.ecd.axway.org/viionascu/dora/-/pages
```

---

## Access Dashboard

### Once Pipeline Completes ✅

Visit: **`https://git.ecd.axway.org/viionascu/dora/-/pages`**

You'll see:
- **Dashboard** with real aisportal metrics
  - 7,182 commits
  - 33 contributors
  - Velocity charts
  - 381 weeks of activity

- **Documentation** at: `/docs/index.html`
  - Beginner's Guide
  - Quick Reference
  - Visual Walkthrough
  - GitLab Integration Guide
  - Complete API documentation

- **Raw Metrics** at: `/calculations/`
  - Global metrics (JSON)
  - Per-repository metrics
  - Historical data

---

## Current Status

### Repository
```
✅ Created at: https://git.ecd.axway.org/viionascu/dora
✅ Main branch: pushed with all code
✅ Visibility: Private
```

### Pipeline
```
⏳ Status: Running
🔗 Monitor at: https://git.ecd.axway.org/viionascu/dora/-/pipelines
📊 Stages: collect → calculate → deploy
⏱️ ETA: 5-10 minutes
```

### Dashboard
```
⏳ Status: Deploying
🌐 URL: https://git.ecd.axway.org/viionascu/dora/-/pages
📈 Metrics: 7,182 commits, 33 contributors
🎯 Data: Real aisportal metrics (no mock data)
```

---

## Troubleshooting During Deployment

### If Pipeline Fails

**Check logs:**
1. Go to: `https://git.ecd.axway.org/viionascu/dora/-/pipelines`
2. Click on failed job
3. Read error message
4. Common issues:

#### ❌ "Clone failed"
- Check GITLAB_TOKEN has `api` and `read_repository` scopes
- Verify aisportal repository exists
- Check branch is `master` (not main)

#### ❌ "File not found"
- Check calculations are in place
- Verify all stages completed

#### ❌ "Pages not published"
- Check public/ folder has index.html
- Verify pages job succeeded
- Wait 1-2 minutes for GitLab to process

**Retry:**
```
https://git.ecd.axway.org/viionascu/dora/-/pipelines
Click "Run Pipeline" button
```

### If Dashboard Shows "N/A"

**Causes:**
- Metrics calculation failed (check Stage 2 logs)
- calculations/ folder not deployed (check Stage 3)
- Browser cache (try Cmd+Shift+R)

**Solution:**
1. Check all pipeline stages passed
2. Verify calculations/ folder populated
3. Clear browser cache and reload

---

## Next Steps

### Wait for Pipeline (5-10 minutes)
1. ⏳ Monitoring pipeline at:
   ```
   https://git.ecd.axway.org/viionascu/dora/-/pipelines
   ```

2. ✅ When all stages pass, dashboard will be live at:
   ```
   https://git.ecd.axway.org/viionascu/dora/-/pages
   ```

3. 🎉 Verify deployment works:
   - Load dashboard
   - Check metrics display
   - Test documentation
   - Confirm GitLab Pages accessible

### After Deployment (Optional)

1. **Setup Scheduled Runs** (daily automatic collection)
   - Visit: `https://git.ecd.axway.org/viionascu/dora/-/schedules`
   - Create schedule: `0 2 * * *` (2 AM UTC daily)

2. **Configure Notifications** (alerts on failure)
   - Project Settings → Integrations
   - Setup Slack, email, or webhook

3. **Monitor Dashboard Usage** (optional analytics)
   - Track metrics over time
   - Set up alerts on anomalies

---

## Key Information

### GitLab Project
- **URL:** `https://git.ecd.axway.org/viionascu/dora`
- **Visibility:** Private
- **Repository:** `https://git.ecd.axway.org/viionascu/dora.git`

### Dashboard/Documentation
- **URL:** `https://git.ecd.axway.org/viionascu/dora/-/pages`
- **Updated:** Automatically with each pipeline run
- **Content:** Dashboard + docs + metrics

### Pipeline/CI
- **Configuration:** `.gitlab-ci.yml`
- **Stages:** collect → calculate → deploy
- **Monitor:** `https://git.ecd.axway.org/viionascu/dora/-/pipelines`

### Metrics Source
- **Repository:** aisportal
- **URL:** `https://git.ecd.axway.org/aisportal/aisportal.git`
- **Branch:** master
- **Commits:** 7,182
- **Contributors:** 33

---

## Quick Links

| Purpose | URL |
|---------|-----|
| **Monitor Pipeline** | https://git.ecd.axway.org/viionascu/dora/-/pipelines |
| **View Repository** | https://git.ecd.axway.org/viionascu/dora |
| **View Dashboard** | https://git.ecd.axway.org/viionascu/dora/-/pages |
| **View Docs** | https://git.ecd.axway.org/viionascu/dora/-/pages/docs/index.html |
| **View CI Config** | https://git.ecd.axway.org/viionascu/dora/-/blob/main/.gitlab-ci.yml |

---

## Summary

🚀 **DORA has been pushed to GitLab and deployment is in progress!**

**What's happening:**
- GitLab project created
- Code pushed to main branch
- CI/CD pipeline triggered automatically
- 3 stages running: collect → calculate → deploy

**What to do:**
1. Monitor pipeline: `https://git.ecd.axway.org/viionascu/dora/-/pipelines`
2. Wait for "pages" job to complete (5-10 min total)
3. View dashboard: `https://git.ecd.axway.org/viionascu/dora/-/pages`

**Dashboard will show:**
- Real metrics from aisportal (7,182 commits, 33 contributors)
- Full documentation with search
- Interactive charts and visualizations
- Raw metrics data in JSON format

---

**Deployment started:** February 3, 2026, ~13:45 UTC
**Expected completion:** 5-10 minutes
**Monitor at:** https://git.ecd.axway.org/viionascu/dora/-/pipelines

