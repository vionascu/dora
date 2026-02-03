#!/usr/bin/env python3
"""
Memory-efficient Git log processor
Streams commits instead of loading all into memory
"""

import subprocess
import json
from pathlib import Path
from typing import Iterator, Dict, Set, Tuple, Optional
from datetime import datetime


class GitCommit:
    """Represents a single git commit"""

    def __init__(self, hash: str, timestamp: str, author_name: str, author_email: str, subject: str):
        self.hash = hash
        self.timestamp = timestamp
        self.author_name = author_name
        self.author_email = author_email
        self.subject = subject

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "hash": self.hash,
            "timestamp": self.timestamp,
            "author_name": self.author_name,
            "author_email": self.author_email,
            "subject": self.subject
        }


class GitLogStats:
    """Accumulates statistics while streaming commits"""

    def __init__(self):
        self.total_commits = 0
        self.authors: Set[str] = set()
        self.first_date: Optional[str] = None
        self.last_date: Optional[str] = None

    def process_commit(self, commit: GitCommit):
        """Process a single commit and update stats"""
        self.total_commits += 1
        self.authors.add(commit.author_email)

        # Extract date from timestamp (format: 2025-02-03 12:34:56 +0000)
        date = commit.timestamp.split(' ')[0]

        if self.first_date is None or date < self.first_date:
            self.first_date = date
        if self.last_date is None or date > self.last_date:
            self.last_date = date

    def to_dict(self) -> Dict:
        """Convert stats to dictionary"""
        return {
            "total_commits": self.total_commits,
            "unique_authors": len(self.authors),
            "authors": sorted(list(self.authors)),
            "first_commit": self.first_date,
            "last_commit": self.last_date
        }


class GitLogProcessor:
    """Streams git commits without loading all into memory"""

    def __init__(self, clone_path: Path):
        """
        Initialize processor

        Args:
            clone_path: Path to cloned repository
        """
        self.clone_path = Path(clone_path)

    def _parse_commit_line_block(self, lines: list, start_idx: int) -> Tuple[Optional[GitCommit], int]:
        """
        Parse a single commit block from git log output

        Format (from git log --format=%H%n%ai%n%an%n%ae%n%s%n--END--):
        - hash
        - timestamp
        - author_name
        - author_email
        - subject
        - --END--

        Args:
            lines: All lines from git log output
            start_idx: Current index in lines array

        Returns:
            Tuple of (GitCommit or None, next_index)
        """
        if start_idx >= len(lines):
            return None, start_idx

        # Skip empty lines
        while start_idx < len(lines) and lines[start_idx].strip() == '':
            start_idx += 1

        if start_idx >= len(lines):
            return None, start_idx

        # Check if we're at an END marker
        if lines[start_idx] == '--END--':
            return None, start_idx + 1

        # We need at least 6 lines: hash, timestamp, author_name, author_email, subject, --END--
        if start_idx + 5 >= len(lines):
            return None, start_idx

        try:
            hash_val = lines[start_idx]
            timestamp = lines[start_idx + 1]
            author_name = lines[start_idx + 2]
            author_email = lines[start_idx + 3]
            subject = lines[start_idx + 4]
            end_marker = lines[start_idx + 5]

            if end_marker != '--END--':
                return None, start_idx + 1

            commit = GitCommit(hash_val, timestamp, author_name, author_email, subject)
            return commit, start_idx + 6

        except (IndexError, ValueError):
            return None, start_idx + 1

    def stream_commits(self) -> Iterator[GitCommit]:
        """
        Stream commits from git log without loading all into memory

        Yields:
            GitCommit objects one at a time

        Raises:
            subprocess.CalledProcessError: If git log fails
        """
        try:
            process = subprocess.Popen(
                ["git", "log", "--all", "--format=%H%n%ai%n%an%n%ae%n%s%n--END--"],
                cwd=self.clone_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Read output line by line
            lines = []
            batch_size = 1000  # Process in batches
            idx = 0

            for line in iter(process.stdout.readline, ''):
                lines.append(line.rstrip('\n'))

                # Process batch when we have enough lines
                if len(lines) >= batch_size:
                    while idx < len(lines):
                        commit, next_idx = self._parse_commit_line_block(lines, idx)
                        if commit is None and next_idx == idx:
                            break
                        if commit:
                            yield commit
                        idx = next_idx

                    # Keep unprocessed lines
                    lines = lines[idx:]
                    idx = 0

            # Process remaining lines
            while idx < len(lines):
                commit, next_idx = self._parse_commit_line_block(lines, idx)
                if commit is None and next_idx == idx:
                    break
                if commit:
                    yield commit
                idx = next_idx

            process.wait()

            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode,
                    "git log",
                    stderr=process.stderr.read() if process.stderr else ""
                )

        except subprocess.CalledProcessError as e:
            raise subprocess.CalledProcessError(
                e.returncode,
                e.cmd,
                stderr=e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr
            )

    def calculate_stats(self) -> GitLogStats:
        """
        Calculate statistics by streaming commits

        Returns:
            GitLogStats object with aggregated statistics
        """
        stats = GitLogStats()

        for commit in self.stream_commits():
            stats.process_commit(commit)

        return stats

    def save_commits_ndjson(self, output_path: Path, limit: Optional[int] = None):
        """
        Save commits to NDJSON format (newline-delimited JSON)
        More memory-efficient than full JSON array

        Args:
            output_path: Path to output file
            limit: Maximum number of commits to save (None = all)
        """
        count = 0

        with open(output_path, 'w') as f:
            for commit in self.stream_commits():
                f.write(json.dumps(commit.to_dict()) + '\n')
                count += 1

                if limit and count >= limit:
                    break

    def save_commits_json(self, output_path: Path, limit: Optional[int] = None):
        """
        Save commits to standard JSON array format
        WARNING: Only use for small repositories

        Args:
            output_path: Path to output file
            limit: Maximum number of commits to save (None = all)
        """
        commits = []
        count = 0

        for commit in self.stream_commits():
            commits.append(commit.to_dict())
            count += 1

            if limit and count >= limit:
                break

        with open(output_path, 'w') as f:
            json.dump({
                "metric_id": "git.commits.raw",
                "total_commits": len(commits),
                "commits": commits,
                "collected_at": datetime.now().isoformat()
            }, f, indent=2)

    def save_stats(self, output_path: Path):
        """
        Save commit statistics to JSON

        Args:
            output_path: Path to output file
        """
        stats = self.calculate_stats()

        stats_dict = stats.to_dict()
        stats_dict.update({
            "metric_id": "git.stats.raw",
            "collected_at": datetime.now().isoformat()
        })

        with open(output_path, 'w') as f:
            json.dump(stats_dict, f, indent=2)
