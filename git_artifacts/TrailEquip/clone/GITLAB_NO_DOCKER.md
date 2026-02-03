# TrailEquip with GitLab (No Docker Needed)

## Summary

Your TrailEquip is **fully ready** and you have **3 excellent options** without Docker:

---

## **Option 1: Push to GitLab Cloud** (5 minutes, EASIEST)

No local setup required. GitLab's cloud runners build and test everything.

```bash
cd ~/Projects/TrailEquip

# Create repo at: https://gitlab.com/projects/new (name it "trail-equip")

git remote add gitlab https://gitlab.com/YOUR-USERNAME/trail-equip.git
git push -u gitlab main

# Open: https://gitlab.com/YOUR-USERNAME/trail-equip/-/pipelines
# Watch the pipeline run!
```

**What happens:**
- GitLab builds Java services (compile, package into JARs)
- GitLab builds React app (webpack, creates dist/)
- Tests run
- Artifacts generated
- You can download everything

**No installation needed!**

---

## **Option 2: Run Locally** (15 minutes)

Have all services running on your machine.

### Prerequisites:
```bash
java -version        # Need Java 21+
npm --version        # Need npm 20+
```

### Install PostgreSQL:
```bash
# Mac
brew install postgresql postgis

# Ubuntu
sudo apt-get install postgresql postgresql-contrib postgis

# Windows
# Download from https://www.postgresql.org/download/windows/
```

### Setup Database:
```bash
createdb trailequip
psql trailequip < ~/Projects/TrailEquip/infra/db/init.sql
```

### Run Services (5 separate terminals):

**Terminal 1:**
```bash
cd ~/Projects/TrailEquip
./gradlew :services:trail-service:bootRun
# Runs on port 8081
```

**Terminal 2:**
```bash
cd ~/Projects/TrailEquip
./gradlew :services:weather-service:bootRun
# Runs on port 8082
```

**Terminal 3:**
```bash
cd ~/Projects/TrailEquip
./gradlew :services:recommendation-service:bootRun
# Runs on port 8083
```

**Terminal 4:**
```bash
cd ~/Projects/TrailEquip
./gradlew :services:api-gateway:bootRun
# Runs on port 8080
```

**Terminal 5:**
```bash
cd ~/Projects/TrailEquip/ui
npm install
npm run dev
# Runs on port 3000
```

### Access:
- UI: http://localhost:3000
- API Docs: http://localhost:8080/swagger-ui.html
- Health: http://localhost:8080/api/v1/health

---

## **Option 3: GitLab Runner on Your Machine** (20 minutes, RECOMMENDED ⭐)

Combine local development with automated CI/CD on your machine.

### Step 1: Install GitLab Runner
```bash
# Mac
brew install gitlab-runner

# Ubuntu
sudo apt-get install gitlab-runner

# Windows
# Download from https://docs.gitlab.com/runner/install/windows.html
```

### Step 2: Get Registration Token
```
1. Go to: https://gitlab.com/YOUR-USERNAME/trail-equip
2. Settings → CI/CD → Runners
3. Copy "Runner registration token" (looks like: GR1348941...)
```

### Step 3: Register Runner
```bash
gitlab-runner register

# When prompted, enter:
# GitLab instance URL: https://gitlab.com/
# Registration token: (paste from above)
# Runner description: local
# Tags: local
# Executor: shell
# Shell: bash
```

### Step 4: Start Runner
```bash
gitlab-runner run

# This will run in the foreground. Keep it running!
# Or run as service:
sudo gitlab-runner install
sudo gitlab-runner start
```

### Step 5: Development Loop
```bash
# Make changes to code
# Commit and push
git commit -am "Your changes"
git push gitlab main

# GitLab detects push
# Pipeline automatically runs on YOUR machine
# Watch: https://gitlab.com/YOUR-USERNAME/trail-equip/-/pipelines
```

**Also run services locally (from Option 2) in separate terminals for active development.**

---

## **Quick Comparison**

| Aspect | Option 1 | Option 2 | Option 3 |
|--------|----------|----------|----------|
| **Setup Time** | 5 min | 15 min | 20 min |
| **Installation** | None | Java, npm, PostgreSQL | Java, npm, PostgreSQL, GitLab Runner |
| **Local Dev** | No | Yes | Yes |
| **CI/CD** | Cloud | None | Your Machine |
| **Cost** | Free (limited) | Free | Free |
| **Complexity** | Lowest | Medium | Medium |
| **Control** | GitLab cloud | Full local | Full local + auto CI/CD |

---

## **Recommended Setup**

**Combine Option 2 + Option 3:**

1. Install GitLab Runner (once)
2. Run services locally (5 terminals) for development
3. Push code → Pipeline runs automatically on your machine
4. View results in GitLab

**Best of both worlds:**
- ✅ Local development flexibility
- ✅ Automated testing on each push
- ✅ No cloud build minutes wasted
- ✅ Fast feedback loop

---

## **Which Should I Choose?**

### Choose **Option 1** if:
- You want to see it work ASAP
- You don't want to install anything
- You're okay with cloud CI/CD

### Choose **Option 2** if:
- You want full control locally
- You don't care about automated CI/CD
- You're doing active development

### Choose **Option 3** if: ⭐
- You want local development + automated CI/CD
- You have 20 minutes for setup
- You want best practice workflow

---

## **Testing & Verification**

After setting up your option:

```bash
# Test API (Option 2 or 3 only)
curl http://localhost:8080/api/v1/health

# Should return:
# {"status":"UP","services":{"trail-service":"UP",...}}

# Test UI
open http://localhost:3000

# See API docs
open http://localhost:8080/swagger-ui.html

# View GitLab Pipeline (Option 1 or 3)
https://gitlab.com/YOUR-USERNAME/trail-equip/-/pipelines
```

---

## **Troubleshooting**

### Runner doesn't pick up jobs
```bash
# Check runner is registered
gitlab-runner list

# Verify tags match (should have "local")
# In .gitlab-ci.yml, jobs should have:
# tags:
#   - local
```

### Services won't start locally
```bash
# Check Java is installed
java -version

# Check npm is installed
npm --version

# Check PostgreSQL is running
# Mac: brew services list
# Ubuntu: sudo service postgresql status
```

### Port already in use
```bash
# Find what's using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>
```

---

## **Next Steps**

1. **Pick your option** (1, 2, or 3)
2. **Follow the setup above**
3. **Verify it works** (test commands above)
4. **Start developing!**

---

## **Reference Files**

- `GITLAB_QUICK_START.md` – Quick reference
- `GITLAB_SETUP.md` – Detailed guides for each option
- `.gitlab-ci.yml` – Cloud pipeline (Option 1)
- `.gitlab-ci-no-docker.yml` – Local runner pipeline (Option 3)

---

## **You're All Set! 🚀**

Pick your option and get started. Everything is configured and ready to go!

Questions? Check the detailed guides or the inline comments in the files.

**Happy coding!**
