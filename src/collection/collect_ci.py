#!/usr/bin/env python3
"""
COLLECTION LAYER - CI Artifacts Extraction
Attempts to collect CI/test/coverage data from repositories
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

class CICollector:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.repos_file = self.root_dir / "ReposInput.md"
        self.git_artifacts = self.root_dir / "git_artifacts"
        self.ci_artifacts = self.root_dir / "ci_artifacts"
        self.ci_artifacts.mkdir(exist_ok=True)

    def parse_repos(self):
        """Parse ReposInput.md"""
        repos = {}
        current_repo = None

        if not self.repos_file.exists():
            return repos

        with open(self.repos_file, 'r') as f:
            for line in f:
                line = line.rstrip()
                if line.startswith("## "):
                    current_repo = line.replace("## ", "").strip()
                    repos[current_repo] = {}
                elif ": " in line and current_repo:
                    key, value = line.split(": ", 1)
                    repos[current_repo][key.strip()] = value.strip()

        return repos

    def collect_repo_ci(self, repo_name, config):
        """Attempt to collect CI artifacts from a repository"""
        print(f"  Processing CI for {repo_name}...")

        repo_dir = self.ci_artifacts / repo_name
        repo_dir.mkdir(exist_ok=True)

        git_clone = self.git_artifacts / repo_name / "clone"
        if not git_clone.exists():
            print(f"    ℹ Git data not collected yet")
            return

        language = config.get("language", "unknown")
        coverage_type = config.get("coverage", "unknown")

        # Create CI info file
        with open(repo_dir / "ci_info.json", 'w') as f:
            json.dump({
                "metric_id": "ci.info.raw",
                "repo": repo_name,
                "language": language,
                "coverage_tool": coverage_type,
                "status": "initialized",
                "note": "Run local tests to populate coverage data",
                "collected_at": datetime.now().isoformat()
            }, f, indent=2)

        # Try to run tests based on language
        if language == "java":
            self._collect_java_tests(repo_name, git_clone, repo_dir)
        elif language == "python":
            self._collect_python_tests(repo_name, git_clone, repo_dir)
        elif language == "mixed":
            self._collect_javascript_tests(repo_name, git_clone, repo_dir)
            self._collect_java_tests(repo_name, git_clone, repo_dir)

        print(f"    ✓ CI initialization complete")

    def _collect_java_tests(self, repo_name, git_clone, repo_dir):
        """Collect Java test and coverage data"""
        print(f"    → Attempting Java test collection...")

        pom_files = [
            p for p in git_clone.rglob("pom.xml")
            if ".git" not in p.parts and "node_modules" not in p.parts
        ]
        gradle_files = [
            p for p in git_clone.rglob("build.gradle.kts")
            if ".git" not in p.parts and "node_modules" not in p.parts
        ] + [
            p for p in git_clone.rglob("build.gradle")
            if ".git" not in p.parts and "node_modules" not in p.parts
        ]

        if not pom_files and not gradle_files:
            print(f"      ℹ No pom.xml or build.gradle(.kts) found")
            return

        coverage_dir = repo_dir / "coverage" / "jacoco"
        coverage_dir.mkdir(parents=True, exist_ok=True)
        collected = 0

        for pom_file in pom_files:
            module_dir = pom_file.parent
            try:
                subprocess.run(
                    ["mvn", "clean", "test", "jacoco:report"],
                    cwd=module_dir,
                    capture_output=True,
                    timeout=600,
                    check=False
                )

                jacoco_path = module_dir / "target" / "site" / "jacoco" / "jacoco.xml"
                if jacoco_path.exists():
                    module_name = module_dir.relative_to(git_clone).as_posix().replace("/", "_")
                    if module_name == ".":
                        module_name = "root"
                    dest = coverage_dir / f"{module_name}.jacoco.xml"
                    with open(jacoco_path, 'rb') as src:
                        with open(dest, 'wb') as dst:
                            dst.write(src.read())
                    collected += 1
                    print(f"      ✓ Collected {dest.relative_to(repo_dir)}")
            except subprocess.TimeoutExpired:
                print(f"      ℹ Maven test timeout in {module_dir}")
            except Exception as e:
                print(f"      ℹ Could not run Maven in {module_dir}: {str(e)}")

        init_script = coverage_dir / "jacoco.init.gradle"
        if not init_script.exists():
            init_script.write_text(
                """
allprojects {
  plugins.withId('java') {
    apply plugin: 'jacoco'
    tasks.withType(Test).configureEach {
      finalizedBy 'jacocoTestReport'
    }
    tasks.register('jacocoTestReport', JacocoReport) {
      dependsOn tasks.withType(Test)
      reports {
        xml.required = true
        html.required = false
        csv.required = false
      }
      def mainSourceSets = project.extensions.findByName('sourceSets')
      if (mainSourceSets != null) {
        classDirectories.setFrom(files(mainSourceSets.main.output))
        sourceDirectories.setFrom(files(mainSourceSets.main.allSource.srcDirs))
      }
      executionData.setFrom(fileTree(dir: buildDir, includes: ['jacoco/test.exec', 'jacoco/test.exec.*']))
    }
  }
}
""".strip()
            )

        gradle_root = git_clone / "gradlew"
        if gradle_root.exists():
            try:
                subprocess.run(
                    ["./gradlew", "test", "jacocoTestReport", "--init-script", str(init_script)],
                    cwd=git_clone,
                    capture_output=True,
                    timeout=900,
                    check=False
                )
            except subprocess.TimeoutExpired:
                print("      ℹ Gradle test timeout in repo root")
            except Exception as e:
                print(f"      ℹ Could not run Gradle in repo root: {str(e)}")

        for gradle_file in gradle_files:
            module_dir = gradle_file.parent
            gradlew = module_dir / "gradlew"
            if gradlew.exists():
                try:
                    subprocess.run(
                        ["./gradlew", "test", "jacocoTestReport", "--init-script", str(init_script)],
                        cwd=module_dir,
                        capture_output=True,
                        timeout=900,
                        check=False
                    )
                except subprocess.TimeoutExpired:
                    print(f"      ℹ Gradle test timeout in {module_dir}")
                except Exception as e:
                    print(f"      ℹ Could not run Gradle in {module_dir}: {str(e)}")

            report_paths = [
                module_dir / "build" / "reports" / "jacoco" / "test" / "jacocoTestReport.xml",
                module_dir / "build" / "reports" / "jacoco" / "test" / "jacocoTestReport.xml"
            ]
            for report in report_paths:
                if report.exists():
                    module_name = module_dir.relative_to(git_clone).as_posix().replace("/", "_")
                    if module_name == ".":
                        module_name = "root"
                    dest = coverage_dir / f"{module_name}.jacoco.xml"
                    with open(report, "rb") as src:
                        with open(dest, "wb") as dst:
                            dst.write(src.read())
                    collected += 1
                    print(f"      ✓ Collected {dest.relative_to(repo_dir)}")

        if collected == 0:
            print(f"      ℹ No jacoco.xml files produced")

    def _collect_python_tests(self, repo_name, git_clone, repo_dir):
        """Collect Python test and coverage data"""
        print(f"    → Attempting Python test collection...")

        requirements_file = git_clone / "requirements.txt"
        setup_file = git_clone / "setup.py"

        if not (requirements_file.exists() or setup_file.exists()):
            print(f"      ℹ No Python project files found")
            return

        try:
            if requirements_file.exists():
                subprocess.run(
                    ["python3", "-m", "pip", "install", "-r", str(requirements_file)],
                    cwd=git_clone,
                    capture_output=True,
                    timeout=600,
                    check=False
                )
            subprocess.run(
                ["python3", "-m", "pip", "install", "pytest-cov"],
                cwd=git_clone,
                capture_output=True,
                timeout=600,
                check=False
            )
            # Run pytest with coverage
            result = subprocess.run(
                ["python3", "-m", "pytest", "--cov=.", "--cov-report=xml", "--tb=short"],
                cwd=git_clone,
                capture_output=True,
                timeout=300,
                check=False
            )

            # Look for coverage results
            coverage_path = git_clone / "coverage.xml"
            if coverage_path.exists():
                coverage_dir = repo_dir / "coverage" / "pytest"
                coverage_dir.mkdir(parents=True, exist_ok=True)
                dest = coverage_dir / "coverage.xml"
                with open(coverage_path, 'rb') as src:
                    with open(dest, 'wb') as dst:
                        dst.write(src.read())
                print(f"      ✓ Collected {dest.relative_to(repo_dir)}")
        except subprocess.TimeoutExpired:
            print(f"      ℹ Pytest timeout (network/build time)")
        except Exception as e:
            print(f"      ℹ Could not run pytest: {str(e)}")

    def _collect_javascript_tests(self, repo_name, git_clone, repo_dir):
        """Collect JavaScript test and coverage data"""
        print(f"    → Attempting JavaScript test collection...")

        package_files = [
            p for p in git_clone.rglob("package.json")
            if ".git" not in p.parts and "node_modules" not in p.parts
        ]
        if not package_files:
            print(f"      ℹ No package.json found")
            return

        coverage_dir = repo_dir / "coverage" / "lcov"
        coverage_dir.mkdir(parents=True, exist_ok=True)
        collected = 0

        for package_json in package_files:
            module_dir = package_json.parent
            try:
                subprocess.run(
                    ["npm", "install", "--silent"],
                    cwd=module_dir,
                    capture_output=True,
                    timeout=600,
                    check=False
                )
                subprocess.run(
                    ["npm", "install", "--no-save", "jest-circus", "jest-jasmine2"],
                    cwd=module_dir,
                    capture_output=True,
                    timeout=600,
                    check=False
                )
                result = subprocess.run(
                    ["npm", "test", "--", "--coverage", "--coverage-reporter=lcov"],
                    cwd=module_dir,
                    capture_output=True,
                    timeout=600,
                    check=False
                )

                lcov_path = module_dir / "coverage" / "lcov.info"
                if lcov_path.exists():
                    fallback_result = None
                    jasmine_result = None
                    config_result = None
                    if lcov_path.stat().st_size == 0:
                        fallback_result = subprocess.run(
                            ["npx", "--no-install", "jest", "--coverage", "--coverageReporters=lcov", "--passWithNoTests"],
                            cwd=module_dir,
                            capture_output=True,
                            timeout=600,
                            check=False
                        )
                        if lcov_path.stat().st_size == 0:
                            jasmine_result = subprocess.run(
                                ["npx", "--no-install", "jest", "--coverage", "--coverageReporters=lcov", "--passWithNoTests", "--testRunner=jest-jasmine2"],
                                cwd=module_dir,
                                capture_output=True,
                                timeout=600,
                                check=False
                            )
                    if lcov_path.stat().st_size == 0:
                        runner_path = (module_dir / "node_modules" / "jest-circus" / "build" / "runner.js").resolve()
                        if runner_path.exists():
                            config_path = module_dir / ".dora-jest.config.js"
                            config_path.write_text(
                                "\n".join([
                                    "module.exports = {",
                                    "  testEnvironment: 'jsdom',",
                                    "  testMatch: ['**/__tests__/**/*.test.js'],",
                                    "  moduleFileExtensions: ['js', 'json'],",
                                    "  transform: {},",
                                    f"  testRunner: '{runner_path.as_posix()}',",
                                    "};",
                                ])
                            )
                            config_result = subprocess.run(
                                ["npx", "--no-install", "jest", "--config", str(config_path.resolve()), "--coverage", "--coverageReporters=lcov", "--passWithNoTests"],
                                cwd=module_dir,
                                capture_output=True,
                                timeout=600,
                                check=False
                            )
                    module_name = module_dir.relative_to(git_clone).as_posix().replace("/", "_")
                    if module_name == ".":
                        module_name = "root"
                    dest = coverage_dir / f"{module_name}.lcov.info"
                    with open(lcov_path, 'r') as src:
                        with open(dest, 'w') as dst:
                            dst.write(src.read())
                    collected += 1
                    print(f"      ✓ Collected {dest.relative_to(repo_dir)}")
                    if lcov_path.stat().st_size == 0:
                        log_path = coverage_dir / f"{module_name}.lcov.log.txt"
                        with open(log_path, "w") as log:
                            log.write("npm test output:\n")
                            log.write(result.stdout.decode(errors="ignore"))
                            log.write("\n\nnpm test error:\n")
                            log.write(result.stderr.decode(errors="ignore"))
                            if fallback_result:
                                log.write("\n\nnpx jest output:\n")
                                log.write(fallback_result.stdout.decode(errors="ignore"))
                                log.write("\n\nnpx jest error:\n")
                                log.write(fallback_result.stderr.decode(errors="ignore"))
                            if jasmine_result:
                                log.write("\n\nnpx jest (jasmine) output:\n")
                                log.write(jasmine_result.stdout.decode(errors="ignore"))
                                log.write("\n\nnpx jest (jasmine) error:\n")
                                log.write(jasmine_result.stderr.decode(errors="ignore"))
                            if config_result:
                                log.write("\n\nnpx jest (custom config) output:\n")
                                log.write(config_result.stdout.decode(errors="ignore"))
                                log.write("\n\nnpx jest (custom config) error:\n")
                                log.write(config_result.stderr.decode(errors="ignore"))
            except subprocess.TimeoutExpired:
                print(f"      ℹ npm test timeout in {module_dir}")
            except Exception as e:
                print(f"      ℹ Could not run npm test in {module_dir}: {str(e)}")

        if collected == 0:
            print(f"      ℹ No lcov.info files produced")

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
