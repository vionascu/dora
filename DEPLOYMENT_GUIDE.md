# DORA Dashboard Deployment Guide

## GitLab CI/CD Pipeline & Pages Deployment

### Pipeline Stages

The `.gitlab-ci.yml` runs three stages automatically on each push to `main`:

1. **collect** - Extracts git data and LOC metrics
   - Job: `collect_git`
   - Output: `git_artifacts/`, LOC data

2. **calculate** - Computes all metrics
   - Job: `calculate_metrics`
   - Output: `calculations/` folder with all JSON metrics

3. **deploy** - Publishes dashboard to GitLab Pages
   - Job: `pages`
   - Output: Deploys `public/` folder to GitLab Pages

### Accessing the Dashboard

#### Option 1: Temporary Artifact Preview (Current Build)
After the `calculate_metrics` job completes, you can preview the dashboard via:
```
https://viionascu.git-pages.ecd.axway.org/-/dora/-/jobs/<JOB_ID>/artifacts/public/index.html
```

**Note:** This is a temporary artifact preview. File paths use relative resolution (`./calculations/`).

#### Option 2: GitLab Pages (Permanent, After Pages Job)
Once the `pages` job completes successfully, access the permanent dashboard:
```
https://viionascu.git-pages.ecd.axway.org/dora/public/
```

**Note:** This is the recommended way to access the dashboard in production.

### Checking Pipeline Status

1. Visit: https://git.ecd.axway.org/viionascu/dora/-/pipelines
2. Look for the latest pipeline run
3. Wait for all jobs to complete (green checkmark ✓)
4. Check the `pages` job status - must be successful for Pages deployment

### Dashboard URLs Quick Reference

| Context | URL | Status |
|---------|-----|--------|
| Local Development | http://localhost:8002/public/index.html | Dev only |
| Artifact Preview | https://viionascu.git-pages.ecd.axway.org/-/dora/-/jobs/JOBID/artifacts/public/index.html | Temporary |
| **GitLab Pages** | **https://viionascu.git-pages.ecd.axway.org/dora/public/** | **Production** |

### Troubleshooting

**404 on GitLab Pages:**
- Check pipeline status at https://git.ecd.axway.org/viionascu/dora/-/pipelines
- Ensure `pages` job completed successfully
- Wait a few moments for Pages to publish

**Charts not showing data:**
- Check browser console (F12) for path errors
- For artifact preview: Paths should resolve to `./calculations/`
- For Pages: Paths should resolve to `/dora/public/calculations/`

**Run Helper Script:**
```bash
bash get_dashboard_url.sh
```

This displays the current pipeline status and dashboard URL information.

