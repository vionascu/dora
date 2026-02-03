# JIRA Export Guide for DORA

This guide explains how to export JIRA data and use it with DORA without API access.

---

## Why Export Instead of API?

- **No API credentials needed** - Simpler, more secure
- **No rate limiting** - Exports are one-time operations
- **Flexible filtering** - You control what gets exported
- **Auditable** - File-based exports are versionable
- **Works offline** - Data persists in git repository

---

## Format 1: CSV Export (Recommended for Simplicity)

CSV is the easiest format to understand and maintain.

### Step 1: Export from JIRA Cloud

1. Navigate to JIRA Filters or Project Board
2. Click **"..."** (more options)
3. Select **"Export"**
4. Choose **"CSV (All Fields)"** or **"CSV (Current Fields)"**
5. Download the file

### Step 2: Clean CSV (Optional but Recommended)

The exported CSV may have extra columns. Keep the essentials:

**Required columns:**
```
Epic ID,Epic Name,Type,Status,Link
```

**Optional columns:**
```
Story Count,Resolution,Assignee,Components
```

**Example cleaned CSV:**
```csv
Epic ID,Epic Name,Type,Status,Story Count,Link
EPIC-1,Authentication Core,Epic,Done,12,https://jira.company.com/browse/EPIC-1
EPIC-2,OAuth2 Integration,Epic,In Progress,8,https://jira.company.com/browse/EPIC-2
US-101,Login Page UI,Story,Done,0,https://jira.company.com/browse/US-101
US-102,OAuth2 Token Handler,Story,In Progress,0,https://jira.company.com/browse/US-102
```

### Step 3: Save to DORA

```bash
# From DORA project root
mkdir -p jira_exports/
cp ~/Downloads/auth-export.csv jira_exports/auth-service.csv

# Name convention: jira_exports/<project-key>.csv
```

### Step 4: Update repos.yaml

```yaml
repositories:
  auth-service:
    url: https://github.com/myorg/auth-service
    jira_export: jira_exports/auth-service.csv
    dora_md: .dora.md
```

---

## Format 2: JSON Export (More Structured)

JSON provides more detailed metadata.

### Step 1: Export from JIRA Cloud

If your JIRA instance has Jira CLI:

```bash
# Using Jira Cloud CLI
jira issue list --project AUTH --format json > ~/Downloads/auth-export.json

# Or manually export via JIRA REST API (if you have temporary access)
curl -u user@company.com:token \
  "https://company.atlassian.net/rest/api/3/search?jql=project=AUTH" \
  > ~/Downloads/auth-export.json
```

### Step 2: Expected JSON Structure

The parser expects this structure:

```json
{
  "issues": [
    {
      "key": "EPIC-1",
      "fields": {
        "type": {
          "name": "Epic"
        },
        "summary": "Authentication Core",
        "status": {
          "name": "Done"
        },
        "customfield_10001": 12  // Story count (varies by instance)
      }
    },
    {
      "key": "US-101",
      "fields": {
        "type": {
          "name": "Story"
        },
        "summary": "Login Page UI",
        "status": {
          "name": "Done"
        },
        "parent": {
          "key": "EPIC-1"
        }
      }
    }
  ]
}
```

### Step 3: Save to DORA

```bash
# From DORA project root
mkdir -p jira_exports/
cp ~/Downloads/auth-export.json jira_exports/auth-service.json
```

### Step 4: Update repos.yaml

```yaml
repositories:
  auth-service:
    url: https://github.com/myorg/auth-service
    jira_export: jira_exports/auth-service.json
    dora_md: .dora.md
```

---

## Handling Multiple JIRA Projects

If you have many repositories, each with different JIRA projects:

```
jira_exports/
├── auth-service.csv           # AUTH project
├── payment-service.csv        # PAY project
├── analytics-service.csv      # ANALYTICS project
└── notification-service.csv   # NOTIF project
```

Each repository's `.dora.md` points to its corresponding export:

```markdown
# auth-service .dora.md
## JIRA Integration
- **Export File:** jira_exports/auth-service.csv
```

```markdown
# payment-service .dora.md
## JIRA Integration
- **Export File:** jira_exports/payment-service.csv
```

---

## Linking Commits to Epics

The system can automatically link commits to JIRA epics by analyzing commit messages.

### Pattern 1: Explicit Epic Reference

Include the epic key in commit message:

```bash
git commit -m "Implement login form

EPIC-1: Authentication Core
- Add email validation
- Add password strength checker
"
```

### Pattern 2: User Story Reference

Reference the user story (which is in an epic):

```bash
git commit -m "Build OAuth2 token handler

Fixes US-102
"
```

### Pattern 3: Multiple Epics

If a change spans multiple epics:

```bash
git commit -m "Security framework update

EPIC-1: Authentication Core
EPIC-5: Security Hardening
"
```

The correlation system will:
1. Parse commit messages
2. Extract JIRA issue keys (EPIC-*, US-*, etc.)
3. Look up issues in the JIRA export
4. Link commits to epics in the output

**Output:** `jira_artifacts/<project>/correlation_map.json`

```json
{
  "EPIC-1": {
    "name": "Authentication Core",
    "commits": ["abc123...", "def456..."],
    "commit_count": 24,
    "lines_changed": 1250
  },
  "EPIC-2": {
    "name": "OAuth2 Integration",
    "commits": ["ghi789..."],
    "commit_count": 3,
    "lines_changed": 145
  }
}
```

---

## Updating JIRA Exports

JIRA data should be kept fresh. Update exports:

### Manual Update

```bash
# 1. Export fresh data from JIRA
# (follow Step 1 above)

# 2. Save to jira_exports/
cp ~/Downloads/auth-export.csv jira_exports/auth-service.csv

# 3. Run pipeline
./run_pipeline.sh

# 4. Commit changes
git add jira_exports/
git commit -m "Update JIRA exports"
git push
```

### Automated Update (GitHub Actions)

Create a workflow that exports JIRA data periodically:

```yaml
# .github/workflows/update-jira-exports.yml
name: Update JIRA Exports

on:
  schedule:
    - cron: '0 2 * * 1'  # Every Monday at 2 AM
  workflow_dispatch:

jobs:
  export:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Export JIRA (using Jira CLI)
        run: |
          jira issue list --project AUTH --format csv > jira_exports/auth-service.csv
          jira issue list --project PAY --format csv > jira_exports/payment-service.csv
        env:
          JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
          JIRA_HOST: company.atlassian.net
          JIRA_USER: bot@company.com

      - name: Commit and Push
        run: |
          git config user.name "DORA Bot"
          git config user.email "dora@company.com"
          git add jira_exports/
          git commit -m "Update JIRA exports [automated]" || true
          git push
```

---

## Handling Export Errors

### Error: "Export file not found"

```
ERROR: jira_exports/auth-service.csv not found
```

**Solution:**
- Create the file manually (follow step 2 above)
- Ensure file path matches `repos.yaml`
- Check folder permissions

### Error: "Invalid CSV format"

```
ERROR: Missing required columns: Epic ID, Epic Name, Status
```

**Solution:**
- Verify CSV headers are correct
- Remove extra columns if needed
- Ensure no empty rows in header
- Check file encoding (should be UTF-8)

### Error: "Invalid JSON format"

```
ERROR: Failed to parse JSON: Expecting 'key' field in issue
```

**Solution:**
- Verify JSON structure matches expected format
- Check that `issues` array exists
- Ensure each issue has `key` field
- Validate JSON syntax

---

## CSV vs JSON: Which to Choose?

| Aspect | CSV | JSON |
|--------|-----|------|
| **Ease of Export** | Click-export from JIRA | CLI or API |
| **Readability** | ✓ Easy to read in spreadsheet | Harder to read raw |
| **Metadata** | Limited fields | Full JIRA metadata |
| **Parsing** | Simple, built-in | More parsing required |
| **Linking Commits** | Manual mention in commits | Automatic parent links |
| **Recommended** | ✓ For simplicity | For detailed analysis |

**Recommendation:** Start with CSV. Move to JSON if you need more metadata.

---

## Best Practices

### 1. Regular Updates
- Update exports monthly (or with each release)
- Commit exports to git for auditability
- Track export history

### 2. Clean Data
- Remove test/spam epics before export
- Use consistent naming (no special chars)
- Ensure status values are standardized

### 3. Meaningful Epic Names
- Use descriptive names (e.g., "OAuth2 Integration", not "Work Item 5")
- Include context in descriptions
- Link to Confluence for details

### 4. Commit Messages
- Reference JIRA issues in commits (EPIC-1, US-102, etc.)
- Makes correlation automatic
- Improves traceability

### 5. Validation
- Check export completeness before updating
- Verify row/record counts haven't dropped
- Spot-check epic/story names

---

## Example: Complete Setup

### 1. Export from JIRA
```bash
# Download auth-export.csv from JIRA UI
```

### 2. Save to DORA
```bash
mkdir -p jira_exports/
mv ~/Downloads/auth-export.csv jira_exports/auth-service.csv
```

### 3. Update repos.yaml
```yaml
repositories:
  auth-service:
    url: https://github.com/myorg/auth-service
    jira_export: jira_exports/auth-service.csv
    dora_md: .dora.md
```

### 4. Update .dora.md in repo
```markdown
# Authentication Service

## JIRA Integration
- **Export File:** jira_exports/auth-service.csv
- **JIRA Project:** AUTH
- **Epics:**
  - EPIC-1: Authentication Core
  - EPIC-2: OAuth2 Integration
```

### 5. Run Pipeline
```bash
./run_pipeline.sh
```

### 6. View Results
Dashboard shows:
- Epics and story counts
- Commits linked to epics
- Progress tracking
- Links to Confluence & JIRA

---

## Support

- See [NON_INTRUSIVE_ARCHITECTURE.md](./NON_INTRUSIVE_ARCHITECTURE.md) for full system design
- See [README.md](../README.md) for configuration details
- Check DORA project structure for example exports
