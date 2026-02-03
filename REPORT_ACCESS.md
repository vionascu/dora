# DORA Metrics Report - Access Guide

## 📊 Live Report Access

### Option 1: Local Browser (Recommended for Development)
```bash
# From DORA project directory
cd /Users/viionascu/Projects/DORA
python3 -m http.server 8888
```
Then open: **http://localhost:8888/public/index.html**

---

### Option 2: GitHub Repository (Raw Files)
Direct links to view report files in GitHub:

- **Main Report**: https://github.com/vionascu/RnDMetrics/blob/main/public/index.html
- **Report Script**: https://github.com/vionascu/RnDMetrics/blob/main/public/report.js
- **Report Styles**: https://github.com/vionascu/RnDMetrics/blob/main/public/report.css

---

### Option 3: GitHub Pages (Production Deployment)
Once GitHub Pages is enabled in repository settings:
- **Dashboard**: https://vionascu.github.io/RnDMetrics/public/index.html

---

## 📈 Report Contents

### Key Findings (7 Cards)
- **Total Development Activity**: 228 commits across all repos
- **Organization Size**: 3 active repositories
- **Team Size**: 4 unique contributors
- **Development Velocity**: 20.27 commits/day average
- **Test Files**: 15 total test files
- **Epics Documented**: 58 epics found
- **User Stories**: 4 user stories identified

### Repository Analysis Section
Per-repository breakdown showing:
- **Commits & Contributors**
  - TrailEquip: 155 commits, 1 contributor, 38.75/day
  - TrailWaze: 17 commits, 2 contributors, 3.4/day
  - RnDMetrics: 56 commits, 1 contributor, 18.67/day

- **DORA Metrics**
  - Lead time (hours between commits)
  - Deployment frequency

- **Test Coverage**
  - Test frameworks: JUnit (Java), unittest (Python), Jest/Mocha (JS)
  - Epics & user stories per repo
  - Sample test file references

### Data Quality & Validation
All 4 quality gates passing:
- ✓ No approximations
- ✓ Required fields present
- ✓ Data bounds valid
- ✓ Traceable to source

### Data Completeness
What we have:
- Git commit history for all 3 repos
- Contributor counts
- Activity velocity metrics
- Lead time calculations
- Test files and frameworks

What requires local execution:
- Test coverage reports (jacoco, lcov, pytest-cov)
- Change failure rate (requires CI/CD tracking)
- Mean time to recovery (requires incident data)

### Technical Details
- Full data pipeline explanation
- Links to raw calculations
- Links to git and CI artifacts
- Metrics definitions

---

## 🔍 Scanned GitHub Repositories

### 1. TrailEquip
- **GitHub**: https://github.com/vionascu/TrailEquip
- **Branch**: main
- **Language**: Java
- **CI**: GitHub Actions
- **Tests**: 8 files (JUnit, Jest/Mocha)
- **Epics**: 0 found
- **User Stories**: 0 found

### 2. TrailWaze
- **GitHub**: https://github.com/vionascu/TrailWaze
- **Branch**: main
- **Language**: Mixed (React Native, JS, Python)
- **CI**: GitHub Actions
- **Tests**: 1 file (Jest/Mocha)
- **Epics**: 15 found
- **User Stories**: 1 found

### 3. RnDMetrics
- **GitHub**: https://github.com/vionascu/RnDMetrics
- **Branch**: main
- **Language**: Python
- **CI**: GitHub Actions
- **Tests**: 6 files (unittest)
- **Epics**: 43 found
- **User Stories**: 3 found

---

## 📁 Data Files Location

### Calculations (Generated Metrics)
- **Global Metrics**: `calculations/global/`
  - `commits.json` - Total commit statistics
  - `summary.json` - Repository summary
  - `tests.json` - Test file counts

- **Per-Repo Metrics**: `calculations/per_repo/{repo}/`
  - `commits.json` - Commit details
  - `contributors.json` - Contributor counts
  - `coverage.json` - Test coverage (N/A - requires local run)
  - `tests.json` - Test framework info
  - `dora_frequency.json` - Deployment frequency proxy

- **Validation Report**: `calculations/MANIFEST.json`
  - Complete validation audit
  - All metrics status
  - Data quality notes

### Raw Artifacts
- **Git Data**: `git_artifacts/{repo}/`
  - `commits.json` - All commits with metadata
  - `authors.json` - Contributor list

- **GitHub Scan**: `git_artifacts/github_scan_artifacts.json`
  - All found epics
  - All user stories
  - Test file references
  - Test framework identification

---

## 🚀 Running the Full Pipeline

```bash
cd /Users/viionascu/Projects/DORA

# Run complete pipeline
bash run_pipeline.sh

# This will:
# 1. Parse ReposInput.md
# 2. Collect git artifacts from all repos
# 3. Collect CI artifacts
# 4. Scan for epics, stories, and tests
# 5. Calculate all metrics
# 6. Validate data quality
# 7. Generate MANIFEST.json

# Then view the report
python3 -m http.server 8888
# Open http://localhost:8888/public/index.html
```

---

## 📋 Latest Update

- **Scan Date**: 2026-02-01
- **Last Pipeline Run**: All quality gates passing ✓
- **Status**: Ready for GitHub Pages deployment

---

## 🔗 Quick Links

- **Local Dashboard**: http://localhost:8888/public/index.html
- **Raw Calculations**: http://localhost:8888/calculations/
- **Git Artifacts**: http://localhost:8888/git_artifacts/
- **CI Artifacts**: http://localhost:8888/ci_artifacts/
- **Validation Manifest**: http://localhost:8888/calculations/MANIFEST.json

---

**Report Generated by DORA Metrics Pipeline**
*Evidence-backed, professionally validated, real data only*
