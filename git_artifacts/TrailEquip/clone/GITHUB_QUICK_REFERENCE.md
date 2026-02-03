# GitHub Migration - Quick Reference

## Your GitHub Account
**URL**: https://github.com/vionascu

---

## Step-by-Step (Copy & Paste)

### 1. Setup GitHub Personal Access Token
```
1. Go to: https://github.com/settings/tokens
2. Click: "Generate new token" → "Generate new token (classic)"
3. Name: TrailEquip-Deploy
4. Expiration: 90 days
5. Scopes: ☑ repo, ☑ workflow
6. Click: "Generate token"
7. COPY THE TOKEN (save temporarily)
```

### 2. Authenticate Git
```bash
# Option A: Using GitHub CLI (easiest)
brew install gh
gh auth login
# Choose: GitHub.com → HTTPS → Y → [paste token]

# Option B: Using Git Credentials
git config --global credential.helper osxkeychain
# (Git will ask for username/password on first push)
```

### 3. Mirror Code to GitHub
```bash
cd /Users/viionascu/Projects/TrailEquip

# Add GitHub remote
git remote add github https://github.com/vionascu/trail-equip.git

# Push all branches and tags
git push github --all
git push github --tags

# Verify
git remote -v
```

### 4. Create GitHub Actions Workflow
```bash
# Create directory
mkdir -p .github/workflows

# Create file: .github/workflows/deploy.yml
# (Copy YAML from GITHUB_SETUP_STEPS.md section 6B)

# Commit
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Actions CI/CD"
git push github main
```

### 5. Connect Railway to GitHub
```
1. Go to: https://railway.app
2. Click: "Create New Project"
3. Select: "Deploy from GitHub"
4. Click: "Authorize Railway"
5. Select: vionascu/trail-equip
6. Click: "Deploy"
```

### 6. Test
```bash
# Make a test change
echo "test" >> README.md
git add README.md
git commit -m "Test GitHub Actions"
git push github main

# Watch: https://github.com/vionascu/trail-equip/actions
```

---

## After Setup Complete

```bash
# Your daily workflow
./gradlew test           # Local
./gradlew build          # Local
git push github main     # Triggers unlimited CI/CD!
```

---

## Documentation References

- Detailed guide: `MIGRATE_TO_GITHUB.md`
- Setup steps: `GITHUB_SETUP_STEPS.md`
- Optimization: `docs/GITLAB_CI_OPTIMIZATION.md`
- CI/CD solution: `CI_CD_SOLUTION.md`

---

## Cost: $0/month Forever ✅

GitHub Actions: Unlimited free minutes
Railway: $0 (free tier)

---

## Your Account Ready
GitHub: https://github.com/vionascu
Email: (associated with GitHub account)

---

**Ready? Start with Step 1 above!**
