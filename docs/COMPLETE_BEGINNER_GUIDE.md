# DORA: Complete Beginner's Guide

**Welcome to DORA!** This is your comprehensive guide to understanding, setting up, and using the DORA Metrics Dashboard system.

---

## Table of Contents

1. [What is DORA?](#what-is-dora)
2. [Core Concepts](#core-concepts)
3. [How It Works: The Big Picture](#how-it-works-the-big-picture)
4. [Architecture Overview](#architecture-overview)
5. [Getting Started (Quick Start)](#getting-started-quick-start)
6. [Detailed Setup Guide](#detailed-setup-guide)
7. [Understanding the System](#understanding-the-system)
8. [How to Use the Dashboard](#how-to-use-the-dashboard)
9. [Adding New Projects](#adding-new-projects)
10. [Troubleshooting](#troubleshooting)
11. [DoraReplicatePROMPT](#dorareplicate-prompt)

---

## What is DORA?

**DORA** = **D**evelopment **O**perations **R**esearch and **A**ssessments

DORA is a professional metrics system that tracks the health and productivity of software development teams. It measures:
- **How fast** teams deploy code
- **How efficiently** teams develop features
- **How stable** the deployed code is
- **How well** teams recover from issues

**Key Philosophy:** DORA collects metrics *without getting in the way*. It never modifies your repositories, never requires API keys, and works completely offline.

### What Makes DORA Special?

| Feature | Why It Matters |
|---------|----------------|
| **Non-Intrusive** | Read-only access, no modifications, no authentication required |
| **Evidence-Based** | Metrics come from real git history, not guesses or approximations |
| **Transparent** | Every number is traceable to its source data |
| **Professional** | Calm, honest metrics—no hype or false precision |
| **Auditable** | All calculations are reproducible and verifiable |
| **Shareable** | Runs on GitHub Pages, easy to share with teams |

---

## Core Concepts

Before diving in, understand these key ideas:

### 1. **Non-Intrusive Collection**
DORA analyzes your code without touching it:
- ✅ Clones your git repositories (read-only)
- ✅ Reads your JIRA exports (you provide them)
- ✅ Reads documentation you've created (`.dora.md` files)
- ❌ Never modifies repositories
- ❌ Never stores API keys
- ❌ Never requires write permissions

### 2. **The Three Data Sources**
DORA gets data from three independent places:

```
📦 Git Repositories   📊 JIRA Exports    📝 Project Docs
        ↓                    ↓                    ↓
    (Source Code)     (Issue Tracking)    (Configuration)
```

### 3. **Artifacts vs. Calculations**
- **Artifacts** = Raw data collected from sources
- **Calculations** = Processed metrics computed from artifacts
- **Dashboard** = Visual display of calculations

Example:
```
Git repository
    ↓
collect_git.py (extracts commits, tags, authors)
    ↓
git_artifacts/my-repo/commits.json (raw data)
    ↓
calculate.py (computes metrics)
    ↓
calculations/per_repo/my-repo/dora_frequency.json (processed metric)
    ↓
public/index.html (displays as chart)
```

### 4. **What Gets Measured?**
- **Deployment Frequency**: How often code is deployed
- **Lead Time**: How long from code commit to deployment
- **Change Failure Rate**: How often deployments break things
- **Time to Recovery**: How fast issues get fixed

---

## How It Works: The Big Picture

### The DORA Pipeline (5 Layers)

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: INPUT                                             │
│  ├─ ReposInput.md (defines which repos to analyze)          │
│  └─ repos.yaml (repository configuration)                   │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: COLLECTION (Extract Raw Data)                     │
│  ├─ collect_git.py → git_artifacts/                         │
│  ├─ collect_ci.py → ci_artifacts/                           │
│  └─ scan_github_artifacts.py → test_artifacts/              │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: CALCULATION (Process Data)                        │
│  ├─ calculate.py → calculations/per_repo/[repo]/            │
│  ├─ calculate_test_metrics.py                               │
│  └─ Merge all sources into unified metrics                  │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 4: VALIDATION (Quality Gates)                        │
│  ├─ validate.py                                             │
│  ├─ Check for approximations                                │
│  ├─ Check value ranges                                      │
│  └─ Verify all inputs exist                                 │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 5: PRESENTATION (Display Results)                    │
│  ├─ public/index.html (dashboard)                           │
│  └─ Served on GitHub Pages (static JSON + HTML)             │
└─────────────────────────────────────────────────────────────┘
```

### Real Example: Calculating Deployment Frequency

```
Git repository has tags: v1.0.0, v1.1.0, v1.2.0, v2.0.0, ...
                         (15 tags over 12 months)
                              ↓
                    collect_git.py extracts tags
                              ↓
                  git_artifacts/tags.json created
                              ↓
            calculate.py reads tags.json
                              ↓
    Computes: 15 tags ÷ 12 months = 1.25 deployments/month
                              ↓
   calculations/per_repo/my-repo/dora_frequency.json created
                              ↓
              Dashboard displays: "1.25 deployments/month"
```

---

## Architecture Overview

### Folder Structure

```
DORA/
│
├── 📄 ReposInput.md              ← Define which repos to analyze
├── 📄 repos.yaml                 ← Repository configuration
├── 📄 package.json               ← Node.js dependencies (for dashboard build)
├── 📄 requirements.txt            ← Python dependencies
│
├── 📂 src/                        ← Python source code
│   ├── collection/               ← Data extraction layer
│   │   ├── collect_git.py        ← Clone repos, extract commits
│   │   ├── collect_ci.py         ← Extract CI/build data
│   │   ├── scan_github_artifacts.py ← Find test results
│   │   └── ... other collectors
│   │
│   ├── calculations/             ← Metrics computation layer
│   │   ├── calculate.py          ← Main metrics engine
│   │   ├── calculate_test_metrics.py
│   │   └── calculate_evolution_metrics.py
│   │
│   ├── validation/               ← Quality assurance layer
│   │   └── validate.py           ← Check data integrity
│   │
│   └── config/                   ← Configuration parsing
│       └── config_parser.py
│
├── 📂 git_artifacts/             ← LAYER 2: Raw git data
│   ├── project-1/
│   │   ├── clone/                ← Cloned repository
│   │   ├── commits.json          ← Extracted commits
│   │   ├── authors.json          ← Unique authors
│   │   └── timeline.json         ← Commit timeline
│   └── project-2/
│       └── ...
│
├── 📂 ci_artifacts/              ← LAYER 2: Raw CI/build data
│   ├── project-1/
│   │   ├── test_results.json
│   │   └── coverage_reports/
│   └── ...
│
├── 📂 calculations/              ← LAYER 3: Processed metrics
│   ├── MANIFEST.json             ← Index of all calculations
│   │
│   ├── global/                   ← Organization-wide metrics
│   │   ├── summary.json
│   │   ├── commits.json
│   │   ├── contributors.json
│   │   └── tests.json
│   │
│   └── per_repo/                 ← Per-project metrics
│       ├── project-1/
│       │   ├── commits.json
│       │   ├── contributors.json
│       │   ├── coverage.json
│       │   ├── dora_frequency.json
│       │   ├── lead_time.json
│       │   ├── tests.json
│       │   └── velocity.json
│       └── project-2/
│           └── ...
│
├── 📂 public/                    ← LAYER 5: Dashboard UI
│   ├── index.html                ← Main dashboard page
│   ├── report.js                 ← Dashboard logic
│   └── report.css                ← Dashboard styling
│
├── 📂 docs/                      ← This documentation
│   ├── COMPLETE_BEGINNER_GUIDE.md (you are here)
│   ├── NON_INTRUSIVE_ARCHITECTURE.md
│   ├── JIRA_EXPORT_GUIDE.md
│   └── ... other guides
│
├── 🔧 run_pipeline.sh            ← Main orchestration script
└── 📄 README.md                  ← Quick overview

```

### How Each Component Works

| Component | Purpose | Input | Output |
|-----------|---------|-------|--------|
| `collect_git.py` | Extract git data | Repository URL | `git_artifacts/` |
| `collect_ci.py` | Extract CI data | CI system logs | `ci_artifacts/` |
| `calculate.py` | Compute metrics | `*_artifacts/` | `calculations/` |
| `validate.py` | Check quality | `calculations/` | Pass/Fail status |
| `public/index.html` | Display dashboard | `calculations/` | Visual charts |

---

## Getting Started (Quick Start)

### Prerequisites

You need:
- Python 3.8 or higher
- Git installed
- A web browser
- No API keys (seriously, zero!)

Check if you have them:
```bash
python3 --version      # Should be 3.8+
git --version          # Should be 2.0+
```

### Installation (First Time Only)

1. **Clone this repository:**
```bash
git clone https://github.com/your-org/DORA.git
cd DORA
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

The `requirements.txt` only has PyYAML (that's it!). DORA uses only standard Python libraries—no bloated dependencies.

3. **Verify Python is configured:**
```bash
python3 -c "import yaml, json, subprocess; print('✓ All dependencies OK')"
```

### Running the Full Pipeline

Execute everything in one command:

```bash
./run_pipeline.sh
```

This will:
1. ✅ Parse configuration
2. ✅ Clone repositories (read-only)
3. ✅ Extract metrics
4. ✅ Calculate DORA metrics
5. ✅ Run quality checks
6. ✅ Report results

Expected output:
```
=== DORA Pipeline Starting ===
[Collection] Cloning repositories...
[Collection] Extracting commits...
[Calculation] Computing metrics...
[Validation] Quality gates...
=== DORA Pipeline Complete ===
✓ All checks passed
```

### View the Dashboard

After running the pipeline:

**Option A: Open in browser**
```bash
open public/index.html
```

**Option B: Serve over HTTP**
```bash
python3 -m http.server 8000
# Then visit: http://localhost:8000/public/
```

**Option C: Deploy to GitHub Pages**
```bash
git add calculations/ public/
git commit -m "Update DORA metrics"
git push origin main
# Enable GitHub Pages in repository settings
# Visit: https://your-username.github.io/DORA/public/
```

---

## Detailed Setup Guide

### Step 1: Define Repositories to Analyze

Edit `ReposInput.md` to list which repositories to analyze:

```markdown
# Repositories to Analyze

## Project 1: Auth Service
- **Repository:** https://github.com/myorg/auth-service.git
- **Branch:** main
- **Language:** Python
- **CI System:** GitHub Actions

## Project 2: Web Dashboard
- **Repository:** https://github.com/myorg/web-dashboard.git
- **Branch:** main
- **Language:** JavaScript/React
- **CI System:** GitHub Actions
```

### Step 2: Configure Repository Settings

Create or edit `repos.yaml`:

```yaml
repositories:
  auth-service:
    repo: https://github.com/myorg/auth-service.git
    branch: main
    language: python
    ci_system: github-actions
    coverage_tools: [pytest-cov]
    artifact_patterns:
      tests:
        local_patterns:
          - file: '**/test_*.py'
            pattern: "def test_"
      epics:
        local_patterns:
          - file: '**/docs/**/*.md'
            regex: Epic\s+(\d+):\s*(.+)

  web-dashboard:
    repo: https://github.com/myorg/web-dashboard.git
    branch: main
    language: javascript
    ci_system: github-actions
    coverage_tools: [nyc]
```

### Step 3: Add JIRA Export (Optional but Recommended)

DORA tracks features and epics from JIRA.

**Export from JIRA:**
1. Go to JIRA
2. Click "Tools" → "Search for Issues"
3. Create filter for your project
4. Click "..." → "Export as CSV"
5. Save to `jira_exports/auth-service.csv`

**CSV Format:**
```csv
Epic ID,Epic Name,Type,Status,Story Count
EPIC-100,User Authentication,Epic,Done,12
EPIC-101,OAuth2 Integration,Epic,In Progress,8
STORY-1,Login Form UI,Story,Done,0
STORY-2,Password Reset,Story,In Progress,0
```

### Step 4: Create .dora.md in Each Repository

In each repository, create `.dora.md` in the root directory:

```markdown
# DORA Project Configuration

## Project Information
- **Name:** Auth Service
- **Repository:** https://github.com/myorg/auth-service
- **Team:** Backend Team
- **Owner:** john.doe@company.com

## JIRA Integration
- **Project Key:** AUTH
- **Export File:** jira_exports/auth-service.csv
- **Epics:** EPIC-100, EPIC-101, EPIC-102

## Documentation Links
- **Architecture:** https://confluence.company.com/display/AUTH/Architecture
- **Deployment Guide:** https://confluence.company.com/display/AUTH/Deployment
- **Runbook:** https://confluence.company.com/display/AUTH/Runbook

## Metrics
- **Language:** Python
- **CI System:** GitHub Actions
- **Coverage Tool:** pytest-cov
```

### Step 5: Run the Pipeline

```bash
./run_pipeline.sh
```

### Step 6: View Results

```bash
open public/index.html
```

---

## Understanding the System

### What Gets Collected?

#### Git Data
```json
{
  "repository": "auth-service",
  "total_commits": 1250,
  "contributors": 15,
  "commit_frequency": 4.8,  // commits per day
  "date_range": {
    "first_commit": "2020-01-15",
    "last_commit": "2024-02-03"
  }
}
```

#### JIRA Data
```json
{
  "repository": "auth-service",
  "epics": [
    {
      "id": "EPIC-100",
      "name": "User Authentication",
      "status": "Done",
      "stories_total": 12,
      "stories_done": 12
    }
  ]
}
```

#### Test Metrics
```json
{
  "repository": "auth-service",
  "tests_total": 450,
  "tests_passed": 440,
  "tests_failed": 10,
  "coverage_percent": 82.5,
  "last_run": "2024-02-03T14:23:00Z"
}
```

### What Gets Calculated?

#### Deployment Frequency
"How often does code get deployed?"

- Calculated from: Git tags matching version pattern (`v*.*.*)
- Formula: `total_tags / months`
- Example: `15 tags / 12 months = 1.25 deployments per month`

#### Lead Time
"How long from commit to deployment?"

- Calculated from: Average time between consecutive commits
- Formula: `total_time_between_commits / number_of_commits`
- Example: `6.2 hours average between commits`

#### Change Failure Rate
"What percent of deployments cause issues?"

- Calculated from: Test failure data + incident reports
- Formula: `failed_deployments / total_deployments`
- Example: `5 failures / 100 deployments = 5% failure rate`

#### Mean Time to Recovery
"How long to fix an issue?"

- Calculated from: Incident data + resolution times
- Formula: `total_resolution_time / number_of_incidents`
- Example: `2.5 hours average resolution time`

### Why These Metrics?

These metrics come from **Google's DORA Research**, which studied thousands of software teams. Teams with high scores on these four metrics are:
- 60% faster at deploying code
- 8x more likely to meet business targets
- 38% more effective at managing unplanned work

Learn more: https://dora.dev

---

## How to Use the Dashboard

### Dashboard Sections

#### 1. Key Findings (Top)
Shows:
- Total commits across all projects
- Number of repositories analyzed
- Active contributors
- Current velocity (commits per day)

#### 2. Projects Overview
Shows:
- List of all analyzed projects
- Commits per project
- Contributors per project
- Last update date

#### 3. Metrics Charts
Shows:
- **Velocity Trend:** Commits over time
- **Test Coverage:** Percentage covered by tests
- **Contributor Growth:** How team is growing
- **Deployment Frequency:** How often code ships

#### 4. Data Quality Section
Shows:
- What data was successfully collected
- Any warnings or issues
- Validation status

#### 5. Raw Data Access
Shows:
- Links to raw JSON files
- Allows power users to explore details
- Full audit trail

### Reading the Dashboard

**Green indicators** = Good (metrics are passing)
**Yellow indicators** = Warning (may need attention)
**Red indicators** = Alert (investigate issue)
**N/A** = Data not available (not an error)

---

## Adding New Projects

### Scenario: You want to add a new project to DORA

Follow these steps:

#### Step 1: Identify the Repository
```
- URL: https://github.com/myorg/new-project.git
- Default branch: main
- Language: Python
- Has tests: Yes (pytest)
```

#### Step 2: Update ReposInput.md
```markdown
## New Project
- **Repository:** https://github.com/myorg/new-project.git
- **Branch:** main
- **Language:** Python
- **CI System:** GitHub Actions
- **Test Framework:** pytest
```

#### Step 3: Update repos.yaml
```yaml
new-project:
  repo: https://github.com/myorg/new-project.git
  branch: main
  language: python
  ci_system: github-actions
  coverage_tools: [pytest-cov]
  artifact_patterns:
    tests:
      local_patterns:
        - file: '**/test_*.py'
    epics:
      local_patterns:
        - file: '**/docs/**/*.md'
          regex: Epic\s+(\d+):\s*(.+)
```

#### Step 4: Create .dora.md in Repository
Commit this to the repository root:

```markdown
# DORA Configuration

## Project Information
- **Name:** New Project
- **Repository:** https://github.com/myorg/new-project

## JIRA Integration
- **Project Key:** NEWP
- **Export File:** jira_exports/new-project.csv

## Documentation
- **Docs:** https://confluence.company.com/display/NEWP/Home
```

#### Step 5: Export JIRA Data (If Using JIRA)
Save to `jira_exports/new-project.csv`

#### Step 6: Run Pipeline
```bash
./run_pipeline.sh
```

#### Step 7: Verify
```bash
open public/index.html
# Look for new project in the dashboard
```

---

## Troubleshooting

### Problem: Pipeline fails with "Clone failed"

**Causes:**
- Repository URL is incorrect
- Network connectivity issue
- Repository doesn't exist
- Permission denied

**Solutions:**
```bash
# Test repository URL manually
git clone --depth=1 https://github.com/myorg/project.git test_clone

# If it works, the issue is in repos.yaml
# If it fails, check:
# 1. URL is correct
# 2. Network is working
# 3. Repository is public (or you have access)
```

### Problem: "JIRA export not found"

**Causes:**
- File path wrong in `repos.yaml`
- File doesn't exist in `jira_exports/`
- Wrong filename

**Solutions:**
```bash
# Check files exist
ls -la jira_exports/

# Verify paths in repos.yaml match actual files
# Expected: jira_exports/[project-name].csv
```

### Problem: Dashboard shows "N/A" for everything

**Causes:**
- Calculations haven't been run
- Calculations failed silently
- Browser is caching old version

**Solutions:**
```bash
# Force recalculation
./run_pipeline.sh

# Clear browser cache
# Then refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)

# Check calculations folder exists
ls -la calculations/
ls -la calculations/per_repo/
ls -la calculations/global/
```

### Problem: "Validation failed: Approximations found"

**Causes:**
- A metric contains "~" or "approx"
- A value looks estimated rather than calculated

**Solutions:**
```bash
# Find the problematic file
grep -r "~\|approx" calculations/

# Fix: Remove approximations or recalculate with actual data
# DORA philosophy: N/A > false precision
```

### Problem: Tests showing 0%

**Causes:**
- Test artifact patterns don't match actual files
- Coverage tools not installed
- Wrong test framework detected

**Solutions:**
```bash
# Verify test files exist
find . -name "test_*.py"  # For Python
find . -name "*.test.js"  # For JavaScript

# Update artifact patterns in repos.yaml to match
# Ensure coverage tool is installed in CI
```

---

## DoraReplicatePROMPT

**Use this prompt to recreate the DORA application from scratch:**

---

### 🎯 DoraReplicatePROMPT: Building DORA from Zero

You are an expert software architect tasked with rebuilding the DORA metrics system from scratch. Here's what you need to build:

#### **Project Overview**
Build a **non-intrusive, evidence-based R&D metrics dashboard** that:
- Collects metrics WITHOUT modifying target repositories
- Requires NO external API keys or authentication
- Operates with READ-ONLY access
- Produces traceable, auditable metrics
- Displays results on a static web dashboard

#### **Core Architecture (5 Layers)**

**Layer 1: INPUT**
- Read configuration from `repos.yaml`
- Parse `ReposInput.md` for repository list
- Load project metadata from `.dora.md` files

**Layer 2: COLLECTION (Extract Raw Data)**
- `collect_git.py`: Clone repositories (shallow), extract commits, tags, authors, timelines
  - Use shallow clones (`--depth=1`) for efficiency
  - Extract: commit count, unique authors, deployment tags
  - Process git log with streaming (O(1) memory)
- `collect_ci.py`: Extract CI/build data from logs
- `scan_github_artifacts.py`: Find test results and coverage reports
  - Auto-detect test frameworks (Java, Python, JavaScript, Go)
  - Extract test coverage percentages
- `collect_loc.py`: Count lines of code per language
- Output: `git_artifacts/`, `ci_artifacts/`, organized by project

**Layer 3: CALCULATION (Process & Merge)**
- `calculate.py`: Main metrics engine
  - Merge git, CI, and documentation data
  - Calculate DORA metrics:
    - **Deployment Frequency**: total_tags / months
    - **Lead Time**: average time between commits
    - **Change Failure Rate**: failed_deployments / total_deployments
  - Calculate trend metrics: velocity over time, contributor growth
- `calculate_test_metrics.py`: Test-specific calculations (pass rate, coverage)
- `calculate_evolution_metrics.py`: Growth patterns, refactorization activity
- All outputs include: `metric_id`, `inputs`, `method`, `calculated_at`
- Output: `calculations/per_repo/[repo]/` and `calculations/global/`

**Layer 4: VALIDATION (Quality Gates)**
- `validate.py`: Enforce quality standards
  - ✗ Reject approximations ("~", "approx", "estimated")
  - ✗ Reject out-of-bounds values (coverage > 100%, negative commits)
  - ✗ Reject missing source inputs
  - ✓ Accept `null` with reason over invented numbers
  - Fail if ANY check fails

**Layer 5: PRESENTATION (Dashboard)**
- `public/index.html`: Static HTML dashboard
  - Reads from `calculations/` (JSON files)
  - Displays charts: velocity, coverage, contributors, frequency
  - Shows per-project and organization-wide metrics
  - Data quality indicators
  - Links to raw JSON files for audit trail
- `public/report.js`: Dashboard logic (data loading, chart rendering)
- `public/report.css`: Professional, calm styling (no hype)

#### **Key Data Structures**

**Calculation Output Format (All Files):**
```json
{
  "metric_id": "repo.dora.deployment_frequency",
  "repo": "auth-service",
  "inputs": ["git_artifacts/auth-service/tags.json"],
  "values": {
    "tags_total": 15,
    "period_months": 12,
    "frequency_per_month": 1.25,
    "frequency_per_week": 0.288
  },
  "method": "Count git tags matching v*.*.* pattern; divide by period",
  "calculated_at": "2026-02-03T10:00:00Z",
  "quality_gates": {
    "status": "PASS",
    "checks": {
      "has_inputs": true,
      "no_approximations": true,
      "values_in_range": true
    }
  }
}
```

**Repository Configuration (repos.yaml):**
```yaml
repositories:
  project-name:
    repo: https://github.com/org/project.git
    branch: main
    language: [python|javascript|go|java|mixed]
    ci_system: [github-actions|gitlab-ci|jenkins]
    coverage_tools: [pytest-cov|nyc|JaCoCo]
    artifact_patterns:
      tests:
        local_patterns:
          - file: '**/*.py'
            pattern: "def test_"
      epics:
        local_patterns:
          - file: '**/docs/**/*.md'
            regex: Epic\s+(\d+)
```

#### **Orchestration**
- `run_pipeline.sh`: Master script that runs all 5 layers in sequence
  1. Parse configuration
  2. Run collectors
  3. Run calculations
  4. Run validation (exit if fails)
  5. Report results

#### **Core Principles**

1. **Non-Intrusive**
   - No API keys stored
   - Read-only access only
   - No repository modifications
   - No external dependencies on authentication

2. **Evidence-Based**
   - Metrics from real source code
   - Traceable to raw data
   - Reproducible calculations
   - No guessing or approximations

3. **Transparent**
   - Every number links to inputs
   - Methods documented
   - All files versioned in Git
   - Full audit trail

4. **Professional**
   - Calm, honest metrics
   - No false precision
   - N/A > invented numbers
   - No hype or marketing language

5. **Auditable**
   - All calculations in JSON
   - Inputs and methods documented
   - Quality gates enforced
   - Validation step mandatory

6. **Maintainable**
   - Clear layer separation
   - Minimal dependencies
   - Standard library focused
   - Simple file-based storage

#### **Technology Stack**
- **Backend**: Python 3.8+ (minimal deps: only PyYAML)
- **Frontend**: HTML5 + JavaScript + CSS (no frameworks needed)
- **Hosting**: GitHub Pages (static JSON + HTML)
- **Storage**: Git (version control for all artifacts and calculations)
- **Data Format**: JSON (human-readable, auditable)

#### **Development Flow**
1. Create configuration files (repos.yaml, ReposInput.md)
2. Implement collectors (one per data source)
3. Implement calculation engine (merge and compute)
4. Implement validation layer (quality gates)
5. Build dashboard (read JSON, render charts)
6. Implement orchestration (pipeline.sh)
7. Deploy to GitHub Pages

#### **Success Criteria**
- ✅ All metrics traceable to source data
- ✅ No approximations in output
- ✅ All calculations documented
- ✅ Dashboard displays correct metrics
- ✅ Pipeline runs end-to-end without API keys
- ✅ Quality gates catch invalid data
- ✅ Dashboard works on GitHub Pages
- ✅ New repositories can be added easily
- ✅ All code is auditable and transparent
- ✅ No external service dependencies

---

### Using This Prompt

To rebuild DORA:
1. **Pass this prompt to an LLM or development team**
2. **Iterate on each layer** (Collection → Calculation → Validation → Presentation)
3. **Test with sample repositories** (try small public repos first)
4. **Deploy to GitHub Pages** for sharing
5. **Document configuration** so others can add projects

### Example Commands (What Your Rebuild Should Support)

```bash
# Full pipeline
./run_pipeline.sh

# Individual steps (for debugging)
python3 src/collection/collect_git.py
python3 src/calculations/calculate.py
python3 src/validation/validate.py

# View dashboard
open public/index.html

# Deploy to GitHub Pages
./deploy_to_github_pages.sh
```

---

## Summary

DORA is a sophisticated yet elegant system for understanding software development team health. It combines:
- **Non-intrusive data collection** (read-only access)
- **Rigorous calculations** (evidence-based, no guessing)
- **Professional presentation** (calm, honest metrics)
- **Complete transparency** (every number is auditable)

By following this guide, you can set up DORA, add your own projects, and start getting real insights into your development process.

**Remember:** The goal is not perfect metrics—it's honest, traceable, auditable metrics that help teams improve.

---

## Next Steps

1. **Run the Quick Start** (takes 5 minutes)
2. **Add Your First Repository** (takes 10 minutes)
3. **Export JIRA Data** (takes 15 minutes, optional)
4. **Share Dashboard** (deploy to GitHub Pages)
5. **Iterate** (add more repos, refine metrics)

Good luck! 🚀

---

**Questions or Issues?**
- Check the [Troubleshooting](#troubleshooting) section above
- Review specific guides in `/docs/` folder
- File an issue on GitHub with:
  - Your pipeline output
  - Your repos.yaml configuration
  - Error messages
