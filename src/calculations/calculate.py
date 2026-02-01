#!/usr/bin/env python3
"""
CALCULATION LAYER - Metrics Computation
Processes raw git and CI artifacts into normalized, auditable metrics
"""

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

class Calculator:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.git_artifacts = self.root_dir / "git_artifacts"
        self.ci_artifacts = self.root_dir / "ci_artifacts"
        self.calculations = self.root_dir / "calculations"

        # Create directory structure
        self.calculations.mkdir(exist_ok=True)
        (self.calculations / "per_repo").mkdir(exist_ok=True)
        (self.calculations / "global").mkdir(exist_ok=True)

    def _write_json(self, path, payload):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)

    def _safe_time_range(self, start, end):
        return {"start": start, "end": end}

    def _repo_inputs(self, repo_name, *relative_paths):
        inputs = []
        for rel in relative_paths:
            if not rel:
                continue
            path = self.root_dir / rel
            if path.exists():
                inputs.append(str(path.relative_to(self.root_dir)))
        return inputs

    def list_repos(self):
        """List repos based on collected artifacts"""
        repos = {}
        if not self.git_artifacts.exists():
            return repos
        for repo_dir in sorted(self.git_artifacts.iterdir()):
            if not repo_dir.is_dir() or repo_dir.name.startswith("."):
                continue
            repos[repo_dir.name] = {}
            ci_info = self.ci_artifacts / repo_dir.name / "ci_info.json"
            if ci_info.exists():
                with open(ci_info, "r") as f:
                    repos[repo_dir.name].update(json.load(f))
        return repos

    def calculate_commits(self, repo_name):
        """Calculate commit metrics for a repository"""
        commits_file = self.git_artifacts / repo_name / "commits.json"

        if not commits_file.exists():
            return {
                "metric_id": "repo.commits",
                "repo": repo_name,
                "repos": [repo_name],
                "inputs": [],
                "time_range": self._safe_time_range(None, None),
                "total_commits": None,
                "unique_dates": None,
                "avg_commits_per_day": None,
                "period_start": None,
                "period_end": None,
                "days_active": None,
                "method": "Count commits in git_artifacts commits.json",
                "reason": "Missing git_artifacts commits.json",
                "calculated_at": datetime.now().isoformat()
            }

        with open(commits_file, 'r') as f:
            commits_data = json.load(f)

        commits = commits_data.get("commits", [])
        if not commits:
            return {
                "metric_id": "repo.commits",
                "repo": repo_name,
                "repos": [repo_name],
                "inputs": [str(commits_file.relative_to(self.root_dir))],
                "time_range": self._safe_time_range(None, None),
                "total_commits": 0,
                "unique_dates": 0,
                "avg_commits_per_day": 0,
                "period_start": None,
                "period_end": None,
                "days_active": 0,
                "method": "Count commits in git_artifacts commits.json",
                "reason": "No commits found in git artifacts",
                "calculated_at": datetime.now().isoformat()
            }

        # Calculate metrics
        dates = [c["timestamp"][:10] for c in commits]
        unique_dates = len(set(dates))
        period_start = min(dates) if dates else None
        period_end = max(dates) if dates else None
        days_active = 0
        if period_start and period_end:
            try:
                start_dt = datetime.fromisoformat(period_start)
                end_dt = datetime.fromisoformat(period_end)
                days_active = (end_dt - start_dt).days + 1
            except ValueError:
                days_active = unique_dates

        result = {
            "metric_id": "repo.commits",
            "repo": repo_name,
            "repos": [repo_name],
            "time_range": self._safe_time_range(period_start, period_end),
            "inputs": [str(commits_file.relative_to(self.root_dir))],
            "total_commits": len(commits),
            "unique_dates": unique_dates,
            "avg_commits_per_day": round(len(commits) / max(1, unique_dates), 2) if unique_dates > 0 else 0,
            "period_start": period_start,
            "period_end": period_end,
            "days_active": days_active,
            "method": "Count commits; average by unique active dates; active period from first to last commit date",
            "calculated_at": datetime.now().isoformat()
        }

        return result

    def calculate_contributors(self, repo_name):
        """Calculate contributor metrics"""
        authors_file = self.git_artifacts / repo_name / "authors.json"
        timeline_file = self.git_artifacts / repo_name / "timeline.json"

        if not authors_file.exists():
            return {
                "metric_id": "repo.contributors",
                "repo": repo_name,
                "repos": [repo_name],
                "inputs": [],
                "time_range": self._safe_time_range(None, None),
                "unique_contributors": None,
                "method": "Count unique author emails in git_artifacts authors.json",
                "reason": "Missing git_artifacts authors.json",
                "calculated_at": datetime.now().isoformat()
            }

        with open(authors_file, 'r') as f:
            authors_data = json.load(f)

        time_range = self._safe_time_range(None, None)
        if timeline_file.exists():
            with open(timeline_file, "r") as f:
                timeline = json.load(f)
                time_range = self._safe_time_range(
                    timeline.get("first_commit"),
                    timeline.get("last_commit")
                )

        return {
            "metric_id": "repo.contributors",
            "repo": repo_name,
            "repos": [repo_name],
            "inputs": self._repo_inputs(repo_name, authors_file.relative_to(self.root_dir), timeline_file.relative_to(self.root_dir)),
            "time_range": time_range,
            "unique_contributors": authors_data.get("unique_authors", 0),
            "method": "Count unique author emails",
            "calculated_at": datetime.now().isoformat()
        }

    def calculate_coverage_percentage(self, repo_name, config):
        """Attempt to extract coverage percentage if available"""
        coverage_tool = config.get("coverage") or config.get("coverage_tool", "")
        ci_dir = self.ci_artifacts / repo_name

        coverage_files = []
        if coverage_tool == "jacoco":
            coverage_files = list(ci_dir.rglob("*.jacoco.xml")) + list(ci_dir.rglob("*jacoco*.xml"))
        elif coverage_tool == "pytest-cov":
            coverage_files = list(ci_dir.rglob("coverage.xml"))
        elif coverage_tool == "lcov":
            coverage_files = list(ci_dir.rglob("*.lcov.info"))

        inputs = [str(f.relative_to(self.root_dir)) for f in coverage_files]

        value = None
        reason = None
        method = f"Parse {coverage_tool} output"

        if inputs:
            try:
                if coverage_tool == "jacoco":
                    total_missed = 0
                    total_covered = 0
                    for coverage_file in coverage_files:
                        tree = ET.parse(coverage_file)
                        root = tree.getroot()
                        counters = root.findall(".//counter")
                        for counter in counters:
                            if counter.get("type") == "LINE":
                                total_missed += int(counter.get("missed", 0))
                                total_covered += int(counter.get("covered", 0))
                                break
                    total = total_missed + total_covered
                    if total > 0:
                        value = round((total_covered / total) * 100, 2)
                elif coverage_tool == "pytest-cov":
                    total_lines = 0
                    total_covered = 0
                    for coverage_file in coverage_files:
                        tree = ET.parse(coverage_file)
                        root = tree.getroot()
                        lines_valid = root.get("lines-valid")
                        lines_covered = root.get("lines-covered")
                        if lines_valid is not None and lines_covered is not None:
                            total_lines += int(lines_valid)
                            total_covered += int(lines_covered)
                    if total_lines > 0:
                        value = round((total_covered / total_lines) * 100, 2)
                elif coverage_tool == "lcov":
                    total_lines = 0
                    hit_lines = 0
                    for coverage_file in coverage_files:
                        with open(coverage_file, "r") as f:
                            for line in f:
                                if line.startswith("LF:"):
                                    total_lines += int(line.strip().split(":")[1])
                                elif line.startswith("LH:"):
                                    hit_lines += int(line.strip().split(":")[1])
                                elif line.startswith("DA:"):
                                    parts = line.strip().split(":")[1].split(",")
                                    if len(parts) >= 2:
                                        total_lines += 1
                                        if int(parts[1]) > 0:
                                            hit_lines += 1
                    if total_lines > 0:
                        value = round((hit_lines / total_lines) * 100, 2)
            except Exception as e:
                reason = f"Coverage parsing failed: {str(e)}"

        if value is None and reason is None:
            reason = f"Coverage data not available (tool: {coverage_tool}, requires local test run)" if not inputs else "Coverage parsing did not produce a value"

        return {
            "metric_id": "repo.coverage",
            "repo": repo_name,
            "repos": [repo_name],
            "inputs": inputs,
            "time_range": self._safe_time_range(None, None),
            "value": value,
            "reason": reason,
            "method": method,
            "calculated_at": datetime.now().isoformat()
        }

    def calculate_dora_frequency(self, repo_name):
        """Calculate deployment frequency (proxied by commit frequency)"""
        # In real DORA, this would use deployment tags or release branches
        # For now, we proxy it using commit frequency
        commits_file = self.git_artifacts / repo_name / "commits.json"

        if not commits_file.exists():
            return {
                "metric_id": "repo.dora_frequency",
                "repo": repo_name,
                "repos": [repo_name],
                "inputs": [],
                "time_range": self._safe_time_range(None, None),
                "value": None,
                "unit": "commits/day",
                "method": "Total commits / days in history (proxy)",
                "reason": "Missing git_artifacts commits.json",
                "calculated_at": datetime.now().isoformat()
            }

        with open(commits_file, 'r') as f:
            commits_data = json.load(f)

        commits = commits_data.get("commits", [])
        if not commits:
            return {
                "metric_id": "repo.dora_frequency",
                "repo": repo_name,
                "repos": [repo_name],
                "inputs": [str(commits_file.relative_to(self.root_dir))],
                "time_range": self._safe_time_range(None, None),
                "value": None,
                "unit": "commits/day",
                "method": "Total commits / days in history (proxy)",
                "reason": "No commits found in git artifacts",
                "calculated_at": datetime.now().isoformat()
            }

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
            "repos": [repo_name],
            "inputs": [str(commits_file.relative_to(self.root_dir))],
            "time_range": self._safe_time_range(min(dates), max(dates)),
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
            return {
                "metric_id": "repo.dora_lead_time",
                "repo": repo_name,
                "repos": [repo_name],
                "inputs": [],
                "time_range": self._safe_time_range(None, None),
                "value": None,
                "unit": "hours",
                "method": "Average time between consecutive commits",
                "reason": "Missing git_artifacts commits.json",
                "calculated_at": datetime.now().isoformat()
            }

        with open(commits_file, 'r') as f:
            commits_data = json.load(f)

        commits = commits_data.get("commits", [])
        if len(commits) < 2:
            return {
                "metric_id": "repo.dora_lead_time",
                "repo": repo_name,
                "repos": [repo_name],
                "value": None,
                "inputs": [str(commits_file.relative_to(self.root_dir))],
                "time_range": self._safe_time_range(None, None),
                "reason": "Less than 2 commits - cannot calculate lead time",
                "method": "Average time between commits",
                "calculated_at": datetime.now().isoformat()
            }

        dates = [c["timestamp"][:10] for c in commits if c.get("timestamp")]

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
            "repos": [repo_name],
            "inputs": [str(commits_file.relative_to(self.root_dir))],
            "time_range": self._safe_time_range(min(dates) if dates else None, max(dates) if dates else None),
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
                self._write_json(repo_calc_dir / filename, metric)
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
        time_range_start = None
        time_range_end = None

        for repo_name in repos:
            repo_calc_dir = self.calculations / "per_repo" / repo_name
            commits_file = repo_calc_dir / "commits.json"

            if commits_file.exists():
                with open(commits_file, 'r') as f:
                    data = json.load(f)
                    total_commits += data.get("total_commits", 0)
                    repos_analyzed.append(repo_name)
                    time_range = data.get("time_range") or {}
                    start = time_range.get("start")
                    end = time_range.get("end")
                    if start:
                        time_range_start = min(time_range_start, start) if time_range_start else start
                    if end:
                        time_range_end = max(time_range_end, end) if time_range_end else end

            # Collect contributors
            authors_file = self.git_artifacts / repo_name / "authors.json"
            if authors_file.exists():
                with open(authors_file, "r") as f:
                    data = json.load(f)
                    for email in data.get("authors", []):
                        all_contributors.add(email)

        # Save global commits
        self._write_json(
            global_dir / "commits.json",
            {
                "metric_id": "global.commits",
                "repos": repos_analyzed,
                "inputs": [str((self.calculations / "per_repo" / r / "commits.json").relative_to(self.root_dir)) for r in repos_analyzed],
                "time_range": self._safe_time_range(time_range_start, time_range_end),
                "total_commits": total_commits,
                "repos_count": len(repos_analyzed),
                "method": "Sum commits across all analyzed repos",
                "calculated_at": datetime.now().isoformat()
            }
        )

        self._write_json(
            global_dir / "contributors.json",
            {
                "metric_id": "global.contributors",
                "repos": repos_analyzed,
                "inputs": [str((self.git_artifacts / r / "authors.json").relative_to(self.root_dir)) for r in repos_analyzed if (self.git_artifacts / r / "authors.json").exists()],
                "time_range": self._safe_time_range(time_range_start, time_range_end),
                "unique_contributors": len(all_contributors) if all_contributors else None,
                "method": "Union of author emails across repos",
                "reason": None if all_contributors else "No authors.json inputs available",
                "calculated_at": datetime.now().isoformat()
            }
        )

        avg_velocity = None
        velocity_values = []
        for repo_name in repos_analyzed:
            repo_commits = self.calculations / "per_repo" / repo_name / "commits.json"
            if repo_commits.exists():
                with open(repo_commits, "r") as f:
                    data = json.load(f)
                    value = data.get("avg_commits_per_day")
                    if isinstance(value, (int, float)):
                        velocity_values.append(value)
        if velocity_values:
            avg_velocity = round(sum(velocity_values) / len(velocity_values), 2)

        self._write_json(
            global_dir / "velocity.json",
            {
                "metric_id": "global.velocity",
                "repos": repos_analyzed,
                "inputs": [str((self.calculations / "per_repo" / r / "commits.json").relative_to(self.root_dir)) for r in repos_analyzed],
                "time_range": self._safe_time_range(time_range_start, time_range_end),
                "value": avg_velocity,
                "unit": "commits/day",
                "method": "Average per-repo avg_commits_per_day",
                "reason": None if avg_velocity is not None else "No per-repo velocity values available",
                "calculated_at": datetime.now().isoformat()
            }
        )

        # Save global summary
        self._write_json(
            global_dir / "summary.json",
            {
                "metric_id": "global.summary",
                "repos": repos_analyzed,
                "inputs": [
                    str((self.calculations / "per_repo" / r / "commits.json").relative_to(self.root_dir))
                    for r in repos_analyzed
                ],
                "time_range": self._safe_time_range(time_range_start, time_range_end),
                "repos_analyzed": repos_analyzed,
                "repos_total_count": len(repos),
                "repos_with_issues": [r for r in repos if r not in repos_analyzed],
                "total_commits": total_commits,
                "unique_contributors": len(all_contributors) if all_contributors else None,
                "method": "Aggregate per-repo commit totals and contributors",
                "calculated_at": datetime.now().isoformat()
            }
        )

        print(f"    ✓ Saved global metrics for {len(repos_analyzed)} repos")

    def write_system_files(self, repos):
        """Write required system calculation files"""
        sanity_checks = {
            "metric_id": "sanity.checks",
            "repos": list(repos.keys()),
            "inputs": [],
            "time_range": self._safe_time_range(None, None),
            "checks": {
                "git_artifacts_present": self.git_artifacts.exists(),
                "ci_artifacts_present": self.ci_artifacts.exists(),
                "calculations_present": self.calculations.exists()
            },
            "method": "Verify presence of required pipeline directories",
            "calculated_at": datetime.now().isoformat()
        }
        self._write_json(self.calculations / "sanity_checks.json", sanity_checks)

        capabilities = {
            "metric_id": "capabilities",
            "repos": list(repos.keys()),
            "inputs": [],
            "time_range": self._safe_time_range(None, None),
            "available_metrics": [
                "repo.commits",
                "repo.contributors",
                "repo.coverage",
                "repo.dora_frequency",
                "repo.dora_lead_time",
                "repo.tests",
                "repo.untested_epics",
                "global.commits",
                "global.contributors",
                "global.velocity",
                "global.summary",
                "global.tests",
                "global.untested_epics"
            ],
            "method": "Static capability declaration from calculation outputs",
            "calculated_at": datetime.now().isoformat()
        }
        self._write_json(self.calculations / "capabilities.json", capabilities)

    def run(self):
        """Execute calculation pipeline"""
        print("\n" + "="*70)
        print("DORA CALCULATION LAYER - Metrics Computation")
        print("="*70 + "\n")

        repos = self.list_repos()
        if not repos:
            print("No repositories found in git_artifacts/")
            return False

        print(f"Computing metrics for {len(repos)} repositories\n")

        for repo_name, config in repos.items():
            self.save_repo_metrics(repo_name, config)

        self.calculate_global_metrics(repos)
        self.write_system_files(repos)

        print(f"\n{'='*70}")
        print("Calculation complete")
        print("="*70 + "\n")

        return True

if __name__ == "__main__":
    calculator = Calculator()
    success = calculator.run()
    exit(0 if success else 1)
