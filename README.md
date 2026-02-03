# DORA Metrics Dashboard

## R&D Metrics Report - Live Dashboard

**View the interactive report:** [Open Dashboard](../public/index.html)

### What's Included

- **Activity Metrics**: Total commits, repositories, contributors, velocity
- **Test Coverage**: Test files, frameworks, epics and user stories
- **DORA Metrics**: Lead time, deployment frequency
- **Repository Analysis**: Per-repo breakdown with all metrics
- **Data Validation**: Full quality gates passing

### Data Sources

- **Git Artifacts**: Direct from GitHub repositories
- **CI/CD Data**: From GitHub Actions workflows
- **Test Files**: Scanned from project directories
- **Epics & Stories**: Found in documentation and test files

### Repositories Analyzed

1. **TrailEquip** - Java microservices (JUnit, Jest/Mocha)
2. **TrailWaze** - React Native mobile app (Jest/Mocha)
3. **RnDMetrics** - Python analytics (unittest)

### Pipeline Status

```
✓ Collection Layer (Git & CI artifacts)
✓ Calculation Layer (Metrics computed)
✓ Validation Layer (All gates pass)
✓ Presentation Layer (Dashboard live)
```

### View Raw Data

- [Calculations Folder](../calculations/)
- [Git Artifacts](../git_artifacts/)
- [CI Artifacts](../ci_artifacts/)
- [Validation Manifest](../calculations/MANIFEST.json)
