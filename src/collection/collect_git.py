#!/usr/bin/env python3
"""
COLLECTION LAYER - Git Data Extraction
Clones repositories and extracts raw git metrics
"""

import subprocess
from datetime import datetime
from pathlib import Path
from src.config.config_parser import RepoConfigParser
from src.collection.git_log_processor import GitLogProcessor


class GitCollector:
    def __init__(self, root_dir=".", config_file=None):
        self.root_dir = Path(root_dir)
        self.git_artifacts = self.root_dir / "git_artifacts"
        self.git_artifacts.mkdir(exist_ok=True)

        # Initialize config parser
        self.config_parser = RepoConfigParser(config_file=config_file)
        is_valid, errors = self.config_parser.load_config()

        if not is_valid:
            raise ValueError(f"Configuration validation errors: {errors}")

    def parse_repos(self):
        """Parse repository configuration"""
        return self.config_parser.get_all_repos()

    def collect_repo(self, repo_name, repo_config):
        """Clone repository and extract git data"""
        print(f"  Collecting {repo_name}...")

        repo_url = repo_config.get("repo")
        branch = repo_config.get("branch", "main")

        if not repo_url:
            print(f"    ✗ No repo URL defined")
            return False

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

        # Extract commits using streaming processor
        try:
            processor = GitLogProcessor(clone_path)

            # Save stats (efficient calculation)
            processor.save_stats(repo_dir / "stats.json")

            # Save commits as JSON (for backward compatibility, but with warning for large repos)
            processor.save_commits_json(repo_dir / "commits.json")

            # Read stats to get summary info
            import json
            with open(repo_dir / "stats.json", 'r') as f:
                stats = json.load(f)

            print(f"    ✓ Extracted {stats['total_commits']} commits, {stats['unique_authors']} authors")
            return True

        except subprocess.CalledProcessError as e:
            print(f"    ✗ Git extraction failed: {str(e)}")
            return False
        except Exception as e:
            print(f"    ✗ Error processing commits: {str(e)}")
            return False

    def run(self):
        """Execute collection pipeline"""
        print("\n" + "="*70)
        print("DORA COLLECTION LAYER - Git Data Extraction")
        print("="*70 + "\n")

        repos = self.parse_repos()
        print(f"Found {len(repos)} repositories in configuration\n")

        success_count = 0
        for repo_name, config in repos.items():
            if self.collect_repo(repo_name, config):
                success_count += 1

        print(f"\n{'='*70}")
        print(f"Collection complete: {success_count}/{len(repos)} successful")
        print("="*70 + "\n")

        return success_count == len(repos)

if __name__ == "__main__":
    collector = GitCollector()
    success = collector.run()
    exit(0 if success else 1)
