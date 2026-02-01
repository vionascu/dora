#!/usr/bin/env python3
"""
CALCULATION LAYER - Metrics Computation
Processes raw git and CI artifacts into normalized, auditable metrics
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

class Calculator:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.git_artifacts = self.root_dir / "git_artifacts"
        self.ci_artifacts = self.root_dir / "ci_artifacts"
        self.calculations = self.root_dir / "calculations"
        self.repos_file = self.root_dir / "ReposInput.md"

        # Create directory structure
        self.calculations.mkdir(exist_ok=True)
        (self.calculations / "per_repo").mkdir(exist_ok=True)
        (self.calculations / "global").mkdir(exist_ok=True)

    def parse_repos(self):
        """Parse ReposInput.md"""
        repos = {}
        current_repo = None

        if not self.repos_file.exists():
            return repos

        with open(self.repos_file, 'r') as f:
            for line in f:
                line = line.rstrip()
                if line.startswith("## "):
                    current_repo = line.replace("## ", "").strip()
                    repos[current_repo] = {}
                elif ": " in line and current_repo:
                    key, value = line.split(": ", 1)
                    repos[current_repo][key.strip()] = value.strip()

        return repos

    def calculate_commits(self, repo_name):
        """Calculate commit metrics for a repository"""
        commits_file = self.git_artifacts / repo_name / "commits.json"

        if not commits_file.exists():
            return None

        with open(commits_file, 'r') as f:
            commits_data = json.load(f)

        commits = commits_data.get("commits", [])
        if not commits:
            return None

        # Calculate metrics
        dates = [c["timestamp"][:10] for c in commits]
        unique_dates = len(set(dates))
        time_range = {
            "start": min(dates) if dates else None,
            "end": max(dates) if dates else None
        }

        result = {
            "metric_id": "repo.commits",
            "repo": repo_name,
            "time_range": time_range,
            "inputs": [str(commits_file.relative_to(self.root_dir))],
            "total_commits": len(commits),
            "unique_dates": unique_dates,
            "avg_commits_per_day": round(len(commits) / max(1, unique_dates), 2) if unique_dates > 0 else 0,
            "method": "Count total commits, divide by unique dates",
            "calculated_at": datetime.now().isoformat()
        }

        return result

    def calculate_contributors(self, repo_name):
        """Calculate contributor metrics"""
        authors_file = self.git_artifacts / repo_name / "authors.json"

        if not authors_file.exists():
            return None

        with open(authors_file, 'r') as f:
            authors_data = json.load(f)

        return {
            "metric_id": "repo.contributors",
            "repo": repo_name,
            "inputs": [str(authors_file.relative_to(self.root_dir))],
            "unique_contributors": authors_data.get("unique_authors", 0),
            "method": "Count unique author emails",
            "calculated_at": datetime.now().isoformat()
        }

    def calculate_coverage_percentage(self, repo_name, config):
        """Attempt to extract coverage percentage if available"""
        coverage_tool = config.get("coverage", "")
        ci_dir = self.ci_artifacts / repo_name

        # This is a placeholder - in production would parse coverage files
        return {
            "metric_id": "repo.coverage",
            "repo": repo_name,
            "value": None,
            "reason": f"Coverage data not available (tool: {coverage_tool}, requires local test run)",
            "method": f"Parse {coverage_tool} output",
            "calculated_at": datetime.now().isoformat()
        }

    def calculate_dora_frequency(self, repo_name):
        """Calculate deployment frequency (proxied by commit frequency)"""
        # In real DORA, this would use deployment tags or release branches
        # For now, we proxy it using commit frequency
        commits_file = self.git_artifacts / repo_name / "commits.json"

        if not commits_file.exists():
            return None

        with open(commits_file, 'r') as f:
            commits_data = json.load(f)

        commits = commits_data.get("commits", [])
        if not commits:
            return None

        # Get time range
        dates = [c["timestamp"][:10] for c in commits]
        first_date = datetime.fromisoformat(min(dates))
        last_date = datetime.fromisoformat(max(dates))
        days = (last_date - first_date).days + 1

        # Calculate as deploys per day
        deploys_per_day = len(commits) / max(1, days)

        return {
            "metric_id": "repo.dora_frequency",
            "repo": repo_name,
            "inputs": [str(commits_file.relative_to(self.root_dir))],
            "value": round(deploys_per_day, 3),
            "unit": "commits/day",
            "method": "Total commits / days in history (proxy: requires git tags for accuracy)",
            "note": "Proxy metric using commit frequency. For true DORA, analyze deployment tags",
            "calculated_at": datetime.now().isoformat()
        }

    def calculate_lead_time(self, repo_name):
        """Calculate lead time for changes (proxy: avg commit timestamp diff)"""
        commits_file = self.git_artifacts / repo_name / "commits.json"

        if not commits_file.exists():
            return None

        with open(commits_file, 'r') as f:
            commits_data = json.load(f)

        commits = commits_data.get("commits", [])
        if len(commits) < 2:
            return {
                "metric_id": "repo.dora_lead_time",
                "repo": repo_name,
                "value": None,
                "reason": "Less than 2 commits - cannot calculate lead time",
                "method": "Average time between commits",
                "calculated_at": datetime.now().isoformat()
            }

        # Sort by timestamp
        sorted_commits = sorted(commits, key=lambda x: x["timestamp"])

        # Calculate time diffs
        diffs = []
        for i in range(1, len(sorted_commits)):
            # Parse timestamps, handling timezone info
            ts1 = sorted_commits[i-1]["timestamp"]
            ts2 = sorted_commits[i]["timestamp"]

            # Remove timezone info if present (e.g., "2026-01-31 20:41:32 +0200" -> "2026-01-31 20:41:32")
            ts1 = ts1.rsplit(' ', 1)[0] if ' ' in ts1 else ts1
            ts2 = ts2.rsplit(' ', 1)[0] if ' ' in ts2 else ts2

            try:
                t1 = datetime.fromisoformat(ts1.replace(' ', 'T'))
                t2 = datetime.fromisoformat(ts2.replace(' ', 'T'))
            except:
                # Fallback to simple split if ISO format fails
                t1 = datetime.strptime(ts1, "%Y-%m-%d %H:%M:%S")
                t2 = datetime.strptime(ts2, "%Y-%m-%d %H:%M:%S")

            diff_hours = (t2 - t1).total_seconds() / 3600
            if diff_hours >= 0:  # Sanity check
                diffs.append(diff_hours)

        if not diffs:
            avg_hours = None
        else:
            avg_hours = round(sum(diffs) / len(diffs), 2)

        return {
            "metric_id": "repo.dora_lead_time",
            "repo": repo_name,
            "inputs": [str(commits_file.relative_to(self.root_dir))],
            "value": avg_hours,
            "unit": "hours",
            "method": "Average time between consecutive commits",
            "note": "Proxy metric. True DORA measures code commit to deployment",
            "calculated_at": datetime.now().isoformat()
        }

    def save_repo_metrics(self, repo_name, config):
        """Calculate and save all per-repo metrics"""
        print(f"  Calculating {repo_name}...")

        repo_calc_dir = self.calculations / "per_repo" / repo_name
        repo_calc_dir.mkdir(exist_ok=True)

        # Calculate all metrics
        metrics = [
            ("commits.json", self.calculate_commits(repo_name)),
            ("contributors.json", self.calculate_contributors(repo_name)),
            ("coverage.json", self.calculate_coverage_percentage(repo_name, config)),
            ("dora_frequency.json", self.calculate_dora_frequency(repo_name)),
            ("lead_time.json", self.calculate_lead_time(repo_name))
        ]

        saved_count = 0
        for filename, metric in metrics:
            if metric is not None:
                with open(repo_calc_dir / filename, 'w') as f:
                    json.dump(metric, f, indent=2)
                saved_count += 1

        print(f"    ✓ Saved {saved_count} metrics")

    def calculate_global_metrics(self, repos):
        """Calculate organization-wide metrics"""
        print("\n  Calculating global metrics...")

        global_dir = self.calculations / "global"

        # Aggregate commits
        total_commits = 0
        repos_analyzed = []
        all_contributors = set()

        for repo_name in repos:
            repo_calc_dir = self.calculations / "per_repo" / repo_name
            commits_file = repo_calc_dir / "commits.json"

            if commits_file.exists():
                with open(commits_file, 'r') as f:
                    data = json.load(f)
                    total_commits += data.get("total_commits", 0)
                    repos_analyzed.append(repo_name)

            # Collect contributors
            contributors_file = repo_calc_dir / "contributors.json"
            if contributors_file.exists():
                with open(contributors_file, 'r') as f:
                    data = json.load(f)
                    all_contributors.add(repo_name)

        # Save global commits
        with open(global_dir / "commits.json", 'w') as f:
            json.dump({
                "metric_id": "global.commits",
                "repos": repos_analyzed,
                "inputs": [str((self.calculations / "per_repo" / r / "commits.json").relative_to(self.root_dir)) for r in repos_analyzed],
                "total_commits": total_commits,
                "repos_count": len(repos_analyzed),
                "method": "Sum commits across all analyzed repos",
                "calculated_at": datetime.now().isoformat()
            }, f, indent=2)

        # Save global summary
        with open(global_dir / "summary.json", 'w') as f:
            json.dump({
                "metric_id": "global.summary",
                "repos_analyzed": repos_analyzed,
                "repos_total_count": len(repos),
                "repos_with_issues": [r for r in repos if r not in repos_analyzed],
                "total_commits": total_commits,
                "unique_repos_with_contributors": len(all_contributors),
                "calculated_at": datetime.now().isoformat()
            }, f, indent=2)

        print(f"    ✓ Saved global metrics for {len(repos_analyzed)} repos")

    def run(self):
        """Execute calculation pipeline"""
        print("\n" + "="*70)
        print("DORA CALCULATION LAYER - Metrics Computation")
        print("="*70 + "\n")

        repos = self.parse_repos()
        if not repos:
            print("No repositories found in ReposInput.md")
            return False

        print(f"Computing metrics for {len(repos)} repositories\n")

        for repo_name, config in repos.items():
            self.save_repo_metrics(repo_name, config)

        self.calculate_global_metrics(repos)

        print(f"\n{'='*70}")
        print("Calculation complete")
        print("="*70 + "\n")

        return True

if __name__ == "__main__":
    calculator = Calculator()
    success = calculator.run()
    exit(0 if success else 1)
