#!/usr/bin/env python3
"""
Abstract coverage tool runners
Unified interface for running different coverage tools
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CoverageResult:
    """Result of coverage tool execution"""
    tool: str
    language: str
    success: bool
    coverage_percentage: Optional[float] = None
    files_covered: int = 0
    lines_covered: int = 0
    lines_total: int = 0
    report_path: Optional[Path] = None
    status_message: str = ""
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "tool": self.tool,
            "language": self.language,
            "success": self.success,
            "coverage_percentage": self.coverage_percentage,
            "files_covered": self.files_covered,
            "lines_covered": self.lines_covered,
            "lines_total": self.lines_total,
            "report_path": str(self.report_path) if self.report_path else None,
            "status_message": self.status_message,
            "errors": self.errors,
            "collected_at": datetime.now().isoformat()
        }


class CoverageToolRunner:
    """Abstract base class for coverage tool runners"""

    def __init__(self, repo_path: Path, output_dir: Path):
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, config: Optional[Dict] = None) -> CoverageResult:
        """
        Run coverage tool

        Args:
            config: Optional tool-specific configuration

        Returns:
            CoverageResult with execution results
        """
        raise NotImplementedError("Subclasses must implement run()")

    def _run_command(self, command: List[str], timeout: int = 600, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """
        Helper to run a command

        Args:
            command: Command to run
            timeout: Command timeout in seconds
            cwd: Working directory (defaults to repo_path)

        Returns:
            CompletedProcess result

        Raises:
            subprocess.CalledProcessError on non-zero exit
        """
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.repo_path,
                capture_output=True,
                timeout=timeout,
                text=True,
                check=False
            )
            return result
        except subprocess.TimeoutExpired as e:
            raise subprocess.TimeoutExpired(command[0], timeout)


class JaCoCoRunner(CoverageToolRunner):
    """Runner for JaCoCo (Java) coverage"""

    def run(self, config: Optional[Dict] = None) -> CoverageResult:
        """Run JaCoCo coverage collection"""
        result = CoverageResult(
            tool="jacoco",
            language="java",
            success=False
        )

        try:
            # Try Maven first
            maven_result = self._run_command(
                ["mvn", "clean", "test", "jacoco:report"],
                timeout=900
            )

            if maven_result.returncode == 0:
                # Look for jacoco.xml
                jacoco_files = list(self.repo_path.rglob("jacoco.xml"))
                jacoco_files = [f for f in jacoco_files if ".git" not in str(f)]

                if jacoco_files:
                    result.report_path = jacoco_files[0]
                    result.success = True
                    result.status_message = f"JaCoCo report found at {result.report_path}"
                    return result

            # Try Gradle if Maven failed
            gradle_result = self._run_command(
                ["./gradlew", "test", "jacocoTestReport"],
                timeout=900
            )

            if gradle_result.returncode == 0:
                jacoco_files = list(self.repo_path.rglob("jacoco.xml"))
                jacoco_files = [f for f in jacoco_files if ".git" not in str(f)]

                if jacoco_files:
                    result.report_path = jacoco_files[0]
                    result.success = True
                    result.status_message = f"JaCoCo report found via Gradle"
                    return result

            result.errors.append("No JaCoCo reports generated")
            result.status_message = "Maven and Gradle test/coverage execution completed but no reports found"

        except subprocess.TimeoutExpired:
            result.errors.append("JaCoCo execution timeout")
            result.status_message = "Build/test execution timeout (likely build time)"
        except Exception as e:
            result.errors.append(str(e))
            result.status_message = f"Error running JaCoCo: {str(e)}"

        return result


class PytestCovRunner(CoverageToolRunner):
    """Runner for pytest-cov (Python) coverage"""

    def run(self, config: Optional[Dict] = None) -> CoverageResult:
        """Run pytest with coverage"""
        result = CoverageResult(
            tool="pytest-cov",
            language="python",
            success=False
        )

        try:
            # Install dependencies
            requirements_file = self.repo_path / "requirements.txt"
            if requirements_file.exists():
                self._run_command(
                    ["pip", "install", "-q", "-r", str(requirements_file)],
                    timeout=600
                )

            # Install pytest and coverage if not present
            self._run_command(
                ["pip", "install", "-q", "pytest", "pytest-cov"],
                timeout=300
            )

            # Run pytest with coverage
            pytest_result = self._run_command(
                ["python", "-m", "pytest", "--cov=.", "--cov-report=xml", "--tb=short", "-v"],
                timeout=300
            )

            # Look for coverage.xml
            coverage_file = self.repo_path / "coverage.xml"
            if coverage_file.exists():
                result.report_path = coverage_file
                result.success = True
                result.status_message = "Coverage report generated via pytest-cov"

                # Try to extract percentage from coverage output
                for line in pytest_result.stdout.split('\n'):
                    if 'TOTAL' in line and '%' in line:
                        # Parse line like "TOTAL 1234 567 54%"
                        parts = line.split()
                        if parts[-1].endswith('%'):
                            try:
                                result.coverage_percentage = float(parts[-1].rstrip('%'))
                            except ValueError:
                                pass

                return result

            result.errors.append("No coverage.xml file generated")
            result.status_message = "Pytest execution completed but no coverage report found"

        except subprocess.TimeoutExpired:
            result.errors.append("pytest-cov execution timeout")
            result.status_message = "Test execution timeout"
        except Exception as e:
            result.errors.append(str(e))
            result.status_message = f"Error running pytest-cov: {str(e)}"

        return result


class LCovRunner(CoverageToolRunner):
    """Runner for LCOV (JavaScript/C) coverage"""

    def run(self, config: Optional[Dict] = None) -> CoverageResult:
        """Run JavaScript tests with LCOV coverage"""
        result = CoverageResult(
            tool="lcov",
            language="javascript",
            success=False
        )

        try:
            # Install dependencies
            npm_install = self._run_command(
                ["npm", "install", "--legacy-peer-deps"],
                timeout=600
            )

            if npm_install.returncode != 0:
                result.status_message = "npm install failed"
                result.errors.append(npm_install.stderr or "npm install failed")

            # Run tests with coverage
            npm_test = self._run_command(
                ["npm", "test", "--", "--coverage", "--coverage-reporter=lcov"],
                timeout=600
            )

            # Look for lcov.info
            lcov_file = self.repo_path / "coverage" / "lcov.info"
            if lcov_file.exists():
                result.report_path = lcov_file
                result.success = True
                result.status_message = "LCOV coverage report generated"
                return result

            result.errors.append("No lcov.info file generated")
            result.status_message = "npm test execution completed but no coverage report found"

        except subprocess.TimeoutExpired:
            result.errors.append("npm test timeout")
            result.status_message = "Test execution timeout"
        except Exception as e:
            result.errors.append(str(e))
            result.status_message = f"Error running npm tests: {str(e)}"

        return result


class CoverageToolRunnerFactory:
    """Factory for creating appropriate coverage tool runner"""

    RUNNERS = {
        'jacoco': JaCoCoRunner,
        'pytest-cov': PytestCovRunner,
        'lcov': LCovRunner,
    }

    @staticmethod
    def create(tool_type: str, repo_path: Path, output_dir: Path) -> Optional[CoverageToolRunner]:
        """
        Create appropriate runner for tool type

        Args:
            tool_type: Type of coverage tool
            repo_path: Path to repository
            output_dir: Output directory for coverage reports

        Returns:
            CoverageToolRunner instance or None if tool not supported
        """
        runner_class = CoverageToolRunnerFactory.RUNNERS.get(tool_type)
        if runner_class:
            return runner_class(repo_path, output_dir)
        return None

    @staticmethod
    def get_supported_tools() -> List[str]:
        """Get list of supported tools"""
        return list(CoverageToolRunnerFactory.RUNNERS.keys())
