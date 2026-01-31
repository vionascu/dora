/**
 * DORA Dashboard - Clean Data Display
 * Loads metrics from calculations/ folder
 * Only displays data that exists - no assumptions
 */

class Dashboard {
  constructor() {
    this.metrics = {};
    this.init();
  }

  async init() {
    try {
      await this.loadAllMetrics();
      this.renderKPIs();
      this.renderRepositories();
    } catch (err) {
      console.error('Error:', err);
      this.showError('Failed to load metrics');
    }
  }

  async loadAllMetrics() {
    // Load global summary
    try {
      const resp = await fetch('../calculations/global/summary.json');
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      this.metrics.global = await resp.json();
    } catch (err) {
      console.warn('Global summary not found:', err);
      this.metrics.global = { repos_analyzed: [] };
    }

    // Load per-repo metrics
    this.metrics.repos = {};
    if (this.metrics.global.repos_analyzed) {
      for (const repo of this.metrics.global.repos_analyzed) {
        this.metrics.repos[repo] = await this.loadRepoMetrics(repo);
      }
    }
  }

  async loadRepoMetrics(repo) {
    const data = {};
    const files = ['commits', 'contributors', 'coverage', 'dora_frequency', 'lead_time'];

    for (const file of files) {
      try {
        const resp = await fetch(`../calculations/per_repo/${repo}/${file}.json`);
        if (resp.ok) {
          data[file] = await resp.json();
        }
      } catch (err) {
        // Silently skip missing files
      }
    }

    return data;
  }

  renderKPIs() {
    const global = this.metrics.global;

    // 1. Total Commits
    let totalCommits = 0;
    for (const repo of (global.repos_analyzed || [])) {
      const commits = this.metrics.repos[repo]?.commits?.total_commits;
      if (commits !== undefined && commits !== null) {
        totalCommits += commits;
      }
    }
    this.updateKPI('commits', totalCommits, `${global.repos_analyzed?.length || 0} repos`);

    // 2. Active Repositories
    const repoCount = global.repos_analyzed?.length || 0;
    this.updateKPI('repos', repoCount, `of ${global.repos_total_count || '?'}`);

    // 3. Contributors
    let totalContributors = 0;
    for (const repo of (global.repos_analyzed || [])) {
      const contrib = this.metrics.repos[repo]?.contributors?.unique_contributors;
      if (contrib !== undefined && contrib !== null) {
        totalContributors += contrib;
      }
    }
    this.updateKPI('contributors', totalContributors, 'across all repos');

    // 4. Activity (avg commits per day across all repos)
    let totalAvgActivity = 0;
    let countWithActivity = 0;
    for (const repo of (global.repos_analyzed || [])) {
      const freq = this.metrics.repos[repo]?.commits?.avg_commits_per_day;
      if (freq !== undefined && freq !== null && !isNaN(freq)) {
        totalAvgActivity += freq;
        countWithActivity++;
      }
    }
    const avgActivity = countWithActivity > 0 ? (totalAvgActivity / countWithActivity).toFixed(2) : 'N/A';
    this.updateKPI('activity', avgActivity, 'org average');
  }

  updateKPI(name, value, meta) {
    const elem = document.getElementById(`kpi-${name}`);
    const metaElem = document.getElementById(`kpi-${name}-meta`);

    if (elem) {
      elem.textContent = typeof value === 'number' ? value.toLocaleString() : value;
    }
    if (metaElem) {
      metaElem.textContent = meta;
    }
  }

  renderRepositories() {
    const tbody = document.getElementById('repos-tbody');
    if (!tbody) return;

    const repos = this.metrics.global.repos_analyzed || [];

    if (repos.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">No repositories found</td></tr>';
      return;
    }

    let html = '';
    for (const repo of repos) {
      const data = this.metrics.repos[repo];
      if (!data) continue;

      const commits = data.commits?.total_commits ?? 'N/A';
      const contributors = data.contributors?.unique_contributors ?? 'N/A';
      const freq = data.commits?.avg_commits_per_day ?? 'N/A';
      const freqDisplay = freq === 'N/A' ? 'N/A' : freq.toFixed(2);

      const range = data.commits?.time_range;
      const period = range
        ? `${range.start} to ${range.end}`
        : 'N/A';

      html += `
        <tr>
          <td><strong>${repo}</strong></td>
          <td>${commits}</td>
          <td>${contributors}</td>
          <td>${freqDisplay}</td>
          <td>${period}</td>
          <td><a href="../calculations/per_repo/${repo}/">View →</a></td>
        </tr>
      `;
    }

    tbody.innerHTML = html;
  }

  showError(message) {
    const tbody = document.getElementById('repos-tbody');
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="6" style="color: red;">Error: ${message}</td></tr>`;
    }
  }
}

// Start
document.addEventListener('DOMContentLoaded', () => {
  new Dashboard();
});
