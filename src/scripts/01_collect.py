#!/usr/bin/env python3
"""
COLLECTION LAYER
Collects raw git and CI artifacts from repositories defined in ReposInput.md
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
import yaml

class Collector:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.repos_input = self.root_dir / "ReposInput.md"
        self.git_artifacts = self.root_dir / "git_artifacts"
        self.ci_artifacts = self.root_dir / "ci_artifacts"
        self.git_artifacts.mkdir(exist_ok=True)
        self.ci_artifacts.mkdir(exist_ok=True)

    def parse_repos_input(self):
        """Parse ReposInput.md and extract repository definitions"""
        repos = {}
        current_repo = None

        with open(self.repos_input, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("##"):
                    current_repo = line.replace("##", "").strip()
                    repos[current_repo] = {}
                elif ":" in line and current_repo:
                    key, value = line.split(":", 1)
                    repos[current_repo][key.strip()] = value.strip()

        return repos

    def collect_git_data(self, repo_name, repo_url, branch="main"):
        """Clone repo and collect git metrics"""
        print(f"  → Collecting git data from {repo_name}...")

        repo_dir = self.git_artifacts / repo_name
        repo_dir.mkdir(exist_ok=True)

        clone_path = repo_dir / "clone"

        # Clone if not exists
        if not clone_path.exists():
            try:
                subprocess.run(
                    ["git", "clone", "--depth=100", "-b", branch, repo_url, str(clone_path)],
                    capture_output=True,
                    timeout=120,
                    check=True
                )
            except subprocess.TimeoutExpired:
                print(f"    ✗ Clone timeout for {repo_name} (network issue)")
                return
            except subprocess.CalledProcessError as e:
                print(f"    ✗ Failed to clone {repo_name}: {e}")
                return

        # Extract git metrics
        try:
            # Get all commits
            result = subprocess.run(
                ["git", "log", "--all", "--format=%H|%ai|%an|%ae|%s"],
                cwd=clone_path,
                capture_output=True,
                text=True,
                check=True
            )

            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    commits.append({
                        "hash": parts[0],
                        "timestamp": parts[1],
                        "author_name": parts[2],
                        "author_email": parts[3],
                        "message": parts[4] if len(parts) > 4 else ""
                    })

            # Save commits
            with open(repo_dir / "commits.json", 'w') as f:
                json.dump({
                    "metric_id": "git.commits",
                    "repo": repo_name,
                    "total_commits": len(commits),
                    "commits": commits,
                    "collected_at": datetime.now().isoformat()
                }, f, indent=2)

            print(f"    ✓ Collected {len(commits)} commits")

        except subprocess.CalledProcessError as e:
            print(f"    ✗ Error collecting git data: {e}")

    def collect_ci_data(self, repo_name, repo_url, branch="main"):
        """Attempt to collect CI artifacts"""
        print(f"  → Collecting CI data from {repo_name}...")

        ci_dir = self.ci_artifacts / repo_name
        ci_dir.mkdir(exist_ok=True)

        # Create placeholder for CI data
        with open(ci_dir / "ci_info.json", 'w') as f:
            json.dump({
                "metric_id": "ci.info",
                "repo": repo_name,
                "status": "requires_local_setup",
                "message": "CI data generation requires repository-specific test setup",
                "collected_at": datetime.now().isoformat()
            }, f, indent=2)

        print(f"    ℹ CI data will be populated after local test runs")

    def run(self):
        """Execute full collection pipeline"""
        print("\n" + "="*60)
        print("DORA COLLECTION LAYER - Starting collection pipeline")
        print("="*60 + "\n")

        repos = self.parse_repos_input()
        print(f"Found {len(repos)} repositories in ReposInput.md\n")

        for repo_name, config in repos.items():
            print(f"Processing {repo_name}...")
            repo_url = config.get("repo")
            branch = config.get("branch", "main")

            if not repo_url:
                print(f"  ✗ No repo URL found for {repo_name}")
                continue

            self.collect_git_data(repo_name, repo_url, branch)
            self.collect_ci_data(repo_name, repo_url, branch)
            print()

        print("="*60)
        print("Collection pipeline complete")
        print("="*60 + "\n")

if __name__ == "__main__":
    collector = Collector()
    collector.run()
