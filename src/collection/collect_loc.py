#!/usr/bin/env python3
"""
COLLECTION LAYER - Lines of Code Extraction
Counts lines of code in repositories using various methods
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple


class LOCCollector:
    """Collects lines of code metrics from repositories"""

    # File extensions to count as code
    CODE_EXTENSIONS = {
        # Web
        '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.scss', '.sass',
        # Backend
        '.py', '.java', '.cs', '.cpp', '.c', '.h', '.go', '.rb', '.php',
        '.rs', '.kt', '.swift', '.m', '.scala', '.groovy', '.sh', '.bash',
        # Data/Config
        '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.properties',
        # Frontend frameworks
        '.vue', '.svelte',
        # Markup
        '.md', '.rst', '.tex',
        # SQL
        '.sql',
        # Other common formats
        '.pl', '.r', '.lua', '.elixir', '.ex', '.exs', '.clj', '.cljs'
    }

    # Exclude patterns (directories/files to skip)
    EXCLUDE_PATTERNS = {
        '.git', '.svn', '.hg', '.bzr',
        'node_modules', 'venv', 'env', '.env',
        'dist', 'build', 'target',
        '.pytest_cache', '__pycache__', '.mypy_cache',
        '.idea', '.vscode', '.DS_Store',
        'coverage', '.coverage',
        'vendor', 'lock', '.lock'
    }

    def __init__(self, root_dir=".", git_artifacts_dir="git_artifacts"):
        self.root_dir = Path(root_dir)
        self.git_artifacts = self.root_dir / git_artifacts_dir
        self.git_artifacts.mkdir(exist_ok=True)

    def _should_count_file(self, file_path: Path) -> bool:
        """Check if file should be counted based on extension"""
        return file_path.suffix.lower() in self.CODE_EXTENSIONS

    def _should_skip_path(self, path_parts) -> bool:
        """Check if path should be skipped based on exclude patterns"""
        for part in path_parts:
            if part in self.EXCLUDE_PATTERNS:
                return True
        return False

    def count_lines_simple(self, directory: Path) -> Tuple[int, int, int]:
        """
        Count lines of code using simple file parsing

        Returns:
            Tuple of (total_lines, file_count, blank_lines)
        """
        total_lines = 0
        file_count = 0
        blank_lines = 0

        try:
            for file_path in directory.rglob('*'):
                # Skip directories and non-code files
                if not file_path.is_file():
                    continue

                # Check exclusions
                relative_path = file_path.relative_to(directory)
                path_parts = relative_path.parts
                if self._should_skip_path(path_parts):
                    continue

                # Check if it's a code file
                if not self._should_count_file(file_path):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            total_lines += 1
                            if line.strip() == '':
                                blank_lines += 1
                    file_count += 1
                except (IOError, OSError):
                    # Skip files we can't read
                    continue

        except Exception as e:
            print(f"    ⚠️  Error counting lines: {str(e)}")

        return total_lines, file_count, blank_lines

    def count_lines_with_cloc(self, directory: Path) -> Dict:
        """
        Count lines of code using cloc tool (if available)
        Falls back to simple counting if cloc not installed

        Returns:
            Dictionary with LOC statistics
        """
        try:
            # Try to use cloc if installed
            result = subprocess.run(
                ['cloc', str(directory), '--json', '--quiet'],
                capture_output=True,
                timeout=60,
                text=True
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass

        # Fallback to simple counting
        total_lines, file_count, blank_lines = self.count_lines_simple(directory)

        return {
            "method": "simple_scan",
            "total": total_lines,
            "files": file_count,
            "blank_lines": blank_lines,
            "code_lines": total_lines - blank_lines
        }

    def collect_repo_loc(self, repo_name: str, clone_path: Path) -> Dict:
        """
        Collect LOC metrics for a repository

        Args:
            repo_name: Name of the repository
            clone_path: Path to the cloned repository

        Returns:
            Dictionary with LOC metrics
        """
        if not clone_path.exists():
            return {
                "metric_id": "git.loc.raw",
                "repo": repo_name,
                "status": "error",
                "reason": "Clone directory not found",
                "collected_at": datetime.now().isoformat()
            }

        try:
            cloc_data = self.count_lines_with_cloc(clone_path)

            # Extract relevant metrics
            if "Total" in cloc_data:
                # cloc JSON format
                total_lines = cloc_data["Total"].get("nFiles", 0)
                code_lines = cloc_data["Total"].get("code", 0)
                comment_lines = cloc_data["Total"].get("comment", 0)
                blank_lines = cloc_data["Total"].get("blank", 0)
            else:
                # Fallback simple format
                total_lines = cloc_data.get("total", 0)
                code_lines = cloc_data.get("code_lines", 0)
                comment_lines = 0
                blank_lines = cloc_data.get("blank_lines", 0)

            return {
                "metric_id": "git.loc.raw",
                "repo": repo_name,
                "status": "success",
                "total_lines_of_code": code_lines,
                "total_lines_including_blank": total_lines,
                "blank_lines": blank_lines,
                "comment_lines": comment_lines,
                "code_only_lines": code_lines - comment_lines if comment_lines > 0 else code_lines,
                "method": cloc_data.get("method", "cloc_tool"),
                "collected_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "metric_id": "git.loc.raw",
                "repo": repo_name,
                "status": "error",
                "reason": f"LOC collection failed: {str(e)}",
                "collected_at": datetime.now().isoformat()
            }

    def run(self):
        """Execute LOC collection for all repositories"""
        print("\n" + "="*70)
        print("DORA COLLECTION LAYER - Lines of Code Extraction")
        print("="*70 + "\n")

        if not self.git_artifacts.exists():
            print("  No git_artifacts directory found. Run collect_git.py first.\n")
            return True

        success_count = 0
        total_count = 0

        for repo_dir in sorted(self.git_artifacts.iterdir()):
            if not repo_dir.is_dir() or repo_dir.name.startswith("."):
                continue

            repo_name = repo_dir.name
            clone_path = repo_dir / "clone"

            if not clone_path.exists():
                print(f"  ⚠️  {repo_name}: Clone not found (skipping LOC collection)")
                continue

            total_count += 1
            print(f"  Collecting LOC for {repo_name}...")

            loc_data = self.collect_repo_loc(repo_name, clone_path)

            # Save LOC data
            output_path = repo_dir / "loc.json"
            with open(output_path, 'w') as f:
                json.dump(loc_data, f, indent=2)

            if loc_data.get("status") == "success":
                loc_count = loc_data.get("total_lines_of_code", 0)
                print(f"    ✓ {loc_count:,} lines of code")
                success_count += 1
            else:
                reason = loc_data.get("reason", "Unknown error")
                print(f"    ✗ {reason}")

        print(f"\n{'='*70}")
        print(f"LOC collection complete: {success_count}/{total_count} successful")
        print("="*70 + "\n")

        return success_count == total_count


if __name__ == "__main__":
    collector = LOCCollector()
    success = collector.run()
    exit(0 if success else 1)
