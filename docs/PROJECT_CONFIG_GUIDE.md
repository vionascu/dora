# Project Configuration Guide (.dora.md)

This guide explains how to create and maintain `.dora.md` configuration files in your repositories.

---

## Overview

Each repository analyzed by DORA should have a `.dora.md` file at its root. This file:

- ✓ Links to JIRA exports (so epics can be correlated)
- ✓ Links to Confluence documentation
- ✓ Contains project metadata
- ✓ Allows DORA to work without API access
- ✓ Is human-readable and easily updated

---

## File Location

```
<repository-root>/
├── .dora.md              ← Create this file
├── src/
├── README.md
├── pom.xml
└── ...
```

---

## Template

Copy and customize this template:

```markdown
# DORA Configuration: <Project Name>

## Project Information

- **Name:** Authentication Service
- **Purpose:** Handle user authentication and authorization
- **Team:** Backend Team
- **GitHub Repository:** https://github.com/myorg/auth-service
- **Primary Language:** Java / Python / TypeScript
- **Framework:** Spring Boot / Django / Express.js

---

## JIRA Integration (via Export)

### JIRA Project Key
- **Project Key:** AUTH
- **Jira Base URL:** https://jira.company.com
- **Export File:** jira_exports/auth-service.csv

### Active Epics
Link to the JIRA export and list active epics. Users should reference the CSV/JSON file.

```csv
Epic Key,Epic Name,Status
EPIC-1,Authentication Core,Done
EPIC-2,OAuth2 Integration,In Progress
EPIC-5,Security Hardening,To Do
```

### Adding Commits to Epics
Include JIRA issue keys in commit messages:

```bash
git commit -m "Implement login page

EPIC-1: Authentication Core
- Add email validation
- Add password field
"
```

---

## Confluence Documentation

### Architecture
- **URL:** https://confluence.company.com/display/ARCH/auth-service
- **Last Updated:** 2026-02-01
- **Maintainer:** @engineering-team

### API Reference
- **URL:** https://confluence.company.com/display/API/auth-service
- **Last Updated:** 2026-01-15
- **Scope:** REST endpoints, authentication flows

### Deployment & Runbook
- **URL:** https://confluence.company.com/display/OPS/auth-deployment
- **Last Updated:** 2026-02-01
- **Scope:** Deployment process, monitoring, troubleshooting

### Additional Documentation
- **Security Policy:** https://confluence.company.com/display/SEC/auth-security
- **Database Schema:** https://confluence.company.com/display/DB/auth-tables

---

## Deployment Information

### Production Environment
- **Primary Branch:** main
- **Deployment Frequency:** Every 2 weeks
- **Last Deployment:** 2026-02-01
- **Deployment URL:** https://auth.company.com
- **Monitoring:** https://grafana.company.com/auth-service

### Version Tagging
- **Tag Pattern:** v*.*.* (e.g., v1.2.3)
- **Release Branch:** release/* (e.g., release/1.2)
- **Hotfix Branch:** hotfix/* (e.g., hotfix/1.2.1)

### CI/CD Pipeline
- **CI System:** GitHub Actions
- **Build Status:** [![CI](https://github.com/myorg/auth-service/actions/workflows/ci.yml/badge.svg)](...)
- **Pipeline File:** .github/workflows/ci.yml

---

## Code Quality & Coverage

### Testing
- **Test Framework:** JUnit 5 / pytest / Jest
- **Test Coverage Tool:** JaCoCo / pytest-cov / NYC
- **Minimum Coverage:** 80%
- **Coverage Report:** Available in CI pipeline

### Code Quality Tools
- **Linter:** ESLint / Checkstyle / Black
- **Code Analysis:** SonarQube / CodeFactor
- **Dependency Check:** OWASP Dependency-Check / Dependabot

---

## Team & Contacts

### Primary Team
- **Team Name:** Backend Engineering
- **Slack Channel:** #auth-service
- **Lead:** @john.doe
- **Oncall:** Follow PagerDuty escalation

### Related Teams
- Frontend Team (UI integration)
- Security Team (audit, compliance)
- DevOps Team (deployment, monitoring)

---

## Dependencies

### External Services
- **Database:** PostgreSQL 14+
- **Cache:** Redis 6+
- **Message Queue:** RabbitMQ 3.9+
- **Identity Provider:** Okta (for OAuth2)

### Key Libraries
```
Spring Security 6.x
Java JWT
OAuth2 Client
```

---

## Important Dates

- **Project Start:** 2024-01-15
- **Last Major Release:** 2026-01-01 (v2.0)
- **Next Planned Release:** 2026-03-01 (v2.1)
- **EOL Date:** No planned EOL

---

## Notes & Additional Context

Any additional information relevant to DORA metrics collection:

- This service handles critical authentication flows
- Performance is critical (SLA: <100ms p99)
- Security is high priority (SOC2 Type II)
- Maintained by 4-person team

---

## Template Usage

To use this template:

1. Copy template below
2. Replace `<Project Name>` and placeholders with real values
3. Commit to repository: `git add .dora.md && git commit -m "Add DORA configuration"`
4. Push to origin: `git push origin main`
5. DORA will automatically pick it up on next pipeline run

---

## Minimal Configuration (Quick Start)

If you just want to get started, use this minimal version:

```markdown
# DORA Configuration

## Project
- **Name:** My Project
- **GitHub:** https://github.com/myorg/my-project

## JIRA Integration
- **Export File:** jira_exports/my-project.csv

## Documentation
- **Architecture:** https://confluence.company.com/my-project-arch
```

The full template above can be filled in gradually.

---

## Field Descriptions

### Project Information

| Field | Purpose | Example |
|-------|---------|---------|
| Name | Human-readable project name | "Authentication Service" |
| Purpose | What the project does | "Handles user authentication" |
| Team | Responsible team | "Backend Team" |
| GitHub | Repository URL | "https://github.com/..." |
| Language | Primary language | "Java" |
| Framework | Framework used | "Spring Boot" |

### JIRA Integration

| Field | Purpose | Example |
|-------|---------|---------|
| Project Key | JIRA project identifier | "AUTH" |
| Export File | Path to export file | "jira_exports/auth.csv" |
| Active Epics | List of epics in CSV format | See template above |

### Confluence Links

| Link Type | Purpose | Update Frequency |
|-----------|---------|------------------|
| Architecture | System design, data flow | Quarterly |
| API Reference | REST endpoints, schemas | When APIs change |
| Deployment | How to deploy | When process changes |
| Security | Security policies | Yearly or as needed |

### Deployment Info

| Field | Purpose | Example |
|-------|---------|---------|
| Primary Branch | Main production branch | "main" |
| Version Tag Pattern | Git tag format | "v*.*.* (e.g., v1.2.3)" |
| Deployment Frequency | How often deployed | "Every 2 weeks" |

---

## Best Practices

### 1. Keep It Current
- Update when major changes occur
- Don't let it become stale
- Review quarterly

### 2. Link to Real Resources
- All Confluence links should be valid
- All GitHub URLs should be accessible
- Test links occasionally

### 3. Use Clear Language
- Use plain English
- Avoid jargon where possible
- Explain acronyms

### 4. Reference External Docs
- Link to Confluence for details
- Don't duplicate Confluence content
- .dora.md is metadata, not documentation

### 5. Automate Where Possible
- Some fields can be computed (e.g., last deployment date)
- Consider a template script to auto-generate parts

### 6. Version Control
- Commit .dora.md to git
- Track changes in commit history
- Treat as part of project documentation

---

## Common Patterns

### Pattern 1: Simple Project (No JIRA)

```markdown
# DORA Configuration

## Project
- **Name:** Utils Library
- **GitHub:** https://github.com/myorg/utils-lib
- **Language:** JavaScript

## Documentation
- **Readme:** https://github.com/myorg/utils-lib#readme
- **API Docs:** https://utils-lib.company.com/docs
```

### Pattern 2: Complex Enterprise Project

```markdown
# DORA Configuration: Payment Processing

## Project
- **Name:** Payment Processing System
- **Team:** Platform Engineering
- **GitHub:** https://github.com/myorg/payment-service

## JIRA Integration
- **Project Key:** PAY
- **Export File:** jira_exports/payment-service.csv

## Confluence
- **Architecture:** https://confluence.company.com/PAY/architecture
- **Integration Guide:** https://confluence.company.com/PAY/integrations
- **Runbook:** https://confluence.company.com/OPS/payment-deployment
- **Incident Response:** https://confluence.company.com/SEC/payment-incidents

## Deployment
- **Primary Branch:** main
- **Staging Branch:** staging
- **Version Pattern:** v*.*.* (semver)
- **Deployment Frequency:** Twice weekly
- **Last Deploy:** 2026-02-01 (v3.4.2)

## Team
- **Team:** Payment Platform
- **Lead:** @payment-team-lead
- **Oncall:** Follow PagerDuty
```

### Pattern 3: Microservices Project (Multiple Repos)

Each microservice has its own `.dora.md`:

**repo: auth-service/.dora.md**
```markdown
# DORA: Authentication Service
- **Export:** jira_exports/auth.csv
- **Confluence:** https://confluence.company.com/ARCH/auth
```

**repo: payment-service/.dora.md**
```markdown
# DORA: Payment Service
- **Export:** jira_exports/payment.csv
- **Confluence:** https://confluence.company.com/ARCH/payment
```

---

## Troubleshooting

### Issue: "Export file not found"
```
Solution:
1. Verify jira_exports/ folder exists in DORA root
2. Check export filename in .dora.md matches actual file
3. Ensure file is committed to git
```

### Issue: "Confluence link returns 404"
```
Solution:
1. Click the link manually to verify it works
2. Update URL in .dora.md if changed
3. Contact documentation owner if page deleted
```

### Issue: "DORA not picking up .dora.md"
```
Solution:
1. Ensure file is named exactly: .dora.md (case-sensitive)
2. Place at repository root (not in subdirectory)
3. Commit and push to repository
4. Run DORA pipeline: ./run_pipeline.sh
```

### Issue: "Epic list is outdated"
```
Solution:
1. Export fresh JIRA data
2. Save to jira_exports/<project>.csv
3. Run DORA pipeline: ./run_pipeline.sh
4. Optional: Update epic list in .dora.md
```

---

## Examples in Real Projects

Real-world examples are in the DORA repository:

- See example `.dora.md` files in test data
- Check DORA's own `.dora.md` for reference
- Examine integration tests for variations

---

## Questions & Support

- See [NON_INTRUSIVE_ARCHITECTURE.md](./NON_INTRUSIVE_ARCHITECTURE.md) for system design
- See [JIRA_EXPORT_GUIDE.md](./JIRA_EXPORT_GUIDE.md) for export details
- See [README.md](../README.md) for pipeline execution
