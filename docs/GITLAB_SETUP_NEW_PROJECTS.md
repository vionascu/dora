# Setting Up GitLab Projects for DORA

**Date:** February 3, 2026
**Purpose:** How to mirror DORA from GitHub to GitLab and add new projects

---

## Scenario: First Time Using GitLab with DORA

Since you don't have any projects on GitLab yet, here are the options:

### Option 1: Mirror DORA to GitLab (Recommended First Step)

This mirrors the existing DORA repository from GitHub to your GitLab instance.

#### Quick Steps:

1. **Create new project on GitLab**
   - Visit: https://git.ecd.axway.org/projects/new
   - Project name: `dora` (or similar)
   - Visibility: Private (or Public if you prefer)
   - Click "Create project"

2. **Mirror from GitHub**
   ```bash
   # Clone with mirror flag
   git clone --mirror https://github.com/vionascu/dora.git dora.git

   # Push to GitLab
   cd dora.git
   git push --mirror https://git.ecd.axway.org/viionascu/dora.git
   ```

3. **Add to DORA tracking**
   ```bash
   cd /Users/viionascu/Projects/DORA
   python src/import_gitlab.py \
     --add-project https://git.ecd.axway.org/viionascu/dora.git
   ```

#### Result:
- DORA will track its own metrics on GitLab
- You'll see DORA metrics on both GitHub and GitLab versions

---

### Option 2: Add Individual GitLab Projects Manually

If you have specific GitLab projects to add:

```bash
python src/import_gitlab.py \
  --add-project https://git.ecd.axway.org/viionascu/my-project.git
```

This adds any GitLab project (yours or others) to DORA tracking.

#### Usage:
```bash
# Add first project
python src/import_gitlab.py \
  --add-project https://git.ecd.axway.org/viionascu/project-one.git

# Add second project
python src/import_gitlab.py \
  --add-project https://git.ecd.axway.org/viionascu/project-two.git

# Add third project
python src/import_gitlab.py \
  --add-project https://git.ecd.axway.org/viionascu/project-three.git
```

Each command adds to the same `repos.yaml` file.

#### Example: Added projects appear in repos.yaml
```yaml
repositories:
  RnDMetrics:
    repo: https://github.com/vionascu/RnDMetrics
    # ... existing GitHub project ...

  TrailEquip:
    repo: https://github.com/vionascu/TrailEquip
    # ... existing GitHub project ...

  TrailWaze:
    repo: https://github.com/vionascu/TrailWaze
    # ... existing GitHub project ...

  dora:
    repo: https://git.ecd.axway.org/viionascu/dora.git        # ← New GitLab
    branch: main
    language: mixed
    ci_system: github-actions
    coverage_tools: []
    # ...

  project-one:
    repo: https://git.ecd.axway.org/viionascu/project-one.git # ← New GitLab
    # ...
```

---

## Full Workflow: From GitHub to GitLab Tracking

### Step 1: Set Up GitLab Projects

**Option A: Create New Projects**
```bash
# Visit GitLab UI and create projects manually
# https://git.ecd.axway.org/projects/new
```

**Option B: Mirror from Existing Git Repos**
```bash
# If you have repos elsewhere
git clone --mirror https://source.example.com/repo.git
cd repo.git
git push --mirror https://git.ecd.axway.org/viionascu/repo.git
```

### Step 2: Add to DORA

**Single Project:**
```bash
python src/import_gitlab.py \
  --add-project https://git.ecd.axway.org/viionascu/my-repo.git
```

**Multiple Projects:**
```bash
# Create a script to add multiple
for project in project-one project-two project-three; do
  python src/import_gitlab.py \
    --add-project https://git.ecd.axway.org/viionascu/$project.git
done
```

**Or use auto-discovery (when you have projects):**
```bash
GITLAB_TOKEN="your_token" python src/import_gitlab.py \
  --username viionascu
```

### Step 3: Run DORA Pipeline

```bash
# Locally
./run_pipeline.sh

# Or via GitHub Actions
gh workflow run dora-pipeline.yml -r main
```

### Step 4: View Results

After 5-10 minutes, visit:
```
https://vionascu.github.io/dora
```

Your GitLab projects will appear in:
- "All Projects" dropdown
- Combined metrics charts
- Repository breakdown section

---

## Command Reference

### Add a GitLab Project

```bash
python src/import_gitlab.py --add-project <URL>
```

**Examples:**
```bash
# Single project
python src/import_gitlab.py \
  --add-project https://git.ecd.axway.org/viionascu/myproject.git

# Project with specific branch
python src/import_gitlab.py \
  --add-project https://git.ecd.axway.org/viionascu/myproject.git
```

### Import All Your Projects

When you have multiple projects on GitLab:

```bash
GITLAB_TOKEN="your_token" python src/import_gitlab.py \
  --username viionascu
```

**Note:** Only works if you have projects created first

### List Available Projects

```bash
GITLAB_TOKEN="your_token" python src/import_gitlab.py \
  --username viionascu \
  --list-only
```

Shows all your projects without importing them.

---

## Mirror GitHub → GitLab in Detail

If you want to mirror all your GitHub repos to GitLab:

### Quick Mirror Command

```bash
# For each GitHub repo you want to mirror:
git clone --mirror https://github.com/vionascu/REPO_NAME.git
cd REPO_NAME.git
git push --mirror https://git.ecd.axway.org/viionascu/REPO_NAME.git
cd ..
rm -rf REPO_NAME.git
```

### Automated Mirror Script

Create `mirror_to_gitlab.sh`:

```bash
#!/bin/bash

GITHUB_USER="vionascu"
GITLAB_USER="viionascu"
GITLAB_URL="https://git.ecd.axway.org"

# List of repos to mirror
REPOS=(
  "RnDMetrics"
  "TrailEquip"
  "TrailWaze"
  "dora"
)

for repo in "${REPOS[@]}"; do
  echo "Mirroring $repo..."

  git clone --mirror "https://github.com/$GITHUB_USER/$repo.git" "$repo.git"
  cd "$repo.git"
  git push --mirror "$GITLAB_URL/$GITLAB_USER/$repo.git"
  cd ..
  rm -rf "$repo.git"

  echo "✅ $repo mirrored"
done

echo "✅ All repos mirrored!"
```

Run it:
```bash
chmod +x mirror_to_gitlab.sh
./mirror_to_gitlab.sh
```

---

## Verify GitLab Setup

### Check repos.yaml

```bash
cat repos.yaml | grep -A 3 "git.ecd.axway.org"
```

Output should show:
```yaml
  your-gitlab-project:
    repo: https://git.ecd.axway.org/viionascu/your-gitlab-project.git
    branch: main
    language: mixed
```

### Test Data Collection

```bash
# Run locally to test
./run_pipeline.sh

# Check for errors
echo $?  # 0 = success, non-zero = error
```

### View in Dashboard

After pipeline runs:
1. Go to https://vionascu.github.io/dora
2. Click "All Projects" dropdown
3. Look for your GitLab projects in the list
4. Should show metrics for both GitHub and GitLab repos

---

## Troubleshooting

### ❌ "git push --mirror" fails

**Cause:** GitLab project doesn't exist or wrong URL

**Solution:**
```bash
# Create the project first on GitLab
# https://git.ecd.axway.org/projects/new
# Then retry push
```

### ❌ Project added but metrics show N/A

**Cause:** Pipeline hasn't run yet or project is empty

**Solution:**
```bash
# Manually trigger pipeline
gh workflow run dora-pipeline.yml -r main

# Wait 5-10 minutes
# Refresh dashboard
```

### ❌ "Permission denied" when pushing

**Cause:** SSH key not configured or wrong URL format

**Solution:**
```bash
# Use HTTPS with token (easier)
git push --mirror https://oauth2:$GITLAB_TOKEN@git.ecd.axway.org/viionascu/project.git

# Or configure SSH key
# https://git.ecd.axway.org/-/profile/keys
```

### ❌ Mixed GitHub and GitLab metrics not showing correctly

**Cause:** Repos.yaml might have mixed URLs

**Solution:**
```bash
# Verify repos.yaml format
cat repos.yaml

# All should be valid URLs:
# GitHub: https://github.com/user/repo.git
# GitLab: https://git.ecd.axway.org/user/repo.git
```

---

## Next Steps

### After First GitLab Projects Added:

1. ✅ **Run pipeline:**
   ```bash
   ./run_pipeline.sh
   ```

2. ✅ **Check dashboard:**
   ```
   https://vionascu.github.io/dora
   ```

3. ✅ **View per-repo metrics:**
   - Select project in dropdown
   - See GitLab-specific metrics

4. ✅ **Monitor in GitHub Actions:**
   - Go to Actions tab
   - Watch DORA pipeline run
   - Check for errors in logs

---

## Integration with GitHub Actions

### Auto-import GitLab Projects Monthly

Add to `.github/workflows/dora-pipeline.yml`:

```yaml
- name: Import GitLab projects
  run: |
    GITLAB_TOKEN=${{ secrets.GITLAB_TOKEN }} python src/import_gitlab.py \
      --username viionascu
```

Then add `GITLAB_TOKEN` secret:
1. GitHub Settings → Secrets
2. New secret: `GITLAB_TOKEN`
3. Paste your GitLab token

---

## FAQ

**Q: Can I have both GitHub and GitLab projects in DORA?**

A: Yes! They're combined in metrics. DORA treats them equally.

**Q: How often does DORA check GitLab?**

A: Same schedule as GitHub - daily at 2 AM UTC, or manually triggered.

**Q: Do I need to configure CI/CD for GitLab projects?**

A: Not required. DORA uses git history only. CI/CD is optional for test coverage data.

**Q: Can I use GitLab CI instead of GitHub Actions?**

A: Not currently. DORA runs in GitHub Actions. But GitLab repos still tracked.

**Q: What if my GitLab project is private?**

A: Use your personal access token for authentication (already set up).

**Q: Can I track projects from multiple GitLab instances?**

A: Not yet. Currently supports one GitLab instance at a time.

---

**Last Updated:** February 3, 2026
**DORA Version:** 1.0
