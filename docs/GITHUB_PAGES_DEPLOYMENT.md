# GitHub Pages Deployment Guide

This guide explains how to deploy DORA metrics to GitHub Pages for easy sharing and access.

---

## Overview

GitHub Pages serves static files (HTML, CSS, JavaScript, JSON) from your repository. Perfect for DORA since:

- ✓ No server to maintain
- ✓ Free hosting
- ✓ Automatic HTTPS
- ✓ Version controlled
- ✓ Shareable public URLs
- ✓ Works with JSON files

---

## Deployment Option A: gh-pages Branch (Recommended)

This approach uses a separate `gh-pages` branch to hold only the dashboard and metrics.

### Step 1: Create gh-pages Branch

```bash
# From DORA repository root
git checkout --orphan gh-pages
git rm -rf .
```

### Step 2: Add Dashboard and Metrics

```bash
# Add public/ (dashboard UI)
cp -r ../public .

# Add calculations/ (JSON metrics)
cp -r ../calculations .

# Add index.html at root (optional, redirects to public)
cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0;url=public/index.html" />
</head>
<body>
    <p>Redirecting to <a href="public/index.html">DORA Dashboard</a>...</p>
</body>
</html>
EOF
```

### Step 3: Commit and Push

```bash
git add .
git commit -m "DORA metrics dashboard - GitHub Pages deployment"
git push -u origin gh-pages
```

### Step 4: Configure GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Under "Build and deployment":
   - Source: `Deploy from a branch`
   - Branch: `gh-pages`
   - Folder: `/ (root)`
3. Click **Save**

### Step 5: Access Dashboard

Wait 1-2 minutes for GitHub to build and deploy.

Then access:
```
https://<username>.github.io/<dora-repo>/public/index.html
```

### Updating Metrics (gh-pages Approach)

```bash
# On main branch: run pipeline
./run_pipeline.sh

# Switch to gh-pages branch
git checkout gh-pages

# Pull latest calculations
git pull origin main -- calculations/
git pull origin main -- public/

# Commit changes
git commit -m "Update DORA metrics"
git push origin gh-pages
```

**Automate with GitHub Actions:**

```yaml
# .github/workflows/deploy-github-pages.yml
name: Deploy DORA to GitHub Pages

on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday
  workflow_dispatch:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: 3.9

      - name: Run DORA Pipeline
        run: ./run_pipeline.sh

      - name: Upload Artifact
        uses: actions/upload-pages-artifact@v2
        with:
          path: 'public/'

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
```

---

## Deployment Option B: /docs Folder on Main Branch

This approach keeps everything on the main branch in a `/docs` folder.

### Step 1: Create docs Structure

```bash
# From DORA repository root
mkdir -p docs/public
mkdir -p docs/calculations
cp -r public/* docs/public/
cp -r calculations/* docs/calculations/
```

### Step 2: Create docs/index.html

```bash
cat > docs/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>DORA Metrics Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <div id="app">
        <h1>DORA Metrics Dashboard</h1>
        <p>Loading dashboard...</p>
    </div>

    <script src="public/app.js"></script>
</body>
</html>
EOF
```

### Step 3: Commit and Push

```bash
git add docs/
git commit -m "Add DORA metrics to GitHub Pages"
git push origin main
```

### Step 4: Configure GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Under "Build and deployment":
   - Source: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/docs`
3. Click **Save**

### Step 5: Access Dashboard

```
https://<username>.github.io/<dora-repo>/docs/public/
```

or if you created index.html:

```
https://<username>.github.io/<dora-repo>/docs/
```

### Updating Metrics (/docs Approach)

```bash
# Run pipeline (generates new calculations/)
./run_pipeline.sh

# Copy to docs/
cp -r calculations/* docs/calculations/

# Commit and push
git add docs/
git commit -m "Update DORA metrics"
git push origin main
```

---

## Deployment Option C: GitHub Actions + Artifacts

Use GitHub's built-in artifact storage for separation.

```yaml
name: DORA CI/CD

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  collect-metrics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: 3.9

      - name: Run Pipeline
        run: ./run_pipeline.sh

      - name: Upload Metrics
        uses: actions/upload-artifact@v3
        with:
          name: dora-metrics
          path: calculations/

  deploy:
    needs: collect-metrics
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}

    steps:
      - uses: actions/checkout@v3

      - name: Download Metrics
        uses: actions/download-artifact@v3
        with:
          name: dora-metrics
          path: calculations/

      - name: Setup Pages
        uses: actions/configure-pages@v3

      - name: Upload Pages Artifact
        uses: actions/upload-pages-artifact@v2
        with:
          path: 'public/'

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
```

---

## Recommended Approach

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **gh-pages branch** | Clean separation, dedicated metrics repo | Two branches to manage | Production deployments |
| **/docs folder** | Simple, all in one branch | Less separation of concerns | Small projects, quick setup |
| **GitHub Actions** | Automated, reproducible, auditable | Most complex setup | Enterprise, scheduled updates |

**Recommendation for most teams:** Use **gh-pages branch** for production, **/docs folder** for quick start.

---

## GitHub Actions Workflow Examples

### Minimal Workflow

```yaml
name: DORA Metrics

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  metrics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: 3.9

      - name: Run Pipeline
        run: ./run_pipeline.sh

      - name: Push Updates
        run: |
          git config user.name "DORA Bot"
          git config user.email "dora@bot.local"
          git add calculations/
          git commit -m "Update DORA metrics [skip ci]" || true
          git push
```

### Production Workflow with Status Checks

```yaml
name: DORA Metrics (Production)

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly at 2 AM
  workflow_dispatch:

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: 3.9

      - name: Run Pipeline
        run: ./run_pipeline.sh
        timeout-minutes: 30

      - name: Validate Metrics
        run: python3 src/validation/validate.py

      - name: Generate Report
        run: |
          echo "## DORA Metrics Report" > metrics-report.md
          echo "Generated: $(date)" >> metrics-report.md
          cat calculations/global/summary.json >> metrics-report.md

      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: metrics-report
          path: metrics-report.md

      - name: Deploy to Pages
        if: success()
        uses: actions/upload-pages-artifact@v2
        with:
          path: 'public/'

      - name: Notify on Failure
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '❌ DORA metrics collection failed. Check workflow logs.'
            })
```

---

## Accessing Metrics via JSON

Since all metrics are JSON files, you can access them programmatically:

```javascript
// Fetch deployment frequency
fetch('https://<username>.github.io/<repo>/calculations/per_repo/<project>/dora.json')
  .then(r => r.json())
  .then(data => console.log('Deployment frequency:', data.deployment_frequency))
```

```bash
# Get metrics via curl
curl https://<username>.github.io/<repo>/calculations/global/summary.json | jq .
```

---

## Security Considerations

### Data Privacy

- ✓ All metrics are public (served on GitHub Pages)
- ✓ No sensitive data in metrics (only counts/rates)
- ✗ Don't include credentials or secrets in calculations/
- ✗ Don't expose private URLs in Confluence links

### Access Control

- GitHub Pages is public by default
- Use `repo-settings` to control branch access
- Only maintainers can push to gh-pages or main
- CI/CD bot account should have write-only access

### Audit Trail

```bash
# See all metric updates
git log --oneline calculations/

# See who made changes
git log --all -- calculations/ -p

# See when metrics changed
git log --follow --date=short --pretty=format:"%h %ad %s" -- calculations/
```

---

## Custom Domain (Optional)

If you want metrics at a custom domain:

1. Create `docs/CNAME` file:
```
metrics.company.com
```

2. Configure DNS:
```
metrics.company.com  CNAME  <username>.github.io
```

3. Commit and push:
```bash
git add docs/CNAME
git commit -m "Add custom domain"
git push
```

---

## Troubleshooting

### Issue: GitHub Pages Not Updating

```
Solution:
1. Check GitHub Actions workflow runs successfully
2. Verify branch/folder is configured in Settings > Pages
3. Check .github/workflows/*.yml for syntax errors
4. Wait 2-3 minutes after push for deployment
```

### Issue: 404 Error When Accessing Dashboard

```
Solution:
1. Verify correct URL (https://<username>.github.io/<repo>/...)
2. Check files exist in repository (public/, calculations/)
3. Verify branch/folder configuration in GitHub Pages settings
4. Check build logs in Settings > Pages
```

### Issue: Metrics Are Stale

```
Solution:
1. Check last workflow run in Actions tab
2. Verify cron schedule if using scheduled trigger
3. Manually trigger workflow: use workflow_dispatch
4. Check for errors in workflow logs
```

### Issue: JSON Files Not Loading in Dashboard

```
Solution:
1. Verify JSON files are in calculations/ folder
2. Check file permissions (should be readable)
3. Verify JSON is valid (use jq or validator)
4. Check browser console for fetch errors
5. Verify CORS headers (GitHub Pages allows same-origin)
```

---

## Performance Tips

### 1. Compress Metrics
```bash
gzip calculations/per_repo/*.json
gzip calculations/global/*.json
```

Configure GitHub Pages to serve gzipped:
```bash
# GitHub automatically serves .json.gz when .json is requested
```

### 2. Use CDN (Optional)
```
CloudFlare → GitHub Pages (free tier available)
```

### 3. Cache Dashboard
```javascript
// In public/app.js
const CACHE_DURATION = 3600; // 1 hour
const CACHE_KEY = 'dora-metrics-cache';

async function fetchMetrics() {
  const cached = localStorage.getItem(CACHE_KEY);
  const now = Date.now();

  if (cached && cached.timestamp > now - CACHE_DURATION) {
    return cached.data;
  }

  // Fetch fresh metrics...
}
```

---

## Backup & Disaster Recovery

### Backup Strategy

```bash
# Keep local backup
git fetch origin gh-pages

# Archive metrics
mkdir -p backups/dora-$(date +%Y%m%d)
cp -r calculations/ backups/dora-$(date +%Y%m%d)/

# Commit backup (optional)
git add backups/
git commit -m "Backup metrics $(date +%Y-%m-%d)"
```

### Restore from GitHub

```bash
# If you accidentally deleted gh-pages
git checkout -b gh-pages origin/gh-pages
```

---

## Summary Checklist

- [ ] Choose deployment option (gh-pages or /docs)
- [ ] Configure GitHub Pages in Settings
- [ ] Set up GitHub Actions workflow (optional but recommended)
- [ ] Test deployment with sample metrics
- [ ] Verify dashboard accessible at correct URL
- [ ] Document metrics URL in README
- [ ] Set up regular metric collection (weekly)
- [ ] Monitor workflow runs for errors
- [ ] Back up metrics regularly

---

## References

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Pages Quickstart](https://docs.github.com/en/pages/quickstart)

---

## Questions & Support

- See [NON_INTRUSIVE_ARCHITECTURE.md](./NON_INTRUSIVE_ARCHITECTURE.md) for system design
- See [README.md](../README.md) for DORA overview
- Check DORA project for example deployments
