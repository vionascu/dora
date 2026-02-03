# DORA Dashboard - Quick Reference Card 📋

**Print this out or bookmark it!**

---

## 🚀 Quick Access

| What | Where | Action |
|------|-------|--------|
| **Dashboard** | https://vionascu.github.io/dora/public/ | Open in browser |
| **Full Guide** | docs/BEGINNERS_GUIDE.md | Read for details |
| **GitHub** | https://github.com/vionascu/dora | Source code |

---

## 📊 What Each Metric Means

### 🎯 Key Metrics

```
📈 VELOCITY
↗️  UP = Good (team working faster)
↘️  DOWN = Watch (team slower)
───  FLAT = Steady (consistent)

🚀 DEPLOYMENT FREQUENCY
↑ More often = Faster releases (good!)
↓ Less often = Slow releases (slower)

⏱️ LEAD TIME
📉 Shorter = Faster to production (good!)
📈 Longer = Slower to production (slower)

✅ CODE QUALITY
🟢 80%+ = Well tested (safe!)
🟠 50-80% = Partly tested (ok)
🔴 <50% = Poorly tested (risky!)

👥 CONTRIBUTORS
🟢 3+ = Good knowledge sharing
🟡 2 = Limited coverage
🔴 1 = Major risk!
```

---

## 🎮 How to Use the Dashboard

### 1️⃣ Load Dashboard
```
URL: https://vionascu.github.io/dora/public/
```

### 2️⃣ Pick a Project
```
Left side dropdown:
- All Projects (see everything)
- RnDMetrics (just this project)
- TrailEquip (just this project)
- TrailWaze (just this project)
```

### 3️⃣ Read the Metrics
```
Right side shows:
- Basic Metrics (commits, people)
- Deployment Metrics (speed)
- Evolution Metrics (trends)
```

### 4️⃣ Filter by Date (Optional)
```
Top of page:
- From date: Click to select
- To date: Click to select
- See metrics for that time period
```

### 5️⃣ Interpret Results
```
Compare to last month:
- ⬆️ Going up = Improving ✓
- ⬇️ Going down = Declining ✗
- ➡️ Staying same = Stable
```

---

## 📊 Understanding the Charts

### 📈 Velocity Trend (Line Chart)
```
Commits
   50 │     ╱╲
      │    ╱  ╲    ╱╲
   40 │   ╱    ╲  ╱  ╲
      │  ╱      ╲╱    ╲╱
   30 │─────────────────
      │ Jan  Feb  Mar  Apr
      └────────────────→

↗️ UP = Getting faster (good!)
↘️ DOWN = Getting slower (watch!)
═ FLAT = Consistent pace (stable)
```

### 🎯 Test Coverage (Donut Chart)
```
    ┌──────────┐
    │  GOOD    │  Green = 85% tested
    │  85%     │  Red = 15% untested
    └──────────┘
      Bad 15%

🟢 High % = Safe to deploy
🔴 Low % = Need more tests
```

### 👥 Contributors (Bar Chart)
```
Person A ████████░░ 8 commits
Person B ██████░░░░ 6 commits
Person C ████░░░░░░ 4 commits

✓ Balanced = Good (knowledge shared)
✗ Dominated = Risk (only 1 person knows)
✓ More people = Better resilience
```

---

## 🎨 Colors Mean This

| Color | Meaning | Action |
|-------|---------|--------|
| 🟢 Green | Good / Healthy | Keep it up! |
| 🟡 Yellow | Warning / Check | Monitor closely |
| 🔴 Red | Problem / Risky | Take action |
| ⚫ Gray | No data / Unknown | Investigate |

---

## 💡 What to Look For

### ✓ Good Signs

- Commits increasing ✓
- More people contributing ✓
- Deploying regularly ✓
- Fast lead time ✓
- High test coverage ✓
- Consistent velocity ✓

### ✗ Bad Signs

- No commits for 2+ weeks ✗
- Only 1 person coding ✗
- Haven't deployed in months ✗
- Slow lead time ✗
- Low test coverage ✗
- Dropping velocity ✗

---

## 🔍 Troubleshooting Quick Fix

| Problem | Quick Fix |
|---------|-----------|
| **Page won't load** | Ctrl+Shift+R (hard refresh) |
| **No data shows** | Wait 10 sec, then F5 (refresh) |
| **My project missing** | Contact tech lead to add it |
| **Numbers look wrong** | Check project has recent commits |
| **Can't find dashboard** | Bookmark it now! |
| **Need help** | Ask your tech lead |

---

## 📞 Who to Contact

| Question | Contact |
|----------|---------|
| How to use dashboard | Tech lead or this guide |
| Data looks wrong | Tech lead |
| Feature request | Project manager |
| Can't see my project | Tech lead |
| Want more details | Read BEGINNERS_GUIDE.md |

---

## 🎯 Using Data for Decisions

### Scenario 1: Velocity Drops
```
Question: "Why less commits this week?"
Possible answers:
- Team vacation
- Waiting on requirements
- Too many bugs to fix
- Blocked on dependencies

Action:
- Ask the team
- Remove blockers
- Plan accordingly
```

### Scenario 2: Low Deployment Frequency
```
Question: "Why aren't we shipping?"
Possible answers:
- Release process is slow
- Waiting for approvals
- Testing takes too long
- Manual steps needed

Action:
- Talk to tech lead
- Identify bottlenecks
- Streamline process
```

### Scenario 3: Low Code Quality
```
Question: "Why is test coverage low?"
Possible answers:
- Team too busy to write tests
- Not enough tools/setup
- No testing requirements
- Tests keep failing

Action:
- Set testing goals
- Add testing support
- Make it required
- Fix broken tests
```

---

## 📱 Mobile Friendly?

✓ Yes! Dashboard works on phones/tablets

**Best experience:** Desktop or laptop

**Mobile tips:**
- Tap "hamburger" menu (≡) if needed
- Scroll to see all metrics
- Use landscape mode for better view

---

## 💾 Save This Reference

### Print It
1. Open this file
2. Print to PDF
3. Save it somewhere
4. Print on paper if you want

### Bookmark It
1. Save URL: https://vionascu.github.io/dora/public/
2. Bookmark in browser
3. Share with team

### Share with Team
1. Share this quick reference
2. Share the beginner guide
3. Train the team together

---

## ⏰ When to Check the Dashboard

**Daily:**
- Developers: Check if metrics changed
- Managers: Quick pulse check

**Weekly:**
- Review velocity
- Check deployment progress
- Identify blockers

**Monthly:**
- Full analysis
- Trend identification
- Planning next month

**Quarterly:**
- Big picture review
- Strategic planning
- Set new goals

---

## 🎓 Learn More

### Want Details?
→ Read: docs/BEGINNERS_GUIDE.md

### Want Technical Info?
→ Read: docs/NON_INTRUSIVE_ARCHITECTURE.md

### Want Setup Help?
→ Read: docs/PROJECT_CONFIG_GUIDE.md

### Want to Contribute?
→ Contact your tech lead

---

## 🔗 Important Links

**Dashboard:**
https://vionascu.github.io/dora/public/

**GitHub Repository:**
https://github.com/vionascu/dora

**Documentation:**
https://github.com/vionascu/dora/tree/main/docs

**This Reference:**
docs/QUICK_REFERENCE_CARD.md

---

## ✅ One-Minute Summary

1. **What:** Tool that measures team speed and code quality
2. **Why:** Make better decisions with real data
3. **Where:** https://vionascu.github.io/dora/public/
4. **How:** Open → Pick project → Read numbers
5. **Use:** Compare to see if improving
6. **Help:** Ask tech lead if confused

---

## 🎯 Your First Visit

**Today:**
- [ ] Bookmark dashboard URL
- [ ] Open dashboard
- [ ] Find your project
- [ ] Look at the metrics
- [ ] Take screenshot

**This Week:**
- [ ] Visit dashboard 2-3 times
- [ ] Get familiar with numbers
- [ ] Ask questions about changes
- [ ] Share with team

**Next Week:**
- [ ] Use data in planning
- [ ] Set improvement goals
- [ ] Track progress

---

**Made for:** Everyone on the team

**Questions?** Ask your tech lead

**Last Updated:** February 3, 2026

