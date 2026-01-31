#!/usr/bin/env python3
"""
CALCULATION LAYER
Processes raw artifacts from git_artifacts/ and ci_artifacts/
Produces normalized metrics in calculations/
"""

import os
import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

class Calculator:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.git_artifacts = self.root_dir / "git_artifacts"
        self.ci_artifacts = self.root_dir / "ci_artifacts"
        self.calculations = self.root_dir / "calculations"
        self.calculations.mkdir(exist_ok=True)
        (self.calculations / "per_repo").mkdir(exist_ok=True)
        (self.calculations / "global").mkdir(exist_ok=True)

    def parse_repos_input(self):
        """Parse repository definitions"""
        repos = {}
        repos_file = self.root_dir / "ReposInput.md"

        if not repos_file.exists():
            return repos

        current_repo = None
        with open(repos_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("##"):
                    current_repo = line.replace("##", "").strip()
                    repos[current_repo] = {}
                elif ":" in line and current_repo:
                    key, value = line.split(":", 1)
                    repos[current_repo][key.strip()] = value.strip()

        return repos

    def calculate_repo_metrics(self, repo_name):
        """Calculate per-repo metrics"""
        print(f"  → Calculating metrics for {repo_name}...")

        repo_calc_dir = self.calculations / "per_repo" / repo_name
        repo_calc_dir.mkdir(exist_ok=True)

        git_dir = self.git_artifacts / repo_name
        commits_file = git_dir / "commits.json"

        if not commits_file.exists():
            print(f"    ✗ No commits data found")
            return None

        try:
            with open(commits_file, 'r') as f:
                commits_data = json.load(f)
            commits = commits_data.get("commits", [])

            # Calculate commit frequency
            if commits:
                dates = [c["timestamp"][:10] for c in commits]
                unique_dates = len(set(dates))
                avg_commits_per_day = len(commits) / max(1, unique_dates)

                with open(repo_calc_dir / "commits.json", 'w') as f:
                    json.dump({
                        "metric_id": "commits.frequency",
                        "repo": repo_name,
                        "inputs": [str(commits_file)],
                        "total_commits": len(commits),
                        "unique_dates": unique_dates,
                        "avg_commits_per_day": round(avg_commits_per_day, 2),
                        "calculated_at": datetime.now().isoformat()
                    }, f, indent=2)

                # Author diversity
                authors = set([c["author_email"] for c in commits])
                with open(repo_calc_dir / "team_diversity.json", 'w') as f:
                    json.dump({
                        "metric_id": "team.diversity",
                        "repo": repo_name,
                        "total_contributors": len(authors),
                        "inputs": [str(commits_file)],
                        "calculated_at": datetime.now().isoformat()
                    }, f, indent=2)

                print(f"    ✓ Calculated {len(commits)} commits from {len(authors)} contributors")
            else:
                print(f"    ✗ No commits found")

        except Exception as e:
            print(f"    ✗ Error: {e}")

    def calculate_global_metrics(self, repos):
        """Calculate organization-wide metrics"""
        print("  → Calculating global metrics...")

        total_commits = 0
        total_contributors = 0
        repos_analyzed = []
        repos_with_issues = []

        for repo_name in repos:
            repo_calc_dir = self.calculations / "per_repo" / repo_name
            commits_file = repo_calc_dir / "commits.json"

            if commits_file.exists():
                try:
                    with open(commits_file, 'r') as f:
                        data = json.load(f)
                        total_commits += data.get("total_commits", 0)
                        repos_analyzed.append(repo_name)
                except:
                    repos_with_issues.append(repo_name)

            diversity_file = repo_calc_dir / "team_diversity.json"
            if diversity_file.exists():
                try:
                    with open(diversity_file, 'r') as f:
                        data = json.load(f)
                        total_contributors += data.get("total_contributors", 0)
                except:
                    pass

        # Global summary
        with open(self.calculations / "global" / "summary.json", 'w') as f:
            json.dump({
                "metric_id": "global.summary",
                "repos_analyzed": repos_analyzed,
                "repos_with_issues": repos_with_issues,
                "total_commits_across_repos": total_commits,
                "unique_contributors": total_contributors,
                "calculation_time": datetime.now().isoformat()
            }, f, indent=2)

        print(f"    ✓ Global metrics calculated for {len(repos_analyzed)} repos")

    def run(self):
        """Execute full calculation pipeline"""
        print("\n" + "="*60)
        print("DORA CALCULATION LAYER - Starting calculation pipeline")
        print("="*60 + "\n")

        repos = self.parse_repos_input()

        if not repos:
            print("⚠ No repositories found in ReposInput.md")
            return

        print(f"Calculating metrics for {len(repos)} repositories...\n")

        for repo_name in repos:
            self.calculate_repo_metrics(repo_name)

        print()
        self.calculate_global_metrics(repos)

        print("\n" + "="*60)
        print("Calculation pipeline complete")
        print("="*60 + "\n")

if __name__ == "__main__":
    calculator = Calculator()
    calculator.run()
