/**
 * DORA Dashboard - Read-Only Presentation Layer
 * Loads and renders metrics from calculations/ folder
 */

class Dashboard {
  constructor() {
    this.baseUrl = '..';  // Relative to calculations/
    this.metrics = {};
    this.init();
  }

  async init() {
    try {
      await this.loadMetrics();
      this.render();
      this.updateTimestamp();
    } catch (err) {
      console.error('Dashboard initialization failed:', err);
      this.showError('Failed to load metrics');
    }
  }

  async loadMetrics() {
    console.log('Loading metrics from calculations/...');

    // Load global metrics
    try {
      const summaryResp = await fetch(`${this.baseUrl}/calculations/global/summary.json`);
      if (!summaryResp.ok) throw new Error(`HTTP ${summaryResp.status}`);
      this.metrics.global = await summaryResp.json();
      console.log('✓ Loaded global summary');
    } catch (err) {
      console.warn('Could not load global summary:', err);
      this.metrics.global = { repos_analyzed: [] };
    }

    // Load per-repo metrics
    this.metrics.repos = {};
    if (this.metrics.global.repos_analyzed) {
      for (const repo of this.metrics.global.repos_analyzed) {
        this.metrics.repos[repo] = {};

        // Load each metric type
        const metrics = ['commits', 'contributors', 'coverage', 'dora_frequency', 'lead_time'];
        for (const metric of metrics) {
          try {
            const resp = await fetch(`${this.baseUrl}/calculations/per_repo/${repo}/${metric}.json`);
            if (resp.ok) {
              this.metrics.repos[repo][metric] = await resp.json();
            }
          } catch (err) {
            console.warn(`Could not load ${repo}/${metric}:`, err);
          }
        }
      }
    }

    console.log('Metrics loaded:', this.metrics);
  }

  render() {
    this.renderGlobalMetrics();
    this.renderRepoMetrics();
    this.renderDoraMetrics();
  }

  renderGlobalMetrics() {
    const container = document.getElementById('global-metrics');
    if (!container) return;

    const global = this.metrics.global;
    let totalCommits = 0;

    // Calculate total commits from all repos
    for (const repo of global.repos_analyzed || []) {
      const commits = this.metrics.repos[repo]?.commits?.total_commits || 0;
      totalCommits += commits;
    }

    // Calculate organization activity
    const reposWithData = (global.repos_analyzed || []).length;
    const avgCommitsPerRepo = reposWithData > 0 ? (totalCommits / reposWithData).toFixed(1) : 0;

    const html = `
      <div class="card">
        <div class="card-label">Total Commits</div>
        <div class="card-value">${totalCommits}</div>
        <div class="card-unit">across all repositories</div>
        <div class="card-meta">
          <div class="card-method">Sum of commits across analyzed repos</div>
          <a href="../calculations/global/commits.json" class="card-link" target="_blank">View calculation</a>
        </div>
      </div>

      <div class="card">
        <div class="card-label">Repositories</div>
        <div class="card-value">${reposWithData}</div>
        <div class="card-unit">in scope (of ${global.repos_total_count || '?'})</div>
        <div class="card-meta">
          <div>${(global.repos_analyzed || []).join(', ')}</div>
          <a href="../calculations/global/summary.json" class="card-link" target="_blank">View summary</a>
        </div>
      </div>

      <div class="card">
        <div class="card-label">Avg Commits/Repo</div>
        <div class="card-value">${avgCommitsPerRepo}</div>
        <div class="card-unit">activity distribution</div>
        <div class="card-meta">
          <div class="card-method">Total commits ÷ number of repos</div>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  renderRepoMetrics() {
    const container = document.getElementById('repos-metrics');
    if (!container) return;

    const repos = this.metrics.repos || {};
    let html = '';

    for (const [repoName, metrics] of Object.entries(repos)) {
      const commits = metrics.commits || {};
      const contributors = metrics.contributors || {};
      const coverage = metrics.coverage || {};

      const commitsValue = commits.total_commits !== undefined ? commits.total_commits : '—';
      const contributorsValue = contributors.unique_contributors !== undefined ? contributors.unique_contributors : '—';
      const coverageValue = coverage.value !== null ? `${coverage.value.toFixed(1)}%` : 'N/A';

      html += `
        <div class="card">
          <div class="repo-card-title">${repoName}</div>
          <div class="card-details">
            <div class="card-detail-item">
              <span class="card-detail-item-label">Commits</span>
              <span class="card-detail-item-value">${commitsValue}</span>
            </div>
            <div class="card-detail-item">
              <span class="card-detail-item-label">Contributors</span>
              <span class="card-detail-item-value">${contributorsValue}</span>
            </div>
            <div class="card-detail-item">
              <span class="card-detail-item-label">Coverage</span>
              <span class="card-detail-item-value">${coverageValue}</span>
            </div>
            <div class="card-detail-item">
              <span class="card-detail-item-label">Frequency</span>
              <span class="card-detail-item-value">${(commits.avg_commits_per_day || 0).toFixed(2)}/day</span>
            </div>
          </div>
          <div class="card-meta">
            <a href="../calculations/per_repo/${repoName}/commits.json" class="card-link" target="_blank">View commits</a>
            <a href="../calculations/per_repo/${repoName}/" class="card-link" target="_blank">All metrics</a>
          </div>
        </div>
      `;
    }

    container.innerHTML = html || '<div class="card"><div class="card-value">No repositories loaded</div></div>';
  }

  renderDoraMetrics() {
    const container = document.getElementById('dora-metrics');
    if (!container) return;

    const repos = this.metrics.repos || {};
    let totalFrequency = 0;
    let totalLeadTime = 0;
    let repoCount = 0;

    // Aggregate DORA metrics
    for (const metrics of Object.values(repos)) {
      if (metrics.dora_frequency?.value !== null && metrics.dora_frequency?.value !== undefined) {
        totalFrequency += metrics.dora_frequency.value;
        repoCount++;
      }
      if (metrics.lead_time?.value !== null && metrics.lead_time?.value !== undefined) {
        totalLeadTime += metrics.lead_time.value;
      }
    }

    const avgFrequency = repoCount > 0 ? (totalFrequency / repoCount).toFixed(3) : '—';
    const avgLeadTime = repoCount > 0 ? (totalLeadTime / repoCount).toFixed(1) : '—';

    const html = `
      <div class="card">
        <div class="card-label">Deployment Frequency</div>
        <div class="card-value">${avgFrequency}</div>
        <div class="card-unit">commits/day (organization average)</div>
        <div class="card-meta">
          <div class="card-method">Proxy: averaged commit frequency across repos</div>
          <span style="display: block; margin-top: 0.5rem; font-size: 0.75rem; color: #8c959f;">
            ⚠ For true DORA: requires deployment tags and CI event timestamps
          </span>
          <a href="../calculations/per_repo/" class="card-link" target="_blank">View per-repo metrics</a>
        </div>
      </div>

      <div class="card">
        <div class="card-label">Lead Time for Changes</div>
        <div class="card-value">${avgLeadTime}</div>
        <div class="card-unit">hours (organization average)</div>
        <div class="card-meta">
          <div class="card-method">Average time between consecutive commits</div>
          <span style="display: block; margin-top: 0.5rem; font-size: 0.75rem; color: #8c959f;">
            ⚠ Proxy metric. True DORA: code commit timestamp to deployment timestamp
          </span>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  updateTimestamp() {
    const timestamp = new Date().toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });

    const elem = document.getElementById('update-time');
    if (elem) {
      elem.textContent = timestamp;
    }
  }

  showError(message) {
    const container = document.getElementById('global-metrics');
    if (container) {
      container.innerHTML = `
        <div class="card" style="grid-column: 1 / -1; border-color: #ffecec; background: #fff5f5;">
          <div style="color: #da3633;">
            <strong>Error:</strong> ${message}
          </div>
          <p style="margin-top: 0.5rem; font-size: 0.875rem; color: #57606a;">
            Check browser console for details. Ensure calculations/ folder exists and contains JSON files.
          </p>
        </div>
      `;
    }
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  new Dashboard();
});
