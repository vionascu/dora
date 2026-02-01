#!/usr/bin/env python3
"""
Calculate test metrics from GitHub scanning
"""

import json
from pathlib import Path
from datetime import datetime

class TestMetricsCalculator:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.git_artifacts = self.root_dir / "git_artifacts"
        self.calculations = self.root_dir / "calculations"

    def _write_json(self, path, payload):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)

    def _repo_names(self):
        if not self.git_artifacts.exists():
            return []
        repos = []
        for entry in sorted(self.git_artifacts.iterdir()):
            if entry.is_dir() and not entry.name.startswith("."):
                repos.append(entry.name)
        return repos

    def calculate_test_metrics(self):
        """Calculate test-related metrics"""
        
        # Load scan results
        scan_file = self.git_artifacts / "github_scan_artifacts.json"
        scan_data = None
        if scan_file.exists():
            with open(scan_file, 'r') as f:
                scan_data = json.load(f)

        results = {}
        repos = self._repo_names()
        
        # Global test metrics
        if scan_data:
            total_test_files = sum(v['count'] for v in scan_data.get('tests', {}).values())
            total_epics = sum(len(v) for v in scan_data.get('epics', {}).values())
            total_user_stories = sum(len(v) for v in scan_data.get('user_stories', {}).values())
        else:
            total_test_files = None
            total_epics = None
            total_user_stories = None
        
        global_tests = {
            "metric_id": "global.tests",
            "repos": repos,
            "inputs": [str(scan_file.relative_to(self.root_dir))] if scan_data else [],
            "time_range": {"start": None, "end": None},
            "total_test_files": total_test_files,
            "total_epics_found": total_epics,
            "total_user_stories_found": total_user_stories,
            "description": "Total test files across all repositories",
            "method": "Scan git_artifacts repositories for test files and epic/story references",
            "reason": None if scan_data else "Missing github_scan_artifacts.json",
            "calculated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Save global tests
        self._write_json(self.calculations / "global" / "tests.json", global_tests)
        results['global'] = global_tests
        
        # Per-repo test metrics
        for repo_name in repos:
            test_info = (scan_data or {}).get('tests', {}).get(repo_name, {})
            frameworks = (scan_data or {}).get('test_frameworks', {}).get(repo_name, [])
            epics = (scan_data or {}).get('epics', {}).get(repo_name, [])
            stories = (scan_data or {}).get('user_stories', {}).get(repo_name, [])

            repo_metrics = {
                "metric_id": f"repo.tests.{repo_name}",
                "repo": repo_name,
                "repos": [repo_name],
                "inputs": [str(scan_file.relative_to(self.root_dir))] if scan_data else [],
                "time_range": {"start": None, "end": None},
                "test_files": test_info.get('count') if scan_data else None,
                "test_frameworks": frameworks if scan_data else None,
                "epics": len(epics) if scan_data else None,
                "user_stories": len(stories) if scan_data else None,
                "sample_test_files": test_info.get('files', [])[:3] if scan_data else None,
                "method": "Scan git_artifacts repositories for test files and epic/story references",
                "reason": None if scan_data else "Missing github_scan_artifacts.json",
                "calculated_at": datetime.utcnow().isoformat() + "Z"
            }
            
            repo_dir = self.calculations / "per_repo" / repo_name
            repo_dir.mkdir(parents=True, exist_ok=True)
            self._write_json(repo_dir / "tests.json", repo_metrics)
            
            results[repo_name] = repo_metrics
        
        return results

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST METRICS CALCULATION")
    print("="*70 + "\n")
    
    calc = TestMetricsCalculator()
    results = calc.calculate_test_metrics()
    
    print(f"✓ Global test metrics saved")
    for repo, metrics in results.items():
        if repo != 'global':
            print(f"✓ Test metrics for {repo}: {metrics.get('test_files')} test files, "
                  f"{metrics.get('epics')} epics, {metrics.get('user_stories')} user stories")
    
    print("\n" + "="*70 + "\n")
