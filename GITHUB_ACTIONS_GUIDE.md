# GitHub Actions - DORA Metrics Pipeline Guide

## 🎯 Quick Overview

Your DORA Metrics Pipeline has **3 automated stages** on GitHub Actions:

```
┌─────────────────────────────────────────────────────────────┐
│  GITHUB ACTIONS: DORA METRICS PIPELINE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ STAGE 1: DATA COLLECTION (5-10 min)                │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │  ✓ Clone repositories from GitHub                  │  │
│  │  ✓ Extract git history & commits                   │  │
│  │  ✓ Scan for test files & frameworks                │  │
│  │  ✓ Find epics & user stories                       │  │
│  │  ✓ Calculate DORA metrics                          │  │
│  │  ✓ Validate data quality                           │  │
│  │  ✓ Generate MANIFEST.json                          │  │
│  │                                                     │  │
│  │  OUTPUT: calculations/, git_artifacts/             │  │
│  └─────────────────────────────────────────────────────┘  │
│                            ↓                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ STAGE 2: BUILD DASHBOARD (1-2 min)                 │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │  ✓ Download Stage 1 artifacts                      │  │
│  │  ✓ Verify all dashboard files exist                │  │
│  │  ✓ Validate metrics data                           │  │
│  │  ✓ Check test framework info                       │  │
│  │                                                     │  │
│  │  OUTPUT: Dashboard ready for deployment             │  │
│  └─────────────────────────────────────────────────────┘  │
│                            ↓                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ STAGE 3: DEPLOY TO GITHUB PAGES (2-3 min)         │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │  ✓ Prepare _site/ deployment folder                │  │
│  │  ✓ Copy dashboard & calculations                   │  │
│  │  ✓ Deploy to GitHub Pages branch                   │  │
│  │  ✓ Generate summary report                         │  │
│  │                                                     │  │
│  │  OUTPUT: Live dashboard on GitHub Pages            │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  TOTAL TIME: ~10-15 minutes                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Workflow Trigger Events

The pipeline runs automatically on:

### 1. **Push to main branch**
   - Triggered by every commit/push
   - Runs all 3 stages
   - Deploys to GitHub Pages

### 2. **Pull requests**
   - Triggered when PR is created
   - Runs Stage 1 & 2 only
   - Skips deployment
   - Validates data before merge

### 3. **Daily schedule**
   - Runs automatically every day at 2 AM UTC
   - Keeps dashboard fresh
   - Can be modified in workflow YAML

### 4. **Manual trigger**
   - Go to **Actions** tab
   - Click **DORA Metrics Pipeline**
   - Click **Run workflow**
   - Select branch and run

---

## 🔍 How to Monitor

### View Workflow Runs

1. Go to your GitHub repository
2. Click **Actions** tab
3. Select **DORA Metrics Pipeline**
4. See all runs with:
   - ✓ Status (success/failure)
   - ⏱ Duration
   - 📅 When it ran
   - 👤 Who triggered it

### Check Individual Stage Status

```
Click on any workflow run
    ↓
Expand each job:
  • collect-data
  • build-dashboard
  • deploy-github-pages
  • workflow-summary
    ↓
View detailed logs for each step
```

### Download Artifacts

```
Click on workflow run
    ↓
Scroll to "Artifacts" section
    ↓
Download "dora-calculations"
    ↓
Contains all metrics & git data
```

---

## 🚀 After Deployment

### View Your Live Dashboard

After successful Stage 3 deployment, dashboard is live at:

```
https://vionascu.github.io/RnDMetrics/public/index.html
```

With access to:
- **Dashboard**: `/public/index.html`
- **Calculations**: `/calculations/MANIFEST.json`
- **Git Data**: `/git_artifacts/`
- **CI Data**: `/ci_artifacts/`

---

## 📊 What Each Stage Does

### Stage 1: Data Collection

```python
# Stage 1 executes these scripts in order:

1. src/collection/collect_git.py
   └─ Clones all repos from ReposInput.md
   └─ Extracts commits, authors, timestamps
   └─ Saves to git_artifacts/{repo}/

2. src/collection/collect_ci.py
   └─ Attempts to run tests locally
   └─ Collects CI artifact data
   └─ Saves to ci_artifacts/{repo}/

3. src/collection/scan_github_artifacts.py
   └─ Scans for test files
   └─ Finds epics & user stories
   └─ Saves to git_artifacts/github_scan_artifacts.json

4. src/calculations/calculate.py
   └─ Processes git data
   └─ Computes DORA metrics
   └─ Saves to calculations/per_repo/

5. src/calculations/calculate_test_metrics.py
   └─ Counts test files
   └─ Aggregates epics & stories
   └─ Saves test metrics

6. src/validation/validate.py
   └─ Runs quality gates
   └─ Validates all metrics
   └─ Checks for approximations

7. Generate MANIFEST.json
   └─ Creates validation report
   └─ Includes all metrics
   └─ Ready for dashboard
```

### Stage 2: Build Dashboard

```
Tasks:
  ✓ Verify index.html exists
  ✓ Verify report.js exists
  ✓ Verify report.css exists
  ✓ Verify MANIFEST.json was generated
  ✓ Parse JSON and confirm metrics present
  ✓ List all repositories found
  ✓ Display test metrics summary

Validates:
  ✓ Dashboard template ready
  ✓ All data files present
  ✓ Metrics are valid JSON
  ✓ No missing repositories
```

### Stage 3: Deploy

```
Tasks:
  ✓ Create _site/ directory
  ✓ Copy public/* to _site/
  ✓ Copy calculations/ to _site/
  ✓ Copy git_artifacts/ to _site/
  ✓ Copy ci_artifacts/ to _site/
  ✓ Copy documentation
  ✓ Deploy _site/ to GitHub Pages gh-pages branch
  ✓ Generate deployment summary

Result:
  ✓ Dashboard live at GitHub Pages
  ✓ All calculations accessible
  ✓ Documentation included
```

---

## 🔧 Configuration

### Edit Workflow File

Path: `.github/workflows/dora-pipeline.yml`

**Change schedule frequency:**
```yaml
schedule:
  - cron: '0 2 * * *'  # Currently: Daily 2 AM UTC
```

Common patterns:
- `0 2 * * *` = Every day 2 AM
- `0 0 * * 0` = Every Monday midnight
- `0 0 1 * *` = 1st of month
- `*/30 * * * *` = Every 30 minutes

**Change Python version:**
```yaml
with:
  python-version: '3.9'  # Currently: Python 3.9
```

**Set custom domain (optional):**
```yaml
cname: dora-metrics.vionascu.dev
```

Or remove `cname:` for default GitHub Pages URL.

---

## ⚠️ Common Issues & Fixes

### Issue 1: Stage 1 Fails - "Collection Failed"

**Error message:** `ModuleNotFoundError` or git clone fails

**Fix:**
1. Check `ReposInput.md` exists
2. Verify repository URLs are correct
3. Check Python version compatibility
4. View logs: Actions → [Run] → collect-data → Logs

### Issue 2: Stage 2 Fails - "Dashboard Build Failed"

**Error message:** `FileNotFoundError` for dashboard files

**Fix:**
1. Verify `public/index.html` exists
2. Verify `calculations/MANIFEST.json` created
3. Check Stage 1 succeeded
4. Download dora-calculations artifact

### Issue 3: Stage 3 Fails - "Deployment Failed"

**Error message:** `Error: 403 Forbidden` or deployment denied

**Fix:**
1. Go to repo Settings → Pages
2. Ensure "GitHub Pages" is enabled
3. Set branch to `main` or `gh-pages`
4. Check token permissions (usually automatic)
5. Verify custom domain setup (if using CNAME)

### Issue 4: Dashboard Shows "N/A" for Metrics

**Error message:** Missing values in dashboard

**Fix:**
1. Check MANIFEST.json exists
2. Verify data in calculations/
3. Run pipeline manually
4. Download and inspect artifacts
5. Check data_quality_notes in MANIFEST.json

---

## 📈 Workflow Status Badge

Add to your README to show workflow status:

```markdown
[![DORA Metrics Pipeline](https://github.com/vionascu/RnDMetrics/actions/workflows/dora-pipeline.yml/badge.svg)](https://github.com/vionascu/RnDMetrics/actions/workflows/dora-pipeline.yml)
```

---

## 🎯 Next Steps

1. **Commit this workflow:**
   ```bash
   git add .github/workflows/dora-pipeline.yml
   git add .github/workflows/README.md
   git commit -m "Add 3-stage DORA metrics pipeline workflow"
   git push origin main
   ```

2. **Enable GitHub Pages** (if not already):
   - Go to Settings → Pages
   - Select "Deploy from a branch"
   - Choose "main" branch
   - Click Save

3. **Watch first run:**
   - Go to Actions tab
   - Click "DORA Metrics Pipeline"
   - Refresh to see progress
   - View logs for any issues

4. **Access live dashboard:**
   - After Stage 3 succeeds
   - Visit: `https://vionascu.github.io/RnDMetrics/public/index.html`
   - Share the link!

---

## 📊 Expected Output

After successful workflow run:

```
✅ STAGE 1: DATA COLLECTION - SUCCESS
   • 228 commits collected
   • 4 contributors found
   • 15 test files identified
   • 58 epics documented
   • 4 user stories found

✅ STAGE 2: BUILD DASHBOARD - SUCCESS
   • Dashboard files verified
   • Metrics data validated
   • 3 repositories confirmed

✅ STAGE 3: DEPLOY TO GITHUB PAGES - SUCCESS
   • Dashboard deployed
   • Calculations accessible
   • Documentation included

🌐 LIVE AT: https://vionascu.github.io/RnDMetrics/public/index.html
```

---

## 🔐 Security

The workflow uses:
- **GITHUB_TOKEN** (automatic - no setup needed)
- **OIDC authentication** for GitHub Pages deployment
- **No external secrets** required
- **Read-only Git access** for collecting artifacts

No API keys or credentials stored!

---

## 📚 Files Reference

Workflow components:
```
.github/
├─ workflows/
│  ├─ dora-pipeline.yml ........... Main 3-stage workflow
│  └─ README.md ................... Workflow documentation
│
scripts used by workflow:
├─ src/collection/collect_git.py
├─ src/collection/collect_ci.py
├─ src/collection/scan_github_artifacts.py
├─ src/calculations/calculate.py
├─ src/calculations/calculate_test_metrics.py
└─ src/validation/validate.py

deployment:
├─ public/index.html ............. Dashboard template
├─ public/report.js .............. Dashboard logic
└─ public/report.css ............. Dashboard styling
```

---

**Ready to deploy?** Push to main and watch your workflow run!

```bash
git add .
git commit -m "Deploy DORA pipeline with GitHub Actions"
git push origin main
# Then check Actions tab to watch 3 stages execute
```
