# DORA: Quick Reference Card

**A one-page cheat sheet for getting things done with DORA.**

---

## Installation (First Time)

```bash
# Clone repository
git clone https://github.com/your-org/DORA.git
cd DORA

# Install Python dependencies
pip install -r requirements.txt

# Verify
python3 -c "import yaml; print('✓ Ready')"
```

---

## Running the Pipeline

```bash
# Full pipeline (recommended)
./run_pipeline.sh

# Individual steps (for debugging)
python3 src/collection/collect_git.py         # Extract git data
python3 src/collection/collect_ci.py          # Extract CI data
python3 src/calculations/calculate.py         # Calculate metrics
python3 src/validation/validate.py            # Validate quality

# View dashboard
open public/index.html
# OR
python3 -m http.server 8000
# Then: http://localhost:8000/public/
```

---

## Adding a Repository

### 1. Update `repos.yaml`
```yaml
my-project:
  repo: https://github.com/org/my-project.git
  branch: main
  language: python
  ci_system: github-actions
  coverage_tools: [pytest-cov]
```

### 2. Create `.dora.md` in repository root
```markdown
# DORA Configuration
- **Name:** My Project
- **Repository:** https://github.com/org/my-project
- **JIRA Export:** jira_exports/my-project.csv
- **Docs:** https://confluence.company.com/...
```

### 3. Export JIRA data (optional)
Save to `jira_exports/my-project.csv`

### 4. Run pipeline
```bash
./run_pipeline.sh
```

---

## File Locations

| What | Where |
|-----|-------|
| Repository config | `repos.yaml` |
| Python collectors | `src/collection/` |
| Python calculators | `src/calculations/` |
| Python validators | `src/validation/` |
| Raw git data | `git_artifacts/[repo]/` |
| Raw CI data | `ci_artifacts/[repo]/` |
| Metrics (JSON) | `calculations/per_repo/[repo]/` |
| Dashboard | `public/index.html` |
| Documentation | `docs/` |

---

## Pipeline Outputs

```
git_artifacts/[repo]/
  ├── commits.json        # Extracted commits
  ├── authors.json        # Unique authors
  ├── tags.json          # Git tags (for deployment frequency)
  └── timeline.json      # Commit timeline

calculations/per_repo/[repo]/
  ├── commits.json       # Commit metrics
  ├── contributors.json  # Contributor analysis
  ├── coverage.json      # Test coverage
  ├── dora_frequency.json # Deployment frequency
  ├── lead_time.json     # Lead time metric
  └── velocity.json      # Velocity trend

calculations/global/
  ├── summary.json       # Organization summary
  ├── commits.json       # Global commit stats
  └── contributors.json  # Global contributor stats
```

---

## DORA Metrics Explained

| Metric | Measures | Calculation | Example |
|--------|----------|-------------|---------|
| **Deployment Frequency** | How often code is deployed | Count git tags / months | 1.25 per month |
| **Lead Time** | Time from commit to deployment | Average time between commits | 6.2 hours |
| **Change Failure Rate** | % of deployments that break things | Failed deployments / total | 5% |
| **Time to Recovery** | How fast issues get fixed | Average incident resolution time | 2.5 hours |

---

## Configuration: repos.yaml

```yaml
repositories:
  project-name:
    repo: https://github.com/org/project.git      # Git URL
    branch: main                                    # Branch to analyze
    language: [python|javascript|go|java|mixed]   # Code language
    ci_system: [github-actions|gitlab-ci|jenkins] # CI system
    coverage_tools: [pytest-cov|nyc|JaCoCo]      # Coverage tools
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

---

## Configuration: .dora.md (in each repository)

```markdown
# DORA Configuration

## Project Information
- **Name:** Project Name
- **Repository:** https://github.com/org/project
- **Team:** Team Name
- **Owner:** owner@company.com

## JIRA Integration
- **Project Key:** PROJ
- **Export File:** jira_exports/project.csv
- **Epics:** EPIC-1, EPIC-2, EPIC-3

## Documentation Links
- **Architecture:** https://confluence.company.com/...
- **Deployment:** https://confluence.company.com/...
- **Runbook:** https://confluence.company.com/...

## Metrics
- **Language:** Python
- **CI System:** GitHub Actions
- **Coverage Tool:** pytest-cov
```

---

## Troubleshooting

### Pipeline fails: "Clone failed"
```bash
# Test repository URL
git clone --depth=1 https://github.com/org/project.git test
# If it fails, check:
# 1. URL is correct
# 2. Repository exists
# 3. Network is working
```

### Dashboard shows N/A
```bash
# Ensure calculations exist
ls -la calculations/per_repo/

# Force recalculation
./run_pipeline.sh

# Clear browser cache
# Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)
```

### JIRA export not found
```bash
# Check file exists
ls -la jira_exports/

# Verify filename matches repos.yaml
# Expected: jira_exports/[project-name].csv
```

### Validation fails
```bash
# Find problems
grep -r "~\|approx" calculations/

# DORA rule: No approximations
# Use exact numbers or null with reason
```

---

## Key Principles (Remember These!)

✅ **DO:**
- Use read-only access only
- Extract data, never modify
- Calculate from real source code
- Document every metric
- Share via GitHub Pages
- Version everything in Git

❌ **DON'T:**
- Store API keys
- Modify target repositories
- Guess or approximate numbers
- Access repositories directly in dashboard
- Use invalid configuration formats
- Skip validation checks

---

## Commands Cheat Sheet

```bash
# Install
pip install -r requirements.txt

# Run everything
./run_pipeline.sh

# Debug: step by step
python3 src/collection/collect_git.py
python3 src/calculations/calculate.py
python3 src/validation/validate.py

# View results
open public/index.html
# OR
python3 -m http.server 8000

# Check dashboard
open calculations/MANIFEST.json

# View raw data
cat calculations/per_repo/[repo]/commits.json

# Deploy to GitHub Pages
git add calculations/ public/
git commit -m "Update DORA metrics"
git push origin main

# Test configuration
python3 -c "import yaml; yaml.safe_load(open('repos.yaml'))"
```

---

## Calculation JSON Format (What You'll See)

```json
{
  "metric_id": "repo.dora.deployment_frequency",
  "repo": "auth-service",
  "inputs": ["git_artifacts/auth-service/tags.json"],
  "values": {
    "tags_total": 15,
    "period_months": 12,
    "frequency_per_month": 1.25,
    "frequency_per_week": 0.288,
    "frequency_per_day": 0.041
  },
  "method": "Count git tags matching version pattern; divide by period in months",
  "calculated_at": "2024-02-03T10:00:00Z",
  "quality_gates": {
    "status": "PASS",
    "checks": {
      "has_all_inputs": true,
      "no_approximations": true,
      "values_in_range": true,
      "well_documented": true
    }
  }
}
```

---

## Files You Need to Edit

| File | When | What |
|------|------|------|
| `repos.yaml` | Adding new projects | Add repository configuration |
| `ReposInput.md` | Adding new projects | List repositories to analyze |
| `.dora.md` | Setting up a project | Create in each repository |
| `jira_exports/*.csv` | Has JIRA data | Export and save CSV files |
| `run_pipeline.sh` | Customizing pipeline | Edit if you need special logic |

---

## Files You Should NOT Edit

| File | Why |
|------|-----|
| `calculations/*` | Auto-generated by pipeline |
| `git_artifacts/*` | Auto-generated by collection |
| `ci_artifacts/*` | Auto-generated by collection |
| `.github/workflows/*` | CI configuration (only if advanced) |

---

## Deployment to GitHub Pages

```bash
# Option 1: Use gh-pages branch
git checkout --orphan gh-pages
cp -r public/* .
cp -r calculations/ .
git add .
git commit -m "Deploy DORA dashboard"
git push origin gh-pages

# Then in GitHub Settings:
# - GitHub Pages source: gh-pages branch

# Option 2: Use /docs folder
mkdir -p docs
cp -r public/* docs/
cp -r calculations docs/
git add docs/
git commit -m "Deploy DORA dashboard"
git push origin main

# Then in GitHub Settings:
# - GitHub Pages source: main branch, /docs folder
```

---

## Getting Help

```bash
# View comprehensive guide
open docs/COMPLETE_BEGINNER_GUIDE.md

# View architecture
open docs/NON_INTRUSIVE_ARCHITECTURE.md

# View visual guide
open docs/VISUAL_ARCHITECTURE_GUIDE.md

# View JIRA guide
open docs/JIRA_EXPORT_GUIDE.md

# View deployment guide
open docs/GITHUB_PAGES_DEPLOYMENT.md
```

---

## Quick Decision Tree

```
Need to...

├─ Set up DORA?
│  └─ Run: ./run_pipeline.sh
│
├─ Add a project?
│  └─ Edit: repos.yaml, ReposInput.md, create .dora.md
│
├─ Add JIRA data?
│  └─ Export CSV from JIRA → save to jira_exports/
│
├─ View dashboard?
│  └─ Run: open public/index.html
│
├─ Troubleshoot?
│  └─ Check: troubleshooting section below
│
├─ Deploy to GitHub Pages?
│  └─ Follow: deployment options above
│
├─ Understand architecture?
│  └─ Read: VISUAL_ARCHITECTURE_GUIDE.md
│
└─ Replicate from scratch?
   └─ Use: DoraReplicatePROMPT section in COMPLETE_BEGINNER_GUIDE.md
```

---

## One-Minute Demo

```bash
# Get started in 60 seconds
cd DORA
pip install -r requirements.txt              # 5 sec
./run_pipeline.sh                            # 30 sec
open public/index.html                       # 5 sec
# Browse dashboard                           # 20 sec

# ✓ Done! You now have metrics
```

---

**Need more details?** → See `docs/COMPLETE_BEGINNER_GUIDE.md`
