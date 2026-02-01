/**
 * R&D Metrics Report - Professional Version
 * Loads and displays only validated data from calculations/ folder
 */

class MetricsReport {
  constructor() {
    this.manifest = null;
    this.init();
  }

  async init() {
    try {
      // Load and validate manifest first
      await this.loadManifest();
      this.renderHeader();
      this.renderFindings();
      this.renderRepositories();
    } catch (err) {
      console.error('Report error:', err);
      this.showError('Failed to load report');
    }
  }

  async loadManifest() {
    const resp = await fetch('../calculations/MANIFEST.json');
    if (!resp.ok) throw new Error('Manifest not found');
    this.manifest = await resp.json();
  }

  renderHeader() {
    // Date
    const dateElem = document.getElementById('report-date');
    if (dateElem) {
      const now = new Date();
      const formatted = now.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
      dateElem.textContent = `Generated ${formatted}`;
    }

    // Validation badge
    const badge = document.getElementById('validation-badge');
    if (badge && this.manifest) {
      const status = this.manifest.validation_status === 'PASS'
        ? '✓ All Quality Gates Passed'
        : '⚠ Validation Issues';
      badge.textContent = status;
    }
  }

  renderFindings() {
    const data = this.manifest;

    // Total commits
    this.updateElement('finding-commits', data.global_metrics['commits.json'].total_commits);

    // Repos
    this.updateElement('finding-repos', data.global_metrics['summary.json'].repos_analyzed);

    // Contributors
    let total = 0;
    for (const repo of Object.keys(data.per_repo_metrics)) {
      total += data.per_repo_metrics[repo].contributors.unique_contributors || 0;
    }
    this.updateElement('finding-contributors', total);

    // Velocity (average across all repos)
    let sumVelocity = 0;
    let count = 0;
    for (const repo of Object.keys(data.per_repo_metrics)) {
      const vel = data.per_repo_metrics[repo].commits.avg_commits_per_day;
      if (vel) {
        sumVelocity += vel;
        count++;
      }
    }
    const avgVel = count > 0 ? (sumVelocity / count).toFixed(2) : 'N/A';
    this.updateElement('finding-velocity', avgVel);

    // Test metrics
    const testingMetrics = data.testing_metrics?.global || {};
    this.updateElement('finding-tests', testingMetrics.total_test_files || 0);
    this.updateElement('finding-epics', testingMetrics.total_epics_found || 0);
    this.updateElement('finding-stories', testingMetrics.total_user_stories_found || 0);
  }

  renderRepositories() {
    const container = document.getElementById('repos-container');
    if (!container) return;

    const repoData = this.manifest.per_repo_metrics;
    const testingData = this.manifest.testing_metrics?.per_repo || {};
    const repoNames = Object.keys(repoData).sort();

    if (repoNames.length === 0) {
      container.innerHTML = '<p>No repositories found.</p>';
      return;
    }

    let html = '';
    for (const repo of repoNames) {
      const data = repoData[repo];
      const tests = testingData[repo] || {};

      html += `
        <div class="repo-detail-card">
          <div class="repo-detail-name">${repo}</div>
          <table class="repo-metrics-table">
            <tr>
              <td>Total Commits</td>
              <td>${data.commits.total_commits}</td>
            </tr>
            <tr>
              <td>Contributors</td>
              <td>${data.contributors.unique_contributors}</td>
            </tr>
            <tr>
              <td>Daily Activity</td>
              <td>${data.commits.avg_commits_per_day.toFixed(2)} commits/day</td>
            </tr>
            <tr>
              <td>Active Period</td>
              <td>${data.commits.period_start} to ${data.commits.period_end}</td>
            </tr>
            <tr>
              <td>Days Active</td>
              <td>${data.commits.days_active}</td>
            </tr>
            <tr>
              <td>Deployment Frequency</td>
              <td>${data.dora_frequency.value} ${data.dora_frequency.unit}</td>
            </tr>
            <tr>
              <td>Lead Time</td>
              <td>${data.lead_time.value} ${data.lead_time.unit}</td>
            </tr>
            <tr>
              <td>Test Files</td>
              <td>${tests.test_files || 0}</td>
            </tr>
            <tr>
              <td>Test Frameworks</td>
              <td>${tests.test_frameworks ? tests.test_frameworks.join(', ') : 'N/A'}</td>
            </tr>
            <tr>
              <td>Epics Found</td>
              <td>${tests.epics || 0}</td>
            </tr>
            <tr>
              <td>User Stories</td>
              <td>${tests.user_stories || 0}</td>
            </tr>
            <tr>
              <td>Test Coverage</td>
              <td><em>${data.coverage.value || 'N/A'}</em></td>
            </tr>
          </table>
        </div>
      `;
    }

    container.innerHTML = html;
  }

  updateElement(id, value) {
    const elem = document.getElementById(id);
    if (elem) {
      if (typeof value === 'number') {
        elem.textContent = value.toLocaleString();
      } else if (Array.isArray(value)) {
        elem.textContent = value.length;
      } else {
        elem.textContent = value || 'N/A';
      }
    }
  }

  showError(message) {
    const container = document.getElementById('repos-container');
    if (container) {
      container.innerHTML = `<p style="color: red;">Error: ${message}</p>`;
    }
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  new MetricsReport();
});
