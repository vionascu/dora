# DORA Metrics Dashboard

A professional, evidence-backed R&D metrics system with a **non-intrusive** collection model.

**Core Principle:** Extract metrics with read-only access. Never modify repositories. Never require external API keys.

**Dashboard does NOT access repositories directly. Truth lives in `calculations/` (JSON files on GitHub Pages).**

## Architecture

```
GIT REPOS        JIRA EXPORTS     PROJECT DOCS     CONFLUENCE
(READ-ONLY)      (CSV/JSON)       (.dora.md)       (REFERENCED)
      ↓                ↓                ↓                ↓
   ╔════════════════════════════════════════════════╗
   ║          COLLECTION LAYER                      ║
   ║  - Git Collector (read-only clones)            ║
   ║  - JIRA Parser (CSV/JSON exports)              ║
   ║  - Documentation Collector (.dora.md)          ║
   ╚════════════════════════════════════════════════╝
                         ↓
         git_artifacts/ + jira_artifacts/ + docs_artifacts/
                         ↓
   ╔════════════════════════════════════════════════╗
   ║          CALCULATION LAYER                     ║
   ║  - Merge and normalize all data                ║
   ║  - Calculate DORA metrics from git tags        ║
   ║  - Link epics to commits                       ║
   ╚════════════════════════════════════════════════╝
                         ↓
                    calculations/ (JSON)
                         ↓
   ╔════════════════════════════════════════════════╗
   ║          OUTPUT LAYER (GitHub Pages)           ║
   ║  - Serve JSON on GitHub Pages                  ║
   ║  - Dashboard displays metrics & links          ║
   ╚════════════════════════════════════════════════╝
                         ↓
                  public/index.html
```

### 1. INPUT Layer: Non-Intrusive Sources

**Three independent data sources, all non-intrusive:**

#### a) Git Repositories (READ-ONLY)
- Clone with `--depth=1` (shallow, efficient)
- Extract: commits, tags, branches, authors
- NO modifications, NO write permissions needed

#### b) JIRA Data (User-Provided Export)
- Users export JIRA data as CSV or JSON
- Stored in `jira_exports/` folder
- No API access required
- Updated manually by users

**Example:**
```csv
# jira_exports/auth-service.csv
Epic ID,Epic Name,Type,Status,Story Count
EPIC-1,Authentication Core,Epic,Done,12
EPIC-2,OAuth2 Integration,Epic,In Progress,8
```

#### c) Project Configuration (.dora.md in each repo)
- Self-contained configuration file in repository root
- Links to JIRA epics, Confluence docs, GitHub repo
- Team and metadata information
- Allows Confluence documentation links

**Example:**
```markdown
# DORA Project Configuration

## Project Information
- **Name:** Authentication Service
- **GitHub:** https://github.com/myorg/auth-service

## JIRA Integration
- **Export File:** jira_exports/auth.csv
- **Epics:** EPIC-1, EPIC-2

## Documentation Links
- **Architecture:** https://confluence.company.com/auth-architecture
- **Runbook:** https://confluence.company.com/auth-runbook
```

### 2. COLLECTION Layer: Non-Intrusive Extraction

Collects data from three independent sources without modification.

**Collectors:**

#### Git Collector
```bash
python3 src/collection/collect_git.py
```
- Shallow clone (read-only, minimal bandwidth)
- Extracts: commits, tags, branches, authors
- Output: `git_artifacts/<repo>/`

#### JIRA Collector
```bash
python3 src/collection/collect_jira.py
```
- Parses CSV or JSON exports
- Links epics to projects
- Output: `jira_artifacts/<repo>/`

#### Documentation Collector
```bash
python3 src/collection/collect_docs.py
```
- Reads `.dora.md` from each repository
- Extracts metadata and Confluence links
- Output: `docs_artifacts/<repo>/`

**Full Collection:**
```bash
./run_pipeline.sh
```

### 3. CALCULATION Layer: Merged & Auditable Metrics

Merges data from git, JIRA, and documentation sources. Every metric is traceable.

**Key principle:** Every metric file includes:
- `metric_id` - Unique identifier
- `inputs` - Source files used
- `values` - Calculated metrics
- `method` - How it was calculated
- `calculated_at` - ISO timestamp

**Outputs:**
```
calculations/
  per_repo/
    auth-service/
      dora.json               # Deployment frequency, lead time
      commits.json            # Commit metrics
      epics.json              # JIRA epic progress
      contributors.json       # Author distribution
      summary.json            # Project summary
    [other projects...]
  global/
    summary.json              # Organization overview
    dora_metrics.json         # Org-wide DORA metrics
```

**Example: Deployment Frequency (from git tags)**
```json
{
  "metric_id": "repo.dora.deployment_frequency",
  "repo": "auth-service",
  "inputs": ["git_artifacts/auth-service/tags.json"],
  "deployment_frequency": {
    "tags_total": 15,
    "period_months": 12,
    "frequency_per_month": 1.25
  },
  "method": "Count git tags matching v*.*.* pattern; divide by period",
  "calculated_at": "2026-02-03T10:00:00Z"
}
```

**Run:**
```bash
python3 src/calculations/calculate.py
```

### 4. OUTPUT Layer: GitHub Pages (JSON + Dashboard)

Serves metrics as JSON files on GitHub Pages. Dashboard reads static JSON.

**Files:**
- `calculations/` - JSON metrics (versioned in Git)
- `public/index.html` - Dashboard UI (reads JSON)

**Deployment:**
```bash
# Option A: Use gh-pages branch
git checkout --orphan gh-pages
cp -r public/* .
cp -r calculations/ .
git push origin gh-pages

# Option B: Use /docs folder on main branch
mkdir -p docs && cp -r public/* docs/ && cp -r calculations docs/
# Configure GitHub Pages to use /docs
```

**Access Dashboard:**
```
https://<username>.github.io/<dora-repo>/public/
```

**Key Features:**
- ✓ No server required (static GitHub Pages)
- ✓ Versioned in Git (full audit trail)
- ✓ Easy to maintain (JSON files)
- ✓ Shareable URLs (public links)

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

### 1. Non-Intrusive Collection
- ✓ Git access: read-only clones only
- ✓ JIRA data: user-provided exports (CSV/JSON)
- ✓ Documentation: `.dora.md` files + Confluence links
- ✗ NO API keys stored in project
- ✗ NO modifications to target repositories

### 2. Dashboard Never Reads Repositories Directly
- ✓ Dashboard reads: `calculations/` (static JSON)
- ✗ Dashboard does NOT read: git repos, API endpoints, databases

### 3. Calculations Are the Source of Truth
- All metrics come from `calculations/` folder
- Every calculation is auditable and traceable
- Every calculation includes source inputs and method

### 4. JIRA Data via Export, Not API
- Users export JIRA data manually (CSV or JSON)
- Store exports in `jira_exports/` folder
- Link via `.dora.md` references
- No API credentials required

### 5. Project Configuration in Each Repo
- Each project MUST have `.dora.md` at root
- Contains: project name, JIRA epic links, Confluence links, team info
- Allows non-intrusive linking of external documentation

### 6. Quality Gates Fail On
- Approximations ("~", "approx", "estimated")
- Missing source inputs
- Out-of-bounds values (coverage > 100%, negative commits)
- Invalid JIRA export formats

### 7. N/A > Invented Numbers
- If a metric cannot be calculated, show: `null` with a `reason`
- Never guess or approximate
- Never show made-up precision

## Adding New Repositories

To analyze a new repository, follow these steps:

### Step 1: Update Configuration
Edit `repos.yaml` to include the new repository:
```yaml
repositories:
  new-project:
    url: https://github.com/myorg/new-project
    jira_export: jira_exports/new-project.csv  # or .json
    dora_md: .dora.md
```

### Step 2: Create .dora.md in Target Repository
Create `.dora.md` in the repository root:
```markdown
# DORA Configuration

## Project Information
- **Name:** New Project
- **GitHub:** https://github.com/myorg/new-project

## JIRA Integration
- **Export File:** jira_exports/new-project.csv
- **Epics:** [List epics from your JIRA export]

## Documentation
- **Architecture:** https://confluence.company.com/new-project
```

### Step 3: Export JIRA Data
Export JIRA issues as CSV or JSON:
```bash
# Save to: jira_exports/new-project.csv
# Columns: Epic ID, Epic Name, Type, Status, Story Count, Link
```

### Step 4: Run Pipeline
```bash
./run_pipeline.sh
```

### Step 5: View Dashboard
```bash
open public/index.html
```

The dashboard automatically discovers and displays metrics for all repositories listed in `repos.yaml`.

## Metrics Reference

### Per-Repository Metrics

**Git-Based Metrics:**
- **commits** - Total commits, frequency, date range
- **contributors** - Unique contributors (by email)
- **deployment_frequency** - Calculated from git tags (v*.*.* pattern)
- **lead_time** - Average time between commits

**JIRA-Based Metrics:**
- **epics** - Epic status distribution (done, in-progress, pending)
- **user_stories** - Stories per epic, completion rate
- **epic_progress** - Percentage of stories completed per epic

**Documentation Metrics:**
- **confluence_links** - Number of linked documentation pages
- **last_updated** - Last update timestamp
- **team_info** - Team responsible for project

### Global Metrics

- **summary.json** - Organization overview (repos analyzed, projects)
- **dora_metrics.json** - Org-wide deployment frequency and lead time
- **epics.json** - All epics across organization

## DORA Metrics (Evidence-Based)

The system calculates DORA metrics from git history:

**Deployment Frequency**
```
Calculated from: git tags matching version pattern (v*.*.*)
Formula: total_tags / period_months
Example: 15 tags in 12 months = 1.25 deployments/month
Source: Fully auditable in calculations/per_repo/<project>/dora.json
```

**Lead Time**
```
Calculated from: time between consecutive commits
Formula: sum(time_between_commits) / number_of_commits
Example: 6.2 hours average between commits
Source: Fully auditable in calculations/per_repo/<project>/dora.json
```

**Important:** These are evidence-based metrics derived from repository data. For complete DORA metrics, you would also need:
- Build/deploy timestamps (not in git history)
- Change failure rate (test pass/fail data)
- Time to recovery (incident resolution data)

See [DORA Research](https://dora.dev) for complete standards.

## Pipeline Execution

### Automated (Recommended)
```bash
./run_pipeline.sh
```

This executes all steps in order:
1. Parse `repos.yaml` configuration
2. Collect git data (read-only clones)
3. Collect JIRA data (parse exports)
4. Collect documentation (.dora.md files)
5. Calculate all metrics
6. Validate quality gates
7. Report results

### Manual Steps (For Debugging)
```bash
# Collect all artifacts
python3 src/collection/collect_git.py
python3 src/collection/collect_jira.py
python3 src/collection/collect_docs.py

# Calculate all metrics
python3 src/calculations/calculate.py

# Validate quality gates
python3 src/validation/validate.py
```

### Scheduled Execution (GitHub Actions)
```yaml
# .github/workflows/dora-weekly.yml
name: DORA Metrics (Weekly)

on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday
  workflow_dispatch:

jobs:
  pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: 3.9

      - name: Run Pipeline
        run: ./run_pipeline.sh

      - name: Deploy to GitHub Pages
        run: ./deploy_to_github_pages.sh
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
- Check repository URLs in `repos.yaml`
- Verify network connectivity
- Ensure git is installed and configured
- Verify read-only access is sufficient

### Collection fails: "JIRA export not found"
- Check `jira_exports/` folder exists
- Verify export file name matches `repos.yaml`
- Check file format (CSV or JSON)
- Ensure headers match expected format

### Collection fails: ".dora.md not found"
- Create `.dora.md` in repository root
- Ensure correct Markdown format
- Include required fields (project name, links)
- Commit and push to repository

### Validation fails: "Approximations found"
- Check calculation files for approximation markers (~, approx)
- Ensure metrics are calculated, not estimated
- Verify JIRA data is properly formatted

### Dashboard shows all N/A
- Verify `calculations/` folder exists and has JSON files
- Run pipeline: `./run_pipeline.sh`
- Check browser console for fetch errors
- Verify GitHub Pages is configured correctly

### No repos appear in dashboard
- Edit `repos.yaml` to add repositories
- Verify `.dora.md` exists in each repo
- Run pipeline: `./run_pipeline.sh`
- Refresh browser cache (Ctrl+Shift+R)

### Confluence links are broken
- Verify URLs in `.dora.md` are correct
- Check page still exists in Confluence
- Update `.dora.md` with correct link
- Re-run pipeline to update dashboard

## Design Philosophy

This system follows:

- **Non-Intrusive**: Read-only access, no API keys, no repository modifications
- **Evidence-Based**: Metrics derived from real source code and git history
- **Traceable**: Every number links to its calculation and raw inputs
- **Transparent**: No hidden logic, no black boxes
- **Professional**: Calm UX, no hype, no false precision
- **Auditable**: All calculations reproducible and checkable
- **Maintainable**: Clear separation: input → collection → calculation → output
- **Scalable**: JSON-based, GitHub Pages hosted, version controlled

## Documentation

For detailed information, see:

1. **[Non-Intrusive Architecture](./docs/NON_INTRUSIVE_ARCHITECTURE.md)** - Complete system design, principles, and data flow
2. **[JIRA Export Guide](./docs/JIRA_EXPORT_GUIDE.md)** - How to export JIRA data (CSV/JSON) and use with DORA
3. **[Project Configuration Guide](./docs/PROJECT_CONFIG_GUIDE.md)** - How to create `.dora.md` in each repository
4. **[GitHub Pages Deployment](./docs/GITHUB_PAGES_DEPLOYMENT.md)** - How to deploy dashboard and metrics to GitHub Pages
5. **[Quick Start](./docs/QUICK_START.md)** - Get started with DORA in 10 minutes

## License

MIT

