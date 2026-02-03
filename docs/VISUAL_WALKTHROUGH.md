# Visual Walkthrough - Your First Time Using DORA 👀

**This guide shows you exactly what you'll see, step by step**

---

## 📍 Step 1: Getting There

### What You Do:
1. Open your browser
2. Go to: `https://vionascu.github.io/dora/public/`
3. Press Enter

### What You Should See:

```
┌──────────────────────────────────────────────────────────┐
│ https://vionascu.github.io/dora/public/      [⟳] [≡]   │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                                                          │
│     R&D Metrics Report                                  │
│                                                          │
│     Professional Metrics Dashboard                      │
│                                                          │
│     Last Updated: 2 hours ago ✓                         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**✓ Success:** You see "R&D Metrics Report" at the top

**✗ Problem:** See "404" or blank page? See Troubleshooting below

---

## 📍 Step 2: Find the Project Selector

### What You Do:
Look at the LEFT side of the screen

### What You Should See:

```
┌─ LEFT SIDE ────────────────┐
│                            │
│  PROJECT SELECTOR          │
│  ──────────────────        │
│                            │
│  🔘 All Projects           │
│  ○  RnDMetrics             │
│  ○  TrailEquip             │
│  ○  TrailWaze              │
│                            │
│  (Your choices depend on   │
│   what projects are set up)│
│                            │
└────────────────────────────┘
```

**Where it is:** Left side, below the title

**What each option does:**
- 🔘 **All Projects** = See all metrics combined
- **RnDMetrics** = Only that project
- **TrailEquip** = Only that project
- **TrailWaze** = Only that project

---

## 📍 Step 3: Select "All Projects" (First Time)

### What You Do:
Click on the **All Projects** button

### What You Should See:

The RIGHT side of the screen fills with information:

```
┌─ RIGHT SIDE ─────────────────────────────────────┐
│                                                   │
│  📊 BASIC METRICS                                │
│  ├─ Total Commits: 241                           │
│  ├─ Unique Contributors: 3                       │
│  ├─ Active Repositories: 3                       │
│  └─ Last Activity: 2 hours ago                   │
│                                                   │
│  🚀 DEPLOYMENT METRICS                           │
│  ├─ Avg Deployment Frequency: ~2 per month      │
│  ├─ Avg Lead Time: 4.2 hours                    │
│  └─ Success Rate: 95%                           │
│                                                   │
│  📈 PROJECT EVOLUTION & ANALYSIS                │
│  ├─ Velocity Trend: Increasing ↗️               │
│  ├─ Code Quality: 85% coverage                  │
│  └─ Team Growth: +1 this month                  │
│                                                   │
└───────────────────────────────────────────────────┘
```

**This shows:** Combined data from all your projects

**Good signs to see:**
- ✓ Commits increasing
- ✓ Multiple contributors
- ✓ Regular deployments
- ✓ Quality > 80%

---

## 📍 Step 4: Click on One Project

### What You Do:
Click on **"RnDMetrics"** (or any other project)

### What Changes:

The right side updates to show ONLY that project:

```
┌─ RIGHT SIDE (After clicking RnDMetrics) ───────┐
│                                                  │
│  📊 BASIC METRICS                               │
│  ├─ Total Commits: 38                           │
│  ├─ Unique Contributors: 1                      │
│  ├─ Last Activity: 1 day ago                    │
│  └─ Average Commits/Day: 0.5                    │
│                                                  │
│  🚀 DEPLOYMENT METRICS                          │
│  ├─ Deployment Frequency: ~1 per month          │
│  ├─ Avg Lead Time: 4.8 hours                    │
│  └─ Success Rate: 100%                          │
│                                                  │
│  📈 PROJECT EVOLUTION                           │
│  ├─ Velocity: 38 commits total                  │
│  ├─ Code Quality: 46.68% coverage               │
│  ├─ Refactoring Activity: Moderate              │
│  └─ AI Usage Patterns: Minimal                  │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Notice:** Numbers are DIFFERENT for each project

**Compare:** See differences in team size, speed, quality

---

## 📍 Step 5: Understanding the Charts

### What You See:

Below the metrics, you'll see CHARTS:

#### Chart 1: 📈 Velocity Trend (Line Chart)
```
Shows how many commits your team makes over time

   Commits
      50 │     ╱╲
         │    ╱  ╲    ╱╲
      40 │   ╱    ╲  ╱  ╲
         │  ╱      ╲╱    ╲╱
      30 │─────────────────
         │ Jan  Feb  Mar  Apr
         └────────────────→ Time

📊 What it means:
  ✓ Line going UP    = Team getting faster (good!)
  ✗ Line going DOWN  = Team getting slower (needs help)
  ═ Line is FLAT     = Consistent pace (stable, predictable)

💡 Action:
  - UP? Keep doing what you're doing! 🎉
  - DOWN? Find out why (blockers, vacations, complexity)
  - Know your baseline to spot changes
```

#### Chart 2: 🎯 Test Coverage (Donut Chart)
```
Shows how much of your code is tested

       ┌─────────────────┐
       │   GOOD CODE     │
       │   ✓ Tested      │  Green = 85% covered
       │     85%         │  Red = 15% untested
       └─────────────────┘
           Bad Code
           Not Tested
              15%

📊 What it means:
  ✓ Green (high %)  = Safe to deploy
  ✗ Red (low %)     = Risky, more tests needed
  ✓ 80%+ is good    = Solid coverage

💡 Action:
  - Growing green? Great testing! ✓
  - Growing red? Add more tests
  - Track coverage trends over time
  - Higher = More confidence in code
```

#### Chart 3: 👥 Contributors (Bar Chart)
```
Shows who is writing the code

Person A ████████░░ 8 commits  (57%)
Person B ██████░░░░ 6 commits  (43%)
Person C ███░░░░░░░ 3 commits  (21%)
Person D ██░░░░░░░░ 2 commits  (14%)

📊 What it means:
  ✓ Balanced bars   = Good knowledge sharing
  ✗ One tall bar    = Risk! Only one person knows the code
  ✓ Many people     = Better resilience, less risk

💡 Action:
  - Only one contributor? Have code reviews to share knowledge
  - Multiple people? Good! Knowledge spread across team
  - New people appearing? Great! Growing the team
  - Someone disappear? Make sure others know the code
```

---

## 📍 Step 6: Using the Date Filter

### What You See (Top of Page):

```
┌───────────────────────────────────────┐
│ DATE FILTER                           │
├───────────────────────────────────────┤
│ From: [Jan 1, 2026]   To: [Feb 1, 2026] │
│                                       │
│ ⟲ This changes all metrics below      │
└───────────────────────────────────────┘
```

### What You Can Do:

**Click on dates to change them:**

1. Click "From" date
2. Select earlier date
3. Metrics update to show that time period
4. Compare old vs new

**Example:**
```
Scenario: January had 20 commits
         February has 30 commits

Interpretation: Team is accelerating! 📈
```

---

## 📍 Step 7: Looking for Good Signs

### On the Dashboard, Look For:

✓ **Green/High Numbers**
```
- Commits: 100+ is good
- Contributors: 3+ is good
- Coverage: 80%+ is good
- Frequency: Regular deployments
```

✓ **Charts Going Up ↗️**
```
- Velocity trend increasing
- Contributors increasing
- Quality improving
```

✓ **Recent Activity**
```
- Last commit: within a few days
- Recent deployments
- Regular updates
```

### Watch Out For ⚠️

✗ **Red/Low Numbers**
```
- Commits: 0 for 2+ weeks
- Contributors: Only 1 person
- Coverage: Less than 50%
- No recent activity
```

✗ **Charts Going Down ↘️**
```
- Velocity dropping
- Quality declining
- Deployment frequency falling
```

---

## 📍 Step 8: Comparing Projects

### What You Can Do:

**Method 1: Click through projects**
```
1. Click "RnDMetrics" → See its metrics
2. Click "TrailEquip" → See its metrics
3. Click "TrailWaze" → See its metrics
4. Compare which is fastest/best
```

**Method 2: Select "All Projects"**
```
See combined view
Understand overall team performance
```

### What to Compare:

```
Question: Which team is fastest?
Answer: Look at deployment frequency & lead time

Question: Which has best quality?
Answer: Look at code coverage percentage

Question: Which team is growing?
Answer: Look at contributor count & velocity trend

Question: Which needs help?
Answer: Look for declining metrics or low numbers
```

---

## 📍 Step 9: Sharing What You Found

### Screenshots:

**What to take:**
1. Open dashboard
2. Select your project
3. Take screenshot (Print Screen button)
4. Paste into email/document
5. Share with team

### What to Say:

**Example:**
```
"Hey team, I checked the metrics dashboard.
RnDMetrics had 38 commits this month with
46% code coverage. We should prioritize
adding more tests."
```

---

## 📍 Step 10: Coming Back Later

### How to Remember:

**Option 1: Bookmark**
```
1. URL: https://vionascu.github.io/dora/public/
2. Ctrl+D (or Cmd+D on Mac)
3. Click "Save"
4. Later: Click bookmark to return
```

**Option 2: History**
```
1. Click browser history (Ctrl+H)
2. Search for "dora" or "github.io"
3. Click to return
```

**Option 3: Favorites**
```
1. Save this guide
2. Keep the URL written down
3. Share with team
```

---

## 🎨 Color Legend

```
What Colors Mean:

🟢 GREEN
├─ Good sign
├─ Metric is healthy
└─ Keep it up!

🟡 YELLOW
├─ Warning
├─ Something to watch
└─ May need attention

🔴 RED
├─ Problem
├─ Action needed
└─ Investigate!

⚫ GRAY
├─ No data
├─ Not enough information
└─ Might need setup
```

---

## 🆘 Troubleshooting Guide

### Problem: Page Won't Load

**Symptom:** Blank page or "404 Not Found"

**Quick Fix:**
1. Check URL: `https://vionascu.github.io/dora/public/`
2. Press Ctrl+Shift+R to hard refresh
3. Try different browser
4. Check internet connection
5. Contact tech lead if still broken

---

### Problem: Dashboard Loads But No Data

**Symptom:** Page loads but metrics are empty or "N/A"

**Quick Fix:**
1. Wait 10 seconds (data might be loading)
2. Press F5 to refresh
3. Check date filter (might be filtering out all data)
4. Select "All Projects"
5. Contact tech lead if empty

---

### Problem: My Project Isn't Listed

**Symptom:** Project doesn't show in project selector

**Quick Fix:**
1. Check project exists on GitHub
2. Check spelling of project name
3. Contact tech lead
4. They need to add it to configuration

---

### Problem: Numbers Look Wrong

**Symptom:** Metrics seem too high/low or different from expected

**Possible Causes:**
- Fresh project (no data yet)
- Git history changed (force push)
- No deployment tags
- Configuration issue

**How to Fix:**
1. Check project has recent commits
2. Contact tech lead to investigate
3. Check if configuration is correct

---

## 📱 Mobile View (if on phone)

**Changes to expect:**
- Some features might be hidden
- Scroll horizontally to see charts
- Tap buttons carefully
- Use landscape mode if available

**Better on:** Desktop or laptop

---

## 🔔 What to Expect Over Time

**First Visit:**
- Will be confused (normal!)
- See lots of numbers
- Don't understand everything yet

**Second Visit:**
- Start recognizing patterns
- Understand which metrics matter
- See if things changed

**Regular Visits (Weekly):**
- Spot trends quickly
- Know what good/bad looks like
- Start using data for decisions

**Monthly View:**
- See big picture
- Plan improvements
- Set goals

---

## ✅ Checklist: "I'm Ready"

- [ ] I know the dashboard URL
- [ ] I can open the dashboard
- [ ] I can find my project
- [ ] I can see the metrics
- [ ] I understand what numbers mean
- [ ] I can read a chart
- [ ] I can identify good vs bad signs
- [ ] I know who to ask for help
- [ ] I've bookmarked the page
- [ ] I've shared with my team

---

## 🎓 Next Steps

### Now:
1. ✓ Visit dashboard
2. ✓ Click around
3. ✓ Get comfortable

### This Week:
1. Check dashboard 2-3 times
2. Note any changes
3. Share findings with team

### Next Week:
1. Use data in meetings
2. Make observations
3. Ask why things changed

### Long Term:
1. Use metrics for planning
2. Set improvement goals
3. Track progress

---

## 📞 Need Help?

| What | Who | How |
|------|-----|-----|
| **Dashboard help** | Tech lead | Ask in person/chat |
| **Data seems wrong** | Tech lead | Show screenshot |
| **Want feature** | Project manager | Describe idea |
| **More questions** | Your team | Group training |

---

## 🎉 You're Ready!

Go visit: **https://vionascu.github.io/dora/public/**

Take your time exploring. You can't break anything by looking around!

---

**Made for:** Everyone who needs to understand DORA

**Questions?** See BEGINNERS_GUIDE.md for more

**Last Updated:** February 3, 2026

