#!/usr/bin/env python3
"""
Configuration parser for DORA projects
Reads and validates YAML/JSON configuration files
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from src.config.schema import RepoConfig, ConfigValidator


class RepoConfigParser:
    """Parses and validates repository configuration"""

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize parser

        Args:
            config_file: Path to repos.yaml or repos.json. If None, looks for repos.yaml in root
        """
        self.config_file = config_file
        self._config_data = None
        self._parsed_repos = None

    def _find_config_file(self) -> Path:
        """Find config file if not explicitly provided"""
        search_paths = [
            Path('repos.yaml'),
            Path('repos.yml'),
            Path('repos.json'),
            Path('config/repos.yaml'),
        ]

        for path in search_paths:
            if path.exists():
                return path

        raise FileNotFoundError("No configuration file found. Expected repos.yaml, repos.yml, or repos.json")

    def _load_yaml(self, file_path: Path) -> Dict:
        """Load YAML configuration file"""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                if data is None:
                    raise ValueError("Configuration file is empty")
                return data
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML file: {str(e)}")

    def _load_json(self, file_path: Path) -> Dict:
        """Load JSON configuration file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON file: {str(e)}")

    def load_config(self) -> Tuple[bool, List[str]]:
        """
        Load and validate configuration file

        Returns:
            Tuple of (is_valid, errors)
        """
        try:
            config_file = self.config_file or self._find_config_file()

            if not config_file.exists():
                return False, [f"Configuration file not found: {config_file}"]

            # Load based on file extension
            if config_file.suffix.lower() in {'.yaml', '.yml'}:
                self._config_data = self._load_yaml(config_file)
            elif config_file.suffix.lower() == '.json':
                self._config_data = self._load_json(config_file)
            else:
                return False, [f"Unsupported configuration file format: {config_file.suffix}"]

            # Validate loaded config
            is_valid, errors = ConfigValidator.validate_config(self._config_data)

            if is_valid:
                self._parse_repos()

            return is_valid, errors

        except Exception as e:
            return False, [f"Error loading configuration: {str(e)}"]

    def _parse_repos(self):
        """Parse repositories from loaded configuration"""
        if not self._config_data:
            raise RuntimeError("Configuration not loaded. Call load_config() first.")

        self._parsed_repos = {}
        for repo_name, repo_data in self._config_data.get('repositories', {}).items():
            coverage_tools = []
            if 'coverage_tools' in repo_data:
                for tool_data in repo_data['coverage_tools']:
                    if isinstance(tool_data, str):
                        coverage_tools.append({'type': tool_data})
                    elif isinstance(tool_data, dict):
                        coverage_tools.append(tool_data)

            self._parsed_repos[repo_name] = RepoConfig(
                name=repo_name,
                repo=repo_data.get('repo', ''),
                branch=repo_data.get('branch', 'main'),
                language=repo_data.get('language', 'unknown'),
                ci_system=repo_data.get('ci_system', 'github-actions'),
                coverage_tools=repo_data.get('coverage_tools', []),
                jira=repo_data.get('jira'),
                artifact_patterns=repo_data.get('artifact_patterns')
            )

    def parse(self) -> Dict[str, Dict]:
        """
        Parse and return configuration as simple dictionaries

        Returns:
            Dictionary of repository configurations
        """
        if not self._config_data:
            raise RuntimeError("Configuration not loaded. Call load_config() first.")

        return self._config_data.get('repositories', {})

    def get_repo(self, repo_name: str) -> Optional[Dict]:
        """
        Get configuration for a specific repository

        Args:
            repo_name: Name of the repository

        Returns:
            Repository configuration dictionary or None
        """
        if not self._config_data:
            raise RuntimeError("Configuration not loaded. Call load_config() first.")

        return self._config_data.get('repositories', {}).get(repo_name)

    def get_all_repos(self) -> Dict[str, Dict]:
        """Get all repository configurations"""
        if not self._config_data:
            raise RuntimeError("Configuration not loaded. Call load_config() first.")

        return self._config_data.get('repositories', {})

    def get_repo_url(self, repo_name: str) -> Optional[str]:
        """Get repository URL"""
        repo_config = self.get_repo(repo_name)
        return repo_config.get('repo') if repo_config else None

    def get_repo_branch(self, repo_name: str, default: str = 'main') -> str:
        """Get repository branch"""
        repo_config = self.get_repo(repo_name)
        return repo_config.get('branch', default) if repo_config else default

    def get_repo_language(self, repo_name: str) -> str:
        """Get repository primary language"""
        repo_config = self.get_repo(repo_name)
        return repo_config.get('language', 'unknown') if repo_config else 'unknown'

    def get_coverage_tools(self, repo_name: str) -> List[Dict]:
        """Get coverage tools for a repository"""
        repo_config = self.get_repo(repo_name)
        if not repo_config:
            return []

        tools = repo_config.get('coverage_tools', [])
        # Normalize to list of dicts
        normalized = []
        for tool in tools:
            if isinstance(tool, str):
                normalized.append({'type': tool})
            elif isinstance(tool, dict):
                normalized.append(tool)
        return normalized

    def has_jira_integration(self, repo_name: str) -> bool:
        """Check if repository has Jira integration enabled"""
        repo_config = self.get_repo(repo_name)
        if not repo_config or 'jira' not in repo_config:
            return False

        jira_config = repo_config.get('jira', {})
        return jira_config.get('enabled', False)

    def get_jira_config(self, repo_name: str) -> Optional[Dict]:
        """Get Jira configuration for a repository"""
        repo_config = self.get_repo(repo_name)
        return repo_config.get('jira') if repo_config else None
