# Auto-Fix Workflow Guide

**Date:** February 3, 2026
**Status:** Active and Monitoring
**Purpose:** Automatically detect and fix common build failures

---

## Overview

The auto-fix workflow is an intelligent, self-healing CI/CD system that:

1. **Monitors** the DORA Metrics Pipeline for failures
2. **Analyzes** error logs to identify known issues
3. **Applies** safe, targeted fixes automatically
4. **Verifies** fixes before committing
5. **Re-runs** the pipeline to confirm success
6. **Prevents** infinite loops with safety checks

---

## How It Works

### 1. Detection Phase

When the DORA Metrics Pipeline fails, the auto-fix workflow automatically triggers and:

1. Downloads all workflow run logs
2. Analyzes logs for known error patterns
3. Identifies fixable issues

**Supported Error Patterns:**

| Error | Pattern | Fix Strategy |
|-------|---------|--------------|
| **Python Import Error** | `ModuleNotFoundError: No module named 'src'` | Verify PYTHONPATH configuration |
| **Git Submodule Error** | `No url found for submodule path` | Update .gitignore patterns |
| **Path Resolution Error** | `MANIFEST.json 404` | Verify path fallback logic |
| **Missing Directories** | `No such file or directory` | Verify directory creation |

### 2. Analysis Phase

The workflow performs intelligent analysis:

```yaml
# Checks performed:
✓ Python module import paths
✓ Git configuration and .gitignore
✓ File paths and locations
✓ Directory structure
✓ Critical configuration files
```

### 3. Fix Phase

For each detected error, the workflow:

1. **Verifies the fix is applicable** - Checks that the issue actually needs fixing
2. **Applies the fix** - Makes minimal, targeted changes
3. **Validates the fix** - Confirms the change is correct
4. **Commits the fix** - Only commits if validation passes

### 4. Verification Phase

After applying fixes:

1. **Checks for changes** - Determines if commits are needed
2. **Commits with context** - Explains what was fixed and why
3. **Pushes to main** - Makes changes available
4. **Re-runs pipeline** - Triggers workflow to test the fix

### 5. Safety Phase

Built-in safeguards prevent problems:

- **Infinite Loop Protection** - Tracks consecutive auto-fix commits, stops at 3
- **Conservative Fixing** - Only fixes known, safe issues
- **No Force Pushes** - Uses normal git operations
- **Audit Trail** - Logs all actions for review
- **Manual Override** - Requires explicit fixes for risky issues

---

## Workflow File Location

```
.github/workflows/auto-fix-failures.yml
```

---

## Current Configuration

### Trigger
```yaml
on:
  workflow_run:
    workflows: ["DORA Metrics Pipeline"]
    types: [completed]
    branches: [main]

if: github.event.workflow_run.conclusion == 'failure'
```

**Only runs when:**
- DORA Metrics Pipeline completes
- The pipeline has FAILED
- Changes are on the main branch

### Permissions
```yaml
permissions:
  contents: write    # Commit and push fixes
  actions: read      # Read workflow logs
```

---

## What Gets Fixed Automatically

### ✅ Safe Auto-Fixes (Applied Immediately)

**1. Python Path Configuration**
- Issue: `ModuleNotFoundError: No module named 'src'`
- Fix: Verify PYTHONPATH is set in workflow
- Risk: Very low - only verification, no changes
- Time to detect and fix: < 1 minute

**2. Git Submodule Configuration**
- Issue: Git tracking clone directories as submodules
- Fix: Update .gitignore with proper patterns
- Risk: Low - adds patterns to ignore file
- Time to detect and fix: < 2 minutes

### ⏳ Requires Manual Review

**1. Path Resolution Issues**
- Issue: MANIFEST.json or calculations not found
- Reason: Requires careful testing to ensure correct fix
- Action: Logs warning, no automatic fix applied
- Developer involvement: Required before deploying

**2. Complex Errors**
- Unknown error patterns that don't match known issues
- Risk: Too high to fix automatically
- Action: Reports to dashboard, requires investigation

---

## Example Scenario

### Scenario: Python Import Error in Build

**Timeline:**

```
14:30 UTC - Build fails with ModuleNotFoundError
           └─ Auto-fix workflow triggered

14:31 UTC - Workflow downloads and analyzes logs
           └─ Detects: Python path configuration issue
           └─ Decision: Safe to verify fix

14:32 UTC - Workflow verifies PYTHONPATH is configured
           └─ Status: ✅ Already configured correctly
           └─ Decision: No changes needed

14:33 UTC - Workflow reports findings
           └─ Logs: "PYTHONPATH already configured"
           └─ Output: Suggests investigating root cause

Result: Auto-fix confirms configuration is correct.
        Developer reviews logs to find actual issue.
```

### Scenario: Git Submodule Error in Build

**Timeline:**

```
15:45 UTC - Build fails with submodule error
           └─ Auto-fix workflow triggered

15:46 UTC - Workflow analyzes logs
           └─ Detects: Git submodule configuration missing
           └─ Decision: Safe to update .gitignore

15:47 UTC - Workflow updates .gitignore
           └─ Adds: git_artifacts/*/clone/ patterns
           └─ Action: Commits fix

15:48 UTC - Workflow commits and pushes
           └─ Commit: "fix: Auto-fix workflow failures"
           └─ Push: main branch updated

15:49 UTC - Pipeline re-triggered
           └─ Workflow dispatched on main
           └─ New run started with fixes applied

16:10 UTC - New build completes ✅ SUCCESS
           └─ Auto-fix successfully resolved issue
           └─ Metrics collection completed
           └─ Dashboard updated
```

---

## Monitoring Auto-Fix Activity

### View Auto-Fix Workflow Runs

1. Go to: https://github.com/vionascu/dora/actions
2. Filter by: `Auto-Fix Workflow Failures`
3. See: When triggered, what was fixed, results

### Check Commit Log

```bash
git log --oneline --grep="Auto-fix"
```

Shows all auto-fix commits with details.

### Review Detailed Logs

Each workflow run includes:

- **Logs Downloaded**: Timestamp and size of collected logs
- **Errors Detected**: All error patterns found
- **Fixes Applied**: Each action taken
- **Safety Checks**: Infinite loop prevention status
- **Results**: Success or manual review needed

---

## Safety Features in Detail

### 1. Infinite Loop Prevention

```bash
# Check: Are we in a loop of auto-fix commits?
LAST_COMMIT_MSG=$(git log -1 --pretty=%B)
COMMIT_COUNT=$(git log --oneline --grep="Auto-fix" | wc -l)

if [ "$COMMIT_COUNT" -gt 3 ]; then
  # Stop - too many consecutive auto-fixes
  exit 1
fi
```

**Limits:**
- Maximum 3 consecutive auto-fix commits
- After that, stops and requires manual intervention
- Prevents degradation of code quality

### 2. Conservative Approach

Only fixes issues where:
- Root cause is well-understood
- Fix is minimal and targeted
- Risk of regression is very low
- Can be verified automatically

### 3. Audit Trail

Every action is logged:
- What error was detected
- What fix was applied
- Whether fix succeeded
- Commit messages explain the fix

### 4. Manual Override

For risky issues:
- Logs warning with details
- Does not auto-commit
- Waits for manual review
- Developer decides on fix

---

## Extending Auto-Fix

### Adding New Error Patterns

To add support for new error types:

1. **Identify the error pattern** in logs
2. **Add detection** in analyze step:
   ```bash
   if echo "$LOGS" | grep -q "your error pattern"; then
     echo "new_error_type=true" >> $GITHUB_OUTPUT
   fi
   ```

3. **Add fix step** (if safe):
   ```yaml
   - name: 🛠️ Fix New Error Type
     if: steps.analyze.outputs.new_error_type == 'true'
     run: |
       # Apply targeted fix
       # Verify fix
       # Log changes
   ```

4. **Test thoroughly** before merging

---

## Workflow Steps Explained

### Step 1: Checkout
```yaml
- name: Checkout repository
  uses: actions/checkout@v3
```
Gets the latest code to analyze and fix.

### Step 2: Download Logs
```yaml
- name: Download workflow logs
  uses: actions/github-script@v7
```
Retrieves all logs from the failed build run.

### Step 3: Analyze Errors
```yaml
- name: 🔎 Analyze Error Patterns
```
Scans logs for known error patterns.

### Step 4: Apply Fixes
```yaml
- name: 🛠️ Fix [Error Type]
```
Applies targeted fixes for detected errors.

### Step 5: Commit Changes
```yaml
- name: Commit fixes (if any)
```
Commits fixes with descriptive message.

### Step 6: Push & Re-Run
```yaml
- name: Push fixes
- name: Trigger workflow re-run
```
Pushes changes and triggers pipeline to test.

### Step 7: Safety Check
```yaml
- name: 🔒 Safety Check - No Infinite Loops
```
Verifies we're not in an infinite loop.

---

## Limitations

### Cannot Fix Automatically

- **Logic errors** in Python code
- **Configuration issues** in YAML files (require careful validation)
- **Missing data sources** (JIRA exports, repositories)
- **Permission issues** (requires repo setup changes)
- **API failures** (external service issues)
- **Resource constraints** (memory, timeout issues)

### Manual Investigation Required For

```
❌ New error patterns not in known list
❌ Complex multi-step failures
❌ Failures affecting multiple components
❌ Failures with unclear root cause
❌ Production data integrity concerns
```

---

## Best Practices

### For Developers

1. **Monitor auto-fix activity** - Check GitHub Actions for what was fixed
2. **Review commits** - Understand what changes were made
3. **Investigate root causes** - Don't rely only on auto-fixes
4. **Update error patterns** - Add new patterns as they're discovered
5. **Test thoroughly** - Always test fixes locally first

### For Operations

1. **Set up notifications** - Get alerted when auto-fix runs
2. **Review weekly** - Check if same errors keep happening
3. **Update fixes** - Improve auto-fix logic as you learn
4. **Monitor metrics** - Track fix success rate
5. **Document issues** - Keep record of recurrent problems

---

## Troubleshooting Auto-Fix

### Auto-Fix Never Triggers

**Check:**
1. Is DORA Metrics Pipeline actually failing?
2. Is auto-fix workflow enabled in repo settings?
3. Check: Settings > Actions > General > "Workflow permissions"

**Solution:**
```bash
# Verify workflow file exists
ls -la .github/workflows/auto-fix-failures.yml

# Check GitHub Actions settings
# Repository > Settings > Actions > General
# Verify "Allow ... actions and reusable workflows" is enabled
```

### Auto-Fix Triggers But Doesn't Fix

**Check:**
1. View workflow logs: Actions > Auto-Fix Workflow Failures
2. See which step failed
3. Check error messages

**Common causes:**
- Permission issues (check `permissions:` in workflow)
- Unrecognized error pattern (not in detection list)
- Git configuration (user.name, user.email not set)

### Infinite Loop Prevention Triggered

**If you see:** "Too many consecutive auto-fix commits"

**Action taken:** Workflow stopped to prevent loop

**Next step:**
1. Review recent auto-fix commits
2. Find root cause of recurring error
3. Implement permanent fix
4. Remove auto-fix commits if necessary

---

## Monitoring Dashboard

### Metrics to Track

| Metric | Target | Current |
|--------|--------|---------|
| Auto-fix success rate | > 90% | Monitor |
| Build failure rate | < 5% | Monitor |
| Average time to fix | < 5 min | Monitor |
| Manual fixes needed | < 20% | Monitor |

### Where to Check

1. **GitHub Actions Tab** - See all auto-fix runs
2. **Commit Log** - Review all auto-fix commits
3. **Build Status** - Check success rates
4. **Alerts** - Get notifications of issues

---

## Future Enhancements

### Potential Improvements

1. **Machine learning** - Learn from successful fixes to detect new patterns
2. **Slack integration** - Notify team of auto-fixes
3. **Rollback capability** - Automatically revert failed auto-fix attempts
4. **Analytics dashboard** - Visualize failure patterns
5. **Smart retry logic** - Exponential backoff for transient errors
6. **Test coverage** - Run tests before committing fixes

---

## Summary

**The auto-fix workflow provides:**

✅ **Automatic detection** of common build failures
✅ **Intelligent fixing** of known, safe issues
✅ **Safety mechanisms** to prevent problems
✅ **Audit trail** of all actions
✅ **Transparent operation** with detailed logging
✅ **Manual escape hatches** for risky situations

**Result:**

- **Faster recovery** from build failures (minutes instead of hours)
- **Reduced manual work** for known issues
- **Better reliability** of CI/CD pipeline
- **Focus on root causes** rather than symptom fixing
- **Continuous improvement** as new patterns are added

---

## Contact & Support

If the auto-fix workflow is:

- **Not triggering** → Check GitHub Actions permissions
- **Fixing too aggressively** → Review safety limits
- **Missing error patterns** → Add new patterns to detection
- **Causing infinite loops** → Review recent commits and reduce retry limit

For issues or questions, check the workflow logs at:
```
https://github.com/vionascu/dora/actions?query=workflow:auto-fix-failures
```

---

**Last Updated:** February 3, 2026
**Status:** Active and Monitoring

