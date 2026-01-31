# DORA Metrics Dashboard

A professional, evidence-backed R&D metrics system with a clear data pipeline.

## Architecture

```
INPUT → COLLECTION → CALCULATION → PRESENTATION
```

### 1. INPUT Layer
**File:** `ReposInput.md`

Define all repositories to be analyzed. This is the source of truth.

```markdown
## ProjectName
repo: https://github.com/owner/repo
branch: main
language: java
ci: github-actions
coverage: jacoco
```

### 2. COLLECTION Layer
**Folder:** `git_artifacts/` and `ci_artifacts/`

Extracts raw data:
- Git commits, authors, timestamps
- CI/CD artifacts (tests, coverage reports)

Run with:
```bash
npm run collect
```

### 3. CALCULATION Layer
**Folder:** `calculations/`

Processes raw data into normalized metrics:
- Per-repository metrics
- Global organization metrics
- Quality validation

Run with:
```bash
npm run calculate
```

### 4. PRESENTATION Layer
**Folder:** `public/`

Read-only dashboard that displays calculated metrics. No direct access to git or CI systems.

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.8+
- Git

### Installation
```bash
npm install
```

### Running the Pipeline

Run the full pipeline (collection → calculation → validation):
```bash
npm run pipeline
```

Or run individual steps:
```bash
npm run collect      # Collection layer
npm run calculate    # Calculation layer
npm run validate     # Quality gates
```

### Start the Dashboard
```bash
npm run dev
```

Then open `http://localhost:5173` (or as shown in console).

## Project Structure

```
DORA/
├── ReposInput.md           # Source of truth - repositories to analyze
├── git_artifacts/          # Raw git data
├── ci_artifacts/           # Raw CI data
├── calculations/           # Processed metrics
│   ├── per_repo/          # Per-repository metrics
│   └── global/            # Organization-wide metrics
├── public/                # Dashboard UI
├── src/
│   └── scripts/           # Pipeline scripts
│       ├── 01_collect.py
│       ├── 02_calculate.py
│       └── 03_validate.js
└── package.json

```

## Key Rules

### 1. No Direct Access
- Dashboard does NOT access git repositories or CI systems
- All data flows through the pipeline

### 2. Data Integrity
- Truth lives in `calculations/`
- If a metric cannot be calculated: show as `N/A`
- Never guess or fabricate data

### 3. Traceability
- Every calculation includes:
  - `metric_id`
  - `inputs` (source files)
  - `formula` or `method`
  - `calculated_at` (timestamp)

### 4. Quality Gates
The validation layer fails if:
- Dashboard references missing calculations
- Calculations reference missing raw inputs
- Values out of bounds
- Any approximations detected

## Adding New Repositories

1. Edit `ReposInput.md`
2. Add new repository entry:
```markdown
## MyNewProject
repo: https://github.com/owner/myproject
branch: main
language: typescript
ci: github-actions
coverage: nyc
```

3. Run the pipeline:
```bash
npm run pipeline
```

4. Dashboard updates automatically

## Metrics Calculated

### Per-Repository
- **Commits**: Total commits, frequency, timeline
- **Team Diversity**: Number of contributors
- **Churn**: Code changes over time (when available)
- **Coverage**: Test coverage percentage (when available)

### Global
- **Total Commits**: Sum across all repos
- **Contributors**: Unique team members
- **Repos Analyzed**: Number in scope
- **Data Completeness**: Which metrics available

## CI/CD Integration

This project is designed to work in CI pipelines:

```yaml
# GitHub Actions example
- name: Run DORA Pipeline
  run: npm run pipeline

- name: Validate Data
  run: npm run validate

- name: Build Dashboard
  run: npm run build

- name: Deploy
  run: npm run deploy
```

## Troubleshooting

### Collection fails
- Check repository URLs in `ReposInput.md`
- Verify git is installed and can access repositories
- Check network connectivity

### No metrics calculated
- Run `npm run collect` first to generate raw data
- Check `git_artifacts/` folder exists and has data
- Review script output for errors

### Dashboard shows N/A for all metrics
- Run `npm run collect`
- Run `npm run calculate`
- Run `npm run validate`
- Check `calculations/` folder has JSON files

## Design Philosophy

This dashboard follows these principles:

- **Evidence-backed**: Only metrics derived from actual data
- **Transparent**: All calculations traceable to source
- **Professional**: Calm, clean UX - no false precision
- **Maintainable**: Clear data flow, separated concerns
- **Scalable**: Add repos by editing ReposInput.md

## License

MIT
