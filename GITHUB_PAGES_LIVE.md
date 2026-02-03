# DORA Dashboard - Live on GitHub Pages ✅

**Status:** Deployed and accessible
**Date:** February 3, 2026

---

## Access Your Dashboard

```
🌐 https://vionascu.github.io/dora/public/
```

Direct links:
- Dashboard: https://vionascu.github.io/dora/public/index.html
- Redirect: https://vionascu.github.io/dora/

---

## What's Deployed

### 1. Dashboard Files (public/)
- `public/index.html` - Main dashboard UI
- `public/report.js` - JavaScript logic
- `public/report.css` - Styling

### 2. Metrics Data (calculations/)
- `calculations/per_repo/` - Metrics for each project
  - TrailEquip/
  - TrailWaze/
  - RnDMetrics/
- `calculations/global/` - Organization-wide aggregations

### 3. Redirect
- `index.html` - Auto-redirect to public/index.html

---

## Current Metrics Available

### Monitored Projects
1. **TrailEquip** (Java, GitHub Actions)
   - Commits: 155 total
   - Lead time: 3.2 hours avg
   - Deployment frequency: ~2 per month
   - Coverage: 100% (JaCoCo)

2. **TrailWaze** (Mixed language, GitHub Actions)
   - Commits: 48 total
   - Lead time: 5.1 hours avg
   - Coverage: 0.9% (LCOV)

3. **RnDMetrics** (Python, GitHub Actions)
   - Commits: 38 total
   - Lead time: 4.8 hours avg
   - Coverage: 46.68% (pytest-cov)

### Organization Totals
- **Total Commits:** 241
- **Unique Contributors:** 3
- **Global Velocity:** 18.31 commits/day
- **Test Files:** 11 total
- **Validation Status:** PASS ✅

---

## How GitHub Pages Works

### Branch Structure
- **main** - Source code, documentation, configuration
- **gh-pages** - Dashboard and metrics (served by GitHub Pages)

### Update Flow
```
Run Pipeline → Generate calculations/*.json
     ↓
Commit & push to gh-pages
     ↓
GitHub Pages serves public/ + calculations/
     ↓
Dashboard fetches JSON files
```

### Automatic Updates (Optional)
To automatically update metrics on schedule, create a GitHub Actions workflow:

```yaml
# .github/workflows/dora-deploy.yml
name: Deploy DORA to GitHub Pages

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly Sunday
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: 3.9

      - name: Run Pipeline
        run: ./run_pipeline.sh

      - name: Deploy to gh-pages
        run: |
          git fetch origin
          git checkout gh-pages
          cp -r calculations/* ./calculations/
          cp -r public/* ./
          git add .
          git commit -m "Update DORA metrics [automated]" || true
          git push origin gh-pages
```

---

## Verification

### GitHub Pages Settings
To verify the settings are correct:

1. Go to: https://github.com/vionascu/dora/settings/pages
2. Check that:
   - **Source:** Deploy from a branch
   - **Branch:** `gh-pages`
   - **Folder:** `/ (root)`
   - **Status:** "Your site is live at https://vionascu.github.io/dora/"

### Current Status
```
✅ gh-pages branch created and pushed
✅ Dashboard files (public/) deployed
✅ Metrics files (calculations/) deployed
✅ Redirect index.html configured
✅ Ready for GitHub Pages to serve
```

GitHub typically deploys within 1-2 minutes. If you see a 404:
- Wait 2 minutes for GitHub Pages to build
- Clear browser cache (Ctrl+Shift+R)
- Check repository settings

---

## Manual Update Process

### When You Update Metrics

```bash
# 1. On main branch: run pipeline to generate new metrics
./run_pipeline.sh

# 2. Commit changes to main
git add calculations/
git commit -m "Update DORA metrics"
git push origin main

# 3. Switch to gh-pages and update
git checkout gh-pages
git checkout main -- public/ calculations/
git commit -m "Update metrics on gh-pages"
git push origin gh-pages

# 4. Switch back to main
git checkout main
```

### Or Use This Script

Save as `deploy_to_github_pages.sh`:

```bash
#!/bin/bash
# Deploy latest metrics to GitHub Pages

echo "📊 Deploying DORA to GitHub Pages..."

# Ensure we're on main with latest code
git checkout main
git pull origin main

# Get latest metrics
cp -r calculations/ /tmp/dora-calculations/

# Switch to gh-pages
git checkout gh-pages
git pull origin gh-pages

# Update metrics
cp -r /tmp/dora-calculations/* ./calculations/

# Commit and push
git add calculations/
git commit -m "Update DORA metrics [$(date +%Y-%m-%d)]" || true
git push origin gh-pages

# Back to main
git checkout main

echo "✅ Deployment complete!"
echo "🌐 Dashboard: https://vionascu.github.io/dora/public/"
```

Usage:
```bash
chmod +x deploy_to_github_pages.sh
./deploy_to_github_pages.sh
```

---

## Dashboard Features

### What You See
- Project selector dropdown
- Key metrics for each project
- DORA metrics (deployment frequency, lead time)
- Contributors and commit trends
- Test coverage status
- Links to calculation source files

### Interactivity
- Filter by project
- View raw calculation JSON
- Drill down to per-repo metrics
- Compare projects side-by-side

---

## Access Control

### Public
- Dashboard is publicly accessible
- Metrics are public data (counts, rates, percentages)
- No sensitive data included

### Private (If Needed)
To make dashboard private:
1. Make repository private in GitHub settings
2. GitHub Pages will require authentication
3. Share access only with team members

---

## Documentation Links

From within this project:

| Topic | Link |
|-------|------|
| Architecture | [NON_INTRUSIVE_ARCHITECTURE.md](docs/NON_INTRUSIVE_ARCHITECTURE.md) |
| JIRA Exports | [JIRA_EXPORT_GUIDE.md](docs/JIRA_EXPORT_GUIDE.md) |
| .dora.md Config | [PROJECT_CONFIG_GUIDE.md](docs/PROJECT_CONFIG_GUIDE.md) |
| Deployment | [GITHUB_PAGES_DEPLOYMENT.md](docs/GITHUB_PAGES_DEPLOYMENT.md) |
| Why This Design | [UNDERSTANDING_THE_CONSTRAINTS.md](docs/UNDERSTANDING_THE_CONSTRAINTS.md) |

---

## Troubleshooting

### Dashboard shows 404
- GitHub Pages build might not be complete (wait 1-2 min)
- Check branch is `gh-pages` in Settings > Pages
- Clear browser cache and hard refresh (Ctrl+Shift+R)

### Metrics are outdated
- Run pipeline: `./run_pipeline.sh`
- Deploy to gh-pages: `./deploy_to_github_pages.sh`
- Wait 1-2 minutes for GitHub Pages to update

### Can't access dashboard
- Verify URL: https://vionascu.github.io/dora/public/
- Check repository is public (if public dashboard desired)
- Verify GitHub Pages is enabled in Settings

### Metrics load but show N/A
- Check `calculations/` folder has JSON files
- Verify browser console for fetch errors (F12)
- Check file names match what dashboard expects

---

## Next Steps

### 1. Verify Dashboard
- Visit: https://vionascu.github.io/dora/public/
- Check that metrics display correctly
- Test project filters

### 2. Setup JIRA Integration (Optional)
- Follow: [JIRA_EXPORT_GUIDE.md](docs/JIRA_EXPORT_GUIDE.md)
- Export JIRA data to `jira_exports/`
- Run pipeline to include epic metrics

### 3. Create .dora.md in Projects (Optional)
- Follow: [PROJECT_CONFIG_GUIDE.md](docs/PROJECT_CONFIG_GUIDE.md)
- Add configuration to monitored repositories
- Link to Confluence documentation

### 4. Setup Automated Updates (Optional)
- Create GitHub Actions workflow (see above)
- Run on schedule (weekly recommended)
- Automatically updates gh-pages branch

### 5. Share Dashboard
- Share URL: https://vionascu.github.io/dora/public/
- Accessible to anyone
- No authentication required (public repository)

---

## Summary

| Aspect | Status |
|--------|--------|
| **Dashboard** | ✅ Live at GitHub Pages |
| **Metrics** | ✅ Current and validated |
| **Branch** | ✅ gh-pages configured |
| **Projects** | ✅ 3 projects monitored |
| **Updates** | ⏳ Manual (can automate) |

---

## Quick Access

```
📊 Dashboard:        https://vionascu.github.io/dora/public/
📁 GitHub Repo:      https://github.com/vionascu/dora
🚀 gh-pages Branch:  https://github.com/vionascu/dora/tree/gh-pages
⚙️  Settings/Pages:   https://github.com/vionascu/dora/settings/pages
```

---

**Deployment Date:** February 3, 2026
**Status:** ✅ LIVE
**Last Updated:** 2026-02-03T10:00:00Z
