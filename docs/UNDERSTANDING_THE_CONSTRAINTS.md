# Understanding DORA's Non-Intrusive Constraints

This document clarifies the key constraints and how the system design addresses them.

---

## Constraint 1: No Direct JIRA API Access

**The Challenge:**
- You don't have JIRA API credentials
- Organization may not grant API access
- API access adds security risk
- API rate limiting can be problematic

**The Solution: Export-Based Integration**

DORA accepts JIRA data via **user-provided exports** (CSV or JSON):

```bash
# User manually exports from JIRA UI
jira_exports/
├── auth-service.csv
├── payment-service.csv
└── analytics-service.csv
```

**How It Works:**

1. **User exports JIRA data** (one-time, periodic, or automated)
2. **DORA reads the export file** (no API call needed)
3. **Parser links epics to git commits** (via commit messages)
4. **Dashboard shows epic progress** (from export data)

**Benefits:**
- ✓ No API credentials stored
- ✓ Works even without API access
- ✓ Data is auditable (stored in git)
- ✓ Can be automated later if API access becomes available
- ✓ Flexible filtering (export only needed data)

**Limitation:**
- ✗ Requires manual export (or simple automation)
- ✗ Not real-time (only as fresh as the export)

**When to Update Exports:**
- Weekly or monthly intervals
- After major releases
- Before analysis/reporting
- Can be automated with GitHub Actions

---

## Constraint 2: Read-Only Repository Access

**The Challenge:**
- Target repositories have read-only access
- Cannot install hooks, create branches, or modify code
- Cannot write credentials to repositories
- Some CI systems may not allow token storage

**The Solution: Non-Intrusive Collection**

DORA **clones repositories and analyzes locally** without any modifications:

```bash
# Shallow clone (efficient, read-only)
git clone --depth=1 https://github.com/myorg/project.git

# Extract metrics locally (no server access needed)
git log --all --format="%H|%ai|%an" > commits.json
git tag -l > tags.json
git branch -a > branches.json
```

**How It Works:**

1. **DORA clones repository** (shallow, read-only)
2. **Analyzes git history locally** (no API calls to git service)
3. **Extracts metrics** (commits, tags, authors, branches)
4. **Never pushes changes** (no write operations)
5. **Cleans up temp files** after analysis

**Key Features:**
- ✓ No permissions needed beyond read access
- ✓ Shallow clones minimize bandwidth
- ✓ Streaming processing prevents memory issues
- ✓ Works with private or public repositories
- ✓ No rate limiting (local analysis)
- ✓ No authentication required for public repos

**Metrics Extracted:**
- Total commits (from git log)
- Commit frequency (commits per day/week/month)
- Deployment frequency (from version tags: v*.*.*)
- Lead time (avg time between commits)
- Contributors (unique authors)
- Branch patterns (release, hotfix, feature)
- Repository metadata

---

## Constraint 3: Self-Contained Project Documentation

**The Challenge:**
- Cannot scrape Confluence directly (authentication, fragility)
- Cannot require external API access
- Need project-specific metadata (team, links, JIRA refs)
- Confluence updates independently

**The Solution: .dora.md Configuration Files**

Each repository includes a **`.dora.md` file** with project metadata:

```markdown
# DORA Configuration

## Project
- **Name:** Authentication Service
- **GitHub:** https://github.com/myorg/auth-service

## JIRA Integration
- **Export File:** jira_exports/auth-service.csv

## Documentation
- **Architecture:** https://confluence.company.com/auth-arch
- **Runbook:** https://confluence.company.com/auth-runbook
- **API Docs:** https://confluence.company.com/auth-api
```

**How It Works:**

1. **User creates `.dora.md`** in repository root
2. **Includes links to JIRA exports and Confluence**
3. **DORA reads the file** (not Confluence directly)
4. **Dashboard displays links** for users to click
5. **Updated manually** when documentation changes

**Key Benefits:**
- ✓ No Confluence authentication needed
- ✓ Links are human-readable and auditable
- ✓ Decoupled from Confluence updates
- ✓ Works even if Confluence is down
- ✓ Self-documenting (metadata is in git)
- ✓ Collaborative (pull requests can update it)

**What Stays in .dora.md:**
- Project name and description
- Links to documentation
- Links to JIRA epics (via exports)
- Team information
- Deployment metadata

**What Stays in Confluence:**
- Detailed documentation (architecture, runbooks, etc.)
- Rich formatting and images
- Organizational knowledge base
- Version history

**Why This Approach:**
- Confluence is authoritative for documentation content
- .dora.md is authoritative for project metadata
- Clean separation of concerns
- Reduces coupling and maintenance burden

---

## Constraint 4: Easy to Maintain Output Format

**The Challenge:**
- Metrics need to be accessible from GitHub Pages
- No database or server setup
- Need something version-controlled and auditable
- Must be updatable without DevOps involvement

**The Solution: JSON Files + GitHub Pages**

DORA outputs all metrics as **JSON files** served on **GitHub Pages**:

```
calculations/
├── per_repo/
│   ├── auth-service/
│   │   ├── dora.json              (deployment frequency, lead time)
│   │   ├── commits.json           (commit metrics)
│   │   ├── epics.json             (JIRA epic progress)
│   │   ├── contributors.json      (author metrics)
│   │   └── summary.json           (project summary)
│   └── [other projects...]
├── global/
│   ├── summary.json               (org-wide summary)
│   └── dora_metrics.json          (aggregated DORA metrics)
└── [metadata files...]
```

**GitHub Pages Setup (Two Options):**

**Option A: gh-pages Branch (Recommended)**
```bash
git checkout --orphan gh-pages
cp -r public/* .           # Dashboard UI
cp -r calculations/* .     # JSON metrics
git push origin gh-pages
```

**Option B: /docs Folder on Main**
```bash
mkdir -p docs/{public,calculations}
cp -r public/* docs/public/
cp -r calculations/* docs/calculations/
git add docs/
git commit -m "Add DORA metrics"
git push
```

**How It Works:**

1. **DORA runs pipeline** (collects → calculates → validates)
2. **Outputs JSON to `calculations/`**
3. **Commits calculations/ to git**
4. **GitHub Pages automatically serves files**
5. **Dashboard reads JSON via fetch()**
6. **Metrics accessible at `https://<user>.github.io/<repo>/`**

**Key Advantages:**
- ✓ No server maintenance
- ✓ Free (included with GitHub)
- ✓ Automatic HTTPS
- ✓ Version controlled (full audit trail)
- ✓ Highly available (CDN-backed)
- ✓ Shareable public URLs
- ✓ Easy to update (just git push)
- ✓ Dashboard is static HTML/JS
- ✓ Metrics are static JSON

**Access Pattern:**
```javascript
// Dashboard fetches JSON directly
fetch('https://user.github.io/dora/calculations/per_repo/auth-service/dora.json')
  .then(r => r.json())
  .then(data => displayMetrics(data))
```

**Example Metric File:**
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

**Maintenance:**
- ✓ Metrics are JSON (human-readable)
- ✓ Stored in git (versionable)
- ✓ No database to manage
- ✓ No server to maintain
- ✓ Easy to debug (inspect files directly)
- ✓ Can be queried with any tool (jq, Python, etc.)

---

## Putting It All Together

Here's how the four constraints work together:

```
USER INPUT
├─ 1. Manually exports JIRA data (CSV/JSON)
│  └─ Stores in: jira_exports/<project>.csv
│
├─ 2. Creates .dora.md in each repository
│  └─ Links to JIRA export + Confluence
│
└─ 3. Repositories have read-only access
   └─ DORA clones them (shallow, non-intrusive)

DORA PIPELINE
├─ Collects git data (read-only clone analysis)
├─ Collects JIRA data (parses export files)
├─ Collects docs data (reads .dora.md files)
└─ Calculates metrics (merges all data)

OUTPUT
├─ Generates JSON files (calculations/)
├─ Commits to git (auditable history)
└─ Deploys to GitHub Pages (easy to share)

RESULT
└─ Dashboard on GitHub Pages shows metrics + links
   └─ All non-intrusive, maintainable, auditable
```

---

## Why This Architecture?

| Aspect | Traditional | DORA Non-Intrusive |
|--------|-------------|-------------------|
| **JIRA Access** | API + credentials | CSV/JSON export |
| **Git Access** | Clone + analyze | Read-only shallow clone |
| **Documentation** | Scrape Confluence | Store links in .dora.md |
| **Output** | Database + server | JSON + GitHub Pages |
| **Maintenance** | DevOps heavy | Simple, git-based |
| **Security** | Multiple auth systems | No credentials |
| **Scalability** | Database scaling | Git/Pages scaling |
| **Auditability** | DB logs | Git history |

**The non-intrusive approach prioritizes:**
1. **Simplicity** - No complex integrations
2. **Security** - No credentials needed
3. **Maintainability** - Git-based, not database-based
4. **Accessibility** - GitHub Pages, not proprietary servers
5. **Auditability** - Version controlled, transparent

---

## Common Questions

### Q: Why not use JIRA API?
**A:** The non-intrusive approach works without API access, making it available to organizations that can't grant credentials. It's also simpler to set up.

### Q: What if the repository is private?
**A:** DORA still works! Clone with appropriate credentials (SSH key, personal token). Read-only is all that's needed.

### Q: How often should I update JIRA exports?
**A:** Weekly is typical. Can be automated with GitHub Actions for bi-weekly or monthly updates. More frequent updates cost more time/resources but provide fresher data.

### Q: Can we add real-time updates?
**A:** Not with current exports. If JIRA API access becomes available, DORA could be extended to pull live data. Export-based approach is a transitional solution.

### Q: What if Confluence links change?
**A:** Update `.dora.md` in the repository. DORA will pick up the change on next pipeline run. It's just metadata, not content.

### Q: Can metrics be kept private?
**A:** Yes! Deploy to private GitHub Pages (requires organization/team settings) or keep calculations/ branch private.

### Q: How long does the pipeline take?
**A:** Depends on repository size. Shallow clones are quick. Typically 5-30 minutes for multiple large repositories.

---

## Extending the System

The non-intrusive approach is extensible:

**Future Enhancements:**
1. Add JIRA API support (if credentials become available)
2. Add Confluence scraping (optional, for richer data)
3. Add CI/CD integration (GitHub Actions, GitLab CI)
4. Add custom metrics (domain-specific calculations)
5. Add real-time updates (webhooks instead of scheduled)

All without breaking the current non-intrusive design.

---

## Summary

The DORA system achieves **"non-intrusive metrics collection"** through:

1. **JIRA Exports** - User-provided data, no API needed
2. **Read-Only Clones** - Shallow git analysis, no modifications
3. **.dora.md Files** - Self-contained metadata per project
4. **GitHub Pages + JSON** - Maintainable, auditable output

This approach is:
- ✓ Simple to implement and maintain
- ✓ Secure (no credentials)
- ✓ Flexible (works with different JIRA/Confluence setups)
- ✓ Scalable (git-based, not database-based)
- ✓ Auditable (full version history)
- ✓ Accessible (standard web technologies)

---

## Further Reading

- [Non-Intrusive Architecture](./NON_INTRUSIVE_ARCHITECTURE.md) - System design
- [JIRA Export Guide](./JIRA_EXPORT_GUIDE.md) - How to export JIRA data
- [Project Configuration Guide](./PROJECT_CONFIG_GUIDE.md) - How to create .dora.md
- [GitHub Pages Deployment](./GITHUB_PAGES_DEPLOYMENT.md) - Deployment options
