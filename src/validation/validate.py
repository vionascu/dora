#!/usr/bin/env python3
"""
VALIDATION LAYER - Quality Gates
Ensures data integrity and catches approximations
"""

import json
import re
from datetime import datetime
from pathlib import Path

class Validator:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.calculations = self.root_dir / "calculations"
        self.repos_file = self.root_dir / "ReposInput.md"
        self.errors = []
        self.warnings = []
        self.approximations_found = 0
        self.out_of_bounds_found = 0
        self.missing_inputs_found = 0
        self.time_range_mismatches = 0

    def _add_error(self, message, category=None):
        self.errors.append(message)
        if category == "approx":
            self.approximations_found += 1
        elif category == "bounds":
            self.out_of_bounds_found += 1
        elif category == "missing_inputs":
            self.missing_inputs_found += 1
        elif category == "time_range":
            self.time_range_mismatches += 1

    def _add_warning(self, message):
        self.warnings.append(message)

    def _load_json(self, path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return None

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

    def validate_structure(self):
        """Validate required directory structure"""
        print("Validating structure...")

        required_dirs = [
            self.calculations,
            self.calculations / "per_repo",
            self.calculations / "global"
        ]

        for d in required_dirs:
            if not d.exists():
                self._add_error(f"Missing directory: {d.relative_to(self.root_dir)}")

        required_files = [
            self.calculations / "sanity_checks.json",
            self.calculations / "capabilities.json"
        ]
        for f in required_files:
            if not f.exists():
                self._add_error(f"Missing calculations file: {f.relative_to(self.root_dir)}")

    def validate_calculations_format(self):
        """Validate all calculation files have required fields"""
        print("Validating calculation files...")

        if not self.calculations.exists():
            return

        required_fields = ["metric_id", "inputs", "method", "time_range", "calculated_at"]

        for calc_file in self.calculations.rglob("*.json"):
            # Skip MANIFEST.json - it's a validation report, not a metric
            if calc_file.name in ("MANIFEST.json", "manifest.json"):
                continue

            try:
                with open(calc_file, 'r') as f:
                    data = json.load(f)

                # Check required fields
                for field in required_fields:
                    if field not in data:
                        self._add_error(f"{calc_file.relative_to(self.root_dir)}: Missing '{field}'")

                if "repo" not in data and "repos" not in data:
                    self._add_error(f"{calc_file.relative_to(self.root_dir)}: Missing 'repo' or 'repos'")

                time_range = data.get("time_range")
                if not isinstance(time_range, dict) or "start" not in time_range or "end" not in time_range:
                    self._add_error(f"{calc_file.relative_to(self.root_dir)}: Invalid 'time_range' (requires start/end)")

                # Check for approximations
                content_str = json.dumps(data)
                if re.search(r'~|approx|estimated', content_str, re.IGNORECASE):
                    self._add_error(f"{calc_file.relative_to(self.root_dir)}: Contains approximation markers", "approx")

                # Check for invalid values
                if isinstance(data.get("value"), (int, float)):
                    if data["value"] < 0:
                        self._add_error(f"{calc_file.relative_to(self.root_dir)}: Negative value not allowed ({data['value']})", "bounds")

                    # Coverage-specific checks
                    if "coverage" in data.get("metric_id", ""):
                        if data["value"] > 100:
                            self._add_error(f"{calc_file.relative_to(self.root_dir)}: Coverage > 100% ({data['value']})", "bounds")

            except json.JSONDecodeError as e:
                self._add_error(f"{calc_file.relative_to(self.root_dir)}: Invalid JSON - {str(e)}")
            except Exception as e:
                self._add_error(f"{calc_file.relative_to(self.root_dir)}: {str(e)}")

    def validate_traceability(self):
        """Validate calculations reference existing inputs"""
        print("Validating traceability...")

        if not self.calculations.exists():
            return

        for calc_file in self.calculations.rglob("*.json"):
            # Skip MANIFEST.json - it's a validation report, not a metric
            if calc_file.name in ("MANIFEST.json", "manifest.json"):
                continue

            try:
                with open(calc_file, 'r') as f:
                    data = json.load(f)

                inputs = data.get("inputs", [])
                if not isinstance(inputs, list):
                    inputs = [inputs]

                for input_path in inputs:
                    if input_path:
                        full_path = self.root_dir / input_path
                        if not full_path.exists():
                            self._add_error(f"{calc_file.relative_to(self.root_dir)}: Referenced input not found: {input_path}", "missing_inputs")

            except Exception:
                pass  # Already reported in format validation

    def validate_global_vs_perrepo(self):
        """Validate global metrics reference per-repo calculations"""
        print("Validating global vs per-repo consistency...")

        global_dir = self.calculations / "global"
        per_repo_dir = self.calculations / "per_repo"

        if not (global_dir.exists() and per_repo_dir.exists()):
            return

        # Check that global commits file references existing repos
        global_commits = global_dir / "commits.json"
        if global_commits.exists():
            try:
                with open(global_commits, 'r') as f:
                    data = json.load(f)
                    repos = data.get("repos", [])

                    for repo in repos:
                        repo_path = per_repo_dir / repo
                        if not repo_path.exists():
                            self._add_error(f"Global metrics reference non-existent repo: {repo}")

            except Exception:
                pass

    def validate_dashboard_requirements(self):
        """Validate required calculation files exist for dashboard consumption"""
        print("Validating dashboard requirements...")

        repos = self.parse_repos()
        required_per_repo = [
            "commits.json",
            "contributors.json",
            "coverage.json",
            "dora_frequency.json",
            "lead_time.json",
            "tests.json"
        ]
        required_global = [
            "commits.json",
            "contributors.json",
            "velocity.json",
            "summary.json",
            "tests.json"
        ]

        for repo in repos.keys():
            repo_dir = self.calculations / "per_repo" / repo
            for filename in required_per_repo:
                if not (repo_dir / filename).exists():
                    self._add_error(f"Missing calculation for dashboard: per_repo/{repo}/{filename}")

        global_dir = self.calculations / "global"
        for filename in required_global:
            if not (global_dir / filename).exists():
                self._add_error(f"Missing calculation for dashboard: global/{filename}")

    def _commit_range_from_raw(self, commits_file):
        data = self._load_json(commits_file)
        if not data:
            return None, None
        commits = data.get("commits", [])
        if not commits:
            return None, None
        dates = [c["timestamp"][:10] for c in commits if c.get("timestamp")]
        if not dates:
            return None, None
        return min(dates), max(dates)

    def validate_time_ranges(self):
        """Validate time_range consistency for commit-based metrics"""
        print("Validating time ranges...")

        for calc_file in self.calculations.rglob("*.json"):
            if calc_file.name in ("MANIFEST.json", "manifest.json"):
                continue
            data = self._load_json(calc_file)
            if not data:
                continue

            time_range = data.get("time_range") or {}
            start = time_range.get("start")
            end = time_range.get("end")

            inputs = data.get("inputs", [])
            if not isinstance(inputs, list):
                inputs = [inputs]

            raw_commit_input = None
            for input_path in inputs:
                if input_path and input_path.endswith("commits.json") and input_path.startswith("git_artifacts/"):
                    raw_commit_input = self.root_dir / input_path
                    break

            if raw_commit_input and raw_commit_input.exists():
                raw_start, raw_end = self._commit_range_from_raw(raw_commit_input)
                if raw_start and raw_end:
                    if start != raw_start or end != raw_end:
                        self._add_error(
                            f"{calc_file.relative_to(self.root_dir)}: time_range mismatch with raw commits ({start}-{end} vs {raw_start}-{raw_end})",
                            "time_range"
                        )

        global_commits = self.calculations / "global" / "commits.json"
        if global_commits.exists():
            data = self._load_json(global_commits)
            if data:
                inputs = data.get("inputs", [])
                per_repo_ranges = []
                for input_path in inputs:
                    per_repo_file = self.root_dir / input_path
                    repo_data = self._load_json(per_repo_file)
                    if repo_data and repo_data.get("time_range"):
                        tr = repo_data["time_range"]
                        if tr.get("start") and tr.get("end"):
                            per_repo_ranges.append((tr["start"], tr["end"]))
                if per_repo_ranges:
                    min_start = min(r[0] for r in per_repo_ranges)
                    max_end = max(r[1] for r in per_repo_ranges)
                    tr = data.get("time_range", {})
                    if tr.get("start") != min_start or tr.get("end") != max_end:
                        self._add_error(
                            f"{global_commits.relative_to(self.root_dir)}: time_range mismatch with per-repo commits ({tr.get('start')}-{tr.get('end')} vs {min_start}-{max_end})",
                            "time_range"
                        )

    def generate_manifest(self):
        """Generate manifest.json for dashboard consumption"""
        print("Generating manifest.json...")

        per_repo_metrics = {}
        per_repo_root = self.calculations / "per_repo"
        for repo_dir in sorted(per_repo_root.iterdir()) if per_repo_root.exists() else []:
            if not repo_dir.is_dir():
                continue
            repo_entry = {}
            for calc_file in sorted(repo_dir.glob("*.json")):
                data = self._load_json(calc_file)
                if not data:
                    continue
                key = calc_file.stem
                repo_entry[key] = {
                    **data,
                    "calculation_path": str(calc_file.relative_to(self.root_dir))
                }
            per_repo_metrics[repo_dir.name] = repo_entry

        global_metrics = {}
        global_dir = self.calculations / "global"
        for calc_file in sorted(global_dir.glob("*.json")) if global_dir.exists() else []:
            data = self._load_json(calc_file)
            if not data:
                continue
            global_metrics[calc_file.name] = {
                **data,
                "calculation_path": str(calc_file.relative_to(self.root_dir))
            }

        total_metrics = 0
        for calc_file in self.calculations.rglob("*.json"):
            if calc_file.name in ("MANIFEST.json", "manifest.json"):
                continue
            total_metrics += 1

        manifest = {
            "manifest_id": "dora.manifest",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "validation_status": "PASS" if not self.errors else "FAIL",
            "summary": {
                "total_metrics": total_metrics,
                "validation_errors": len(self.errors),
                "validation_warnings": len(self.warnings),
                "approximations_found": self.approximations_found,
                "out_of_bounds_values": self.out_of_bounds_found,
                "missing_inputs": self.missing_inputs_found,
                "time_range_mismatches": self.time_range_mismatches
            },
            "global_metrics": global_metrics,
            "per_repo_metrics": per_repo_metrics,
            "errors": self.errors,
            "warnings": self.warnings
        }

        manifest_path = self.calculations / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        manifest_upper = self.calculations / "MANIFEST.json"
        with open(manifest_upper, "w") as f:
            json.dump(manifest, f, indent=2)

    def report(self):
        """Print validation report"""
        print("\n" + "="*70)
        print(f"VALIDATION RESULTS")
        print("="*70)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for err in self.errors:
                print(f"  ✗ {err}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warn in self.warnings:
                print(f"  ⚠ {warn}")

        if not self.errors and not self.warnings:
            print("\n✅ All quality gates passed!")

        print("="*70 + "\n")

        return len(self.errors) == 0

    def run(self):
        """Execute validation pipeline"""
        print("\n" + "="*70)
        print("DORA VALIDATION LAYER - Quality Gates")
        print("="*70 + "\n")

        self.validate_structure()
        self.validate_calculations_format()
        self.validate_traceability()
        self.validate_global_vs_perrepo()
        self.validate_dashboard_requirements()
        self.validate_time_ranges()
        self.generate_manifest()

        return self.report()

if __name__ == "__main__":
    validator = Validator()
    success = validator.run()
    exit(0 if success else 1)
