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
    const primary = await fetch('../calculations/MANIFEST.json');
    if (primary.ok) {
      this.manifest = await primary.json();
      return;
    }

    const fallback = await fetch('./calculations/MANIFEST.json');
    if (!fallback.ok) throw new Error('Manifest not found');
    this.manifest = await fallback.json();
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
    const globalCommits = data.global_metrics['commits.json'];
    this.updateElement('finding-commits', globalCommits?.total_commits);

    // Repos
    const globalSummary = data.global_metrics['summary.json'];
    this.updateElement('finding-repos', globalSummary?.repos_analyzed?.length);

    // Contributors
    const globalContributors = data.global_metrics['contributors.json'];
    this.updateElement('finding-contributors', globalContributors?.unique_contributors);

    // Velocity (average across all repos)
    const globalVelocity = data.global_metrics['velocity.json'];
    this.updateElement('finding-velocity', globalVelocity?.value);

    // Test metrics
    const globalTests = data.global_metrics['tests.json'];
    this.updateElement('finding-tests', globalTests?.total_test_files);
    this.updateElement('finding-epics', globalTests?.total_epics_found);
    this.updateElement('finding-stories', globalTests?.total_user_stories_found);

    this.attachFindingLinks('finding-commits', globalCommits);
    this.attachFindingLinks('finding-repos', globalSummary);
    this.attachFindingLinks('finding-contributors', globalContributors);
    this.attachFindingLinks('finding-velocity', globalVelocity);
    this.attachFindingLinks('finding-tests', globalTests);
    this.attachFindingLinks('finding-epics', globalTests);
    this.attachFindingLinks('finding-stories', globalTests);
  }

  renderRepositories() {
    const container = document.getElementById('repos-container');
    if (!container) return;

    const repoData = this.manifest.per_repo_metrics;
    const repoNames = Object.keys(repoData).sort();

    if (repoNames.length === 0) {
      container.innerHTML = '<p>No repositories found.</p>';
      return;
    }

    let html = '';
    for (const repo of repoNames) {
      const data = repoData[repo];
      const tests = data.tests || {};

      html += `
        <div class="repo-detail-card">
          <div class="repo-detail-name">${repo}</div>
          <table class="repo-metrics-table">
            <tr>
              <td>Total Commits</td>
              <td>${this.formatValue(data.commits?.total_commits)}${this.renderMetricLinks(data.commits)}</td>
            </tr>
            <tr>
              <td>Contributors</td>
              <td>${this.formatValue(data.contributors?.unique_contributors)}${this.renderMetricLinks(data.contributors)}</td>
            </tr>
            <tr>
              <td>Daily Activity</td>
              <td>${this.formatValue(data.commits?.avg_commits_per_day, 'commits/day')}${this.renderMetricLinks(data.commits)}</td>
            </tr>
            <tr>
              <td>Active Period</td>
              <td>${this.formatRange(data.commits?.period_start, data.commits?.period_end)}${this.renderMetricLinks(data.commits)}</td>
            </tr>
            <tr>
              <td>Days Active</td>
              <td>${this.formatValue(data.commits?.days_active)}${this.renderMetricLinks(data.commits)}</td>
            </tr>
            <tr>
              <td>Deployment Frequency</td>
              <td>${this.formatValue(data.dora_frequency?.value, data.dora_frequency?.unit)}${this.renderMetricLinks(data.dora_frequency)}</td>
            </tr>
            <tr>
              <td>Lead Time</td>
              <td>${this.formatValue(data.lead_time?.value, data.lead_time?.unit)}${this.renderMetricLinks(data.lead_time)}</td>
            </tr>
            <tr>
              <td>Test Files</td>
              <td>${this.formatValue(tests.test_files)}${this.renderMetricLinks(tests)}</td>
            </tr>
            <tr>
              <td>Test Frameworks</td>
              <td>${this.formatList(tests.test_frameworks)}${this.renderMetricLinks(tests)}</td>
            </tr>
            <tr>
              <td>Epics Found</td>
              <td>${this.formatValue(tests.epics)}${this.renderMetricLinks(tests)}</td>
            </tr>
            <tr>
              <td>User Stories</td>
              <td>${this.formatValue(tests.user_stories)}${this.renderMetricLinks(tests)}</td>
            </tr>
            <tr>
              <td>Test Coverage</td>
              <td><em>${this.formatValue(data.coverage?.value)}${this.renderMetricLinks(data.coverage)}</em></td>
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
      elem.textContent = this.formatValue(value);
    }
  }

  formatValue(value, unit) {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') {
      const formatted = Number.isFinite(value) ? value.toLocaleString() : 'N/A';
      return unit ? `${formatted} ${unit}` : formatted;
    }
    if (Array.isArray(value)) return value.length.toLocaleString();
    if (value === '') return 'N/A';
    return unit ? `${value} ${unit}` : value;
  }

  formatRange(start, end) {
    if (!start || !end) return 'N/A';
    return `${start} to ${end}`;
  }

  formatList(list) {
    if (!Array.isArray(list) || list.length === 0) return 'N/A';
    return list.join(', ');
  }

  attachFindingLinks(id, metric) {
    const valueElem = document.getElementById(id);
    if (!valueElem || !metric) return;
    const card = valueElem.closest('.finding-card');
    if (!card) return;
    const existing = card.querySelector('.metric-links');
    if (existing) return;
    const links = document.createElement('div');
    links.className = 'metric-links';
    links.innerHTML = this.renderMetricLinks(metric, true);
    card.appendChild(links);
  }

  renderMetricLinks(metric, compact = false) {
    if (!metric) return '';
    const calc = metric.calculation_path
      ? `<a href="../${metric.calculation_path}">calc</a>`
      : 'calc N/A';
    const inputs = Array.isArray(metric.inputs) && metric.inputs.length > 0
      ? metric.inputs.map((input) => `<a href="../${input}">${this.basename(input)}</a>`).join(', ')
      : 'inputs N/A';
    const label = compact ? '' : '<div class="metric-links">';
    const tail = compact ? '' : '</div>';
    return `${label}<span>${calc}</span> <span>${inputs}</span>${tail}`;
  }

  basename(path) {
    if (!path) return '';
    const parts = path.split('/');
    return parts[parts.length - 1];
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
