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

    def calculate_test_metrics(self):
        """Calculate test-related metrics"""
        
        # Load scan results
        scan_file = self.git_artifacts / "github_scan_artifacts.json"
        if not scan_file.exists():
            print("No scan artifacts found")
            return {}
        
        with open(scan_file, 'r') as f:
            scan_data = json.load(f)
        
        results = {}
        
        # Global test metrics
        total_test_files = sum(v['count'] for v in scan_data['tests'].values())
        total_epics = sum(len(v) for v in scan_data['epics'].values())
        
        global_tests = {
            "metric_id": "global.tests",
            "value": total_test_files,
            "total_epics": total_epics,
            "description": "Total test files across all repositories",
            "calculated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Save global tests
        (self.calculations / "global" / "tests.json").write_text(
            json.dumps(global_tests, indent=2)
        )
        results['global'] = global_tests
        
        # Per-repo test metrics
        for repo_name, test_info in scan_data['tests'].items():
            repo_metrics = {
                "metric_id": f"repo.tests.{repo_name}",
                "repo": repo_name,
                "test_files": test_info['count'],
                "test_frameworks": scan_data['test_frameworks'].get(repo_name, []),
                "epics_found": len(scan_data['epics'].get(repo_name, [])),
                "user_stories_found": len(scan_data['user_stories'].get(repo_name, [])),
                "sample_tests": test_info['files'][:3],
                "calculated_at": datetime.utcnow().isoformat() + "Z"
            }
            
            repo_dir = self.calculations / "per_repo" / repo_name
            repo_dir.mkdir(parents=True, exist_ok=True)
            (repo_dir / "tests.json").write_text(json.dumps(repo_metrics, indent=2))
            
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
            print(f"✓ Test metrics for {repo}: {metrics['test_files']} test files, "
                  f"{metrics['epics_found']} epics, {metrics['user_stories_found']} user stories")
    
    print("\n" + "="*70 + "\n")
