#!/usr/bin/env python3
"""
Calculate evolution metrics for tracking project progress and improvements
- Velocity trends (commits over time)
- Coverage trends
- Team growth/churn
- Refactorization activity
- AI usage indicators
- Code quality metrics
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

class EvolutionMetricsCalculator:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.git_artifacts = self.root_dir / "git_artifacts"
        self.calculations = self.root_dir / "calculations"

    def _write_json(self, path, payload):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)

    def _load_commits(self, repo_name):
        """Load commits from git artifacts"""
        commits_file = self.git_artifacts / repo_name / "commits.json"
        if not commits_file.exists():
            return []
        with open(commits_file, "r") as f:
            data = json.load(f)
        return data.get("commits", [])

    def _repo_names(self):
        if not self.git_artifacts.exists():
            return []
        repos = []
        for entry in sorted(self.git_artifacts.iterdir()):
            if entry.is_dir() and not entry.name.startswith("."):
                repos.append(entry.name)
        return repos

    def calculate_velocity_trends(self, repo_name):
        """Calculate velocity trends: commits per week over time"""
        commits = self._load_commits(repo_name)
        if not commits:
            return None

        # Parse commits by date
        commits_by_date = defaultdict(int)
        for commit in commits:
            timestamp = commit.get("timestamp", "")
            if timestamp:
                # Extract date (YYYY-MM-DD)
                date = timestamp.split(" ")[0]
                commits_by_date[date] += 1

        if not commits_by_date:
            return None

        # Group by week
        commits_by_week = defaultdict(int)
        week_labels = []

        for date_str in sorted(commits_by_date.keys()):
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                # ISO week format: YYYY-WXX
                week_key = date.strftime("%Y-W%W")
                commits_by_week[week_key] += commits_by_date[date_str]
            except:
                pass

        return {
            "metric_id": f"repo.velocity_trend.{repo_name}",
            "repo": repo_name,
            "repos": [repo_name],
            "inputs": [str((self.git_artifacts / repo_name / "commits.json").relative_to(self.root_dir))],
            "time_range": {"start": min(commits_by_date.keys()), "end": max(commits_by_date.keys())},
            "weekly_data": dict(sorted(commits_by_week.items())),
            "total_commits": len(commits),
            "weeks_active": len(commits_by_week),
            "avg_commits_per_week": round(len(commits) / len(commits_by_week), 2) if commits_by_week else 0,
            "method": "Count commits by ISO week to show velocity trends over time",
            "calculated_at": datetime.utcnow().isoformat() + "Z"
        }

    def calculate_contributor_growth(self, repo_name):
        """Track contributor growth over time"""
        commits = self._load_commits(repo_name)
        if not commits:
            return None

        # Track cumulative unique contributors by date
        contributors_by_date = {}
        seen_authors = set()

        for commit in sorted(commits, key=lambda c: c.get("timestamp", "")):
            author = commit.get("author", "")
            timestamp = commit.get("timestamp", "")
            if author and timestamp:
                date = timestamp.split(" ")[0]
                if author not in seen_authors:
                    seen_authors.add(author)
                    if date not in contributors_by_date:
                        contributors_by_date[date] = 0
                    contributors_by_date[date] = len(seen_authors)

        if not contributors_by_date:
            return None

        dates = sorted(contributors_by_date.keys())

        return {
            "metric_id": f"repo.contributor_growth.{repo_name}",
            "repo": repo_name,
            "repos": [repo_name],
            "inputs": [str((self.git_artifacts / repo_name / "commits.json").relative_to(self.root_dir))],
            "time_range": {"start": dates[0], "end": dates[-1]},
            "growth_timeline": dict(sorted(contributors_by_date.items())),
            "total_contributors": len(seen_authors),
            "first_contributor_date": dates[0],
            "latest_contributor_date": dates[-1],
            "avg_new_contributors_per_month": round(len(seen_authors) / (len(set(d[:7] for d in dates)) or 1), 2),
            "method": "Track unique contributors cumulative growth over time",
            "calculated_at": datetime.utcnow().isoformat() + "Z"
        }

    def analyze_refactorization_activity(self, repo_name):
        """Detect refactorization and optimization work"""
        commits = self._load_commits(repo_name)
        if not commits:
            return None

        refactor_keywords = {
            "refactor": [],
            "optimize": [],
            "improve": [],
            "cleanup": [],
            "cleanup": [],
            "tech debt": [],
            "deprecat": [],
        }

        for commit in commits:
            message = commit.get("subject", "").lower()
            for keyword in refactor_keywords:
                if keyword in message:
                    refactor_keywords[keyword].append({
                        "timestamp": commit.get("timestamp", ""),
                        "author": commit.get("author", ""),
                        "subject": commit.get("subject", "")
                    })

        total_refactor_commits = sum(len(v) for v in refactor_keywords.values())

        return {
            "metric_id": f"repo.refactorization_activity.{repo_name}",
            "repo": repo_name,
            "repos": [repo_name],
            "inputs": [str((self.git_artifacts / repo_name / "commits.json").relative_to(self.root_dir))],
            "time_range": {"start": commits[0].get("timestamp", "")[:10] if commits else None,
                          "end": commits[-1].get("timestamp", "")[:10] if commits else None},
            "refactor_events": {k: len(v) for k, v in refactor_keywords.items() if v},
            "total_refactor_commits": total_refactor_commits,
            "refactor_percentage": round((total_refactor_commits / len(commits) * 100), 2) if commits else 0,
            "timeline": {k: [c["timestamp"][:10] for c in v] for k, v in refactor_keywords.items() if v},
            "method": "Analyze commit messages for refactorization-related keywords",
            "calculated_at": datetime.utcnow().isoformat() + "Z"
        }

    def analyze_ai_usage(self, repo_name):
        """Detect AI-assisted development patterns"""
        commits = self._load_commits(repo_name)
        if not commits:
            return None

        ai_indicators = {
            "claude": [],
            "chatgpt": [],
            "copilot": [],
            "ai-generated": [],
            "assisted": [],
            "generated": [],
        }

        bug_fix_commits = []
        feature_commits = []
        large_commits = []

        for commit in commits:
            message = commit.get("subject", "").lower()

            # Check for explicit AI mentions
            for indicator in ai_indicators:
                if indicator in message:
                    ai_indicators[indicator].append({
                        "timestamp": commit.get("timestamp", ""),
                        "author": commit.get("author", ""),
                        "subject": commit.get("subject", "")
                    })

            # Categorize commits
            if any(kw in message for kw in ["fix", "bug", "issue", "patch"]):
                bug_fix_commits.append(commit)
            if any(kw in message for kw in ["feature", "add", "implement", "new"]):
                feature_commits.append(commit)

        explicit_ai_commits = sum(len(v) for v in ai_indicators.values())

        return {
            "metric_id": f"repo.ai_usage_indicators.{repo_name}",
            "repo": repo_name,
            "repos": [repo_name],
            "inputs": [str((self.git_artifacts / repo_name / "commits.json").relative_to(self.root_dir))],
            "time_range": {"start": commits[0].get("timestamp", "")[:10] if commits else None,
                          "end": commits[-1].get("timestamp", "")[:10] if commits else None},
            "explicit_ai_mentions": {k: len(v) for k, v in ai_indicators.items() if v},
            "total_ai_attributed_commits": explicit_ai_commits,
            "ai_percentage": round((explicit_ai_commits / len(commits) * 100), 2) if commits else 0,
            "bug_fix_commits": len(bug_fix_commits),
            "feature_commits": len(feature_commits),
            "bug_fix_percentage": round((len(bug_fix_commits) / len(commits) * 100), 2) if commits else 0,
            "feature_percentage": round((len(feature_commits) / len(commits) * 100), 2) if commits else 0,
            "note": "Explicit AI mentions detected from commit messages",
            "method": "Analyze commit messages for AI framework mentions and work pattern indicators",
            "calculated_at": datetime.utcnow().isoformat() + "Z"
        }

    def analyze_code_quality_evolution(self, repo_name):
        """Analyze code quality changes over time"""
        # Check if coverage data exists
        coverage_file = self.calculations / "per_repo" / repo_name / "coverage.json"
        commits = self._load_commits(repo_name)

        if not coverage_file.exists() or not commits:
            return None

        with open(coverage_file, "r") as f:
            coverage_data = json.load(f)

        coverage_value = coverage_data.get("value")

        if coverage_value is None:
            return None

        # Analyze commit patterns
        total_commits = len(commits)
        weeks_active = len(set(c.get("timestamp", "")[:10] for c in commits if c.get("timestamp")))

        # Estimate code maturity
        if coverage_value >= 80:
            quality_grade = "A"
            quality_status = "Excellent"
        elif coverage_value >= 70:
            quality_grade = "B"
            quality_status = "Good"
        elif coverage_value >= 60:
            quality_grade = "C"
            quality_status = "Fair"
        elif coverage_value >= 50:
            quality_grade = "D"
            quality_status = "Poor"
        else:
            quality_grade = "F"
            quality_status = "Critical"

        return {
            "metric_id": f"repo.code_quality_evolution.{repo_name}",
            "repo": repo_name,
            "repos": [repo_name],
            "inputs": [
                str((self.git_artifacts / repo_name / "commits.json").relative_to(self.root_dir)),
                str(coverage_file.relative_to(self.root_dir))
            ],
            "time_range": {"start": commits[0].get("timestamp", "")[:10] if commits else None,
                          "end": commits[-1].get("timestamp", "")[:10] if commits else None},
            "coverage_percentage": coverage_value,
            "quality_grade": quality_grade,
            "quality_status": quality_status,
            "total_commits": total_commits,
            "weeks_active": weeks_active,
            "commits_per_week": round(total_commits / weeks_active, 2) if weeks_active else 0,
            "maturity_score": round((coverage_value + (total_commits / 100 * 10)) / 2, 2),
            "method": "Combine coverage metrics with commit activity to assess code quality evolution",
            "calculated_at": datetime.utcnow().isoformat() + "Z"
        }

    def calculate_evolution_metrics(self):
        """Calculate all evolution metrics"""
        results = {}
        repos = self._repo_names()

        print("\n" + "="*70)
        print("EVOLUTION METRICS CALCULATION")
        print("="*70 + "\n")

        for repo_name in repos:
            print(f"Analyzing {repo_name}...")

            # Velocity trends
            velocity = self.calculate_velocity_trends(repo_name)
            if velocity:
                self._write_json(
                    self.calculations / "per_repo" / repo_name / "velocity_trend.json",
                    velocity
                )
                results[f"{repo_name}_velocity"] = velocity
                print(f"  ✓ Velocity trends: {velocity['weeks_active']} weeks active")

            # Contributor growth
            contributors = self.calculate_contributor_growth(repo_name)
            if contributors:
                self._write_json(
                    self.calculations / "per_repo" / repo_name / "contributor_growth.json",
                    contributors
                )
                results[f"{repo_name}_contributors"] = contributors
                print(f"  ✓ Contributor growth: {contributors['total_contributors']} contributors")

            # Refactorization activity
            refactor = self.analyze_refactorization_activity(repo_name)
            if refactor:
                self._write_json(
                    self.calculations / "per_repo" / repo_name / "refactorization_activity.json",
                    refactor
                )
                results[f"{repo_name}_refactor"] = refactor
                print(f"  ✓ Refactorization: {refactor['total_refactor_commits']} commits ({refactor['refactor_percentage']}%)")

            # AI usage indicators
            ai_usage = self.analyze_ai_usage(repo_name)
            if ai_usage:
                self._write_json(
                    self.calculations / "per_repo" / repo_name / "ai_usage_indicators.json",
                    ai_usage
                )
                results[f"{repo_name}_ai"] = ai_usage
                print(f"  ✓ AI indicators: {ai_usage['total_ai_attributed_commits']} commits with AI mentions ({ai_usage['ai_percentage']}%)")

            # Code quality evolution
            quality = self.analyze_code_quality_evolution(repo_name)
            if quality:
                self._write_json(
                    self.calculations / "per_repo" / repo_name / "code_quality_evolution.json",
                    quality
                )
                results[f"{repo_name}_quality"] = quality
                print(f"  ✓ Code quality: Grade {quality['quality_grade']} ({quality['quality_status']})")

        print("\n" + "="*70)
        print(f"Evolution metrics calculated for {len(repos)} repositories")
        print("="*70 + "\n")

        return results

if __name__ == "__main__":
    calc = EvolutionMetricsCalculator()
    results = calc.calculate_evolution_metrics()
