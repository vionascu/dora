# DORA Dashboard - Beginner's Guide ✨

**For: Non-technical users, Junior developers, Project managers**

**What this guide covers: Everything from start to finish**

---

## 📚 Table of Contents

1. [What is DORA?](#what-is-dora)
2. [How Everything Works (Visual Guide)](#how-everything-works)
3. [The Three Parts of DORA](#the-three-parts)
4. [Where to Find Everything](#where-to-find-everything)
5. [Step-by-Step: Your First Time](#step-by-step-your-first-time)
6. [Understanding What You See](#understanding-what-you-see)
7. [Common Questions](#common-questions)
8. [Troubleshooting (Simple Version)](#troubleshooting-simple-version)

---

## 🤔 What is DORA?

**DORA = Deployment Frequency, Leads Time, Change Failure Rate, Recovery Time**

In simple words: **It measures how fast and reliable your software team is.**

**Think of it like:**
```
🚀 How quickly can you ship new features?
✅ How often do things break?
🔧 How fast can you fix problems?
📊 How many people are working on code?
```

**Why should you care?**
- See if your team is getting faster or slower
- Identify what's working well
- Find problems before they become big issues
- Celebrate team achievements with data

---

## 🎯 How Everything Works (Visual Guide)

### The Big Picture

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  YOUR REPOSITORIES (GitHub)                                          │
│  ├─ Repository 1 (Code + History)                                  │
│  ├─ Repository 2 (Code + History)                                  │
│  └─ Repository 3 (Code + History)                                  │
│                                                                       │
│  📊 Your Configuration Files (.dora.md in each repo)                │
│                                                                       │
│  ⚙️ DORA System (Automatic)                                         │
│  ├─ Reads your repositories (doesn't change anything!)              │
│  ├─ Reads your config files                                         │
│  ├─ Calculates all the metrics                                      │
│  └─ Creates visualizations                                          │
│                                                                       │
│  📈 DASHBOARD (GitHub Pages)                                        │
│  └─ Shows all your metrics in one place                             │
│                                                                       │
│  🌐 Access Anywhere                                                  │
│  └─ View from any browser, any device                               │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow (Step by Step)

```
Step 1: Code in GitHub
   ↓
   Your repositories have code and history
   (DORA only READS this - never changes it)

Step 2: Configuration
   ↓
   .dora.md files tell DORA about your project
   (Team info, links, important dates)

Step 3: DORA Analyzes
   ↓
   Automatic process:
   • Counts commits (code changes)
   • Measures deployment speed
   • Tracks team velocity
   • Checks code quality

Step 4: Results Generated
   ↓
   JSON files with all the numbers
   (You don't need to look at these)

Step 5: Dashboard Shows Results
   ↓
   Pretty charts and graphs
   Easy to understand information

Step 6: You Make Decisions
   ↓
   Use the data to improve your process
```

---

## 🔄 The Three Parts of DORA

### Part 1: INPUT (Where DORA gets information)

```
📥 INPUT LAYER
├─ GitHub Repositories (READ ONLY)
│  └─ Code commits
│  └─ Branch history
│  └─ Deployment tags
│
├─ Configuration Files (.dora.md)
│  └─ Team information
│  └─ Important dates
│  └─ Project links
│
└─ (Optional) JIRA Data
   └─ Epics and stories
   └─ Sprint information
```

**What you need to do:**
- Keep your GitHub repos up to date (you're already doing this!)
- Add a `.dora.md` file to each repo (optional but helpful)
- That's it! ✓

---

### Part 2: PROCESSING (What DORA does)

```
⚙️ PROCESSING LAYER (AUTOMATIC)
├─ Collection Phase
│  ├─ Read all commits
│  ├─ Count changes
│  └─ Extract metadata
│
├─ Calculation Phase
│  ├─ Calculate speed metrics
│  ├─ Measure quality
│  ├─ Track velocity
│  └─ Generate statistics
│
└─ Validation Phase
   ├─ Check data quality
   ├─ Verify calculations
   └─ Ensure accuracy
```

**What you need to do:**
- Nothing! This happens automatically
- The system runs on schedule
- Or you can trigger it manually

---

### Part 3: OUTPUT (What you see)

```
📊 OUTPUT LAYER (Dashboard)
├─ Project Overview
│  ├─ All your projects listed
│  └─ Quick status check
│
├─ Metrics Display
│  ├─ Deployment frequency
│  ├─ Lead time for changes
│  ├─ Team velocity
│  ├─ Code quality
│  └─ Evolution trends
│
├─ Team Analytics
│  ├─ Contributors
│  ├─ Activity timeline
│  └─ Performance trends
│
└─ Export Options
   ├─ View raw data
   └─ Share with team
```

**What you need to do:**
- Visit the dashboard URL
- Click around to explore
- Share findings with your team

---

## 🗺️ Where to Find Everything

### 1. The Dashboard (What You See)

**URL:** https://vionascu.github.io/dora/public/

**What's there:**
- All your metrics in one place
- Charts and graphs
- Project selector
- Date filters
- Team statistics

**How to get there:**
1. Copy the URL above
2. Paste in your browser
3. Press Enter
4. Bookmark it! (You'll use it often)

---

### 2. Your GitHub Repositories (Where Code Lives)

**URL:** https://github.com/vionascu/dora

**What's here:**
- Source code for DORA system
- Configuration files
- Documentation
- Settings

**For you to know:**
- You don't need to change anything here
- Just know it exists
- It's where DORA gets its configuration

---

### 3. Configuration Files (Optional - Helpful)

**Location:** In each of your GitHub repositories

**File name:** `.dora.md`

**What to put in it:**
```
# Project Name

## Team
- Team Lead: John Doe
- Team Members: 5 people

## Links
- Confluence: https://...
- Jira: https://...

## Important Dates
- Launch Date: 2024-01-15
- Last Major Update: 2024-02-01
```

**Why it helps:**
- Adds context to your metrics
- Helps team members find information
- Makes reports more meaningful

---

## 📖 Step-by-Step: Your First Time

### First Visit to Dashboard

**Step 1: Open the Dashboard**
```
URL: https://vionascu.github.io/dora/public/
Action: Copy, paste, press Enter
```

**Step 2: See What's There**

You should see:
- A title "R&D Metrics Report"
- A list of projects on the left
- Lots of colorful metrics on the right

**Step 3: Select a Project**

```
LEFT SIDE of screen:
┌─────────────────┐
│  All Projects   │  ← Click this first to see all
│  ─────────────  │
│  RnDMetrics     │
│  TrailEquip     │
│  TrailWaze      │
└─────────────────┘
```

Click on any project to see just that project's data.

**Step 4: Look at the Metrics**

```
RIGHT SIDE of screen:
┌────────────────────────────────────┐
│ 📊 Basic Metrics                   │
│ ├─ Commits: 241 total              │
│ ├─ Contributors: 3 people          │
│ └─ Last update: 2 hours ago        │
│                                     │
│ 🚀 Deployment Metrics              │
│ ├─ Frequency: ~2 per month         │
│ ├─ Lead Time: 4.2 hours average    │
│ └─ Success Rate: 95%               │
│                                     │
│ 📈 Project Evolution               │
│ ├─ Velocity Trend: Increasing      │
│ ├─ Code Quality: Stable            │
│ └─ Team Growth: +1 this month      │
└────────────────────────────────────┘
```

---

### Understanding the Metrics

#### Commits
- **What it means:** Number of code changes
- **Good sign:** Steady increases = active development
- **Bad sign:** Long periods of zero = team might be blocked

#### Contributors
- **What it means:** Number of people making changes
- **Good sign:** 3+ people = good knowledge sharing
- **Bad sign:** Only 1 person = bus factor risk

#### Deployment Frequency
- **What it means:** How often you release to production
- **Good sign:** Regular, predictable releases
- **Bad sign:** Very rare or unpredictable

#### Lead Time
- **What it means:** Time from idea to deployed in production
- **Good sign:** Short (hours/days) = fast
- **Bad sign:** Long (weeks/months) = slow process

#### Velocity
- **What it means:** How much work the team completes
- **Good sign:** Consistent or increasing
- **Bad sign:** Dropping = team struggles

#### Code Quality
- **What it means:** How many tests and how well tested
- **Good sign:** High percentage (>80%)
- **Bad sign:** Low percentage = more bugs

---

## 📊 Understanding What You See

### Charts and Graphs Explained

Below the metrics numbers, you'll see visual charts. Here's what they mean:

---

### 📈 Velocity Trend (Line Chart)

**What you see:**
A line graph that goes up and down over time, showing how many commits your team makes each week.

```
   Commits
      50 │     ╱╲
         │    ╱  ╲    ╱╲
      40 │   ╱    ╲  ╱  ╲
         │  ╱      ╲╱    ╲╱
      30 │─────────────────
         │ Jan  Feb  Mar  Apr
         └────────────────→ Time
```

**What it means:**

| Pattern | Meaning | Action |
|---------|---------|--------|
| **Line going UP ↗️** | Team is writing more code | Great! Team is productive |
| **Line going DOWN ↘️** | Team is writing less code | Investigate why (vacation? blockers?) |
| **Line is FLAT ═** | Consistent work rate | Good predictability |
| **Sudden drop** | Something changed | Could be positive or negative - check it out |
| **Sudden spike** | Burst of activity | Maybe a deadline push or new features |

**What's healthy:**
- Consistent velocity is predictable (easier to plan)
- Gradual increases mean team improving
- Drops usually indicate obstacles (fix them!)

---

### 🎯 Test Coverage (Donut Chart)

**What you see:**
A colorful circle (donut shape) divided into sections. Green = code that's tested. Red = code that's not tested.

```
       ┌──────────────────┐
       │    ✓ GOOD        │  Green = 85% covered
       │    Tested        │
       │     85%          │  Red = 15% untested
       └──────────────────┘
          Bad Code
          Untested 15%
```

**What it means:**

| Coverage Level | Status | Risk Level | Action |
|---|---|---|---|
| **80-100% (big green)** | Excellent | 🟢 Low risk | Keep it up! Safe to deploy |
| **60-80% (medium green)** | Good | 🟡 Medium risk | Add more tests soon |
| **40-60% (small green)** | Poor | 🟠 High risk | Urgent: More tests needed |
| **Under 40% (mostly red)** | Dangerous | 🔴 Critical risk | STOP! Add tests before release |

**Why this matters:**
- High coverage = Fewer surprises when deploying
- Low coverage = More bugs appear in production
- Growing coverage = Team is improving

---

### 👥 Contributors (Bar Chart)

**What you see:**
A bar chart showing each team member and how many commits they've made.

```
Person A ████████░░ 8 commits  (57%)
Person B ██████░░░░ 6 commits  (43%)
Person C ████░░░░░░ 4 commits  (29%)
Person D ██░░░░░░░░ 2 commits  (14%)
```

**What it means:**

| Pattern | Status | Risk Level | Meaning |
|---------|--------|-----------|---------|
| **Bars all similar height** | Balanced | 🟢 Low risk | Great! Knowledge is shared |
| **One very tall bar** | Dominated | 🔴 High risk | Only one person knows this code! |
| **Gradually getting smaller** | Healthy | 🟢 Normal | Core team with contributors |
| **New bars appearing** | Growing | 🟢 Good sign | New team members onboarding |
| **Person disappears** | Attrition | 🟡 Watch it | Make sure others know their code |

**Why this matters:**
- Balanced team = Less risk if someone leaves
- One person = What happens if they quit?
- Growing diversity = Team learning from each other

---

### 💡 How to Use These Charts

**Daily:**
- Glance at trends
- Notice any major changes

**Weekly:**
- Check if line is going up or down
- Is coverage staying stable?
- Are new people contributing?

**Monthly:**
- Compare to last month's chart
- Identify patterns
- Plan improvements

---

### 🎯 What's a "Good" Dashboard?

Look for:
✓ Velocity line: Stable or increasing
✓ Test coverage: Green and high
✓ Contributors: Balanced and growing
✓ All numbers: Trending in right direction
✓ Recent activity: Updates from past few days

Worry about:
✗ Velocity dropping for weeks
✗ Coverage going red
✗ Only one person contributing
✗ No activity for months
✗ Numbers getting worse

---

## 🤔 Common Questions

### Q: Can I change the metrics myself?
**A:** No, they're calculated automatically from your code. To change them, change your development process!

---

### Q: How often are the metrics updated?
**A:** Daily (automatically every night at 2 AM UTC)

**Can I force an update?**
Yes! The team can trigger it manually if needed.

---

### Q: What if my project isn't showing?
**A:** It needs to be in the GitHub configuration. Contact your team lead to add it.

---

### Q: Can I export this data?
**A:** Yes! You can:
- Take screenshots
- Copy tables
- Download JSON files (technical)
- Share the dashboard URL

---

### Q: Is this data real or estimated?
**A:** Real! It reads actual commits, actual deployments, and actual code.

---

### Q: What if the numbers look wrong?
**A:** Common reasons:
- Force pushes (git history changed)
- Missing deployment tags
- Configuration issues

Contact your tech lead to investigate.

---

### Q: Can I see historical data?
**A:** Yes! Use the date filters at the top of the dashboard.

---

### Q: How is "Lead Time" calculated?
**A:** Average time between commits (shows how fast changes move through pipeline)

---

### Q: What's "Velocity"?
**A:** How many commits per day. Higher = faster development.

---

## 🔧 Troubleshooting (Simple Version)

### Problem: Dashboard shows "404 Not Found"

**What it means:** Page doesn't exist

**How to fix:**
1. Check the URL is correct: `https://vionascu.github.io/dora/public/`
2. Wait 2 minutes (might still be loading)
3. Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
4. Clear browser cache if still broken
5. Try a different browser

---

### Problem: Dashboard loads but no data shows

**What it means:** Data might be loading or missing

**How to fix:**
1. Wait 10 seconds (might still loading)
2. Refresh the page: `F5`
3. Open browser console: `F12`
4. Look for error messages (red text)
5. If you see errors, screenshot and contact tech lead

---

### Problem: My project doesn't show in the list

**What it means:** Project not configured in DORA

**How to fix:**
1. Check if your repository is on GitHub
2. Check if it's in the DORA configuration
3. Contact your tech lead or project manager
4. They need to add it to repos.yaml

---

### Problem: Numbers look wrong / Very low/high

**What it means:** Data calculation issue or config problem

**How to fix:**
1. Check the project has recent activity
2. Check deployments are properly tagged in git
3. Check `.dora.md` file exists in the repo
4. Contact tech lead to investigate

---

### Problem: Can't remember the dashboard URL

**Solution:**
1. Bookmark this page
2. Ask your team lead
3. Google "DORA dashboard vionascu"
4. Or just remember: `https://vionascu.github.io/dora/public/`

---

## 🎓 Tips for Non-Technical People

### Keep It Simple

Don't worry about:
- How metrics are calculated (it's technical)
- GitHub configuration (let tech people handle it)
- JSON files (you don't need to see them)

### Focus On:
- Is velocity going up or down?
- Are we deploying more often?
- Is code quality improving?
- Are we getting faster?

---

### Good Questions to Ask Your Team

- "Why did velocity drop this week?"
- "Can we deploy more frequently?"
- "How can we improve code quality?"
- "Are we moving faster than last month?"
- "What's preventing faster deployments?"

---

### How to Use This for Decisions

```
If Velocity is LOW:
→ Team might need help
→ Check if there are blockers
→ Consider adding resources

If Deployment Frequency is LOW:
→ Check if release process is slow
→ Look for automation opportunities
→ Ask team what's blocking releases

If Lead Time is HIGH:
→ Changes take too long to reach production
→ Process might be complex
→ Consider streamlining

If Code Quality is LOW:
→ More testing needed
→ Could cause problems in production
→ Prioritize test improvements
```

---

## 📞 Need Help?

### For Dashboard Questions:
1. Check this guide first
2. Ask your tech lead
3. Contact project manager

### For Data Issues:
1. Take a screenshot
2. Note the project name
3. Note the time/date
4. Contact tech lead with this info

### For Feature Requests:
1. Describe what you want to see
2. Explain why it would help
3. Contact product owner/team lead

---

## ✅ Quick Checklist

- [ ] I know the dashboard URL
- [ ] I can find my project in the list
- [ ] I understand what commits means
- [ ] I understand what velocity means
- [ ] I can identify improving metrics (up = good)
- [ ] I can identify declining metrics (down = bad)
- [ ] I know who to ask for help
- [ ] I've bookmarked the dashboard

---

## 🎯 Next Steps

### Week 1: Get Familiar
- Visit dashboard 2-3 times
- Click around and explore
- Read metrics for your project
- Share with your team

### Week 2: Start Using Data
- Notice trends
- Ask questions about changes
- Share observations with team
- Use data in stand-ups

### Week 3: Make Decisions
- Use metrics in planning
- Identify improvement opportunities
- Set goals based on data
- Track progress toward goals

---

## 📊 Glossary (Simple Terms)

| Term | Simple Explanation | Example |
|------|-------------------|---------|
| **Commit** | A code change saved to GitHub | "Fixed the login bug" |
| **Deployment** | Sending code to production | "Released v2.1.0" |
| **Velocity** | How fast team writes code | "50 commits per week" |
| **Lead Time** | Time to get code to production | "4 hours from commit to live" |
| **Frequency** | How often something happens | "Deploy 2 times per month" |
| **Coverage** | Percentage of code tested | "80% of code has tests" |
| **Repository** | Folder of code on GitHub | "The trailequip project" |
| **Tag** | Label for important versions | "v2.0.0 release" |
| **Metric** | A measurement | "50 commits this month" |
| **Trend** | Direction something is going | "Velocity increasing" |

---

## 🎉 You're Ready!

You now know:
- ✓ What DORA is
- ✓ How it works
- ✓ Where to find the dashboard
- ✓ How to read the metrics
- ✓ What the numbers mean
- ✓ How to troubleshoot basic issues
- ✓ How to use the data

**Go visit the dashboard: https://vionascu.github.io/dora/public/**

Happy exploring! 🚀

---

**Questions? Ask your team lead or project manager.**

**Last Updated:** February 3, 2026

