/**
 * R&D Metrics Report Generator
 * Loads validated data from calculations/ folder
 * Presents as a coherent professional report
 */

class Report {
  constructor() {
    this.data = {};
    this.init();
  }

  async init() {
    try {
      await this.loadData();
      this.renderReport();
    } catch (err) {
      console.error('Error:', err);
      this.showError('Failed to load report data');
    }
  }

  async loadData() {
    // Load global data
    const globalSummary = await this.fetchJSON('../calculations/global/summary.json');
    const globalCommits = await this.fetchJSON('../calculations/global/commits.json');

    this.data.global = {
      ...globalSummary,
      ...globalCommits
    };

    // Load per-repo data
    this.data.repos = {};
    for (const repo of (this.data.global.repos_analyzed || [])) {
      const repoData = {};
      repoData.commits = await this.fetchJSON(`../calculations/per_repo/${repo}/commits.json`);
      repoData.contributors = await this.fetchJSON(`../calculations/per_repo/${repo}/contributors.json`);
      repoData.coverage = await this.fetchJSON(`../calculations/per_repo/${repo}/coverage.json`);
      repoData.dora_frequency = await this.fetchJSON(`../calculations/per_repo/${repo}/dora_frequency.json`);
      repoData.lead_time = await this.fetchJSON(`../calculations/per_repo/${repo}/lead_time.json`);

      this.data.repos[repo] = repoData;
    }
  }

  async fetchJSON(path) {
    try {
      const resp = await fetch(path);
      if (!resp.ok) return null;
      return await resp.json();
    } catch (err) {
      return null;
    }
  }

  renderReport() {
    this.renderDate();
    this.renderSummary();
    this.renderRepositories();
  }

  renderDate() {
    const elem = document.getElementById('report-date');
    if (elem) {
      const now = new Date();
      const formatted = now.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
      elem.textContent = `Generated ${formatted}`;
    }
  }

  renderSummary() {
    const global = this.data.global;

    // Total commits
    const totalCommits = global.total_commits || 0;
    this.updateElement('summary-commits', totalCommits);

    // Repos
    const repoCount = global.repos_analyzed?.length || 0;
    this.updateElement('summary-repos', repoCount);

    // Contributors
    let totalContributors = 0;
    for (const repo of (global.repos_analyzed || [])) {
      const contrib = this.data.repos[repo]?.contributors?.unique_contributors;
      if (contrib !== undefined && contrib !== null) {
        totalContributors += contrib;
      }
    }
    this.updateElement('summary-contributors', totalContributors);

    // Activity
    let totalActivity = 0;
    let countWithActivity = 0;
    for (const repo of (global.repos_analyzed || [])) {
      const freq = this.data.repos[repo]?.commits?.avg_commits_per_day;
      if (freq !== undefined && freq !== null && !isNaN(freq)) {
        totalActivity += freq;
        countWithActivity++;
      }
    }
    const avgActivity = countWithActivity > 0 ? (totalActivity / countWithActivity).toFixed(2) : 'N/A';
    this.updateElement('summary-activity', avgActivity);
  }

  renderRepositories() {
    const container = document.getElementById('repos-list');
    if (!container) return;

    const repos = this.data.global.repos_analyzed || [];
    if (repos.length === 0) {
      container.innerHTML = '<p style="text-align: center; color: #999;">No repositories found.</p>';
      return;
    }

    let html = '';
    for (const repo of repos) {
      const repoData = this.data.repos[repo];
      if (!repoData || !repoData.commits) continue;

      const commits = repoData.commits.total_commits || 'N/A';
      const contributors = repoData.contributors?.unique_contributors || 'N/A';
      const freq = repoData.commits.avg_commits_per_day;
      const freqDisplay = freq !== undefined && freq !== null ? freq.toFixed(2) : 'N/A';
      const range = repoData.commits.time_range;
      const period = range ? `${range.start} to ${range.end}` : 'N/A';

      html += `
        <div class="repo-card">
          <div class="repo-name">${repo}</div>
          <div class="repo-metrics">
            <div class="repo-metric">
              <div class="repo-metric-label">Commits</div>
              <div class="repo-metric-value">${commits}</div>
            </div>
            <div class="repo-metric">
              <div class="repo-metric-label">Contributors</div>
              <div class="repo-metric-value">${contributors}</div>
            </div>
            <div class="repo-metric">
              <div class="repo-metric-label">Activity/Day</div>
              <div class="repo-metric-value">${freqDisplay}</div>
            </div>
          </div>
          <div class="repo-period">Period: ${period}</div>
        </div>
      `;
    }

    container.innerHTML = html;
  }

  updateElement(id, value) {
    const elem = document.getElementById(id);
    if (elem) {
      elem.textContent = typeof value === 'number' ? value.toLocaleString() : value;
    }
  }

  showError(message) {
    console.error(message);
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  new Report();
});
