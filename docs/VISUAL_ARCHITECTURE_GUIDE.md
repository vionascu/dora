# DORA: Visual Architecture Guide

**A visual walkthrough of how DORA works—perfect for visual learners!**

---

## 1. The Big Picture: DORA in One Image

```
                    YOUR REPOSITORIES
                         ↓
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
     Git Repos      JIRA Exports    Project Docs
     (Source)       (Features)      (Metadata)
          ↓              ↓              ↓
          └──────────────┼──────────────┘
                         ↓
          ╔══════════════════════════════╗
          ║   COLLECTION LAYER           ║  ← Extract raw data
          ║  (Python scripts)            ║
          ╚══════════════════════════════╝
                         ↓
           git_artifacts/ + ci_artifacts/ + jira_artifacts/
                    (raw JSON files)
                         ↓
          ╔══════════════════════════════╗
          ║   CALCULATION LAYER          ║  ← Compute metrics
          ║  (Python scripts)            ║
          ╚══════════════════════════════╝
                         ↓
              calculations/ (JSON metrics)
                    per_repo/ + global/
                         ↓
          ╔══════════════════════════════╗
          ║   VALIDATION LAYER           ║  ← Check quality
          ║  (Python scripts)            ║
          ╚══════════════════════════════╝
                         ↓
          ╔══════════════════════════════╗
          ║   PRESENTATION LAYER         ║  ← Display results
          ║  (HTML/CSS/JavaScript)       ║
          ║  public/index.html           ║
          ╚══════════════════════════════╝
                         ↓
                  GitHub Pages
                  (shareable URL)
```

---

## 2. How Data Flows (Step-by-Step Example)

### Example: Analyzing Deployment Frequency

```
STEP 1: Repository has tags
┌─────────────────────────────────────┐
│ Git tags:                           │
│ - v1.0.0 (Jan 2024)                 │
│ - v1.1.0 (Feb 2024)                 │
│ - v1.2.0 (Mar 2024)                 │
│ - v2.0.0 (Apr 2024)                 │
│ ... 11 more tags ...                │
│                                     │
│ TOTAL: 15 tags in 12 months         │
└─────────────────────────────────────┘

              ↓

STEP 2: collect_git.py extracts this
┌─────────────────────────────────────┐
│ git_artifacts/my-repo/tags.json     │
│                                     │
│ {                                   │
│   "total_tags": 15,                 │
│   "tags": [                         │
│     "v1.0.0", "v1.1.0", ...        │
│   ]                                 │
│ }                                   │
└─────────────────────────────────────┘

              ↓

STEP 3: calculate.py processes this
┌─────────────────────────────────────┐
│ Input: 15 tags, 12 months           │
│                                     │
│ Calculation:                        │
│ 15 tags ÷ 12 months = 1.25          │
│                                     │
│ Frequency: 1.25 deployments/month   │
└─────────────────────────────────────┘

              ↓

STEP 4: Result stored
┌─────────────────────────────────────┐
│ calculations/per_repo/my-repo/      │
│   dora_frequency.json               │
│                                     │
│ {                                   │
│   "metric_id": "repo.dora.freq",    │
│   "frequency_per_month": 1.25,      │
│   "inputs": [...],                  │
│   "method": "count tags / months"   │
│ }                                   │
└─────────────────────────────────────┘

              ↓

STEP 5: Dashboard displays it
┌─────────────────────────────────────┐
│  📊 Deployment Frequency            │
│  ┌───────────────────────┐           │
│  │ 1.25 deployments/mo   │           │
│  └───────────────────────┘           │
│                                     │
│  (Chart showing trend over time)    │
│                                     │
│  [View Raw Data]  [Audit Trail]    │
└─────────────────────────────────────┘
```

---

## 3. The 5 Layers of DORA

### Layer 1: INPUT
```
┌─────────────────────────────────────┐
│ LAYER 1: INPUT CONFIGURATION        │
├─────────────────────────────────────┤
│                                     │
│ 📄 repos.yaml                       │
│    ├─ Repository URLs               │
│    ├─ Branches                      │
│    └─ Languages                     │
│                                     │
│ 📄 ReposInput.md                    │
│    └─ Human-readable list           │
│                                     │
│ Defines WHAT to analyze             │
│                                     │
└─────────────────────────────────────┘
      ↓
   (Configuration loaded)
```

### Layer 2: COLLECTION
```
┌─────────────────────────────────────┐
│ LAYER 2: COLLECTION                 │
├─────────────────────────────────────┤
│                                     │
│  🔍 collect_git.py                  │
│     ├─ Clone repos (read-only)      │
│     └─ Extract commits, tags        │
│        → git_artifacts/             │
│                                     │
│  🔍 collect_ci.py                   │
│     ├─ Read CI logs                 │
│     └─ Extract build/test data      │
│        → ci_artifacts/              │
│                                     │
│  🔍 scan_github_artifacts.py        │
│     ├─ Find test results            │
│     └─ Extract coverage             │
│        → test_artifacts/            │
│                                     │
│ Collects RAW DATA                   │
│ (No processing, just extraction)    │
│                                     │
└─────────────────────────────────────┘
      ↓
  JSON files created
  (*_artifacts/ folders)
```

### Layer 3: CALCULATION
```
┌─────────────────────────────────────┐
│ LAYER 3: CALCULATION                │
├─────────────────────────────────────┤
│                                     │
│ 📊 calculate.py                     │
│    ├─ Read all *_artifacts/         │
│    ├─ Merge data                    │
│    ├─ Compute metrics:              │
│    │  - Deployment Frequency        │
│    │  - Lead Time                   │
│    │  - Test metrics                │
│    │  - Contributor stats           │
│    └─ Write calculations/            │
│                                     │
│ PROCESSES and MERGES data           │
│ (Creates metrics from raw data)     │
│                                     │
└─────────────────────────────────────┘
      ↓
  JSON metrics created
  (calculations/ folders)
```

### Layer 4: VALIDATION
```
┌─────────────────────────────────────┐
│ LAYER 4: VALIDATION                 │
├─────────────────────────────────────┤
│                                     │
│ ✓ validate.py checks:               │
│                                     │
│  ✗ No approximations (~, approx)   │
│  ✗ No out-of-range values          │
│  ✗ No missing inputs               │
│  ✓ All inputs documented           │
│  ✓ Calculations are traceable      │
│                                     │
│ QUALITY GATES                       │
│ (Ensures data integrity)            │
│                                     │
│ Result: PASS or FAIL                │
│ (Pipeline stops if FAIL)            │
│                                     │
└─────────────────────────────────────┘
      ↓
  Pass → continue to Layer 5
  Fail → pipeline stops
```

### Layer 5: PRESENTATION
```
┌─────────────────────────────────────┐
│ LAYER 5: PRESENTATION               │
├─────────────────────────────────────┤
│                                     │
│ 📊 public/index.html                │
│    ├─ Reads calculations/           │
│    ├─ Renders charts                │
│    ├─ Shows metrics                 │
│    └─ Links to raw data             │
│                                     │
│ 🎨 report.js (logic)                │
│    └─ Data loading, charting        │
│                                     │
│ 🎨 report.css (styling)             │
│    └─ Professional design           │
│                                     │
│ DISPLAYS RESULTS                    │
│ (Interactive dashboard)             │
│                                     │
│ Hosted on GitHub Pages              │
│ (public URL)                        │
│                                     │
└─────────────────────────────────────┘
      ↓
  Dashboard accessible
  (https://user.github.io/dora/)
```

---

## 4. File Organization

```
DORA/
│
├── 📂 Input Layer
│   ├── repos.yaml              ← Configuration
│   └── ReposInput.md           ← Repository list
│
├── 📂 Collection Layer
│   ├── src/collection/
│   │   ├── collect_git.py
│   │   ├── collect_ci.py
│   │   └── scan_github_artifacts.py
│   │
│   └── [artifacts folders]
│       ├── git_artifacts/      ← Raw git data
│       ├── ci_artifacts/       ← Raw CI data
│       └── test_artifacts/     ← Raw test data
│
├── 📂 Calculation Layer
│   ├── src/calculations/
│   │   ├── calculate.py
│   │   └── calculate_test_metrics.py
│   │
│   └── calculations/           ← Processed metrics
│       ├── per_repo/
│       │   ├── project1/
│       │   ├── project2/
│       │   └── ...
│       └── global/
│
├── 📂 Validation Layer
│   └── src/validation/
│       └── validate.py
│
├── 📂 Presentation Layer
│   └── public/
│       ├── index.html          ← Dashboard
│       ├── report.js
│       └── report.css
│
├── 🔧 Orchestration
│   └── run_pipeline.sh
│
└── 📚 Documentation
    └── docs/
        ├── COMPLETE_BEGINNER_GUIDE.md
        └── ...
```

---

## 5. Data Formats (At Each Layer)

### At Layer 2 (Collection Output)
```json
// git_artifacts/project1/commits.json
{
  "repository": "my-project",
  "total_commits": 1250,
  "date_range": {
    "first": "2020-01-15",
    "last": "2024-02-03"
  },
  "authors": ["alice@company.com", "bob@company.com", ...]
}
```

### At Layer 3 (Calculation Output)
```json
// calculations/per_repo/project1/dora_frequency.json
{
  "metric_id": "repo.dora.deployment_frequency",
  "repo": "my-project",
  "inputs": ["git_artifacts/project1/tags.json"],
  "values": {
    "tags_total": 15,
    "period_months": 12,
    "frequency_per_month": 1.25
  },
  "method": "Count git tags / period in months",
  "calculated_at": "2024-02-03T10:00:00Z",
  "quality_gates": {
    "status": "PASS"
  }
}
```

### At Layer 5 (Dashboard Display)
```html
<!-- public/index.html renders -->
<div class="metric-card">
  <h3>Deployment Frequency</h3>
  <div class="value">1.25</div>
  <div class="unit">deployments/month</div>
  <canvas id="frequency-chart"></canvas>
  <a href="...">View Raw Data</a>
</div>
```

---

## 6. The Full Pipeline in One Command

```
./run_pipeline.sh
    ↓
┌─────────────────────────────────────┐
│ INPUT LAYER                         │
│ - Load repos.yaml                   │
│ - Parse ReposInput.md               │
└─────────────────────────────────────┘
    ↓
    python3 src/collection/collect_git.py
    ↓
┌─────────────────────────────────────┐
│ COLLECTION LAYER                    │
│ - Clone repos                       │
│ - Extract commits, tags             │
│ - Create git_artifacts/             │
└─────────────────────────────────────┘
    ↓
    python3 src/collection/collect_ci.py
    ↓
┌─────────────────────────────────────┐
│ COLLECTION LAYER (continued)        │
│ - Extract CI data                   │
│ - Extract test data                 │
│ - Create ci_artifacts/ & test_...   │
└─────────────────────────────────────┘
    ↓
    python3 src/calculations/calculate.py
    ↓
┌─────────────────────────────────────┐
│ CALCULATION LAYER                   │
│ - Merge all artifacts               │
│ - Compute metrics                   │
│ - Create calculations/              │
└─────────────────────────────────────┘
    ↓
    python3 src/validation/validate.py
    ↓
┌─────────────────────────────────────┐
│ VALIDATION LAYER                    │
│ - Check quality gates               │
│ - Verify data integrity             │
│ - PASS or FAIL                      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ PRESENTATION LAYER                  │
│ (automatic)                         │
│ - Dashboard reads calculations/     │
│ - Renders metrics                   │
│ - Ready to view                     │
└─────────────────────────────────────┘
    ↓
✓ PIPELINE COMPLETE

open public/index.html
```

---

## 7. What Happens to Your Code?

```
YOUR GIT REPOSITORY
│
├─ Commits ──→ DORA clones (read-only) ──→ Extracts ──→ commit_count
├─ Tags     ──→ DORA clones (read-only) ──→ Extracts ──→ deployment_frequency
├─ Authors  ──→ DORA clones (read-only) ──→ Extracts ──→ contributor_count
└─ History  ──→ DORA clones (read-only) ──→ Extracts ──→ lead_time

                      (no changes made!)


YOUR JIRA PROJECT
│
├─ Epic 1 ────→ You export CSV ──→ DORA parses ──→ epic_status
├─ Epic 2 ────→ You export CSV ──→ DORA parses ──→ epic_progress
└─ Stories ───→ You export CSV ──→ DORA parses ──→ story_count

                (no API access!)


YOUR DORA PROJECT
│
├─ git_artifacts/ ──────────────────────┐
├─ ci_artifacts/                        ├─→ calculations/ ──→ public/
├─ jira_artifacts/ ─────────────────────┘              (JSON)    (HTML)
│
└─ All versioned in Git
   (Full audit trail, trackable, reproducible)
```

---

## 8. Key Principles Visualized

### Principle 1: Non-Intrusive Access
```
Your Repository          DORA System
     │                       │
     │ ←── read-only clone ──┤
     │                       │
     ├─ .git/ (analyzed)     │
     ├─ src/ (analyzed)      │
     ├─ tests/ (analyzed)    │
     │                       │
     └─ (NO changes)    (NO modifications made)
```

### Principle 2: Traceable Metrics
```
Git Tag v1.2.0
    ↓
git_artifacts/.../tags.json
    ↓
calculate.py
    ↓
calculations/.../dora_frequency.json
    {
      "inputs": ["git_artifacts/.../tags.json"],  ← Source
      "method": "count tags / period",             ← How
      "calculated_at": "...",                      ← When
      "values": {"frequency": 1.25}                ← Result
    }
    ↓
public/index.html [View Raw Data]  ← Link back to source
```

### Principle 3: Quality Gates
```
calculated_value = "~42"    ← Has approximation ~
     ↓
Validation Layer
     ↓
❌ REJECTED (no approximations allowed)
     ↓
Fix: Remove approximation or recalculate
     ↓
calculated_value = 42       ← Exact value
     ↓
Validation Layer
     ↓
✓ PASSED
```

---

## 9. Adding a New Repository (Visual)

```
BEFORE                          AFTER
┌─────────────────┐            ┌─────────────────┐
│ repos.yaml      │            │ repos.yaml      │
│                 │            │                 │
│ - project1      │     add     │ - project1      │
│ - project2      │ ───────→    │ - project2      │
│ - project3      │   entry     │ - project3      │
│                 │            │ - project4  ← NEW
│                 │            │                 │
└─────────────────┘            └─────────────────┘
        ↓                               ↓
  Dashboard shows                  run_pipeline.sh
  3 projects                              ↓
                            Dashboard shows
                            4 projects
                                    ↓
                            new project data
                            appears in charts
```

---

## 10. Dashboard: What You'll See

```
DORA METRICS DASHBOARD
═══════════════════════════════════════════════════════

📊 KEY FINDINGS
  • Total Commits: 5,234
  • Repositories: 4
  • Contributors: 28
  • Current Velocity: 12 commits/day

───────────────────────────────────────────────────────

📈 DEPLOYMENT FREQUENCY
  Project 1:  1.25 deployments/month  [====━━━━]
  Project 2:  2.10 deployments/month  [=======━]
  Project 3:  0.75 deployments/month  [==━━━━━]

───────────────────────────────────────────────────────

⏱️  LEAD TIME
  Project 1:  6.2 hours average  [Chart showing trend]
  Project 2:  4.5 hours average
  Project 3:  8.1 hours average

───────────────────────────────────────────────────────

🧪 TEST COVERAGE
  Project 1:  82.5%  [████████░░]
  Project 2:  91.2%  [█████████░]
  Project 3:  65.3%  [██████░░░░]

───────────────────────────────────────────────────────

👥 CONTRIBUTORS
  Over Time: [Chart showing growth trend]
  Active Now: 28

───────────────────────────────────────────────────────

✓ DATA QUALITY
  Status: PASSED
  Last Updated: 2024-02-03 10:30 AM
  Quality Checks: All passed

───────────────────────────────────────────────────────

🔗 RAW DATA ACCESS
  [View All Calculations]  [Audit Trail]  [Download JSON]
```

---

## Quick Mental Model

Think of DORA like **a librarian**:

```
LIBRARIAN ANALOGY:

Your Code Repository  = Library
(filled with books)

DORA              = Librarian

Steps:
1. Librarian visits library (collect_git.py)
   - Counts books (commits)
   - Notes publication dates (tags)
   - Records authors (contributors)
   - Nothing is changed!

2. Librarian organizes notes (calculate.py)
   - "Books per month: 4"
   - "Unique authors: 12"
   - "Time between books: 2 weeks avg"

3. Librarian checks notes for accuracy (validate.py)
   - Are numbers reasonable?
   - Are sources documented?
   - Anything suspicious?

4. Librarian creates report (public/index.html)
   - Displays findings
   - Links to original books
   - Shows trends

5. Report goes on bulletin board (GitHub Pages)
   - Everyone can read it
   - Numbers are traceable to books
   - Process is transparent
```

---

## Summary

DORA is like an **X-ray for your development team**:
- Takes snapshots of code health
- Shows trends over time
- Points out patterns
- Is transparent and auditable
- Never gets in the way

The 5-layer architecture ensures:
1. **INPUT** ← Configuration
2. **COLLECTION** ← Raw data extraction
3. **CALCULATION** ← Metric computation
4. **VALIDATION** ← Quality assurance
5. **PRESENTATION** ← Visual dashboard

Each layer is independent and can be understood separately, but together they create a powerful, traceable system for understanding software development.

**Now you understand the architecture!** 🎉
