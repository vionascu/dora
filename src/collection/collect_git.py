#!/usr/bin/env python3
"""
COLLECTION LAYER - Git Data Extraction
Clones repositories and extracts raw git metrics
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

class GitCollector:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.repos_file = self.root_dir / "ReposInput.md"
        self.git_artifacts = self.root_dir / "git_artifacts"
        self.git_artifacts.mkdir(exist_ok=True)

    def parse_repos(self):
        """Parse ReposInput.md"""
        repos = {}
        current_repo = None

        if not self.repos_file.exists():
            raise FileNotFoundError(f"ReposInput.md not found at {self.repos_file}")

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

    def collect_repo(self, repo_name, repo_url, branch="main"):
        """Clone repository and extract git data"""
        print(f"  Collecting {repo_name}...")

        repo_dir = self.git_artifacts / repo_name
        repo_dir.mkdir(exist_ok=True)
        clone_path = repo_dir / "clone"

        # Clone repository
        if not clone_path.exists():
            try:
                subprocess.run(
                    ["git", "clone", "-b", branch, repo_url, str(clone_path)],
                    capture_output=True,
                    timeout=180,
                    check=True
                )
                print(f"    ✓ Cloned successfully")
            except subprocess.TimeoutExpired:
                print(f"    ✗ Clone timeout")
                return False
            except subprocess.CalledProcessError as e:
                print(f"    ✗ Clone failed: {e.stderr.decode()}")
                return False

        # Extract commits
        try:
            result = subprocess.run(
                ["git", "log", "--all", "--format=%H%n%ai%n%an%n%ae%n%s%n--END--"],
                cwd=clone_path,
                capture_output=True,
                text=True,
                check=True
            )

            commits = []
            lines = result.stdout.strip().split('\n')
            i = 0
            while i < len(lines):
                if lines[i] == '--END--':
                    i += 1
                    continue

                if i + 4 < len(lines):
                    commits.append({
                        "hash": lines[i],
                        "timestamp": lines[i+1],
                        "author_name": lines[i+2],
                        "author_email": lines[i+3],
                        "subject": lines[i+4]
                    })
                    i += 6  # Skip --END-- line
                else:
                    break

            with open(repo_dir / "commits.json", 'w') as f:
                json.dump({
                    "metric_id": "git.commits.raw",
                    "repo": repo_name,
                    "branch": branch,
                    "total_commits": len(commits),
                    "commits": commits,
                    "collected_at": datetime.now().isoformat()
                }, f, indent=2)

            # Extract authors
            authors = list(set([c["author_email"] for c in commits]))
            with open(repo_dir / "authors.json", 'w') as f:
                json.dump({
                    "metric_id": "git.authors.raw",
                    "repo": repo_name,
                    "unique_authors": len(authors),
                    "authors": authors,
                    "collected_at": datetime.now().isoformat()
                }, f, indent=2)

            # Extract first and last commit dates
            if commits:
                dates = [c["timestamp"][:10] for c in commits]
                first_date = min(dates)
                last_date = max(dates)

                with open(repo_dir / "timeline.json", 'w') as f:
                    json.dump({
                        "metric_id": "git.timeline.raw",
                        "repo": repo_name,
                        "first_commit": first_date,
                        "last_commit": last_date,
                        "collected_at": datetime.now().isoformat()
                    }, f, indent=2)

            print(f"    ✓ Extracted {len(commits)} commits, {len(authors)} authors")
            return True

        except subprocess.CalledProcessError as e:
            print(f"    ✗ Git extraction failed: {e.stderr.decode()}")
            return False

    def run(self):
        """Execute collection pipeline"""
        print("\n" + "="*70)
        print("DORA COLLECTION LAYER - Git Data Extraction")
        print("="*70 + "\n")

        repos = self.parse_repos()
        print(f"Found {len(repos)} repositories in ReposInput.md\n")

        success_count = 0
        for repo_name, config in repos.items():
            repo_url = config.get("repo")
            branch = config.get("branch", "main")

            if not repo_url:
                print(f"  ✗ {repo_name}: No repo URL defined")
                continue

            if self.collect_repo(repo_name, repo_url, branch):
                success_count += 1

        print(f"\n{'='*70}")
        print(f"Collection complete: {success_count}/{len(repos)} successful")
        print("="*70 + "\n")

        return success_count == len(repos)

if __name__ == "__main__":
    collector = GitCollector()
    success = collector.run()
    exit(0 if success else 1)
