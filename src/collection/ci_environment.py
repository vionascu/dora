#!/usr/bin/env python3
"""
CI Environment validation and detection
Checks for required tools and services
"""

import subprocess
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class EnvironmentCheckResult:
    """Result of an environment check"""
    name: str
    installed: bool
    version: Optional[str] = None
    path: Optional[str] = None
    error: Optional[str] = None


@dataclass
class EnvironmentReport:
    """Full environment report"""
    available_tools: Dict[str, EnvironmentCheckResult] = field(default_factory=dict)
    missing_tools: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    is_valid: bool = True

    def get_status_string(self) -> str:
        """Get human-readable status"""
        if self.is_valid:
            return "valid"
        elif self.missing_tools:
            return "missing_dependencies"
        else:
            return "warnings"


class CIEnvironmentValidator:
    """Validates CI environment for test execution"""

    # Define tool checks: tool_name -> (command, version_flag, version_pattern)
    TOOLS = {
        'java': (['java', '-version'], '-version', None),
        'javac': (['javac', '-version'], '-version', None),
        'maven': (['mvn', '-version'], '-version', None),
        'gradle': (['./gradlew', '--version'], '--version', None),
        'python3': (['python3', '--version'], '--version', None),
        'pip': (['pip', '--version'], '--version', None),
        'npm': (['npm', '--version'], '--version', None),
        'node': (['node', '--version'], '--version', None),
        'go': (['go', 'version'], 'version', None),
        'docker': (['docker', '--version'], '--version', None),
        'git': (['git', '--version'], '--version', None),
    }

    # Define required tools by language
    LANGUAGE_REQUIREMENTS = {
        'java': {
            'required': ['java', 'mvn'],
            'optional': ['gradle', 'docker']
        },
        'python': {
            'required': ['python3', 'pip'],
            'optional': ['docker']
        },
        'javascript': {
            'required': ['node', 'npm'],
            'optional': ['docker']
        },
        'go': {
            'required': ['go'],
            'optional': ['docker']
        },
        'mixed': {
            'required': ['java', 'python3', 'node'],
            'optional': ['mvn', 'npm', 'docker']
        }
    }

    @staticmethod
    def check_tool(tool_name: str) -> EnvironmentCheckResult:
        """
        Check if a tool is installed and get its version

        Args:
            tool_name: Name of tool to check

        Returns:
            EnvironmentCheckResult with installation status and version
        """
        if tool_name not in CIEnvironmentValidator.TOOLS:
            return EnvironmentCheckResult(name=tool_name, installed=False, error="Unknown tool")

        command, version_flag, version_pattern = CIEnvironmentValidator.TOOLS[tool_name]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                timeout=5,
                text=True
            )

            if result.returncode == 0:
                # Extract version from output
                output = result.stdout + result.stderr
                version = CIEnvironmentValidator._extract_version(output)

                return EnvironmentCheckResult(
                    name=tool_name,
                    installed=True,
                    version=version,
                    path=command[0]
                )
            else:
                return EnvironmentCheckResult(
                    name=tool_name,
                    installed=False,
                    error=f"Exit code {result.returncode}"
                )

        except FileNotFoundError:
            return EnvironmentCheckResult(
                name=tool_name,
                installed=False,
                error="Not found in PATH"
            )
        except subprocess.TimeoutExpired:
            return EnvironmentCheckResult(
                name=tool_name,
                installed=False,
                error="Timeout"
            )
        except Exception as e:
            return EnvironmentCheckResult(
                name=tool_name,
                installed=False,
                error=str(e)
            )

    @staticmethod
    def _extract_version(output: str) -> Optional[str]:
        """Extract version string from command output"""
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            if 'version' in line.lower() or line and line[0].isdigit():
                return line
        return None

    @staticmethod
    def validate_language(language: str) -> EnvironmentReport:
        """
        Validate environment for a specific language

        Args:
            language: Programming language ('java', 'python', 'javascript', 'go', 'mixed')

        Returns:
            EnvironmentReport with validation results
        """
        report = EnvironmentReport()

        if language not in CIEnvironmentValidator.LANGUAGE_REQUIREMENTS:
            report.warnings.append(f"Unknown language: {language}")
            report.is_valid = False
            return report

        requirements = CIEnvironmentValidator.LANGUAGE_REQUIREMENTS[language]
        required_tools = requirements.get('required', [])
        optional_tools = requirements.get('optional', [])

        # Check required tools
        for tool in required_tools:
            result = CIEnvironmentValidator.check_tool(tool)
            report.available_tools[tool] = result

            if not result.installed:
                report.missing_tools.append(tool)
                report.is_valid = False
            else:
                print(f"    ✓ {tool}: {result.version or 'installed'}")

        # Check optional tools (warnings if missing)
        for tool in optional_tools:
            result = CIEnvironmentValidator.check_tool(tool)
            report.available_tools[tool] = result

            if not result.installed:
                report.warnings.append(f"Optional tool {tool} not found")
            else:
                print(f"    ✓ {tool}: {result.version or 'installed'}")

        return report

    @staticmethod
    def validate_coverage_tool(tool_type: str, language: str) -> EnvironmentReport:
        """
        Validate environment for a specific coverage tool

        Args:
            tool_type: Type of coverage tool ('jacoco', 'lcov', 'pytest-cov', etc.)
            language: Programming language for context

        Returns:
            EnvironmentReport with validation results
        """
        report = EnvironmentReport()

        coverage_tool_requirements = {
            'jacoco': {
                'language': 'java',
                'required': ['java', 'mvn'],
                'optional': ['gradle']
            },
            'lcov': {
                'language': 'javascript',
                'required': ['node', 'npm'],
                'optional': []
            },
            'pytest-cov': {
                'language': 'python',
                'required': ['python3'],
                'optional': []
            },
            'cobertura': {
                'language': 'java',
                'required': ['java'],
                'optional': ['mvn', 'gradle']
            },
            'coverage': {
                'language': 'python',
                'required': ['python3', 'pip'],
                'optional': []
            }
        }

        if tool_type not in coverage_tool_requirements:
            report.warnings.append(f"Unknown coverage tool: {tool_type}")
            return report

        requirements = coverage_tool_requirements[tool_type]

        # Check if tool matches language
        if language != 'unknown' and language != requirements['language']:
            report.warnings.append(
                f"Coverage tool {tool_type} for {requirements['language']}, "
                f"but language is {language}"
            )

        # Check required tools
        for tool in requirements.get('required', []):
            result = CIEnvironmentValidator.check_tool(tool)
            report.available_tools[tool] = result

            if not result.installed:
                report.missing_tools.append(tool)
                report.is_valid = False

        # Check optional tools
        for tool in requirements.get('optional', []):
            result = CIEnvironmentValidator.check_tool(tool)
            report.available_tools[tool] = result

            if not result.installed:
                report.warnings.append(f"Optional {tool} not found for {tool_type}")

        return report

    @staticmethod
    def check_service(service_name: str, port: Optional[int] = None) -> bool:
        """
        Check if a service is running

        Args:
            service_name: Name of service (e.g., 'postgres', 'redis', 'mysql')
            port: Optional port to check

        Returns:
            True if service is reachable, False otherwise
        """
        service_ports = {
            'postgres': 5432,
            'postgresql': 5432,
            'mysql': 3306,
            'redis': 6379,
            'mongodb': 27017,
            'elasticsearch': 9200,
        }

        check_port = port or service_ports.get(service_name.lower())

        if not check_port:
            return False

        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', check_port))
            sock.close()
            return result == 0
        except Exception:
            return False
