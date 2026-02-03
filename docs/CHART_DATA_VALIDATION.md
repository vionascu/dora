# Chart Data Validation & Sources

**Date:** February 3, 2026
**Status:** All charts use REAL DATA ONLY - No mock or invented data
**Purpose:** Document data sources, validation, and handling for dashboard charts

---

## Overview

All charts on the DORA dashboard display **validated, real data** from the calculations folder. This document explains:
- Where each chart gets its data
- How data is validated
- What happens if data is unavailable
- How to verify data authenticity

---

## Chart Data Sources

### 📈 Velocity Trend (Line Chart)

**Data Source:**
```
calculations/global/velocity.json
```

**What It Shows:**
Weekly commit velocity over time

**Real Data Loaded:**
- `weekly_data` object containing weeks and commit counts
- Time range from calculations
- Calculated from actual git commits

**Data Validation:**
1. ✅ Check that `weekly_data` exists
2. ✅ Verify it contains week identifiers and numeric values
3. ✅ Validate all numbers are positive integers
4. ✅ Confirm time_range is present

**Example Real Data:**
```json
{
  "metric_id": "global.velocity",
  "weekly_data": {
    "2026-W03": 1,
    "2026-W04": 55
  },
  "value": 18.31,
  "unit": "commits/day",
  "method": "Average per-repo avg_commits_per_day",
  "calculated_at": "2026-02-03T10:04:06.814475"
}
```

**If Data Unavailable:**
Display: `📊 N/A - Velocity data not available`

Source shown: `calculations/global/velocity.json`

---

### 🎯 Test Coverage (Donut Chart)

**Data Source:**
```
calculations/global/commits.json
```

**What It Shows:**
Percentage of code that is tested vs untested

**Real Data Loaded:**
- `coverage_percentage` field if available
- Calculated from test coverage tools (pytest-cov, lcov, jacoco, etc.)

**Data Validation:**
1. ✅ Check that `coverage_percentage` exists and is numeric
2. ✅ Verify value is between 0 and 100
3. ✅ Validate source tool is identified

**Example Real Data:**
```json
{
  "metric_id": "global.commits",
  "coverage_percentage": 65,
  "coverage_tool": "pytest-cov",
  "tested_lines": 6500,
  "total_lines": 10000
}
```

**If Data Unavailable:**
Display: `🎯 N/A - Test coverage data not available (requires local test run)`

Source shown: `calculations/global/commits.json`

**Why Might It Show N/A?**
- ⚠️ Test coverage tool not configured
- ⚠️ Local test suite not run
- ⚠️ CI/CD doesn't have coverage reporting
- ⚠️ Coverage data not committed to repository

**To Fix:**
1. Configure test coverage tool (pytest-cov, lcov, jacoco)
2. Run tests locally: `./run_pipeline.sh`
3. Generate coverage report
4. Coverage data will appear in next dashboard update

---

### 👥 Contributors (Bar Chart)

**Data Source:**
```
calculations/global/commits.json
```

**What It Shows:**
Top contributors and their commit counts

**Real Data Loaded:**
- `contributors_by_commits` array
- Each contributor: name, commits, percentage
- Extracted from git history

**Data Validation:**
1. ✅ Check that `contributors_by_commits` array exists
2. ✅ Verify each entry has `name` and `commits` fields
3. ✅ Validate `commits` values are positive integers
4. ✅ Confirm totals add up correctly

**Example Real Data:**
```json
{
  "metric_id": "global.commits",
  "contributors_by_commits": [
    {
      "name": "Alice Smith",
      "commits": 156,
      "percentage": 35.2
    },
    {
      "name": "Bob Johnson",
      "commits": 134,
      "percentage": 30.2
    },
    {
      "name": "Carol White",
      "commits": 98,
      "percentage": 22.1
    }
  ]
}
```

**If Data Unavailable:**
Display: `👥 N/A - Contributors breakdown not available`

Source shown: `calculations/global/commits.json`

**Note:** Top 10 contributors displayed if more than 10 contributors exist

---

## Data Flow

### How Real Data Gets to Charts

```
┌─────────────────────────────────────────────────────┐
│ 1. Git Repository                                   │
│    (commits, authors, history)                      │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│ 2. GitHub Actions - Data Collection                 │
│    - collect_git.py (extracts git data)             │
│    - calculate.py (computes metrics)                │
│    - calculate_test_metrics.py (test data)          │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│ 3. calculations/ Folder (Raw Metrics)               │
│    ├─ global/velocity.json                          │
│    ├─ global/commits.json                           │
│    ├─ global/contributors.json                      │
│    └─ per_repo/[repo]/...                           │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│ 4. GitHub Pages - Dashboard Deployment              │
│    (automatic deployment via workflow)              │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│ 5. Browser - Dashboard Charts                       │
│    📈 Velocity Trend                                │
│    🎯 Test Coverage                                 │
│    👥 Contributors                                  │
└─────────────────────────────────────────────────────┘
```

---

## Validation Process

### Pre-Render Validation

Before rendering each chart, the dashboard performs these checks:

**Step 1: Load Data**
```javascript
const velocityData = await fetch('calculations/global/velocity.json');
```

**Step 2: Validate Structure**
```javascript
if (!velocityData.weekly_data) {
  // Data missing - show N/A
}
```

**Step 3: Validate Content**
```javascript
const weeklyData = velocityData.weekly_data;
const isValid = Object.values(weeklyData).every(v => typeof v === 'number' && v >= 0);
if (!isValid) {
  // Invalid data - show N/A
}
```

**Step 4: Render or Fall Back**
```javascript
if (isValid) {
  renderChart(validData);  // ✅ Real data
} else {
  showNA();  // N/A message
}
```

---

## Console Logging for Verification

Open browser console (F12) to see data loading details:

### Success Messages
```
✅ Velocity Chart - Real data loaded: { weeks: 8, dataPoints: [1, 55, ...] }
✅ Coverage Chart - Real data loaded: { tested: 65%, untested: 35% }
✅ Contributors Chart - Real data loaded: { contributors: 3, totalCommits: 288 }
```

### Warning Messages
```
⚠️ Velocity data not available: Failed to load calculations/global/velocity.json
⚠️ Coverage data not available: No coverage_percentage in commits data
⚠️ Contributors data not available: No contributors_by_commits array
```

---

## Data Source Attribution

Each chart displays its data source:

```
📊 Data: Data from 8 weeks | Source: calculations/global/velocity.json
📊 Data: 65% tested | Source: calculations/global/commits.json
📊 Data: Top 3 contributors | Source: calculations/global/commits.json
```

---

## Common "N/A" Scenarios

### Scenario 1: No Velocity Data
**Why:** Repository has no commits in tracked period
**Fix:** Push commits to repository
**Time to Fix:** Immediate (after next build)

### Scenario 2: No Coverage Data
**Why:** Test coverage tool not configured
**Fix:**
1. Install test coverage tool (pytest-cov, lcov, jacoco)
2. Run tests: `./run_pipeline.sh`
3. Generate coverage reports
**Time to Fix:** 24 hours (next scheduled build)

### Scenario 3: No Contributor Data
**Why:** Repository is private or no git history
**Fix:** Ensure repository is added to DORA config
**Time to Fix:** Next build after configuration

---

## Data Freshness

### Update Schedule

**Automatic (Every 24 hours):**
- 2:00 AM UTC - Daily scheduled workflow
- Collects latest git data
- Updates all calculations
- Refreshes dashboard

**Manual Trigger:**
```bash
# Force immediate update
gh workflow run dora-pipeline.yml -r main
```

**Last Updated:**
Dashboard shows "Last Updated: [timestamp]" in header

---

## Accessing Raw Data

### View Calculations
```
https://github.com/vionascu/dora/tree/main/calculations
```

### Download Specific Metrics
```
calculations/global/velocity.json
calculations/global/commits.json
calculations/global/contributors.json
```

### Per-Repository Data
```
calculations/per_repo/[repo-name]/velocity_trend.json
calculations/per_repo/[repo-name]/contributors.json
```

---

## Data Validation Checklist

Use this to verify dashboard data integrity:

- [ ] All charts load without errors
- [ ] Console shows ✅ success messages
- [ ] No ⚠️ warning messages in console
- [ ] Data source paths shown under each chart
- [ ] Numbers are reasonable for your team
- [ ] Timestamp shows recent update
- [ ] All expected repositories visible
- [ ] No "N/A" for available metrics

---

## No Mock Data Policy

**IMPORTANT:** The dashboard has a strict "no mock data" policy:

✅ **ALLOWED:**
- Real data from calculations/
- Validated numeric values
- N/A display when data missing
- Historical data from git
- Calculated metrics

❌ **NOT ALLOWED:**
- Random generated numbers
- Placeholder/sample data
- Invented contributor names
- Estimated or approximated values
- Hardcoded test data

---

## Troubleshooting

### Chart Shows "N/A"

1. Check browser console (F12) for error messages
2. Visit `calculations/[source-file]` to see if data exists
3. If file doesn't exist, run: `gh workflow run dora-pipeline.yml`
4. Wait 5 minutes for workflow to complete
5. Refresh dashboard

### Wrong Numbers in Chart

1. Verify data in raw JSON file
2. Check calculation method in metric metadata
3. Ensure git history is complete (fetch all branches)
4. Run local verification: `python src/validate.py`

### Chart Doesn't Render

1. Check browser console for JavaScript errors
2. Verify Chart.js library loaded (CDN accessible)
3. Clear browser cache: Ctrl+Shift+R
4. Try different browser

---

## Summary

All charts on the DORA dashboard:

✅ Display **REAL data only** from calculations/
✅ Validate data before rendering
✅ Show **N/A** if data unavailable
✅ Display data sources for transparency
✅ Use no mock or invented data
✅ Trace back to source repositories
✅ Update automatically every 24 hours
✅ Can be manually triggered for fresh data

**No guessing. No invented data. Only facts.**

---

**Last Updated:** February 3, 2026
**Data Policy:** Real Data Only - Validated Before Display
