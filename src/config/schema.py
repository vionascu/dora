#!/usr/bin/env python3
"""
Configuration schema validation for DORA projects
Provides validation for repos configuration
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class CoverageTool:
    """Coverage tool configuration"""
    type: str  # 'jacoco', 'lcov', 'pytest-cov', 'cobertura'
    config: Dict = field(default_factory=dict)
    minimum_threshold: Optional[float] = None

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate coverage tool config"""
        errors = []
        valid_types = {'jacoco', 'lcov', 'pytest-cov', 'cobertura', 'coverage', 'codecov'}

        if self.type not in valid_types:
            errors.append(f"Invalid coverage tool type: {self.type}. Must be one of {valid_types}")

        if self.minimum_threshold is not None:
            if not 0 <= self.minimum_threshold <= 100:
                errors.append(f"minimum_threshold must be between 0-100, got {self.minimum_threshold}")

        return len(errors) == 0, errors


@dataclass
class JiraConfig:
    """Jira integration configuration"""
    enabled: bool = False
    base_url: Optional[str] = None
    project_key: Optional[str] = None
    auth_type: str = "api_key"  # 'api_key', 'oauth', 'basic'
    api_key_env: Optional[str] = None

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate Jira config"""
        errors = []

        if self.enabled:
            if not self.base_url:
                errors.append("Jira enabled but base_url not provided")
            if not self.project_key:
                errors.append("Jira enabled but project_key not provided")
            if self.auth_type not in {'api_key', 'oauth', 'basic'}:
                errors.append(f"Invalid auth_type: {self.auth_type}")

        return len(errors) == 0, errors


@dataclass
class ArtifactPattern:
    """Artifact detection pattern"""
    file: str  # File glob pattern
    regex: str  # Regex pattern to extract artifact
    description: Optional[str] = None

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate pattern"""
        errors = []

        if not self.file:
            errors.append("Artifact pattern file must be specified")
        if not self.regex:
            errors.append("Artifact pattern regex must be specified")

        return len(errors) == 0, errors


@dataclass
class RepoConfig:
    """Repository configuration"""
    name: str
    repo: str  # Repository URL
    branch: str = "main"
    language: str = "unknown"  # 'java', 'python', 'javascript', 'go', 'mixed'
    ci_system: str = "github-actions"  # 'github-actions', 'jenkins', 'circleci'
    coverage_tools: List[CoverageTool] = field(default_factory=list)
    jira: Optional[JiraConfig] = None
    artifact_patterns: Optional[Dict] = None

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate repository configuration"""
        errors = []

        # Required fields
        if not self.name:
            errors.append("Repository name is required")
        if not self.repo:
            errors.append("Repository URL is required")
        if not self.repo.startswith(('http://', 'https://', 'git@')):
            errors.append(f"Invalid repository URL: {self.repo}")

        # Valid languages
        valid_languages = {'java', 'python', 'javascript', 'go', 'rust', 'mixed', 'unknown'}
        if self.language not in valid_languages:
            errors.append(f"Invalid language: {self.language}. Must be one of {valid_languages}")

        # Valid CI systems
        valid_ci = {'github-actions', 'jenkins', 'circleci', 'gitlab-ci', 'unknown'}
        if self.ci_system not in valid_ci:
            errors.append(f"Invalid CI system: {self.ci_system}. Must be one of {valid_ci}")

        # Validate coverage tools
        for tool in self.coverage_tools:
            valid, tool_errors = tool.validate()
            errors.extend(tool_errors)

        # Validate Jira if present
        if self.jira:
            valid, jira_errors = self.jira.validate()
            errors.extend(jira_errors)

        return len(errors) == 0, errors


@dataclass
class Config:
    """Root configuration"""
    repositories: Dict[str, RepoConfig]
    schema_version: str = "1.0"

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate entire configuration"""
        errors = []

        if not self.repositories:
            errors.append("No repositories defined in configuration")

        for repo_name, repo_config in self.repositories.items():
            valid, repo_errors = repo_config.validate()
            if not valid:
                errors.append(f"Repository '{repo_name}' validation errors: {repo_errors}")

        return len(errors) == 0, errors


class ConfigValidator:
    """Validates configuration against schema"""

    @staticmethod
    def validate_config(config: Dict) -> Tuple[bool, List[str]]:
        """
        Validate configuration dictionary

        Args:
            config: Configuration dictionary (typically from YAML)

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        # Check root structure
        if 'repositories' not in config:
            errors.append("Configuration must have 'repositories' key")
            return False, errors

        if not isinstance(config['repositories'], dict):
            errors.append("'repositories' must be a dictionary")
            return False, errors

        # Parse repositories
        repo_configs = {}
        for repo_name, repo_data in config['repositories'].items():
            try:
                coverage_tools = []
                if 'coverage_tools' in repo_data:
                    for tool_data in repo_data['coverage_tools']:
                        if isinstance(tool_data, str):
                            coverage_tools.append(CoverageTool(type=tool_data))
                        elif isinstance(tool_data, dict):
                            coverage_tools.append(CoverageTool(**tool_data))

                jira_data = None
                if 'jira' in repo_data:
                    jira_data = JiraConfig(**repo_data['jira'])

                repo_config = RepoConfig(
                    name=repo_name,
                    repo=repo_data.get('repo', ''),
                    branch=repo_data.get('branch', 'main'),
                    language=repo_data.get('language', 'unknown'),
                    ci_system=repo_data.get('ci_system', 'github-actions'),
                    coverage_tools=coverage_tools,
                    jira=jira_data,
                    artifact_patterns=repo_data.get('artifact_patterns')
                )

                valid, repo_errors = repo_config.validate()
                if not valid:
                    errors.extend([f"{repo_name}: {err}" for err in repo_errors])
                else:
                    repo_configs[repo_name] = repo_config

            except Exception as e:
                errors.append(f"Failed to parse repository '{repo_name}': {str(e)}")

        root_config = Config(repositories=repo_configs)
        valid, root_errors = root_config.validate()
        errors.extend(root_errors)

        return len(errors) == 0, errors
