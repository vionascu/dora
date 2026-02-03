#!/usr/bin/env python3
"""
COLLECTION LAYER - CI Artifacts Extraction
Collects CI/test/coverage data with environment validation and dynamic framework detection
"""

import json
from datetime import datetime
from pathlib import Path
from src.config.config_parser import RepoConfigParser
from src.collection.ci_environment import CIEnvironmentValidator
from src.collection.framework_detector import FrameworkDetector
from src.collection.coverage_tool_runner import CoverageToolRunnerFactory


class CICollector:
    def __init__(self, root_dir=".", config_file=None):
        self.root_dir = Path(root_dir)
        self.git_artifacts = self.root_dir / "git_artifacts"
        self.ci_artifacts = self.root_dir / "ci_artifacts"
        self.ci_artifacts.mkdir(exist_ok=True)

        # Initialize config parser
        self.config_parser = RepoConfigParser(config_file=config_file)
        is_valid, errors = self.config_parser.load_config()

        if not is_valid:
            raise ValueError(f"Configuration validation errors: {errors}")

    def parse_repos(self):
        """Parse repository configuration"""
        return self.config_parser.get_all_repos()

    def collect_repo_ci(self, repo_name, config):
        """
        Collect CI/test/coverage data from a repository

        Validates environment, detects frameworks, and runs appropriate coverage tools
        """
        print(f"  Processing CI for {repo_name}...")

        repo_dir = self.ci_artifacts / repo_name
        repo_dir.mkdir(exist_ok=True)

        git_clone = self.git_artifacts / repo_name / "clone"
        if not git_clone.exists():
            print(f"    ℹ Git data not collected yet")
            return

        language = config.get("language", "unknown")
        configured_tools = self.config_parser.get_coverage_tools(repo_name) or []

        # Step 1: Validate environment
        print(f"    → Validating environment for {language}...")
        env_report = CIEnvironmentValidator.validate_language(language)

        if not env_report.is_valid:
            print(f"    ✗ Missing required tools: {env_report.missing_tools}")

        if env_report.warnings:
            for warning in env_report.warnings:
                print(f"    ⚠ {warning}")

        # Step 2: Detect frameworks
        print(f"    → Detecting test frameworks...")
        detected_test_fw = FrameworkDetector.detect_test_framework(git_clone, language)
        detected_coverage_tool = FrameworkDetector.detect_coverage_tool(git_clone, language)

        print(f"    ✓ Detected: {detected_test_fw}, Coverage: {detected_coverage_tool}")

        # Step 3: Run coverage tools
        coverage_results = []

        # If tools are configured, use those; otherwise use auto-detected
        tools_to_run = []

        if configured_tools:
            for tool in configured_tools:
                tool_type = tool.get('type') if isinstance(tool, dict) else tool
                tools_to_run.append(tool_type)
        elif detected_coverage_tool:
            tools_to_run.append(detected_coverage_tool)

        for tool_type in tools_to_run:
            print(f"    → Running coverage with {tool_type}...")

            runner = CoverageToolRunnerFactory.create(tool_type, git_clone, repo_dir / "coverage")
            if runner is None:
                print(f"      ✗ No runner available for {tool_type}")
                continue

            result = runner.run()
            coverage_results.append(result)

            if result.success:
                print(f"      ✓ Success: {result.status_message}")
            else:
                print(f"      ⚠ {result.status_message}")
                if result.errors:
                    for error in result.errors:
                        print(f"        - {error}")

        # Step 4: Save CI info
        ci_info = {
            "metric_id": "ci.info.raw",
            "repo": repo_name,
            "language": language,
            "environment_validation": {
                "status": "valid" if env_report.is_valid else "missing_dependencies",
                "available_tools": {
                    name: {
                        "installed": result.installed,
                        "version": result.version
                    }
                    for name, result in env_report.available_tools.items()
                },
                "missing_tools": env_report.missing_tools,
                "warnings": env_report.warnings
            },
            "framework_detection": {
                "test_framework": detected_test_fw,
                "coverage_tool": detected_coverage_tool
            },
            "coverage_results": [r.to_dict() for r in coverage_results],
            "collected_at": datetime.now().isoformat()
        }

        with open(repo_dir / "ci_info.json", 'w') as f:
            json.dump(ci_info, f, indent=2)

        print(f"    ✓ CI collection complete")

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
