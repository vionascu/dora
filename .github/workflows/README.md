# DORA Metrics Pipeline - GitHub Actions Workflow

## Overview

The DORA Metrics Pipeline is a fully automated GitHub Actions workflow that runs in **3 stages**:

1. **Data Collection** - Collects git and CI artifacts, calculates metrics
2. **Dashboard Building** - Verifies and prepares dashboard for deployment
3. **GitHub Pages Deployment** - Deploys the dashboard to GitHub Pages

---

## 📋 Workflow: `dora-pipeline.yml`

### Triggers

The pipeline runs automatically on:

- **Push to main branch** - Every commit to main
- **Pull requests** - Validation without deployment
- **Daily schedule** - 2 AM UTC every day (configurable)

Manual trigger available in GitHub UI under "Actions" tab.

---

## 🏗️ Stage 1: Data Collection

**Job:** `collect-data`
**Duration:** ~5-10 minutes
**Runner:** `ubuntu-latest`

### Steps:

1. **Checkout repository** (v3)
   - Fetches full commit history (`fetch-depth: 0`)

2. **Setup Python** (3.9)
   - Installs Python runtime

3. **Create directories**
   - Ensures all required folders exist

4. **Parse Repository Configuration**
   - Reads `ReposInput.md`
   - Displays repositories to be analyzed

5. **Collect Git Artifacts**
   - Clones all repositories (from `ReposInput.md`)
   - Extracts commit history, authors, timestamps
   - Stores in `git_artifacts/{repo}/`

6. **Collect CI Artifacts**
   - Scans for test files and CI data
   - Attempts local test execution
   - Stores in `ci_artifacts/{repo}/`

7. **Scan GitHub for Epics & Tests**
   - Searches each repo for epic documentation
   - Identifies user story patterns
   - Detects test files and frameworks
   - Stores in `git_artifacts/github_scan_artifacts.json`

8. **Calculate Metrics**
   - Processes git data
   - Computes DORA metrics
   - Generates per-repo metrics
   - Stores in `calculations/per_repo/`

9. **Calculate Test Metrics**
   - Aggregates test file counts
   - Counts epics and user stories
   - Creates test metrics files

10. **Validate Data Quality**
    - Runs quality gates
    - Checks for approximations
    - Validates bounds and completeness

11. **Generate Validation Manifest**
    - Creates `MANIFEST.json`
    - Includes all metrics and test data
    - Validates against schema

12. **Upload Artifacts**
    - Stores calculations for next stage
    - Retains for 30 days

### Output

```
✓ calculations/
  ├─ MANIFEST.json (validation report)
  ├─ global/
  │  ├─ commits.json
  │  ├─ summary.json
  │  └─ tests.json
  └─ per_repo/
     ├─ TrailEquip/
     ├─ TrailWaze/
     └─ RnDMetrics/

✓ git_artifacts/
  ├─ {repo}/
  │  ├─ commits.json
  │  └─ authors.json
  └─ github_scan_artifacts.json

✓ ci_artifacts/
  └─ {repo}/
```

---

## 📊 Stage 2: Build Dashboard

**Job:** `build-dashboard`
**Duration:** ~1-2 minutes
**Depends on:** `collect-data` (must succeed)
**Runner:** `ubuntu-latest`

### Steps:

1. **Checkout repository**
   - Fetches latest code

2. **Download calculation artifacts**
   - Retrieves outputs from Stage 1

3. **Verify Dashboard Files**
   - Checks presence of:
     - `public/index.html`
     - `public/report.js`
     - `public/report.css`
     - `calculations/MANIFEST.json`

4. **Verify Dashboard Data**
   - Parses `MANIFEST.json`
   - Validates metrics are present
   - Confirms test data included
   - Lists all repositories

### Output

```
✓ Dashboard verified
  ├─ HTML template ready
  ├─ JavaScript logic loaded
  ├─ CSS styling present
  └─ Data manifest validated
```

---

## 🚀 Stage 3: Deploy to GitHub Pages

**Job:** `deploy-github-pages`
**Duration:** ~2-3 minutes
**Depends on:** `collect-data` & `build-dashboard` (must succeed)
**Conditions:**
- Only runs on `push` to `main` branch
- Skips on pull requests
- Runner:** `ubuntu-latest`

### Permissions

```yaml
contents: read          # Read repository
pages: write           # Write to Pages
id-token: write        # OIDC token
```

### Steps:

1. **Checkout repository**

2. **Download calculation artifacts**

3. **Prepare deployment package**
   - Creates `_site/` directory
   - Copies dashboard files
   - Copies calculations folder
   - Copies documentation

4. **Deploy to GitHub Pages**
   - Uses `peaceiris/actions-gh-pages@v3`
   - Publishes to `gh-pages` branch
   - Optional: Sets CNAME record

5. **Deployment Summary**
   - Displays live dashboard URL
   - Lists access points

### Configuration

**CNAME (Optional)**
```yaml
cname: dora-metrics.vionascu.dev
```

Replace with your domain or remove for default `github.io` URL.

### Output

```
Dashboard available at:
  https://vionascu.github.io/RnDMetrics/public/index.html

With access to:
  /public/              - Dashboard
  /calculations/        - Metrics data
  /git_artifacts/       - Raw git data
  /ci_artifacts/        - CI artifacts
  /README.md            - Documentation
```

---

## ✅ Final Status: Workflow Summary

**Job:** `workflow-summary`
**Duration:** ~10 seconds
**Depends on:** All stages
**Runs:** Always (even if previous stages fail)

### Output

```
╔════════════════════════════════════════════════════════════════════╗
║           DORA METRICS PIPELINE - WORKFLOW COMPLETE               ║
╚════════════════════════════════════════════════════════════════════╝

STAGE 1: DATA COLLECTION
  Status: success
  Tasks: [8 items] ✓

STAGE 2: BUILD DASHBOARD
  Status: success
  Tasks: [2 items] ✓

STAGE 3: DEPLOY TO GITHUB PAGES
  Status: success
  Tasks: [2 items] ✓

✅ ALL STAGES COMPLETED SUCCESSFULLY
```

---

## 📊 Data Flow

```
ReposInput.md
    ↓
Stage 1: Collect
  ├─ Clone repos
  ├─ Extract commits
  ├─ Scan for tests/epics
  ├─ Calculate metrics
  └─ Validate quality
    ↓
    [artifacts uploaded]
    ↓
Stage 2: Build
  ├─ Download artifacts
  ├─ Verify files
  └─ Validate data
    ↓
Stage 3: Deploy
  ├─ Prepare _site/
  ├─ Deploy to Pages
  └─ Generate summary
    ↓
GitHub Pages Live
```

---

## 🔍 Monitoring

### View Workflow Runs

1. Go to **Actions** tab in repository
2. Select **DORA Metrics Pipeline**
3. View all runs with:
   - Start/end times
   - Duration
   - Status (success/failure)
   - Stage details

### View Detailed Logs

1. Click on any workflow run
2. Expand each job (collect-data, build-dashboard, deploy-github-pages)
3. See full console output for each step

### Artifacts

1. Click on workflow run
2. Scroll to **Artifacts** section
3. Download `dora-calculations` (30-day retention)

---

## ⚙️ Configuration

### Schedule Frequency

Edit `.github/workflows/dora-pipeline.yml`:

```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

Common cron patterns:
- `0 2 * * *` = Daily 2 AM UTC
- `0 0 * * 0` = Weekly Monday midnight
- `0 0 1 * *` = Monthly 1st day midnight

### Python Version

```yaml
with:
  python-version: '3.9'
```

### GitHub Pages Domain

```yaml
cname: dora-metrics.vionascu.dev
```

Or remove for default: `https://vionascu.github.io/RnDMetrics/`

---

## 🚨 Troubleshooting

### Stage 1 Fails: "Collection Failed"

Check:
- `ReposInput.md` exists and is valid
- GitHub credentials (if private repos)
- Python dependencies

View logs:
```
Actions → DORA Metrics Pipeline → [Run] → collect-data → Logs
```

### Stage 2 Fails: "Dashboard Build Failed"

Check:
- `public/index.html` exists
- `calculations/MANIFEST.json` was generated
- All required files in Stage 1

### Stage 3 Fails: "Deployment Failed"

Check:
- GitHub Pages enabled in Settings
- Branch set to `main` or `gh-pages`
- CNAME record (if using custom domain)

---

## 📱 Access Dashboard

After successful deployment:

**Direct URL:**
```
https://vionascu.github.io/RnDMetrics/public/index.html
```

**View Calculations:**
```
https://vionascu.github.io/RnDMetrics/calculations/MANIFEST.json
```

**Raw Git Artifacts:**
```
https://vionascu.github.io/RnDMetrics/git_artifacts/
```

---

## 🎯 Best Practices

1. **Commit changes regularly**
   - Triggers pipeline automatically
   - Generates fresh metrics

2. **Monitor workflow runs**
   - Check Actions tab weekly
   - Review any failures

3. **Update ReposInput.md**
   - Add/remove repositories
   - Pipeline auto-adjusts

4. **Check GitHub Pages settings**
   - Verify "Deploy from a branch" is enabled
   - Confirm correct branch selected

5. **Review deployed dashboard**
   - Test all metric cards
   - Verify data accuracy
   - Check links work

---

## 📚 Related Files

- `.github/workflows/dora-pipeline.yml` - This workflow
- `ReposInput.md` - Repository configuration
- `src/collection/collect_git.py` - Git collection script
- `src/calculations/calculate.py` - Metrics calculator
- `src/validation/validate.py` - Data validator
- `public/index.html` - Dashboard template
- `public/report.js` - Dashboard logic

---

## ✅ Summary

The DORA Pipeline workflow is a **production-ready CI/CD system** that:

✓ Automatically collects metrics from GitHub
✓ Calculates DORA performance indicators
✓ Validates data quality
✓ Generates professional dashboard
✓ Deploys to GitHub Pages
✓ Runs on schedule or on-demand

**Total execution time:** ~10-15 minutes
**Failure notifications:** GitHub Actions email alerts
**Manual runs:** Available in Actions tab

---

**Questions or issues?** Check `REPORT_ACCESS.md` for dashboard access options.
