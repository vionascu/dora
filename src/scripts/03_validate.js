#!/usr/bin/env node
/**
 * VALIDATION LAYER
 * Quality gates to ensure data integrity
 */

const fs = require('fs');
const path = require('path');

class Validator {
  constructor(rootDir = '.') {
    this.rootDir = rootDir;
    this.errors = [];
    this.warnings = [];
  }

  log(msg) {
    console.log(msg);
  }

  validate() {
    this.log('\n' + '='.repeat(60));
    this.log('DORA VALIDATION LAYER - Quality gates');
    this.log('='.repeat(60) + '\n');

    this.validateDirectories();
    this.validateCalculations();
    this.validateDataIntegrity();

    this.log('\n' + '='.repeat(60));
    this.log(`Validation Results:`);
    this.log(`  Errors: ${this.errors.length}`);
    this.log(`  Warnings: ${this.warnings.length}`);
    this.log('='.repeat(60) + '\n');

    if (this.errors.length > 0) {
      this.log('❌ VALIDATION FAILED\n');
      this.errors.forEach(e => this.log(`  ✗ ${e}`));
      return false;
    }

    this.log('✓ All quality gates passed\n');
    return true;
  }

  validateDirectories() {
    this.log('Checking required directories...');

    const dirs = [
      'git_artifacts',
      'ci_artifacts',
      'calculations/per_repo',
      'calculations/global'
    ];

    dirs.forEach(dir => {
      if (!fs.existsSync(path.join(this.rootDir, dir))) {
        this.errors.push(`Missing directory: ${dir}`);
      }
    });

    if (this.errors.length === 0) {
      this.log('  ✓ All required directories present\n');
    }
  }

  validateCalculations() {
    this.log('Checking calculation files...');

    const calcDir = path.join(this.rootDir, 'calculations');
    const globalDir = path.join(calcDir, 'global');

    if (!fs.existsSync(globalDir)) {
      this.warnings.push('No global calculations found yet');
      return;
    }

    const files = fs.readdirSync(globalDir).filter(f => f.endsWith('.json'));

    if (files.length === 0) {
      this.warnings.push('No calculation files generated yet');
      return;
    }

    files.forEach(file => {
      try {
        const content = JSON.parse(fs.readFileSync(path.join(globalDir, file), 'utf8'));
        if (!content.metric_id) {
          this.errors.push(`Missing metric_id in ${file}`);
        }
      } catch (e) {
        this.errors.push(`Invalid JSON in ${file}: ${e.message}`);
      }
    });

    if (this.errors.length === 0) {
      this.log(`  ✓ Found ${files.length} valid calculation files\n`);
    }
  }

  validateDataIntegrity() {
    this.log('Checking data integrity...');

    const calcDir = path.join(this.rootDir, 'calculations');
    const perRepoDir = path.join(calcDir, 'per_repo');

    if (!fs.existsSync(perRepoDir)) {
      this.warnings.push('No per-repo calculations found yet');
      return;
    }

    const repos = fs.readdirSync(perRepoDir);
    const issues = [];

    repos.forEach(repo => {
      const repoDir = path.join(perRepoDir, repo);
      const files = fs.readdirSync(repoDir).filter(f => f.endsWith('.json'));

      files.forEach(file => {
        try {
          const content = JSON.parse(fs.readFileSync(path.join(repoDir, file), 'utf8'));

          // Check for approximations
          const jsonStr = JSON.stringify(content);
          if (jsonStr.includes('~') || jsonStr.includes('approx') || jsonStr.includes('estimated')) {
            this.errors.push(`Approximations found in ${repo}/${file}`);
          }

          // Check for null values
          if (content.value === null && !content.reason) {
            this.warnings.push(`N/A value in ${repo}/${file} without explanation`);
          }
        } catch (e) {
          this.errors.push(`Invalid JSON in ${repo}/${file}`);
        }
      });
    });

    if (this.errors.length === 0) {
      this.log('  ✓ Data integrity checks passed\n');
    }
  }
}

const validator = new Validator();
const passed = validator.validate();
process.exit(passed ? 0 : 1);
