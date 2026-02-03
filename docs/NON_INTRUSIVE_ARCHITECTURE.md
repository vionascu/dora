# DORA Non-Intrusive Metrics Collection Architecture

**Version:** 2.0 (Non-Intrusive Mode)

**Philosophy:** Extract metrics from repositories with read-only access. Never modify target repositories. Never require API keys to external systems. Keep the system maintainable and scalable.

---

## Overview

DORA has been transformed into a **non-intrusive metrics collection system** that:

1. **Scans repositories with read-only access** - No write permissions needed
2. **Accepts JIRA data exports** - Works with CSV or JSON exports (no API access required)
3. **Reads documentation from project files** - Each project includes a `.dora.md` configuration file
4. **Outputs metrics to GitHub Pages** - JSON-based, easy to maintain, statically served

### Core Principle
**"Non-Intrusive = Read-Only + Self-Contained Configuration"**

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    INPUT SOURCES (Non-Intrusive)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Git Repositories (READ-ONLY)                                   │
│     ├─ Clone with --depth (minimal transfer)                       │
│     ├─ Extract: commits, branches, tags, authors                   │
│     └─ No modifications, no hooks, no side effects                 │
│                                                                     │
│  2. JIRA Data Export (User-Provided)                               │
│     ├─ CSV format: ID, Title, Type, Status, Resolution, Link      │
│     ├─ JSON format: Standard Jira export                           │
│     └─ Stored in: jira_exports/<project>.csv or .json             │
│                                                                     │
│  3. Project Configuration (.dora.md in each repo)                  │
│     ├─ Project name                                                │
│     ├─ Links to JIRA epics (via JIRA export)                       │
│     ├─ Links to Confluence documentation                           │
│     ├─ Links to GitHub repo                                        │
│     └─ Metadata (team, deployment info)                            │
│                                                                     │
│  4. Confluence Documentation (User-Referenced)                     │
│     └─ Linked from .dora.md, not scraped directly                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    COLLECTION LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Git Metrics Collector                                          │
│     ├─ Clone repositories (shallow, read-only)                     │
│     ├─ Extract: commit history, authors, branches, tags           │
│     └─ Output: git_artifacts/<repo>/                              │
│                                                                     │
│  2. JIRA Data Processor                                            │
│     ├─ Parse CSV or JSON exports                                   │
│     ├─ Link epics to project via .dora.md references              │
│     └─ Output: jira_artifacts/<project>/                          │
│                                                                     │
│  3. Documentation Collector                                        │
│     ├─ Read .dora.md from each repository                          │
│     ├─ Parse Confluence links (stored for reference)               │
│     └─ Output: docs_artifacts/<project>/                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CALCULATION LAYER                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Merge & Calculate Metrics:                                        │
│                                                                     │
│  1. Git Metrics                                                    │
│     ├─ Commit frequency (from git history)                        │
│     ├─ Deployment frequency (from version tags)                   │
│     ├─ Lead time (avg time between commits)                       │
│     ├─ Contributors & author distribution                         │
│     └─ Branch patterns (release, hotfix, feature)                 │
│                                                                     │
│  2. JIRA-Linked Metrics                                            │
│     ├─ Epics by status                                            │
│     ├─ User stories per epic                                      │
│     ├─ Epic completion rate                                       │
│     └─ Linked commits per epic (via commit message analysis)      │
│                                                                     │
│  3. Documentation Metrics                                          │
│     ├─ Links to Confluence pages (for audit)                      │
│     ├─ Last updated (from .dora.md or git history)                │
│     └─ Project metadata                                           │
│                                                                     │
│  Output: calculations/ (JSON files, GitHub Pages ready)           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OUTPUT LAYER (GitHub Pages)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  JSON Metrics (calculations/ folder)                               │
│  └─ Committed to gh-pages branch or separate docs/ folder         │
│     ├─ Readable by GitHub Pages                                   │
│     ├─ Versionable in Git                                         │
│     ├─ No database required                                       │
│     └─ Shareable via GitHub URLs                                  │
│                                                                     │
│  Dashboard (public/)                                               │
│  └─ Static HTML + JS                                              │
│     ├─ Reads calculations/ JSON files                             │
│     ├─ Renders metrics & insights                                 │
│     ├─ Filters by project, date range                             │
│     └─ Links to source data & Confluence                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Input Layer: Data Sources

### 1. Git Repositories (READ-ONLY)

**Access Requirements:**
- Clone access (HTTPS or SSH)
- NO write permissions needed
- NO branch creation or modifications

**Collection Process:**

```bash
# Shallow clone for efficiency
git clone --depth=1 <repo-url> <local-path>

# Extract metrics
git log --all --format="%H|%ai|%an|%ae" > commits.json
git branch -a > branches.json
git tag -l > tags.json
```

**Output:**
```
git_artifacts/<project>/
├── clone/                    (cloned repository)
├── commits.json              (all commits with metadata)
├── tags.json                 (release/version tags)
├── branches.json             (branch information)
└── stats.json                (summary: total commits, authors, date range)
```

**Key Metrics from Git:**
- Total commits
- Commit frequency (commits/day)
- Deployment frequency (tags/tags_per_period)
- Lead time (avg time between commits)
- Active contributors
- Branch patterns

---

### 2. JIRA Data Export (User-Provided)

**Why No API Access?**
- Many organizations restrict API access
- Credentials are sensitive
- Exports provide flexibility (can filter/modify before import)

**Supported Formats:**

#### Option A: CSV Format (Recommended for simplicity)

**File:** `jira_exports/<project>.csv`

```csv
Epic ID,Epic Name,Type,Status,Resolution,Story Count,Link
EPIC-1,Authentication System,Epic,Done,Fixed,12,https://jira.company.com/browse/EPIC-1
EPIC-2,Payment Integration,Epic,In Progress,None,8,https://jira.company.com/browse/EPIC-2
US-101,Login Page UI,Story,Done,Fixed,0,https://jira.company.com/browse/US-101
US-102,OAuth2 Integration,Story,In Progress,None,0,https://jira.company.com/browse/US-102
```

**How to Export from JIRA:**
```
1. Go to JIRA > Issues & Filters > Export
2. Select: "CSV (Current Fields)"
3. Filter by project (if needed)
4. Download file
5. Save as: jira_exports/<project>.csv
```

#### Option B: JSON Format (More structured)

**File:** `jira_exports/<project>.json`

```json
{
  "issues": [
    {
      "key": "EPIC-1",
      "type": "Epic",
      "summary": "Authentication System",
      "status": "Done",
      "resolution": "Fixed",
      "customfields": {
        "Story Count": 12
      },
      "fields": {
        "link": "https://jira.company.com/browse/EPIC-1"
      }
    }
  ]
}
```

**How to Export from JIRA:**
```
1. Use JIRA REST API (optional, if API access available later)
2. Or use Jira Cloud CLI: jira export --format=json > project.json
3. Save as: jira_exports/<project>.json
```

**Processing:**
```python
# src/collection/collect_jira.py

1. Parse CSV or JSON
2. Extract epics and user stories
3. Link to projects via .dora.md references
4. Store in jira_artifacts/<project>/
5. Include metadata for later correlation
```

**Output:**
```
jira_artifacts/<project>/
├── epics.json                (extracted epics with metadata)
├── stories.json              (extracted user stories)
└── correlation_map.json      (epic → commits mapping)
```

---

### 3. Project Configuration (.dora.md)

**Location:** Root of each Git repository

**Purpose:**
- Self-contained project metadata
- Links to JIRA epics (via export)
- Links to Confluence documentation
- Links to GitHub repository
- Additional project context

**Format:**

```markdown
# DORA Project Configuration

## Project Information
- **Name:** Authentication Service
- **GitHub Repository:** https://github.com/myorg/auth-service
- **Team:** Backend Team

## JIRA Integration (via Export)
- **JIRA Project Key:** AUTH
- **JIRA Export File:** jira_exports/auth.csv
- **Epic Link Pattern:** EPIC-1, EPIC-2 (these are in the export)
  - EPIC-1: Authentication Core
  - EPIC-2: OAuth2 Integration

## Documentation Links
- **Architecture:** https://confluence.company.com/pages/auth-architecture
- **API Reference:** https://confluence.company.com/pages/auth-api
- **Runbook:** https://confluence.company.com/pages/auth-runbook

## Deployment Information
- **Production Branch:** main
- **Staging Branch:** staging
- **Version Tag Pattern:** v*.*.* (e.g., v1.2.3)
- **Deployment Frequency:** Every 2 weeks
- **Last Production Deployment:** 2026-02-01

## Additional Metadata
- **Language:** Java
- **Framework:** Spring Boot
- **Coverage Tool:** JaCoCo
- **CI/CD:** GitHub Actions
```

**How to Use:**

1. **Create `.dora.md` in each repository root**
2. **Fill in project-specific information**
3. **Include links to your JIRA exports and Confluence pages**
4. **Commit and push to repository**

**Parser Output:**
```
docs_artifacts/<project>/
├── metadata.json             (parsed .dora.md)
├── confluence_links.json     (Confluence page references)
└── jira_references.json      (JIRA epic/story links)
```

---

### 4. Confluence Documentation (Referenced, Not Scraped)

**Access Model:**
- Links are stored in `.dora.md`
- Dashboard displays links for users to click
- No automatic scraping of Confluence content
- Keeps system simple and non-intrusive

**Why This Approach?**
- Confluence API requires authentication
- Scraping breaks with page layout changes
- Users can update `.dora.md` when documentation changes
- Maintains data freshness through manual curation

---

## Collection Layer: Extractors

### Phase 1: Git Collector

**File:** `src/collection/collect_git.py`

```python
class GitCollector:
    def __init__(self, config):
        self.config = config

    def collect(self, project_config):
        """
        1. Clone repository (shallow, read-only)
        2. Extract commits, tags, branches
        3. Save to git_artifacts/<project>/
        """
        # Clone
        self.git_clone(project_config)

        # Extract metrics
        commits = self.extract_commits()
        tags = self.extract_tags()
        branches = self.extract_branches()
        stats = self.calculate_stats(commits)

        # Save
        self.save_artifacts(commits, tags, branches, stats)
```

**Key Features:**
- ✓ Shallow clones (minimal bandwidth)
- ✓ Streaming processing (O(1) memory)
- ✓ No modifications to repository
- ✓ Handles read-only access gracefully

---

### Phase 2: JIRA Collector

**File:** `src/collection/collect_jira.py`

```python
class JiraCollector:
    def __init__(self, config):
        self.config = config

    def collect(self, project_config):
        """
        1. Read JIRA export (CSV or JSON)
        2. Parse epics and stories
        3. Link to project via .dora.md
        4. Save to jira_artifacts/<project>/
        """
        # Determine format
        export_file = self.locate_export(project_config)

        if export_file.endswith('.csv'):
            data = self.parse_csv(export_file)
        else:
            data = self.parse_json(export_file)

        # Extract and correlate
        epics = self.extract_epics(data)
        stories = self.extract_stories(data)
        correlation = self.create_correlation(epics, stories)

        # Save
        self.save_artifacts(epics, stories, correlation)
```

**Processing:**
- Parse CSV using Python's `csv` module
- Parse JSON using standard `json` module
- Build correlation maps (epic → story → commit)
- Store in structured format for calculations

---

### Phase 3: Documentation Collector

**File:** `src/collection/collect_docs.py`

```python
class DocumentationCollector:
    def __init__(self, config):
        self.config = config

    def collect(self, project_config):
        """
        1. Clone repository (if not already done)
        2. Find and parse .dora.md
        3. Extract metadata and links
        4. Save to docs_artifacts/<project>/
        """
        # Find .dora.md
        dora_file = self.find_dora_md(project_config)

        if not dora_file:
            return self.create_default_metadata()

        # Parse
        metadata = self.parse_dora_md(dora_file)
        confluence_links = self.extract_confluence_links(metadata)
        jira_refs = self.extract_jira_references(metadata)

        # Save
        self.save_artifacts(metadata, confluence_links, jira_refs)
```

**Parsing Rules:**
- Markdown format (easy to read and edit)
- Key-value pairs: `- **Key:** Value`
- Links: Confluence & GitHub URLs
- Team and metadata information

---

## Calculation Layer: Metrics

### From Git Data

```json
{
  "metric_id": "repo.dora.commit_frequency",
  "repo": "auth-service",
  "time_range": {
    "start": "2026-01-01",
    "end": "2026-02-03"
  },
  "inputs": ["git_artifacts/auth-service/commits.json"],
  "commits": {
    "total": 156,
    "per_day": 3.2,
    "per_week": 22.3
  },
  "method": "Count commits per day from git history",
  "calculated_at": "2026-02-03T10:00:00Z"
}
```

### From JIRA Data

```json
{
  "metric_id": "jira.epic_progress",
  "project": "auth-service",
  "inputs": ["jira_artifacts/auth-service/epics.json"],
  "epics": [
    {
      "key": "EPIC-1",
      "name": "Authentication Core",
      "status": "Done",
      "story_count": 12,
      "completed_stories": 12
    },
    {
      "key": "EPIC-2",
      "name": "OAuth2 Integration",
      "status": "In Progress",
      "story_count": 8,
      "completed_stories": 5
    }
  ],
  "method": "Parsed from JIRA export; linked via .dora.md",
  "calculated_at": "2026-02-03T10:00:00Z"
}
```

### Combined Metrics

```json
{
  "metric_id": "project.dora_summary",
  "project": "auth-service",
  "inputs": [
    "git_artifacts/auth-service/commits.json",
    "jira_artifacts/auth-service/epics.json",
    "docs_artifacts/auth-service/metadata.json"
  ],
  "deployment_frequency": {
    "tags_total": 15,
    "tags_period": 15,
    "frequency_per_month": 2.1
  },
  "lead_time": {
    "avg_hours_between_commits": 6.2,
    "estimated_days": 0.26
  },
  "epics": {
    "total": 2,
    "completed": 1,
    "in_progress": 1
  },
  "documentation": {
    "confluence_links": 3,
    "last_updated": "2026-02-01"
  },
  "method": "Aggregated from git, JIRA, and documentation sources",
  "calculated_at": "2026-02-03T10:00:00Z"
}
```

---

## Output Layer: GitHub Pages

### Data Format

All metrics are JSON files stored in `calculations/` folder:

```
calculations/
├── per_repo/
│   ├── auth-service/
│   │   ├── dora.json              (deployment frequency, lead time)
│   │   ├── commits.json           (commit metrics)
│   │   ├── epics.json             (JIRA epic progress)
│   │   ├── contributors.json      (author metrics)
│   │   └── summary.json           (project summary)
│   ├── payment-service/
│   └── [other projects...]
├── global/
│   ├── summary.json               (all projects aggregated)
│   ├── dora_metrics.json          (org-wide DORA metrics)
│   └── manifest.json              (metric catalog)
└── [metadata files...]
```

### GitHub Pages Setup

**Option A: gh-pages Branch (Recommended)**

```bash
# Create orphan gh-pages branch
git checkout --orphan gh-pages
git rm -rf .

# Create index.html and necessary files
cp -r public/* .
cp -r calculations/ .

# Commit and push
git add .
git commit -m "DORA metrics dashboard"
git push origin gh-pages
```

**Option B: /docs Folder**

```bash
# Use /docs folder on main branch
mkdir -p docs/calculations
cp -r calculations/* docs/calculations/
cp public/index.html docs/

# Commit and push
git add docs/
git commit -m "DORA metrics"
git push origin main

# Configure GitHub Pages to use /docs folder
# Settings > Pages > Source: main branch /docs folder
```

### Accessing Dashboard

```
https://<username>.github.io/<dora-repo>/public/
# or
https://<username>.github.io/<dora-repo>/docs/public/
```

### Dashboard Features

```html
<!-- public/index.html -->

<div id="dashboard">
  <!-- 1. Project Selector -->
  <select id="project-filter">
    <option value="all">All Projects</option>
    <option value="auth-service">Authentication Service</option>
    <option value="payment-service">Payment Service</option>
  </select>

  <!-- 2. Metrics Display -->
  <div class="metric-card">
    <h3>Deployment Frequency</h3>
    <p class="metric-value">2.1 per month</p>
    <a href="#calculation-source">View Calculation</a>
  </div>

  <!-- 3. JIRA Epics -->
  <div class="epics-section">
    <h3>JIRA Epics</h3>
    <ul>
      <li>EPIC-1: Authentication Core (Done)</li>
      <li>EPIC-2: OAuth2 Integration (In Progress)</li>
    </ul>
    <a href="https://confluence.company.com/pages/auth">View in Confluence</a>
  </div>

  <!-- 4. Documentation Links -->
  <div class="docs-section">
    <h3>Documentation</h3>
    <ul>
      <li><a href="...">Architecture</a></li>
      <li><a href="...">API Reference</a></li>
      <li><a href="...">Runbook</a></li>
    </ul>
  </div>
</div>
```

---

## Data Flow Example

### Scenario: Analyzing "auth-service" Project

```
1. INPUT
   ├─ GitHub Repo: https://github.com/myorg/auth-service
   ├─ .dora.md: Contains links to JIRA export & Confluence
   ├─ JIRA Export: jira_exports/auth.csv (manually exported)
   └─ Confluence Pages: (referenced, not scraped)

2. COLLECTION
   ├─ Git Collector
   │  ├─ Clone repo (read-only)
   │  ├─ Extract commits & tags
   │  └─ Save to git_artifacts/auth-service/
   │
   ├─ JIRA Collector
   │  ├─ Read jira_exports/auth.csv
   │  ├─ Parse epics & stories
   │  └─ Save to jira_artifacts/auth-service/
   │
   └─ Documentation Collector
      ├─ Read .dora.md from repo
      ├─ Extract Confluence links
      └─ Save to docs_artifacts/auth-service/

3. CALCULATION
   ├─ Merge git, JIRA, and docs data
   ├─ Calculate deployment frequency (from tags)
   ├─ Calculate lead time (from commits)
   ├─ Aggregate JIRA epic progress
   └─ Save to calculations/per_repo/auth-service/

4. OUTPUT
   ├─ Commit calculations/ to gh-pages
   ├─ GitHub Pages serves public/index.html
   ├─ Dashboard reads calculations/*.json
   └─ User views metrics + links to Confluence
```

---

## Key Design Principles

### 1. Non-Intrusive
- ✓ Read-only access to repositories
- ✓ No API keys stored in project
- ✓ User provides JIRA exports manually
- ✓ Documentation links, not scraping

### 2. Self-Contained
- ✓ Each project has a `.dora.md` file
- ✓ All metadata in one place
- ✓ No external database required
- ✓ Works offline after initial collection

### 3. Maintainable
- ✓ JSON output (human-readable)
- ✓ GitHub Pages (no server to maintain)
- ✓ Versioned in Git (full audit trail)
- ✓ Simple collection scripts (easy to debug)

### 4. Scalable
- ✓ Collection modules are independent
- ✓ Can run collectors in parallel
- ✓ Shallow clones reduce bandwidth
- ✓ Stream processing keeps memory constant

---

## Configuration Management

### Global Configuration

**File:** `repos.yaml`

```yaml
metrics_config:
  collection:
    git:
      clone_depth: 1
      include_history: true
    jira:
      export_format: csv
      supported_formats: [csv, json]
    documentation:
      filename: .dora.md
      confluence_verify: false  # Just store links, don't verify

  calculation:
    time_periods: [day, week, month, quarter]
    tag_patterns:
      - v*.*.*
      - release-*
    branch_patterns:
      - main
      - master
      - release/*

  output:
    format: json
    github_pages: true
    base_url: "https://<username>.github.io/<repo>"

repositories:
  auth-service:
    url: https://github.com/myorg/auth-service
    jira_export: jira_exports/auth.csv
    dora_md: .dora.md  # Path in repo

  payment-service:
    url: https://github.com/myorg/payment-service
    jira_export: jira_exports/payment.json
    dora_md: .dora.md
```

---

## Pipeline Execution

### Full Pipeline

```bash
# 1. Collect all data
python3 src/collection/collect_git.py
python3 src/collection/collect_jira.py
python3 src/collection/collect_docs.py

# 2. Calculate metrics
python3 src/calculations/calculate.py

# 3. Validate quality gates
python3 src/validation/validate.py

# 4. Deploy to GitHub Pages
./deploy_to_github_pages.sh
```

### Automated (GitHub Actions)

```yaml
# .github/workflows/dora-pipeline.yml
name: DORA Metrics Collection

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: 3.9

      - name: Collect Metrics
        run: ./run_pipeline.sh

      - name: Deploy to GitHub Pages
        run: ./deploy_to_github_pages.sh
```

---

## Troubleshooting

### No JIRA data found
- Check `jira_exports/` folder exists
- Verify export file format (CSV or JSON)
- Ensure file name matches `repos.yaml` configuration

### .dora.md not found
- Create `.dora.md` in repository root
- Ensure correct format (Markdown)
- Commit and push to repository

### Confluence links return 404
- Check URL is correct in `.dora.md`
- Verify page still exists in Confluence
- Update `.dora.md` with correct link

### Metrics not updating
- Check pipeline ran successfully: `./run_pipeline.sh`
- Verify `calculations/` folder has JSON files
- Check GitHub Pages is enabled in Settings
- Clear browser cache and reload

---

## Security Considerations

### Credentials & Secrets
- ✓ NO hardcoded credentials in code
- ✓ NO API keys in repositories
- ✓ Git cloning uses public HTTPS (no auth needed)
- ✓ JIRA exports are user-provided (no API keys)

### Data Access
- ✓ Read-only git access (no modifications)
- ✓ Public repositories recommended
- ✓ Dashboard data is public (GitHub Pages)
- ✓ No sensitive data in metrics

### Audit Trail
- ✓ All calculations logged with timestamps
- ✓ Inputs documented in each metric file
- ✓ Full history in Git commits
- ✓ Verifiable data lineage

---

## Extending the System

### Adding New Data Sources

```python
# Create new collector in src/collection/collect_<source>.py

class MySourceCollector:
    def __init__(self, config):
        self.config = config

    def collect(self, project_config):
        # 1. Fetch/read data (non-intrusively)
        data = self.fetch_data(project_config)

        # 2. Parse and normalize
        normalized = self.normalize(data)

        # 3. Save artifacts
        self.save_artifacts(normalized)
```

### Adding New Metrics

```python
# In src/calculations/calculate.py

def calculate_new_metric(raw_data):
    """
    Calculate new metric from raw data
    """
    metric = {
        "metric_id": "project.new_metric",
        "repo": raw_data['repo'],
        "inputs": ["raw_artifacts/..."],
        "value": compute_value(raw_data),
        "method": "Description of calculation",
        "calculated_at": datetime.utcnow().isoformat()
    }
    return metric
```

---

## Summary

This non-intrusive architecture:

| Aspect | Approach |
|--------|----------|
| Git Access | Read-only cloning, no API keys |
| JIRA Data | User-provided exports (CSV/JSON) |
| Documentation | Links in `.dora.md`, no scraping |
| Output | JSON files on GitHub Pages |
| Maintenance | Simple, no database or servers |
| Scalability | Collectors independent, parallel-ready |
| Auditability | Full history in Git, transparent calculations |

---

## References

- [DORA Research](https://dora.dev)
- [GitHub Pages Guide](https://pages.github.com)
- [Metrics Documentation](./METRICS_REFERENCE.md)
