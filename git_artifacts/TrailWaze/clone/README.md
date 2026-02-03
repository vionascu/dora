# Trailwaze

[![pipeline status](https://gitlab.com/vic.ionascu/trailwaze/badges/main/pipeline.svg)](https://gitlab.com/vic.ionascu/trailwaze/-/pipelines)

Offline-first hiking navigation inspired by Waze.

## Repo structure

- Mobile app (Expo / React Native): `apps/mobile`
- Product epics and stories: `docs/mvp-epics.md`

## Web quickstart (step-by-step)

```bash
cd apps/mobile
npm install
npx expo start --web
```

1) Open the URL shown in the terminal.
2) You should see the map with hiking trails highlighted.
3) Click "Raporteaza", pick a report type, then click the map to drop a pin.

## Run the app (native)

```bash
cd apps/mobile
npm install
npx expo start
```

## Reporting guide (web)

1) Click "Raporteaza".
2) Choose a report type (Urs, Copac cazut, Grohotis, Cabana full).
3) Click the map where the issue is located.
4) A pin appears with the report type initial.

Reports are stored in memory during the session.

## Tests

```bash
cd apps/mobile
npm test
```

## Dashboard

Generate an interactive repository dashboard with comprehensive project metrics and analytics:

```bash
python3 tools/trailwaze_dashboard.py
```

This generates a dashboard and opens a local web server at `http://localhost:4173/` showing:

**Key Metrics:**
- 📈 Total Commits (from git history)
- 📝 Lines of Code (source, tests, config, docs)
- ✅ Total Tests (detected from test files)
- 🧪 Test Coverage (calculated from LOC ratio)
- 👥 Contributors (from git authors)
- ⏱️ Project Age (days since first commit)

**Interactive Charts:**
- Commit Growth (timeline)
- Code Breakdown (source/tests/config/docs)
- Test Distribution
- File Types Distribution
- Project Health Metrics (radar)

**Data Tables:**
- Test Files (with test counts and status)
- Source Code Files (with LOC)
- Project Summary (repository details and metrics)

### Options

```bash
python3 tools/trailwaze_dashboard.py                    # Current repository
python3 tools/trailwaze_dashboard.py --repo /path/to/repo  # Scan any repository
python3 tools/trailwaze_dashboard.py --port 5000        # Custom port
python3 tools/trailwaze_dashboard.py --out /tmp/dash    # Custom output directory
python3 tools/trailwaze_dashboard.py --open             # Auto-open in browser
```

### Works with Any Repository

The dashboard automatically detects and analyzes:
- Git commit history and contributors
- Code structure (all major languages)
- Test files and frameworks (Jest, Pytest, JUnit, etc.)
- Dependencies (npm, pip, go modules, etc.)
- CI/CD platforms (GitLab CI, GitHub Actions, etc.)
- Project organization and code quality

## CI pipeline

GitLab CI runs two stages:

- `verify`: prints Node and npm versions
- `test`: installs dependencies and runs `npm test` for the mobile app
