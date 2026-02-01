#!/usr/bin/env python3
"""
VALIDATION LAYER - Quality Gates
Ensures data integrity and catches approximations
"""

import json
import re
from pathlib import Path

class Validator:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.calculations = self.root_dir / "calculations"
        self.errors = []
        self.warnings = []

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
                self.errors.append(f"Missing directory: {d.relative_to(self.root_dir)}")

    def validate_calculations_format(self):
        """Validate all calculation files have required fields"""
        print("Validating calculation files...")

        if not self.calculations.exists():
            return

        required_fields = ["metric_id", "calculated_at"]

        for calc_file in self.calculations.rglob("*.json"):
            # Skip MANIFEST.json - it's a validation report, not a metric
            if calc_file.name == "MANIFEST.json":
                continue

            try:
                with open(calc_file, 'r') as f:
                    data = json.load(f)

                # Check required fields
                for field in required_fields:
                    if field not in data:
                        self.errors.append(f"{calc_file.relative_to(self.root_dir)}: Missing '{field}'")

                # Check for approximations
                content_str = json.dumps(data)
                if re.search(r'~|approx|estimated', content_str, re.IGNORECASE):
                    self.errors.append(f"{calc_file.relative_to(self.root_dir)}: Contains approximation markers")

                # Check for invalid values
                if isinstance(data.get("value"), (int, float)):
                    if data["value"] < 0:
                        self.errors.append(f"{calc_file.relative_to(self.root_dir)}: Negative value not allowed ({data['value']})")

                    # Coverage-specific checks
                    if "coverage" in data.get("metric_id", ""):
                        if data["value"] > 100:
                            self.errors.append(f"{calc_file.relative_to(self.root_dir)}: Coverage > 100% ({data['value']})")

            except json.JSONDecodeError as e:
                self.errors.append(f"{calc_file.relative_to(self.root_dir)}: Invalid JSON - {str(e)}")
            except Exception as e:
                self.errors.append(f"{calc_file.relative_to(self.root_dir)}: {str(e)}")

    def validate_traceability(self):
        """Validate calculations reference existing inputs"""
        print("Validating traceability...")

        if not self.calculations.exists():
            return

        for calc_file in self.calculations.rglob("*.json"):
            # Skip MANIFEST.json - it's a validation report, not a metric
            if calc_file.name == "MANIFEST.json":
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
                            self.warnings.append(f"{calc_file.relative_to(self.root_dir)}: Referenced input not found: {input_path}")

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
                            self.errors.append(f"Global metrics reference non-existent repo: {repo}")

            except Exception:
                pass

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

        return self.report()

if __name__ == "__main__":
    validator = Validator()
    success = validator.run()
    exit(0 if success else 1)
