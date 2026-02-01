#!/usr/bin/env python3
"""
COLLECTION LAYER - CI Artifacts Extraction
Attempts to collect CI/test/coverage data from repositories
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

class CICollector:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.repos_file = self.root_dir / "ReposInput.md"
        self.git_artifacts = self.root_dir / "git_artifacts"
        self.ci_artifacts = self.root_dir / "ci_artifacts"
        self.ci_artifacts.mkdir(exist_ok=True)

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

    def collect_repo_ci(self, repo_name, config):
        """Attempt to collect CI artifacts from a repository"""
        print(f"  Processing CI for {repo_name}...")

        repo_dir = self.ci_artifacts / repo_name
        repo_dir.mkdir(exist_ok=True)

        git_clone = self.git_artifacts / repo_name / "clone"
        if not git_clone.exists():
            print(f"    ℹ Git data not collected yet")
            return

        language = config.get("language", "unknown")
        coverage_type = config.get("coverage", "unknown")

        # Create CI info file
        with open(repo_dir / "ci_info.json", 'w') as f:
            json.dump({
                "metric_id": "ci.info.raw",
                "repo": repo_name,
                "language": language,
                "coverage_tool": coverage_type,
                "status": "initialized",
                "note": "Run local tests to populate coverage data",
                "collected_at": datetime.now().isoformat()
            }, f, indent=2)

        # Try to run tests based on language
        if language == "java":
            self._collect_java_tests(repo_name, git_clone, repo_dir)
        elif language == "python":
            self._collect_python_tests(repo_name, git_clone, repo_dir)
        elif language == "mixed":
            self._collect_javascript_tests(repo_name, git_clone, repo_dir)

        print(f"    ✓ CI initialization complete")

    def _collect_java_tests(self, repo_name, git_clone, repo_dir):
        """Collect Java test and coverage data"""
        print(f"    → Attempting Java test collection...")

        pom_file = git_clone / "pom.xml"
        if not pom_file.exists():
            print(f"      ℹ No pom.xml found")
            return

        try:
            # Run Maven tests with coverage
            result = subprocess.run(
                ["mvn", "clean", "test", "jacoco:report"],
                cwd=git_clone,
                capture_output=True,
                timeout=300,
                check=False
            )

            # Look for jacoco results
            jacoco_path = git_clone / "target" / "site" / "jacoco" / "jacoco.xml"
            if jacoco_path.exists():
                with open(jacoco_path, 'rb') as src:
                    with open(repo_dir / "jacoco.xml", 'wb') as dst:
                        dst.write(src.read())
                print(f"      ✓ Collected jacoco.xml")
        except subprocess.TimeoutExpired:
            print(f"      ℹ Maven test timeout (network/build time)")
        except Exception as e:
            print(f"      ℹ Could not run Maven: {str(e)}")

    def _collect_python_tests(self, repo_name, git_clone, repo_dir):
        """Collect Python test and coverage data"""
        print(f"    → Attempting Python test collection...")

        requirements_file = git_clone / "requirements.txt"
        setup_file = git_clone / "setup.py"

        if not (requirements_file.exists() or setup_file.exists()):
            print(f"      ℹ No Python project files found")
            return

        try:
            # Run pytest with coverage
            result = subprocess.run(
                ["python3", "-m", "pytest", "--cov", "--cov-report=xml", "--tb=short"],
                cwd=git_clone,
                capture_output=True,
                timeout=300,
                check=False
            )

            # Look for coverage results
            coverage_path = git_clone / "coverage.xml"
            if coverage_path.exists():
                with open(coverage_path, 'rb') as src:
                    with open(repo_dir / "coverage.xml", 'wb') as dst:
                        dst.write(src.read())
                print(f"      ✓ Collected coverage.xml")
        except subprocess.TimeoutExpired:
            print(f"      ℹ Pytest timeout (network/build time)")
        except Exception as e:
            print(f"      ℹ Could not run pytest: {str(e)}")

    def _collect_javascript_tests(self, repo_name, git_clone, repo_dir):
        """Collect JavaScript test and coverage data"""
        print(f"    → Attempting JavaScript test collection...")

        package_json = git_clone / "package.json"
        if not package_json.exists():
            print(f"      ℹ No package.json found")
            return

        try:
            # Run npm tests with coverage
            result = subprocess.run(
                ["npm", "test", "--", "--coverage", "--coverage-reporter=lcov"],
                cwd=git_clone,
                capture_output=True,
                timeout=300,
                check=False
            )

            # Look for lcov results
            lcov_path = git_clone / "coverage" / "lcov.info"
            if lcov_path.exists():
                with open(lcov_path, 'r') as src:
                    with open(repo_dir / "lcov.info", 'w') as dst:
                        dst.write(src.read())
                print(f"      ✓ Collected lcov.info")
        except subprocess.TimeoutExpired:
            print(f"      ℹ npm test timeout (network/build time)")
        except Exception as e:
            print(f"      ℹ Could not run npm test: {str(e)}")

    def run(self):
        """Execute CI collection pipeline"""
        print("\n" + "="*70)
        print("DORA COLLECTION LAYER - CI Artifacts Extraction")
        print("="*70 + "\n")

        repos = self.parse_repos()
        print(f"Processing CI data for {len(repos)} repositories\n")

        for repo_name, config in repos.items():
            self.collect_repo_ci(repo_name, config)

        print(f"\n{'='*70}")
        print("CI artifacts collection complete")
        print("="*70 + "\n")

        return True

if __name__ == "__main__":
    collector = CICollector()
    success = collector.run()
    exit(0 if success else 1)
