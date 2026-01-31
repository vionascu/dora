# DORA Metrics Dashboard

A professional, evidence-backed R&D metrics system with a strict 4-stage pipeline architecture.

**Dashboard does NOT access repositories directly. Truth lives in `calculations/`.**

## Architecture

```
INPUT → COLLECTION → CALCULATION → PRESENTATION

ReposInput.md → git_artifacts/ + ci_artifacts/ → calculations/ → public/index.html
```

### 1. INPUT Layer: `ReposInput.md`

Source of truth. Defines all repositories to analyze.

```markdown
## TrailEquip
repo: https://github.com/vionascu/TrailEquip
branch: main
language: java
ci: github-actions
coverage: jacoco

## TrailWaze
repo: https://github.com/vionascu/TrailWaze
branch: main
language: mixed
ci: github-actions
coverage: lcov

## RnDMetrics
repo: https://github.com/vionascu/RnDMetrics
branch: main
language: python
ci: github-actions
coverage: pytest-cov
```

### 2. COLLECTION Layer: Raw Artifacts

Extracts raw git and CI data.

**Inputs:**
- Git repositories (cloned and analyzed)
- CI artifacts (test results, coverage reports)

**Outputs:**
```
git_artifacts/
  <repo>/
    commits.json          # All commits with timestamps
    authors.json          # Unique contributors
    timeline.json         # Date range

ci_artifacts/
  <repo>/
    ci_info.json          # CI tool info
    [coverage files]      # jacoco.xml, lcov.info, coverage.xml
```

**Run:**
```bash
python3 src/collection/collect_git.py
python3 src/collection/collect_ci.py
```

### 3. CALCULATION Layer: Normalized Metrics

Processes raw artifacts into auditable, traceable metrics.

**Key principle:** Every metric file includes:
- `metric_id` - Unique identifier
- `inputs` - Source files used
- `value` - The actual metric
- `method` - How it was calculated
- `calculated_at` - ISO timestamp

**Outputs:**
```
calculations/
  per_repo/
    TrailEquip/
      commits.json
      contributors.json
      coverage.json
      dora_frequency.json
      lead_time.json
    [other repos...]
  global/
    commits.json         # Sum of all repos
    summary.json         # Organization overview
```

**Example calculation file:**
```json
{
  "metric_id": "repo.commits",
  "repo": "TrailEquip",
  "time_range": {
    "start": "2024-01-01",
    "end": "2026-02-01"
  },
  "inputs": ["git_artifacts/TrailEquip/commits.json"],
  "total_commits": 155,
  "avg_commits_per_day": 0.21,
  "method": "Count total commits, divide by unique dates",
  "calculated_at": "2026-02-01T00:13:17Z"
}
```

**Run:**
```bash
python3 src/calculations/calculate.py
```

### 4. PRESENTATION Layer: Dashboard

Read-only view of metrics from `calculations/`. No access to git or CI systems.

**File:** `public/index.html`

**Responsibilities:**
- Display metrics
- Link to calculation files and raw inputs
- Professional UX (calm, minimal, trustworthy)

## Quick Start

### Prerequisites
- Python 3.8+
- Git
- A browser

### Run Full Pipeline

```bash
./run_pipeline.sh
```

This executes in order:
1. Parse `ReposInput.md`
2. Collect git data
3. Collect CI data
4. Calculate metrics
5. Validate quality gates
6. Report success/failure

### View Dashboard

```bash
open public/index.html
# or serve over HTTP:
python3 -m http.server 8000
# Then: http://localhost:8000/public/
```

## Project Structure

```
DORA/
├── ReposInput.md                    # INPUT: Repository definitions (source of truth)
├── git_artifacts/                   # COLLECTION: Raw git data
│   ├── TrailEquip/
│   │   ├── clone/                  # Cloned repository
│   │   ├── commits.json
│   │   ├── authors.json
│   │   └── timeline.json
│   └── [other repos...]
├── ci_artifacts/                    # COLLECTION: Raw CI data
├── calculations/                    # CALCULATION: Normalized metrics (truth for dashboard)
│   ├── per_repo/
│   │   ├── TrailEquip/
│   │   │   ├── commits.json
│   │   │   ├── contributors.json
│   │   │   ├── coverage.json
│   │   │   ├── dora_frequency.json
│   │   │   └── lead_time.json
│   │   └── [other repos...]
│   └── global/
│       ├── commits.json
│       └── summary.json
├── public/                          # PRESENTATION: Dashboard (reads calculations/)
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── src/
│   ├── collection/
│   │   ├── collect_git.py           # Git data extraction
│   │   └── collect_ci.py            # CI data extraction
│   ├── calculations/
│   │   └── calculate.py             # Metric computation
│   └── validation/
│       └── validate.py              # Quality gates
├── run_pipeline.sh                  # Pipeline orchestration
└── README.md                        # This file
```

## Key Rules (Non-Negotiable)

### 1. Dashboard Never Reads Repositories Directly
- ✓ Dashboard reads: `calculations/`
- ✗ Dashboard does NOT read: git repos, CI systems, API endpoints

### 2. Calculations Are the Source of Truth
- All metrics come from `calculations/`
- Every calculation is auditable and traceable
- Every calculation includes source inputs

### 3. ReposInput.md Controls Scope
- Only repositories listed here are analyzed
- Adding a new repo requires editing this file
- Removing a repo requires editing this file

### 4. Quality Gates Fail On
- Approximations ("~", "approx", "estimated")
- Missing source inputs
- Out-of-bounds values (coverage > 100%, negative commits)
- Time range mismatches

### 5. N/A > Invented Numbers
- If a metric cannot be calculated, show: `null` with a `reason`
- Never guess or approximate
- Never show made-up precision

## Adding New Repositories

**Important:** When you add new repositories, the pipeline will automatically collect and calculate metrics.

### Step 1: Edit ReposInput.md
```markdown
## MyNewProject
repo: https://github.com/owner/myproject
branch: main
language: typescript
ci: github-actions
coverage: nyc
```

### Step 2: Run Pipeline
```bash
./run_pipeline.sh
```

### Step 3: View Dashboard
```bash
open public/index.html
```

The dashboard automatically discovers and displays metrics for all repositories listed in `ReposInput.md`.

## Metrics Reference

### Per-Repository Metrics

- **commits** - Total commits, frequency, date range
- **contributors** - Unique contributors (by email)
- **coverage** - Test coverage percentage (when available)
- **dora_frequency** - Proxy: commits per day (requires deployment tags for true DORA)
- **lead_time** - Proxy: average time between commits (requires CI timestamps for true DORA)

### Global Metrics

- **commits.json** - Sum of commits across all repos
- **summary.json** - Organization overview (repos analyzed, issues)

## DORA Metrics Note

The dashboard displays DORA proxy metrics based on git history:

- **Deployment Frequency** = commits/day (requires deployment tags for accuracy)
- **Lead Time** = avg hours between commits (requires build/deploy timestamps for accuracy)

True DORA metrics require:
- Git commit timestamp
- Build/deploy completion timestamp
- Change failure tracking (automated tests)
- MTTR measurement (time to production fix)

See [DORA Research](https://dora.dev) for standards.

## Pipeline Execution

### Manual Steps
```bash
# Collect all artifacts
python3 src/collection/collect_git.py
python3 src/collection/collect_ci.py

# Calculate all metrics
python3 src/calculations/calculate.py

# Validate quality gates
python3 src/validation/validate.py
```

### Automated (Recommended)
```bash
./run_pipeline.sh
```

## Validation & Quality Gates

The validation layer enforces:
```bash
python3 src/validation/validate.py
```

**Checks:**
- ✓ Required directories exist
- ✓ All calculation files have `metric_id` and `calculated_at`
- ✓ No approximations ("~", "approx")
- ✓ Values are in valid ranges (coverage ≤ 100%, commits ≥ 0)
- ✓ All referenced inputs exist
- ✓ Global metrics reference existing repos

**Failure:** Pipeline exits with status 1 if any check fails.

## Troubleshooting

### Collection fails: "Clone failed"
- Check repository URLs in `ReposInput.md`
- Verify network connectivity
- Ensure git is installed and configured

### Validation fails: "Approximations found"
- Check calculation files for approximation markers
- Ensure metrics are calculated, not estimated

### Dashboard shows all N/A
- Verify `calculations/` folder exists
- Run pipeline: `./run_pipeline.sh`
- Check browser console for fetch errors

### No repos appear in dashboard
- Edit `ReposInput.md` to add repositories
- Run pipeline: `./run_pipeline.sh`
- Refresh browser

## Design Philosophy

This system follows:

- **Evidence-Based**: Metrics derived from real source code and CI systems
- **Traceable**: Every number links to its calculation and raw inputs
- **Transparent**: No hidden logic, no black boxes
- **Professional**: Calm UX, no hype, no false precision
- **Auditable**: All calculations reproducible and checkable
- **Maintainable**: Clear separation: input → collection → calculation → presentation

## License

MIT

