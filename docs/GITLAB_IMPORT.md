# GitLab Project Import Guide

**Date:** February 3, 2026
**Purpose:** How to import projects from GitLab instances into DORA metrics tracking

---

## Overview

DORA can track projects from both GitHub and GitLab. This guide explains how to import your GitLab projects into the DORA metrics system.

---

## Quick Start

### Option 1: Import Public Projects (No Authentication)

If your GitLab projects are public, you can import them without authentication:

```bash
python src/import_gitlab.py \
  --gitlab-url https://git.ecd.axway.org \
  --username viionascu
```

This will:
1. Connect to the GitLab instance
2. Find all public projects for the user
3. Add them to `repos.yaml`
4. Ready for metrics collection

### Option 2: Import Private Projects (With Authentication)

For private projects, provide a GitLab Personal Access Token:

```bash
export GITLAB_TOKEN="your_token_here"
python src/import_gitlab.py \
  --gitlab-url https://git.ecd.axway.org \
  --username viionascu
```

Or pass token directly:

```bash
python src/import_gitlab.py \
  --gitlab-url https://git.ecd.axway.org \
  --username viionascu \
  --token "your_token_here"
```

---

## Step-by-Step: Getting Your GitLab Token

### For Axway Enterprise GitLab (git.ecd.axway.org)

1. **Log in to GitLab**
   - Visit: https://git.ecd.axway.org
   - Sign in with your Axway credentials

2. **Navigate to Access Tokens**
   - Click your profile icon (top-right corner)
   - Select "Settings"
   - Go to "Access Tokens" (left sidebar)

3. **Create New Token**
   - Click "Add new token" button
   - Name: `dora-metrics` (or similar)
   - Scopes: Select these minimum scopes:
     - ☑️ `api` - Access your API
     - ☑️ `read_repository` - Read repository data
   - Click "Create personal access token"

4. **Copy and Save Token**
   - ⚠️ **IMPORTANT:** Copy the token immediately - you won't see it again!
   - Store it safely (password manager, secure note, etc.)

---

## Command Line Reference

### Basic Syntax

```bash
python src/import_gitlab.py [OPTIONS]
```

### Available Options

| Option | Required | Description | Example |
|--------|----------|-------------|---------|
| `--gitlab-url` | No | GitLab instance URL | `https://git.ecd.axway.org` |
| `--username` | ✅ Yes | GitLab username | `viionascu` |
| `--token` | No | Personal access token | `glpat-xxxxx...` |
| `--config` | No | repos.yaml path | `repos.yaml` |

### Examples

**Import from Axway GitLab:**
```bash
python src/import_gitlab.py --username viionascu
```

**Import from different GitLab instance:**
```bash
python src/import_gitlab.py \
  --gitlab-url https://gitlab.company.com \
  --username myusername
```

**Import to specific config file:**
```bash
python src/import_gitlab.py \
  --username viionascu \
  --config custom_repos.yaml
```

---

## What Gets Imported

When you import a GitLab project, DORA automatically detects:

### Detected Information

| Field | How It's Determined |
|-------|-------------------|
| **Repository URL** | From GitLab project settings |
| **Default Branch** | From GitLab project default branch |
| **Language** | Auto-detected from project description |
| **CI System** | Set to `github-actions` (customizable) |
| **Coverage Tools** | Empty by default (customize as needed) |

### Example: What Gets Added to repos.yaml

```yaml
repositories:
  MyProject:
    repo: https://git.ecd.axway.org/myteam/my-project.git
    branch: main
    language: python
    ci_system: github-actions
    coverage_tools:
      - type: pytest-cov
        minimum_threshold: 75
    artifact_patterns:
      epics:
        local_patterns:
          - file: "**/docs/**/*.md"
            regex: "Epic\\s+(\\d+):\\s*(.+)"
      stories:
        local_patterns:
          - file: "**/docs/**/*.md"
            regex: "US(\\d+\\.d+)"
```

---

## After Import: Next Steps

### 1. Verify Import

Open `repos.yaml` and verify all projects were added correctly:

```bash
cat repos.yaml | grep -A 5 "repo:"
```

You should see your GitLab projects listed.

### 2. Update Coverage Tools (Optional)

If you know the coverage tools used by each project, update them:

```yaml
repositories:
  MyJavaProject:
    coverage_tools:
      - type: jacoco
        minimum_threshold: 80

  MyPythonProject:
    coverage_tools:
      - type: pytest-cov
        minimum_threshold: 75
```

### 3. Run Data Collection

Trigger the DORA pipeline to start collecting metrics:

```bash
# Locally
./run_pipeline.sh

# Via GitHub Actions (if repo is on GitHub)
gh workflow run dora-pipeline.yml -r main
```

### 4. View Dashboard

After pipeline completes (5-10 minutes), check the dashboard:

```
https://vionascu.github.io/dora
```

Your GitLab projects should appear in:
- Charts & Visualizations
- Repository Analysis section
- "All Projects" dropdown

---

## Troubleshooting

### ❌ Error: "User not found"

**Cause:** Username doesn't exist on that GitLab instance

**Solution:**
```bash
# Verify username is correct
# Check at: https://git.ecd.axway.org/users/[username]
```

### ❌ Error: "Authentication failed"

**Cause:** Token is invalid or expired

**Solution:**
1. Generate a new token (see "Getting Your Token" above)
2. Make sure token has `api` and `read_repository` scopes
3. Try again with new token

### ❌ Error: "Private key not found"

**Cause:** SSH authentication needed for private projects

**Solution:**
1. Use Personal Access Token method (recommended)
2. Or configure SSH key for GitLab

### ❌ No projects found

**Cause:** User has no projects OR they're all archived

**Solution:**
1. Verify user has active projects
2. Check GitLab UI: https://git.ecd.axway.org/[username]
3. Make sure projects aren't archived

### ⚠️ Projects already in config

**Status:** Not an error - import skips projects already configured

**Solution:** This is normal behavior. If you want to re-import:
1. Remove the project from `repos.yaml`
2. Run import again

---

## Security: Protecting Your Token

### DO's ✅
- ✅ Store token in password manager
- ✅ Use environment variable: `export GITLAB_TOKEN=...`
- ✅ Add `.gitignore` entry for any token files
- ✅ Rotate token regularly (monthly)
- ✅ Use token with minimal required scopes

### DON'Ts ❌
- ❌ Don't commit token to Git
- ❌ Don't share token in messages/emails
- ❌ Don't paste token in scripts directly
- ❌ Don't use in public repositories
- ❌ Don't grant unnecessary scopes

### Revoking Compromised Token

If you accidentally expose your token:

1. **Immediately revoke it:**
   - Go to GitLab: https://git.ecd.axway.org/-/profile/personal_access_tokens
   - Click "Revoke" on the exposed token

2. **Generate new token**
   - Create fresh token with same scopes
   - Update your configuration

3. **Update DORA pipeline**
   - If token stored in GitHub Actions secrets, update it there too

---

## Advanced: Multiple GitLab Instances

You can import from multiple GitLab instances:

```bash
# Import from Axway GitLab
python src/import_gitlab.py \
  --gitlab-url https://git.ecd.axway.org \
  --username viionascu

# Import from another instance
python src/import_gitlab.py \
  --gitlab-url https://internal-gitlab.example.com \
  --username viionascu \
  --token "different_token"
```

All projects will be added to the same `repos.yaml` file.

---

## Monitoring Imported Projects

### In Dashboard

After import and data collection runs, you'll see:

```
📊 Data Sources:
  - RnDMetrics (GitHub)
  - TrailEquip (GitHub)
  - TrailWaze (GitHub)
  - MyGitLabProject (GitLab) ← Your new imports
  - AnotherProject (GitLab)
```

### In Metrics

- **Total Commits:** Sum of commits from all repos (GitHub + GitLab)
- **Contributors:** Combined across all repositories
- **Velocity:** Aggregated development speed
- **Test Coverage:** Per-repository coverage (if configured)

### Per-Repository View

Click project dropdown to see GitLab project metrics:

```
All Projects         ← Shows combined metrics
├─ RnDMetrics       ← GitHub
├─ TrailEquip       ← GitHub
├─ TrailWaze        ← GitHub
├─ MyGitLabProject  ← GitLab import ✨
└─ AnotherProject   ← GitLab import ✨
```

---

## FAQ

**Q: Can I import all projects from an organization?**

A: Currently imports user projects. For organization projects, use the organization's admin username or API.

**Q: Do I need GitHub Actions setup for GitLab projects?**

A: Not required for metrics collection. DORA uses git history, not CI/CD logs (unless you configure CI artifacts).

**Q: Will imported projects affect existing metrics?**

A: No - new projects are added to calculations. Existing GitHub projects unchanged.

**Q: How often are GitLab projects updated?**

A: Same as GitHub projects - daily at 2:00 AM UTC, or manually via `gh workflow run dora-pipeline.yml`.

**Q: Can I remove a project from tracking?**

A: Yes - remove it from `repos.yaml` and run pipeline again.

**Q: What if project names are duplicated between GitHub and GitLab?**

A: Use different names in `repos.yaml`. For example:
```yaml
repositories:
  RnDMetrics-GitHub:  # ← Renamed
  RnDMetrics-GitLab:  # ← Renamed
```

---

## Integration with GitHub Actions

### Automated Import on Schedule

Add this to `.github/workflows/dora-pipeline.yml` to auto-import from GitLab monthly:

```yaml
- name: Import GitLab Projects
  run: |
    python src/import_gitlab.py \
      --gitlab-url https://git.ecd.axway.org \
      --username viionascu
  env:
    GITLAB_TOKEN: ${{ secrets.GITLAB_TOKEN }}
```

Then add secret to GitHub:
1. Go to repo Settings → Secrets and variables
2. New repository secret
3. Name: `GITLAB_TOKEN`
4. Value: Your GitLab token

---

## Support & Help

### Resources
- [GitLab API Docs](https://docs.gitlab.com/ee/api/)
- [Personal Access Tokens](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)
- [DORA Documentation](./index.html)

### Common Issues
- [Troubleshooting section above](#troubleshooting)
- Check console logs: `python src/import_gitlab.py --help`

---

**Last Updated:** February 3, 2026
**DORA Version:** 1.0
