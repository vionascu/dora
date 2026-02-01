#!/usr/bin/env python3
"""
Scan GitHub repositories for epics, user stories, and test files
"""

import json
import re
import subprocess
from pathlib import Path
from collections import defaultdict

class GitHubScanner:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.git_artifacts = self.root_dir / "git_artifacts"
        self.results = {
            "epics": defaultdict(list),
            "user_stories": defaultdict(list),
            "tests": defaultdict(lambda: {"files": [], "count": 0}),
            "test_frameworks": defaultdict(set)
        }

    def scan_for_epics_and_stories(self, repo_path):
        """Search for files containing epic or user story references"""
        repo_name = repo_path.parent.name if repo_path.name == "clone" else repo_path.name
        
        # Common patterns for epic/story files
        patterns = [
            "**/*epic*",
            "**/*story*",
            "**/*user*story*",
            "**/*US*",
            "**/*requirement*",
            "**/*specification*",
            "**/docs/**",
            "**/issues/**",
            "**/*.md"
        ]
        
        for pattern in patterns:
            for file_path in repo_path.glob(pattern):
                if file_path.is_file() and not any(p in str(file_path) for p in ['.git', '__pycache__', 'node_modules', '.gradle']):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # Look for epic/story keywords
                        if re.search(r'epic|epic\s*story|us-\d+|user\s*story', content, re.IGNORECASE):
                            rel_path = file_path.relative_to(repo_path)
                            
                            # Extract mentions
                            epics = re.findall(r'[Ee]pic[:\s]+([^\n]+)', content)
                            stories = re.findall(r'[Uu]ser\s*[Ss]tory|US-\d+|[US]S-\d+', content)
                            
                            if epics or stories:
                                self.results["epics"][repo_name].extend(epics[:3])  # Top 3
                                self.results["user_stories"][repo_name].extend(list(set(stories))[:5])  # Top 5
                    except:
                        pass

    def scan_for_tests(self, repo_path):
        """Search for test files"""
        repo_name = repo_path.parent.name if repo_path.name == "clone" else repo_path.name
        
        # Test file patterns by language
        test_patterns = {
            "java": ["**/*Test.java", "**/*Tests.java", "**/test/**/*.java"],
            "javascript": ["**/*.test.js", "**/*.spec.js", "**/test/**/*.js"],
            "python": ["**/test_*.py", "**/*_test.py", "**/tests/**/*.py"],
            "go": ["**/*_test.go"],
        }
        
        # Generic patterns
        generic_patterns = ["**/test/**", "**/tests/**", "**/__tests__/**"]
        
        all_patterns = list(test_patterns.values())[0] + generic_patterns
        
        test_files = []
        test_count = 0
        frameworks = set()
        
        for pattern in all_patterns:
            for test_file in repo_path.glob(pattern):
                if test_file.is_file() and test_file.name not in [f.name for f in test_files]:
                    test_files.append(test_file)
                    test_count += 1
                    
                    # Detect test framework
                    try:
                        with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if 'import unittest' in content or 'from unittest' in content:
                                frameworks.add('unittest')
                            if 'import pytest' in content or 'from pytest' in content:
                                frameworks.add('pytest')
                            if 'import org.junit' in content:
                                frameworks.add('JUnit')
                            if 'describe(' in content or 'it(' in content:
                                frameworks.add('Jest/Mocha')
                    except:
                        pass
        
        self.results["tests"][repo_name] = {
            "files": [str(f.relative_to(repo_path)) for f in test_files[:10]],
            "count": test_count
        }
        self.results["test_frameworks"][repo_name] = list(frameworks)

    def save_results(self):
        """Save scan results"""
        output = {
            "epics": dict(self.results["epics"]),
            "user_stories": dict(self.results["user_stories"]),
            "tests": dict(self.results["tests"]),
            "test_frameworks": dict(self.results["test_frameworks"])
        }
        
        artifacts_file = self.git_artifacts / "github_scan_artifacts.json"
        with open(artifacts_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        return output

    def scan_all_repos(self):
        """Scan all cloned repositories"""
        print("\n" + "="*70)
        print("GITHUB ARTIFACT SCANNER - Epics, User Stories, and Tests")
        print("="*70 + "\n")
        
        if not self.git_artifacts.exists():
            print("No git artifacts found. Run collection layer first.")
            return {}
        
        for repo_dir in sorted(self.git_artifacts.iterdir()):
            if repo_dir.is_dir() and not repo_dir.name.startswith('.'):
                clone_dir = repo_dir / "clone"
                if not clone_dir.exists():
                    print(f"Skipping {repo_dir.name} (no clone directory)")
                    continue
                print(f"Scanning {repo_dir.name}...")
                self.scan_for_epics_and_stories(clone_dir)
                self.scan_for_tests(clone_dir)
                print(f"  ✓ Scan complete for {repo_dir.name}\n")
        
        results = self.save_results()
        
        print("\n" + "="*70)
        print("SCAN RESULTS")
        print("="*70)
        print(f"Epics found: {sum(len(v) for v in results['epics'].values())}")
        print(f"User stories found: {sum(len(v) for v in results['user_stories'].values())}")
        print(f"Total test files: {sum(v['count'] for v in results['tests'].values())}")
        print("="*70 + "\n")
        
        return results

if __name__ == "__main__":
    scanner = GitHubScanner()
    results = scanner.scan_all_repos()
