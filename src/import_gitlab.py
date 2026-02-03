#!/usr/bin/env python3
"""
GitLab Project Importer for DORA Metrics
Imports projects from GitLab instances and adds them to the DORA configuration.
"""

import os
import sys
import json
import yaml
import argparse
from typing import List, Dict, Optional
import urllib.request
import urllib.parse

class GitLabImporter:
    def __init__(self, gitlab_url: str, token: Optional[str] = None):
        """
        Initialize GitLab importer.

        Args:
            gitlab_url: Base URL of GitLab instance (e.g., https://git.ecd.axway.org)
            token: Personal access token for authentication (optional for public projects)
        """
        self.gitlab_url = gitlab_url.rstrip('/')
        self.token = token or os.getenv('GITLAB_TOKEN')
        self.api_url = f"{self.gitlab_url}/api/v4"

    def _make_request(self, endpoint: str, debug: bool = False) -> Optional[Dict]:
        """
        Make authenticated request to GitLab API.

        Args:
            endpoint: API endpoint (without base URL)
            debug: Print debug information

        Returns:
            Parsed JSON response or None if request fails
        """
        url = f"{self.api_url}{endpoint}"
        headers = {}

        if self.token:
            headers['PRIVATE-TOKEN'] = self.token

        if debug:
            print(f"  📡 GET {endpoint}")

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                if debug and isinstance(data, list):
                    print(f"  ✓ Got {len(data)} items")
                return data
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print(f"❌ Authentication failed. Check your GITLAB_TOKEN.")
                return None
            elif e.code == 404:
                if debug:
                    print(f"  ✗ Not found")
                return None
            else:
                print(f"❌ GitLab API error: {e.code}")
                if debug:
                    print(f"  URL: {url}")
                return None
        except Exception as e:
            print(f"❌ Error making request: {e}")
            if debug:
                print(f"  URL: {url}")
            return None

    def get_user_projects(self, username: str) -> List[Dict]:
        """
        Get all projects for a user.

        Args:
            username: GitLab username

        Returns:
            List of project dictionaries
        """
        # Try to get user ID first
        user_data = self._make_request(f"/users?username={username}")
        if not user_data or len(user_data) == 0:
            print(f"❌ User '{username}' not found")
            return []

        user_id = user_data[0]['id']
        print(f"✅ Found user: {username} (ID: {user_id})")

        # Get projects for this user - try multiple approaches
        projects = []

        # Approach 1: Get all projects and filter by user
        print(f"🔍 Searching for projects owned by {username}...")
        page = 1
        while True:
            endpoint = f"/projects?owned=true&archived=false&per_page=100&page={page}"
            page_projects = self._make_request(endpoint)

            if not page_projects:
                break

            if len(page_projects) == 0:
                break

            # Filter to only this user's projects
            user_projects = [p for p in page_projects if p.get('owner', {}).get('username') == username or p.get('creator_id') == user_id]
            projects.extend(user_projects)
            page += 1

        # If no projects found, try the direct user endpoint
        if not projects:
            print(f"📋 Trying direct user endpoint...")
            page = 1
            while True:
                endpoint = f"/users/{user_id}/projects?per_page=100&page={page}&archived=false"
                page_projects = self._make_request(endpoint)

                if not page_projects:
                    break

                if len(page_projects) == 0:
                    break

                projects.extend(page_projects)
                page += 1

        return projects

    def project_to_repo_config(self, project: Dict, language: Optional[str] = None,
                              ci_system: str = "github-actions",
                              coverage_tools: Optional[List[Dict]] = None) -> Dict:
        """
        Convert GitLab project to DORA repo configuration.

        Args:
            project: GitLab project data
            language: Programming language (auto-detected if None)
            ci_system: CI system type
            coverage_tools: List of coverage tools

        Returns:
            Repo configuration dictionary
        """
        if coverage_tools is None:
            coverage_tools = []

        return {
            'repo': project['http_url_to_repo'],
            'branch': project.get('default_branch', 'main'),
            'language': language or self._detect_language(project.get('description', '')),
            'ci_system': ci_system,
            'coverage_tools': coverage_tools,
            'artifact_patterns': {
                'epics': {
                    'local_patterns': [
                        {
                            'file': '**/docs/**/*.md',
                            'regex': 'Epic\\s+(\\d+):\\s*(.+)'
                        }
                    ]
                },
                'stories': {
                    'local_patterns': [
                        {
                            'file': '**/docs/**/*.md',
                            'regex': 'US(\\d+\\.\\d+)'
                        }
                    ]
                }
            }
        }

    def _detect_language(self, description: str) -> str:
        """Detect language from project description."""
        description_lower = description.lower()
        if 'python' in description_lower:
            return 'python'
        elif 'java' in description_lower:
            return 'java'
        elif 'typescript' in description_lower or 'typescript' in description_lower:
            return 'typescript'
        elif 'javascript' in description_lower or 'node' in description_lower:
            return 'javascript'
        elif 'go' in description_lower:
            return 'go'
        else:
            return 'mixed'

    def import_projects(self, username: str, repo_config_file: str = 'repos.yaml') -> bool:
        """
        Import projects from GitLab user.

        Args:
            username: GitLab username
            repo_config_file: Path to repos.yaml file

        Returns:
            True if successful, False otherwise
        """
        projects = self.get_user_projects(username)

        if not projects:
            print("❌ No projects found")
            return False

        print(f"\n✅ Found {len(projects)} projects:\n")
        for proj in projects:
            print(f"  • {proj['name']} ({proj['path_with_namespace']})")

        # Load existing config
        if os.path.exists(repo_config_file):
            with open(repo_config_file, 'r') as f:
                config = yaml.safe_load(f)
        else:
            config = {'repositories': {}}

        if 'repositories' not in config:
            config['repositories'] = {}

        # Add projects to config
        added = 0
        for proj in projects:
            repo_name = proj['name']

            if repo_name in config['repositories']:
                print(f"⚠️  {repo_name} already in config, skipping")
                continue

            # Create config for this project
            config['repositories'][repo_name] = self.project_to_repo_config(proj)
            added += 1
            print(f"✅ Added {repo_name}")

        # Save updated config
        with open(repo_config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        print(f"\n✅ Updated {repo_config_file} with {added} new projects")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Import GitLab projects into DORA configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import public projects
  python src/import_gitlab.py --gitlab-url https://git.ecd.axway.org --username viionascu

  # Import with authentication
  GITLAB_TOKEN=your_token python src/import_gitlab.py --gitlab-url https://git.ecd.axway.org --username viionascu

  # Add specific project directly
  python src/import_gitlab.py --add-project https://git.ecd.axway.org/viionascu/my-project.git

  # List available projects for a user
  GITLAB_TOKEN=your_token python src/import_gitlab.py --gitlab-url https://git.ecd.axway.org --username viionascu --list-only
        """
    )

    parser.add_argument('--gitlab-url', default='https://git.ecd.axway.org',
                       help='GitLab instance URL (default: https://git.ecd.axway.org)')
    parser.add_argument('--username',
                       help='GitLab username')
    parser.add_argument('--token', help='GitLab personal access token (or use GITLAB_TOKEN env var)')
    parser.add_argument('--config', default='repos.yaml',
                       help='Path to repos.yaml configuration file')
    parser.add_argument('--add-project', help='Add a specific GitLab project by URL')
    parser.add_argument('--list-only', action='store_true',
                       help='List projects without importing')

    args = parser.parse_args()

    # Handle direct project addition
    if args.add_project:
        importer = GitLabImporter(args.gitlab_url, args.token)
        # Parse project name from URL
        project_url = args.add_project.rstrip('/')
        project_name = project_url.split('/')[-1].replace('.git', '')

        # Load config
        if os.path.exists(args.config):
            with open(args.config, 'r') as f:
                config = yaml.safe_load(f)
        else:
            config = {'repositories': {}}

        if 'repositories' not in config:
            config['repositories'] = {}

        # Add project
        config['repositories'][project_name] = {
            'repo': args.add_project,
            'branch': 'main',
            'language': 'mixed',
            'ci_system': 'github-actions',
            'coverage_tools': [],
            'artifact_patterns': {
                'epics': {
                    'local_patterns': [
                        {
                            'file': '**/docs/**/*.md',
                            'regex': 'Epic\\s+(\\d+):\\s*(.+)'
                        }
                    ]
                },
                'stories': {
                    'local_patterns': [
                        {
                            'file': '**/docs/**/*.md',
                            'regex': 'US(\\d+\\.\\d+)'
                        }
                    ]
                }
            }
        }

        # Save config
        with open(args.config, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        print(f"✅ Added project: {project_name}")
        print(f"   URL: {args.add_project}")
        print(f"   Config: {args.config}")
        sys.exit(0)

    # Handle user-based import
    if not args.username:
        parser.error('Either --username or --add-project is required')
        sys.exit(1)

    importer = GitLabImporter(args.gitlab_url, args.token)

    if args.list_only:
        projects = importer.get_user_projects(args.username)
        if projects:
            print(f"\n✅ Found {len(projects)} projects:\n")
            for p in projects:
                print(f"  • {p['name']}")
                print(f"    URL: {p['http_url_to_repo']}")
                print()
        sys.exit(0)

    success = importer.import_projects(args.username, args.config)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
