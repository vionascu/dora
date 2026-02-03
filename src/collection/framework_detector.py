#!/usr/bin/env python3
"""
Test framework and coverage tool detection
Auto-detects test frameworks and coverage tools from project configuration
"""

import xml.etree.ElementTree as ET
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class FrameworkDetector:
    """Detects test frameworks and coverage tools from project configuration"""

    @staticmethod
    def detect_java_framework(repo_path: Path) -> Tuple[Optional[str], Optional[str]]:
        """
        Detect Java test framework and coverage tool

        Args:
            repo_path: Path to repository

        Returns:
            Tuple of (test_framework, coverage_tool)
        """
        test_framework = None
        coverage_tool = None

        # Check Maven pom.xml
        pom_files = list(repo_path.rglob("pom.xml"))
        pom_files = [p for p in pom_files if ".git" not in str(p)]

        for pom_file in pom_files:
            try:
                tree = ET.parse(pom_file)
                root = tree.getroot()

                # Get namespace
                ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

                # Check for JUnit
                junit_deps = root.findall(".//m:groupId[text()='junit']", ns)
                if not junit_deps:
                    junit_deps = root.findall(".//groupId[text()='junit']")
                if junit_deps:
                    test_framework = "JUnit"

                # Check for TestNG
                testng_deps = root.findall(".//m:artifactId[text()='testng']", ns)
                if not testng_deps:
                    testng_deps = root.findall(".//artifactId[text()='testng']")
                if testng_deps:
                    test_framework = "TestNG"

                # Check for JaCoCo
                jacoco_plugins = root.findall(".//m:artifactId[text()='jacoco-maven-plugin']", ns)
                if not jacoco_plugins:
                    jacoco_plugins = root.findall(".//artifactId[text()='jacoco-maven-plugin']")
                if jacoco_plugins:
                    coverage_tool = "jacoco"

                # Check for Cobertura
                cobertura_plugins = root.findall(".//m:artifactId[text()='cobertura-maven-plugin']", ns)
                if not cobertura_plugins:
                    cobertura_plugins = root.findall(".//artifactId[text()='cobertura-maven-plugin']")
                if cobertura_plugins:
                    coverage_tool = "cobertura"

            except Exception:
                pass

        # Check Gradle build.gradle or build.gradle.kts
        gradle_files = list(repo_path.rglob("build.gradle"))
        gradle_files.extend(list(repo_path.rglob("build.gradle.kts")))
        gradle_files = [f for f in gradle_files if ".git" not in str(f)]

        for gradle_file in gradle_files:
            try:
                with open(gradle_file, 'r', errors='ignore') as f:
                    content = f.read()

                # Check for JUnit
                if 'org.junit' in content or 'junit' in content.lower():
                    test_framework = "JUnit"

                # Check for TestNG
                if 'org.testng' in content:
                    test_framework = "TestNG"

                # Check for Spock
                if 'spock' in content.lower():
                    test_framework = "Spock"

                # Check for JaCoCo
                if 'jacoco' in content.lower():
                    coverage_tool = "jacoco"

                # Check for Cobertura
                if 'cobertura' in content.lower():
                    coverage_tool = "cobertura"

            except Exception:
                pass

        if not test_framework:
            test_framework = "JUnit"  # Default for Java
        if not coverage_tool:
            coverage_tool = "jacoco"  # Default for Java

        return test_framework, coverage_tool

    @staticmethod
    def detect_python_framework(repo_path: Path) -> Tuple[Optional[str], Optional[str]]:
        """
        Detect Python test framework and coverage tool

        Args:
            repo_path: Path to repository

        Returns:
            Tuple of (test_framework, coverage_tool)
        """
        test_framework = None
        coverage_tool = None

        requirements_files = [
            repo_path / "requirements.txt",
            repo_path / "requirements-dev.txt",
            repo_path / "setup.py",
            repo_path / "pyproject.toml"
        ]

        for req_file in requirements_files:
            if not req_file.exists():
                continue

            try:
                with open(req_file, 'r', errors='ignore') as f:
                    content = f.read().lower()

                # Check for test frameworks
                if 'pytest' in content:
                    test_framework = "pytest"
                elif 'unittest' in content:
                    test_framework = "unittest"
                elif 'nose' in content:
                    test_framework = "nose"

                # Check for coverage tools
                if 'pytest-cov' in content or 'coverage' in content:
                    coverage_tool = "pytest-cov"
                elif 'nose' in content and 'coverage' in content:
                    coverage_tool = "coverage"

            except Exception:
                pass

        if not test_framework:
            test_framework = "pytest"  # Default for Python
        if not coverage_tool:
            coverage_tool = "pytest-cov"  # Default for Python

        return test_framework, coverage_tool

    @staticmethod
    def detect_javascript_framework(repo_path: Path) -> Tuple[Optional[str], Optional[str]]:
        """
        Detect JavaScript test framework and coverage tool

        Args:
            repo_path: Path to repository

        Returns:
            Tuple of (test_framework, coverage_tool)
        """
        test_framework = None
        coverage_tool = None

        package_files = list(repo_path.rglob("package.json"))
        package_files = [f for f in package_files if ".git" not in str(f) and "node_modules" not in str(f)]

        for package_file in package_files:
            try:
                with open(package_file, 'r') as f:
                    package_data = json.load(f)

                dev_deps = package_data.get('devDependencies', {})
                deps = package_data.get('dependencies', {})
                all_deps = {**dev_deps, **deps}

                # Check for test frameworks
                if 'jest' in all_deps:
                    test_framework = "Jest"
                    coverage_tool = "lcov"  # Jest uses LCOV by default
                elif 'mocha' in all_deps:
                    test_framework = "Mocha"
                elif 'vitest' in all_deps:
                    test_framework = "Vitest"

                # Check for coverage tools
                if 'nyc' in all_deps:
                    coverage_tool = "nyc"
                elif 'istanbul' in all_deps:
                    coverage_tool = "istanbul"

            except Exception:
                pass

        if not test_framework:
            test_framework = "Jest"  # Default for JavaScript
        if not coverage_tool:
            coverage_tool = "lcov"  # Default for JavaScript

        return test_framework, coverage_tool

    @staticmethod
    def detect_go_framework(repo_path: Path) -> Tuple[Optional[str], Optional[str]]:
        """
        Detect Go test framework and coverage tool

        Args:
            repo_path: Path to repository

        Returns:
            Tuple of (test_framework, coverage_tool)
        """
        # Go has built-in testing, coverage is standard
        return "Go testing", "go cover"

    @staticmethod
    def detect_test_framework(repo_path: Path, language: str) -> Optional[str]:
        """
        Detect test framework for a given language

        Args:
            repo_path: Path to repository
            language: Programming language

        Returns:
            Name of detected test framework, or None
        """
        if language == "java":
            framework, _ = FrameworkDetector.detect_java_framework(repo_path)
            return framework
        elif language == "python":
            framework, _ = FrameworkDetector.detect_python_framework(repo_path)
            return framework
        elif language == "javascript":
            framework, _ = FrameworkDetector.detect_javascript_framework(repo_path)
            return framework
        elif language == "go":
            framework, _ = FrameworkDetector.detect_go_framework(repo_path)
            return framework
        else:
            return None

    @staticmethod
    def detect_coverage_tool(repo_path: Path, language: str) -> Optional[str]:
        """
        Detect coverage tool for a given language

        Args:
            repo_path: Path to repository
            language: Programming language

        Returns:
            Name of detected coverage tool, or None
        """
        if language == "java":
            _, tool = FrameworkDetector.detect_java_framework(repo_path)
            return tool
        elif language == "python":
            _, tool = FrameworkDetector.detect_python_framework(repo_path)
            return tool
        elif language == "javascript":
            _, tool = FrameworkDetector.detect_javascript_framework(repo_path)
            return tool
        elif language == "go":
            _, tool = FrameworkDetector.detect_go_framework(repo_path)
            return tool
        else:
            return None

    @staticmethod
    def detect_all(repo_path: Path, language: str) -> Dict[str, Optional[str]]:
        """
        Detect all framework and coverage information

        Args:
            repo_path: Path to repository
            language: Programming language

        Returns:
            Dictionary with detected frameworks and tools
        """
        if language == "java":
            test_fw, coverage = FrameworkDetector.detect_java_framework(repo_path)
        elif language == "python":
            test_fw, coverage = FrameworkDetector.detect_python_framework(repo_path)
        elif language == "javascript":
            test_fw, coverage = FrameworkDetector.detect_javascript_framework(repo_path)
        elif language == "go":
            test_fw, coverage = FrameworkDetector.detect_go_framework(repo_path)
        else:
            test_fw, coverage = None, None

        return {
            "test_framework": test_fw,
            "coverage_tool": coverage,
            "language": language
        }
