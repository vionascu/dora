# DORA Metrics Pipeline - Complete Deployment Guide

## 🎯 What You Have Now

A **fully automated 3-stage GitHub Actions workflow** that:

1. **Collects** data from GitHub repositories
2. **Builds** a professional metrics dashboard
3. **Deploys** the dashboard to GitHub Pages

Total time: ~10-15 minutes per run.

---

## 📋 Files Created

### Workflow Configuration
```
.github/workflows/
├─ dora-pipeline.yml .......................... Main 3-stage workflow
└─ README.md .................................. Workflow documentation
```

### Documentation
```
├─ GITHUB_ACTIONS_GUIDE.md .................... Quick start guide
├─ WORKFLOW_DEPLOYMENT.md ..................... This file
├─ REPORT_ACCESS.md ........................... Dashboard access guide
└─ docs/index.md .............................. GitHub Pages docs
```

---

## 🚀 Quick Start

### Step 1: Push Workflow to GitHub

```bash
cd /Users/viionascu/Projects/DORA

git add .github/workflows/dora-pipeline.yml
git add .github/workflows/README.md
git add GITHUB_ACTIONS_GUIDE.md
git add WORKFLOW_DEPLOYMENT.md

git commit -m "Deploy 3-stage GitHub Actions workflow"
git push origin main
```

### Step 2: Enable GitHub Pages

1. Go to your **GitHub repository**
2. Click **Settings**
3. Go to **Pages** (left sidebar)
4. Under "Build and deployment":
   - Select "Deploy from a branch"
   - Choose **main** branch
   - Choose **/ (root)** folder
5. Click **Save**

### Step 3: Watch Workflow Execute

1. Go to **Actions** tab
2. Click **DORA Metrics Pipeline**
3. Watch real-time progress:
   - ✅ collect-data (5-10 min)
   - ✅ build-dashboard (1-2 min)
   - ✅ deploy-github-pages (2-3 min)

### Step 4: View Live Dashboard

After deployment succeeds (15 min), visit:

```
https://vionascu.github.io/RnDMetrics/public/index.html
```

---

## 🔄 Workflow Stages

### STAGE 1: Data Collection (5-10 minutes)

**Job:** `collect-data`

Performs 8 steps:
1. Parse `ReposInput.md` configuration
2. Clone all GitHub repositories
3. Extract git artifacts (commits, authors, timestamps)
4. Collect CI artifacts (test files, frameworks)
5. Scan for epics and user stories
6. Calculate DORA metrics
7. Calculate test metrics
8. Validate data quality

**Produces:**
- `calculations/` - All computed metrics
- `git_artifacts/` - Raw GitHub data
- `ci_artifacts/` - CI/CD data
- `github_scan_artifacts.json` - Scan results

**Artifacts:** Uploaded for 30 days

---

### STAGE 2: Build Dashboard (1-2 minutes)

**Job:** `build-dashboard`

**Depends on:** `collect-data` must succeed ✓

Performs 2 steps:
1. Verify all dashboard files exist
   - `public/index.html`
   - `public/report.js`
   - `public/report.css`
2. Validate metrics data
   - Parse `MANIFEST.json`
   - Confirm all metrics present
   - Check test frameworks

**Validates:**
- Dashboard template ready
- All data files present
- Metrics are valid JSON
- No missing repositories

**Status:** Ready for deployment

---

### STAGE 3: Deploy to GitHub Pages (2-3 minutes)

**Job:** `deploy-github-pages`

**Depends on:** Both Stage 1 & 2 must succeed ✓

**Condition:** Only runs on push to main (not on PRs)

Performs 2 steps:
1. Prepare deployment package
   - Create `_site/` directory
   - Copy `public/*` (dashboard)
   - Copy `calculations/*` (metrics)
   - Copy `git_artifacts/*` (raw data)
   - Copy `ci_artifacts/*` (CI data)
   - Copy documentation

2. Deploy to GitHub Pages
   - Push to `gh-pages` branch
   - Publish via GitHub Pages
   - Generate deployment summary

**Result:**
- 🚀 Dashboard live
- 📊 Metrics accessible
- 📁 Raw data inspectable
- 📚 Documentation included

---

## ⏱️ Workflow Triggers

### Automatic: Push to main
```
Any commit to main branch
  ↓
Automatically triggers all 3 stages
  ↓
Deploys to GitHub Pages
```

### Automatic: Pull Requests
```
Pull request opened
  ↓
Runs Stage 1 & 2 only (no deployment)
  ↓
Validates before merge
```

### Automatic: Daily Schedule
```
Every day at 2 AM UTC
  ↓
Runs full pipeline
  ↓
Keeps dashboard fresh with latest data
```

### Manual: From Actions Tab
```
Actions → DORA Metrics Pipeline → Run workflow
  ↓
Select branch
  ↓
Click "Run workflow"
  ↓
All 3 stages execute
```

---

## 🔍 Monitoring Workflow

### View Workflow Status

1. Go to GitHub repository
2. Click **Actions** tab
3. Select **DORA Metrics Pipeline**
4. See all runs with:
   - ✅ Status (success/failure)
   - ⏱ Duration
   - 📅 When it ran
   - 👤 Who triggered it

### View Individual Stage

Click on any workflow run:
```
Workflow run page
├─ collect-data
│  ├─ Parse repos
│  ├─ Clone repos
│  ├─ Extract git
│  ├─ Collect CI
│  ├─ Scan GitHub
│  ├─ Calculate metrics
│  ├─ Validate
│  └─ Generate manifest
├─ build-dashboard
│  ├─ Verify files
│  └─ Validate data
└─ deploy-github-pages
   ├─ Prepare _site/
   ├─ Deploy
   └─ Summary
```

### View Detailed Logs

Click on any step to expand and see full console output

### Download Artifacts

```
Workflow run page
  ↓
Scroll to "Artifacts" section
  ↓
Download "dora-calculations"
  ↓
Contains all metrics & git data
```

---

## 🔧 Configuration Options

### Change Schedule Frequency

Edit `.github/workflows/dora-pipeline.yml`:

```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

Common patterns:
- `0 2 * * *` = Every day 2 AM UTC
- `0 0 * * 0` = Every Monday midnight
- `0 0 1 * *` = 1st of month midnight
- `*/30 * * * *` = Every 30 minutes

### Change Python Version

```yaml
with:
  python-version: '3.9'
```

### Set Custom Domain (Optional)

```yaml
cname: dora-metrics.vionascu.dev
```

Or remove for default: `https://vionascu.github.io/RnDMetrics/`

---

## 📊 What Gets Deployed

After successful Stage 3, GitHub Pages contains:

```
https://vionascu.github.io/RnDMetrics/
│
├─ public/index.html ......................... 📊 LIVE DASHBOARD
│
├─ calculations/
│  ├─ MANIFEST.json ......................... 📋 Validation Report
│  ├─ global/
│  │  ├─ commits.json
│  │  ├─ summary.json
│  │  └─ tests.json
│  └─ per_repo/
│     ├─ TrailEquip/ ........................ Java metrics
│     ├─ TrailWaze/ ......................... React metrics
│     └─ RnDMetrics/ ........................ Python metrics
│
├─ git_artifacts/
│  ├─ TrailEquip/
│  ├─ TrailWaze/
│  ├─ RnDMetrics/
│  └─ github_scan_artifacts.json
│
├─ ci_artifacts/
│  ├─ TrailEquip/
│  ├─ TrailWaze/
│  └─ RnDMetrics/
│
└─ README.md ............................... 📚 Documentation
```

---

## ✅ Verify Deployment

### Check Workflow Succeeded

```
Actions → DORA Metrics Pipeline → Latest run
  ↓
All 3 jobs show ✅ (green checkmark)
```

### Check GitHub Pages Enabled

```
Settings → Pages
  ↓
Shows "Your site is published at: https://..."
```

### Visit Dashboard

```
https://vionascu.github.io/RnDMetrics/public/index.html
  ↓
Dashboard loads with all metrics
```

### Verify Metrics Display

Dashboard should show:
- ✅ 7 key finding cards
- ✅ 228 total commits
- ✅ 3 repositories
- ✅ 4 contributors
- ✅ 15 test files
- ✅ 58 epics
- ✅ 4 user stories
- ✅ Repository analysis table
- ✅ Validation status (all passing)

---

## 🚨 Troubleshooting

### Issue: Workflow doesn't start

**Check:**
- YAML file at `.github/workflows/dora-pipeline.yml`
- File name has no typos
- YAML syntax is valid (use YAML linter)

**Fix:**
```bash
# Verify file exists
ls -la .github/workflows/dora-pipeline.yml

# Check YAML syntax
python3 -m yaml .github/workflows/dora-pipeline.yml
```

### Issue: Stage 1 fails

**Check:**
- `ReposInput.md` exists and is formatted correctly
- Repository URLs are accessible
- Python 3.9+ installed on runner

**View logs:**
- Actions → Run → collect-data → Logs
- Look for error in git clone or Python script

**Fix:**
- Verify `ReposInput.md` format
- Check repo URLs are correct
- Run locally: `python3 src/collection/collect_git.py`

### Issue: Stage 2 fails

**Check:**
- Stage 1 succeeded
- Dashboard files exist: `public/index.html`, `public/report.js`, `public/report.css`
- `calculations/MANIFEST.json` was created

**Fix:**
- Download `dora-calculations` artifact
- Verify `MANIFEST.json` has content
- Check dashboard files are not corrupted

### Issue: Stage 3 fails

**Check:**
- GitHub Pages is enabled (Settings → Pages)
- Branch is set to `main` or `gh-pages`
- Permissions are correct

**Fix:**
- Enable GitHub Pages in Settings
- Set "Deploy from a branch" to main
- Wait a few minutes for Pages to initialize

### Issue: Dashboard shows "N/A" for metrics

**Check:**
- MANIFEST.json loaded correctly
- Metrics were calculated in Stage 1
- No JavaScript errors (browser console)

**Fix:**
- Download artifacts from workflow
- Check `calculations/MANIFEST.json` content
- Run Stage 1 manually to verify calculations

---

## 📈 Success Indicators

### ✅ Workflow Running

- Actions tab shows "DORA Metrics Pipeline"
- Workflow runs appear in history
- Each stage completes in expected time

### ✅ Data Collection Working

- Stage 1 completes in 5-10 minutes
- Artifact "dora-calculations" available
- No errors in logs

### ✅ Dashboard Building

- Stage 2 completes in 1-2 minutes
- Verifies all dashboard files
- Validates metrics data

### ✅ Deployment Successful

- Stage 3 completes in 2-3 minutes
- GitHub Pages shows published status
- Dashboard accessible at GitHub.io URL

### ✅ Dashboard Live

- Page loads without errors
- Metrics display correctly
- All 7 cards show values
- Repository table populated
- Validation status shows "PASS"

---

## 📚 Documentation Index

1. **GITHUB_ACTIONS_GUIDE.md**
   - Quick start
   - Workflow overview
   - Common issues & fixes
   - Configuration options

2. **.github/workflows/README.md**
   - Detailed workflow documentation
   - Stage-by-stage breakdown
   - Data flow diagram
   - Security & permissions

3. **REPORT_ACCESS.md**
   - Dashboard access methods
   - Data file locations
   - Repository details
   - Quick links

4. **docs/index.md**
   - GitHub Pages landing page
   - Dashboard overview
   - Data sources

---

## 🎯 Next Steps

1. **Commit & Push**
   ```bash
   git add -A
   git commit -m "Deploy 3-stage GitHub Actions workflow"
   git push origin main
   ```

2. **Enable GitHub Pages**
   - Settings → Pages
   - Select "Deploy from a branch"
   - Choose "main" branch
   - Click Save

3. **Monitor First Run**
   - Go to Actions tab
   - Watch each stage execute
   - Verify no errors

4. **Check Deployment**
   - Wait 15 minutes
   - Visit dashboard URL
   - Verify metrics display

5. **Set Schedule (Optional)**
   - Edit `.github/workflows/dora-pipeline.yml`
   - Adjust `schedule:` cron expression
   - Commit & push to update

---

## 🎓 Understanding the Workflow

### Why 3 Stages?

1. **Separation of Concerns**
   - Stage 1: Data collection is independent
   - Stage 2: Validation is quick and cheap
   - Stage 3: Deployment only if all pass

2. **Failure Isolation**
   - If Stage 1 fails, Stages 2&3 don't run
   - If Stage 2 fails, Stage 3 doesn't run
   - No partial deployments

3. **Performance**
   - Stages can be optimized independently
   - Each stage has clear inputs/outputs
   - Easy to debug and fix

4. **Monitoring**
   - Clear status for each stage
   - Detailed logs per step
   - Easy to identify failures

---

## 💡 Pro Tips

1. **Monitor Regularly**
   - Check Actions tab weekly
   - Review any failed runs
   - Download artifacts to inspect

2. **Update ReposInput.md**
   - Add new repositories anytime
   - Remove obsolete repos
   - Pipeline auto-adjusts

3. **Version Your Data**
   - Artifacts are retained 30 days
   - Download important runs
   - Compare metrics over time

4. **Share Dashboard**
   - Public GitHub Pages URL
   - No authentication needed
   - Share with stakeholders

5. **Automate Everything**
   - Workflow runs automatically
   - No manual intervention needed
   - Set and forget!

---

## ✨ Summary

You now have:

✅ **Fully automated CI/CD pipeline**
✅ **3-stage workflow on GitHub Actions**
✅ **Data collection from GitHub**
✅ **Professional metrics dashboard**
✅ **Deployment to GitHub Pages**
✅ **Real-time monitoring**
✅ **Zero manual steps required**
✅ **Production-ready system**

**Total setup time:** ~5 minutes
**Total execution time:** ~15 minutes per run
**Cost:** Free on public GitHub repos!

---

**Questions?** Check the documentation files or view workflow logs in Actions tab.

**Ready to deploy?** Push to main and watch the magic happen! 🚀
