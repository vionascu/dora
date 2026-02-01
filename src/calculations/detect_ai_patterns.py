#!/usr/bin/env python3
"""
Advanced AI Usage Detection
Analyzes commit patterns to identify AI-assisted development
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class AIPatternDetector:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.git_artifacts = self.root_dir / "git_artifacts"
        self.calculations = self.root_dir / "calculations"

        # AI framework patterns
        self.ai_frameworks = {
            "Claude": [r"\bclaude\b", r"\banchropic\b"],
            "ChatGPT": [r"\bchatgpt\b", r"\bgpt-[0-9]", r"\bopenai\b", r"\bai-generated\b"],
            "GitHub Copilot": [r"\bcopilot\b", r"\bcodex\b"],
            "Gemini": [r"\bgemini\b", r"\bbard\b"],
            "Other LLM": [r"\bllm\b", r"\blarge\s+language\s+model\b"],
        }

        # Code pattern keywords
        self.pattern_keywords = {
            "bulk_updates": [r"\bbulk\b", r"\bmass\b", r"\bgenerated\b", r"\bauto\b"],
            "refactor": [r"\brefactor\b", r"\bcleanup\b", r"\breorg\b"],
            "optimization": [r"\boptimiz\b", r"\bperformance\b", r"\bspeed\b"],
            "code_generation": [r"\bgenerate", r"\bscaffold\b", r"\bboilerplate\b", r"\btemplate\b"],
            "documentation": [r"\bdoc\b", r"\breadme\b", r"\bcomment\b", r"\bjavadoc\b"],
            "style_changes": [r"\bformat\b", r"\blint\b", r"\bstyle\b", r"\bindent\b"],
        }

    def _load_commits(self, repo_name):
        """Load commits from git artifacts"""
        commits_file = self.git_artifacts / repo_name / "commits.json"
        if not commits_file.exists():
            return []
        with open(commits_file, "r") as f:
            data = json.load(f)
        return data.get("commits", [])

    def _repo_names(self):
        if not self.git_artifacts.exists():
            return []
        repos = []
        for entry in sorted(self.git_artifacts.iterdir()):
            if entry.is_dir() and not entry.name.startswith("."):
                repos.append(entry.name)
        return repos

    def detect_ai_mentions(self, text):
        """Detect explicit AI framework mentions"""
        mentions = {}
        text_lower = text.lower()

        for framework, patterns in self.ai_frameworks.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    mentions[framework] = True
                    break

        return mentions

    def detect_code_patterns(self, text):
        """Detect code change patterns"""
        patterns = {}
        text_lower = text.lower()

        for pattern_name, keywords in self.pattern_keywords.items():
            for keyword in keywords:
                if re.search(keyword, text_lower, re.IGNORECASE):
                    patterns[pattern_name] = True
                    break

        return patterns

    def analyze_commit_clustering(self, commits):
        """Detect rapid bulk commits (potential AI-generated)"""
        if len(commits) < 10:
            return None

        # Sort commits by timestamp
        sorted_commits = sorted(commits, key=lambda c: c.get("timestamp", ""))

        # Find clusters of commits within 1 hour
        clusters = []
        current_cluster = [sorted_commits[0]]

        for i in range(1, len(sorted_commits)):
            curr_time = sorted_commits[i].get("timestamp", "")
            prev_time = sorted_commits[i-1].get("timestamp", "")

            if curr_time and prev_time:
                try:
                    # Simple time difference check (within same day typically)
                    curr_date = curr_time[:10]
                    prev_date = prev_time[:10]

                    if curr_date == prev_date:
                        current_cluster.append(sorted_commits[i])
                    else:
                        if len(current_cluster) >= 5:  # Cluster of 5+ commits
                            clusters.append(current_cluster)
                        current_cluster = [sorted_commits[i]]
                except:
                    pass

        if len(current_cluster) >= 5:
            clusters.append(current_cluster)

        return {
            "suspicious_clusters": len(clusters),
            "avg_cluster_size": sum(len(c) for c in clusters) / len(clusters) if clusters else 0,
            "max_cluster_size": max(len(c) for c in clusters) if clusters else 0,
            "cluster_details": [
                {
                    "date": c[0].get("timestamp", "")[:10],
                    "commit_count": len(c),
                    "subjects": [x.get("subject", "") for x in c[:3]]
                } for c in clusters[:5]  # Top 5 clusters
            ]
        }

    def calculate_ai_score(self, repo_name):
        """Calculate comprehensive AI usage score"""
        commits = self._load_commits(repo_name)
        if not commits:
            return None

        ai_mentions = defaultdict(int)
        code_patterns = defaultdict(int)
        ai_attributed_commits = []

        for commit in commits:
            subject = commit.get("subject", "")

            # Check for AI mentions
            mentions = self.detect_ai_mentions(subject)
            if mentions:
                ai_attributed_commits.append({
                    "timestamp": commit.get("timestamp", ""),
                    "author": commit.get("author_name", "") or commit.get("author", ""),
                    "subject": subject,
                    "frameworks": list(mentions.keys())
                })

            for framework in mentions:
                ai_mentions[framework] += 1

            # Detect code patterns
            patterns = self.detect_code_patterns(subject)
            for pattern in patterns:
                code_patterns[pattern] += 1

        # Analyze clustering
        clustering = self.analyze_commit_clustering(commits)

        # Calculate AI probability score (0-100)
        ai_score = 0
        ai_score += len(ai_attributed_commits) * 10  # Explicit mentions weight
        if clustering:
            ai_score += min(clustering["suspicious_clusters"] * 2, 30)  # Cluster activity

        ai_score = min(ai_score, 100)  # Cap at 100

        commit_dates = sorted([c.get("timestamp", "")[:10] for c in commits if c.get("timestamp")])
        return {
            "metric_id": f"repo.ai_analysis.{repo_name}",
            "repo": repo_name,
            "repos": [repo_name],
            "inputs": [str((self.git_artifacts / repo_name / "commits.json").relative_to(self.root_dir))],
            "time_range": {
                "start": commit_dates[0] if commit_dates else None,
                "end": commit_dates[-1] if commit_dates else None
            },
            "ai_probability_score": ai_score,
            "ai_score_interpretation": self._interpret_score(ai_score),
            "explicit_ai_mentions": dict(ai_mentions),
            "ai_attributed_commits": len(ai_attributed_commits),
            "ai_commits_percentage": round((len(ai_attributed_commits) / len(commits) * 100), 2) if commits else 0,
            "code_pattern_analysis": dict(code_patterns),
            "commit_clustering": clustering,
            "sample_ai_commits": [
                {
                    "timestamp": c["timestamp"],
                    "author": c["author"],
                    "subject": c["subject"],
                    "frameworks": c["frameworks"]
                } for c in ai_attributed_commits[:10]
            ],
            "total_commits_analyzed": len(commits),
            "method": "Detect AI mentions, code patterns, and commit clustering behavior",
            "note": "AI score is speculative; explicit mentions in commits are more reliable",
            "calculated_at": datetime.utcnow().isoformat() + "Z"
        }

    def _interpret_score(self, score):
        """Interpret AI probability score"""
        if score == 0:
            return "No AI indicators detected"
        elif score < 20:
            return "Minimal AI usage indicators"
        elif score < 40:
            return "Some AI-assisted commits detected"
        elif score < 60:
            return "Moderate AI usage indicators"
        elif score < 80:
            return "Significant AI usage patterns"
        else:
            return "Heavy AI-assisted development"

    def generate_global_ai_report(self, repo_analyses):
        """Generate organization-wide AI usage report"""
        total_ai_score = 0
        total_ai_commits = 0
        total_commits = 0

        repo_rankings = []

        for repo_name, analysis in repo_analyses.items():
            if analysis:
                score = analysis.get("ai_probability_score", 0)
                ai_commits = analysis.get("ai_attributed_commits", 0)
                total_commits_repo = analysis.get("total_commits_analyzed", 0)

                total_ai_score += score
                total_ai_commits += ai_commits
                total_commits += total_commits_repo

                repo_rankings.append({
                    "repo": repo_name,
                    "score": score,
                    "ai_commits": ai_commits,
                    "percentage": analysis.get("ai_commits_percentage", 0)
                })

        avg_ai_score = total_ai_score / len(repo_analyses) if repo_analyses else 0

        # Get global time range from global commits metric if available
        global_commits_file = self.calculations / "global" / "commits.json"
        global_time_range = {"start": None, "end": None}

        if global_commits_file.exists():
            try:
                import json
                with open(global_commits_file, "r") as f:
                    global_commits_data = json.load(f)
                    if global_commits_data.get("time_range"):
                        global_time_range = global_commits_data["time_range"]
            except:
                pass

        return {
            "metric_id": "global.ai_usage_analysis",
            "repos": list(repo_analyses.keys()),
            "inputs": [str(global_commits_file.relative_to(self.root_dir))],  # Reference global commits instead
            "time_range": global_time_range,
            "global_ai_score": round(avg_ai_score, 2),
            "score_interpretation": self._interpret_score(avg_ai_score),
            "total_ai_commits": total_ai_commits,
            "total_commits_analyzed": total_commits,
            "global_ai_percentage": round((total_ai_commits / total_commits * 100), 2) if total_commits else 0,
            "repositories_ranked": sorted(repo_rankings, key=lambda x: x["score"], reverse=True),
            "method": "Aggregate AI analysis across all repositories",
            "calculated_at": datetime.utcnow().isoformat() + "Z"
        }

    def analyze_all_repos(self):
        """Run AI analysis on all repositories"""
        results = {}
        repos = self._repo_names()

        print("\n" + "="*70)
        print("AI USAGE PATTERN DETECTION")
        print("="*70 + "\n")

        for repo_name in repos:
            print(f"Analyzing {repo_name} for AI indicators...")
            analysis = self.calculate_ai_score(repo_name)

            if analysis:
                # Save per-repo analysis
                repo_dir = self.calculations / "per_repo" / repo_name
                repo_dir.mkdir(parents=True, exist_ok=True)
                with open(repo_dir / "ai_analysis.json", "w") as f:
                    json.dump(analysis, f, indent=2)

                results[repo_name] = analysis

                score = analysis.get("ai_probability_score", 0)
                ai_commits = analysis.get("ai_attributed_commits", 0)
                print(f"  ✓ AI Score: {score}/100 | AI Commits: {ai_commits} | Interpretation: {analysis['ai_score_interpretation']}")

        # Generate global report
        if results:
            global_report = self.generate_global_ai_report(results)
            global_dir = self.calculations / "global"
            global_dir.mkdir(parents=True, exist_ok=True)
            with open(global_dir / "ai_usage_analysis.json", "w") as f:
                json.dump(global_report, f, indent=2)

            print(f"\n✓ Global AI Analysis: {global_report['global_ai_score']}/100")
            print(f"  Organization AI Score: {global_report['score_interpretation']}")

        print("\n" + "="*70)
        print(f"AI analysis complete for {len(repos)} repositories")
        print("="*70 + "\n")

        return results

if __name__ == "__main__":
    detector = AIPatternDetector()
    detector.analyze_all_repos()
