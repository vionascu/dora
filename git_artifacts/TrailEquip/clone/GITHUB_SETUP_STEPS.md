# GitHub Setup - Step by Step Manual Instructions

Since you need GitHub authentication, here are the exact steps to migrate:

---

## Step 1: Create Personal Access Token on GitHub

This allows your computer to push to GitHub without entering password every time.

### A. Go to GitHub Settings

1. Visit: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"

### B. Create Token

1. **Token name**: `TrailEquip-Deploy` (or any name)
2. **Expiration**: 90 days (or Unlimited)
3. **Scopes**: Check these boxes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)

4. Click "Generate token"

### C. Save Token

⚠️ **IMPORTANT**: Copy the token immediately! You won't see it again.

```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Save it somewhere safe temporarily (you'll only need it once for setup).

---

## Step 2: Create Repository on GitHub

### A. Go to GitHub Create Repo

Visit: https://github.com/new

### B. Fill in Details

- **Owner**: vionascu (your account)
- **Repository name**: `trail-equip`
- **Description**: "Hiking trail discovery app with interactive maps"
- **Visibility**: Public
- **Initialize repository**: Leave unchecked (we're importing from GitLab)

### C. Click "Create repository"

You'll see a page with setup instructions. Copy the HTTPS URL shown.

---

## Step 3: Setup Git Authentication (One Time)

### Option A: Using GitHub CLI (Easiest)

```bash
# Install GitHub CLI (if not already installed)
brew install gh

# Authenticate
gh auth login
# Choose: GitHub.com
# Choose: HTTPS
# Choose: Y to authenticate with token
# Paste your token from Step 1
```

### Option B: Using Git Credentials

On macOS:

```bash
# Setup credential caching
git config --global credential.helper osxkeychain

# Next push, enter:
# Username: vionascu
# Password: [paste token from Step 1]
```

---

## Step 4: Add GitHub Remote and Push

```bash
cd /Users/viionascu/Projects/TrailEquip

# Add GitHub as remote
git remote add github https://github.com/vionascu/trail-equip.git

# Push all branches
git push github --all

# Push all tags
git push github --tags

# Verify
git remote -v
```

**Expected output**:
```
gitlab  https://gitlab.com/vic.ionascu/trail-equip.git (fetch)
gitlab  https://gitlab.com/vic.ionascu/trail-equip.git (push)
github  https://github.com/vionascu/trail-equip.git (fetch)
github  https://github.com/vionascu/trail-equip.git (push)
```

---

## Step 5: Verify on GitHub

Visit: https://github.com/vionascu/trail-equip

Check:
- ✅ All files present
- ✅ Commit history visible
- ✅ Branches showing
- ✅ README displays
- ✅ Docs folder visible

---

## Step 6: Setup GitHub Actions

### A. Create Workflow Directory

```bash
mkdir -p .github/workflows
```

### B. Create Workflow File

Create: `.github/workflows/deploy.yml`

Content:
```yaml
name: Build and Deploy Docker

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}

      - name: Log deployment info
        run: |
          echo "Docker image built and pushed!"
          echo "Image: ghcr.io/${{ github.repository }}:latest"
```

### C. Commit and Push

```bash
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Actions CI/CD workflow"
git push github main
```

---

## Step 7: Connect Railway to GitHub

### A. Go to Railway Dashboard

Visit: https://railway.app

### B. Create New Project

1. Click "Create New Project"
2. Select "Deploy from GitHub"
3. Click "Authorize Railway"
4. Choose: `vionascu/trail-equip`
5. Click "Deploy"

Railway automatically deploys on every push! ✅

---

## Step 8: Make Primary Remote (Optional)

If you want to use GitHub as your primary:

```bash
# Change origin to GitHub
git remote set-url origin https://github.com/vionascu/trail-equip.git

# Keep GitLab as backup (optional)
git remote set-url gitlab https://gitlab.com/vic.ionascu/trail-equip.git
```

---

## Step 9: Test Everything

### Test GitHub Actions

```bash
# Make a test commit
echo "# Test on GitHub" >> README.md
git add README.md
git commit -m "Test GitHub Actions"
git push github main

# Watch build: https://github.com/vionascu/trail-equip/actions
```

### Test Railway

1. Go to Railway dashboard
2. Watch deployment logs
3. Get public URL
4. Test in browser: `https://your-railway-url.app`

---

## Complete Workflow After Setup

```bash
# Local development
./gradlew test
./gradlew build

# Commit and push
git add .
git commit -m "Your changes"
git push github main

# GitHub Actions runs (unlimited! ✅)
# Railway auto-deploys
# Done in 9 minutes!
```

---

## Troubleshooting

### "Permission denied"
- Check your Personal Access Token is correct
- Run: `gh auth status` to verify

### "Repository not found"
- Verify repository was created: https://github.com/vionascu/trail-equip
- Check repo name matches exactly

### "Authentication failed"
- Create new Personal Access Token
- Use GitHub CLI: `gh auth login`

### GitHub Actions won't run
- Check workflow file: `.github/workflows/deploy.yml` exists
- Verify syntax is correct (YAML indentation matters)
- Check Actions tab: https://github.com/vionascu/trail-equip/actions

---

## What You Now Have

After completing all steps:

✅ Code mirrored to GitHub with full history
✅ GitHub Actions configured (unlimited CI/CD)
✅ Railway auto-deploying from GitHub
✅ Public URL for everyone to access
✅ Zero cost, unlimited deployments
✅ Can push 100+ times per month without limits

---

## Cost Breakdown

```
GitHub Actions:  Free (unlimited)
Railway:         $0/month (free tier)
Domain:          Free (railway.app)
─────────────────────────────────
Total:           $0/month forever!
```

---

## Quick Command Reference

```bash
# Create token at: https://github.com/settings/tokens

# Setup auth
gh auth login
# Choose GitHub.com → HTTPS → Y → [paste token]

# Navigate to project
cd /Users/viionascu/Projects/TrailEquip

# Add GitHub remote
git remote add github https://github.com/vionascu/trail-equip.git

# Push everything
git push github --all && git push github --tags

# Create workflow
mkdir -p .github/workflows
# Add deploy.yml with content above

# Test
git push github main
# Check: https://github.com/vionascu/trail-equip/actions
```

---

## Next Steps

1. ✅ Follow Steps 1-8 above (takes ~15 minutes)
2. ✅ Test with Step 9
3. ✅ Enjoy unlimited CI/CD! 🎉

---

**Need help?** Each section has detailed instructions. GitHub setup is simple once you know the steps!

**Ready?** Start with Step 1: Create Personal Access Token
