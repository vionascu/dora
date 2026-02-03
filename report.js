/**
 * R&D Metrics Report - Professional Version with Project & Date Filtering
 * Loads and displays only validated data from calculations/ folder
 */

class MetricsReport {
  constructor() {
    this.manifest = null;
    this.selectedProject = 'all';
    this.dateFilterFrom = null;
    this.dateFilterTo = null;
    // Detect base path for GitHub Pages deployment
    // window.location.pathname = /dora/public/ or /dora/public/index.html
    this.basePath = this.detectBasePath();
    this.init();
  }

  detectBasePath() {
    // From /dora/public/index.html, we need /dora/ as base
    const pathname = window.location.pathname;
    console.log('Current pathname:', pathname);

    if (pathname.includes('/dora/public')) {
      return '/dora/';
    } else if (pathname.includes('/public')) {
      return '/';
    }
    return '';
  }

  async init() {
    try {
      await this.loadManifest();
      this.setupSidebar();
      this.setupEventListeners();
      this.renderHeader();
      this.render();
      // Render charts after main content loads
      setTimeout(() => this.renderCharts(), 500);
    } catch (err) {
      console.error('Report error:', err);
      this.showError('Failed to load report');
    }
  }

  async loadManifest() {
    // GitHub Pages serves from: https://vionascu.github.io/dora/public/
    // Calculations are at: https://vionascu.github.io/dora/calculations/
    const paths = [
      this.basePath + 'calculations/MANIFEST.json',  // Absolute path using detected base (PRIMARY)
      '../calculations/MANIFEST.json',                // Parent directory relative path
      './calculations/MANIFEST.json'                  // Same directory relative path
    ];

    for (const path of paths) {
      try {
        console.log(`Trying to fetch MANIFEST from: ${path}`);
        const response = await fetch(path, { cache: 'no-cache' });
        if (response.ok) {
          console.log(`✅ Loaded MANIFEST from: ${path}`);
          this.manifest = await response.json();
          return;
        } else {
          console.log(`Response not ok from ${path}: ${response.status}`);
        }
      } catch (err) {
        console.warn(`⚠️ Failed to load from ${path}:`, err.message);
        continue;
      }
    }

    throw new Error('Failed to load MANIFEST.json from any path. Tried: ' + paths.join(', '));
  }

  setupSidebar() {
    // Attach click handler to "All Projects" button
    const allProjectsBtn = document.querySelector('[data-project="all"]');
    if (allProjectsBtn) {
      allProjectsBtn.addEventListener('click', () => this.selectProject('all'));
    }

    // Create project buttons
    const projectList = document.getElementById('project-list');
    const repos = Object.keys(this.manifest.per_repo_metrics).sort();

    repos.forEach(repo => {
      const btn = document.createElement('button');
      btn.className = 'project-btn';
      btn.textContent = repo;
      btn.dataset.project = repo;
      btn.addEventListener('click', () => this.selectProject(repo));
      projectList.appendChild(btn);
    });

    // Set initial date range based on available data
    this.setDefaultDateRange();
  }

  setDefaultDateRange() {
    const dateFromInput = document.getElementById('date-from');
    const dateToInput = document.getElementById('date-to');

    // Get min and max dates from all repos
    let minDate = null;
    let maxDate = null;

    for (const repo of Object.keys(this.manifest.per_repo_metrics)) {
      const commits = this.manifest.per_repo_metrics[repo].commits;
      if (commits && commits.period_start) {
        if (!minDate || commits.period_start < minDate) {
          minDate = commits.period_start;
        }
      }
      if (commits && commits.period_end) {
        if (!maxDate || commits.period_end > maxDate) {
          maxDate = commits.period_end;
        }
      }
    }

    if (minDate) dateFromInput.value = minDate;
    if (maxDate) dateToInput.value = maxDate;
  }

  setupEventListeners() {
    const applyBtn = document.getElementById('apply-date-filter');
    const resetBtn = document.getElementById('reset-date-filter');

    applyBtn.addEventListener('click', () => {
      const from = document.getElementById('date-from').value;
      const to = document.getElementById('date-to').value;
      this.applyDateFilter(from, to);
    });

    resetBtn.addEventListener('click', () => {
      document.getElementById('date-from').value = '';
      document.getElementById('date-to').value = '';
      this.dateFilterFrom = null;
      this.dateFilterTo = null;
      this.render();
    });
  }

  selectProject(project) {
    this.selectedProject = project;

    // Update button states
    document.querySelectorAll('.project-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    document.querySelector(`[data-project="${project}"]`).classList.add('active');

    this.render();
  }

  applyDateFilter(from, to) {
    this.dateFilterFrom = from || null;
    this.dateFilterTo = to || null;

    // Show feedback on which filter is active
    const filterBtn = document.getElementById('apply-date-filter');
    if (from || to) {
      filterBtn.textContent = `✓ Filter Active (${from || 'start'} to ${to || 'end'})`;
      filterBtn.style.background = '#007acc';
    } else {
      filterBtn.textContent = 'Apply Filter';
      filterBtn.style.background = '#28a745';
    }

    this.render();
  }

  render() {
    this.renderFindings();
    this.renderRepositories();
    this.renderEvolutionMetrics().catch(err => console.error('Evolution metrics error:', err));
  }

  renderHeader() {
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

    if (this.selectedProject === 'all') {
      // Show global metrics - with date filtering if applicable
      let filteredCommits;

      if (this.dateFilterFrom || this.dateFilterTo) {
        // Aggregate commits from projects that fall within date range
        filteredCommits = this.getAggregatedCommitsForDateRange();
      } else {
        filteredCommits = data.global_metrics['commits.json'];
      }

      this.updateElement('finding-commits', filteredCommits?.total_commits);

      const globalSummary = data.global_metrics['summary.json'];
      this.updateElement('finding-repos', globalSummary?.repos_analyzed?.length);

      const globalContributors = data.global_metrics['contributors.json'];
      this.updateElement('finding-contributors', globalContributors?.unique_contributors);

      // Velocity should also be recalculated for date range
      let globalVelocity;
      if (this.dateFilterFrom || this.dateFilterTo) {
        globalVelocity = { value: filteredCommits?.avg_commits_per_day || 0 };
      } else {
        globalVelocity = data.global_metrics['velocity.json'];
      }
      this.updateElement('finding-velocity', globalVelocity?.value);

      const globalTests = data.global_metrics['tests.json'];
      this.updateElement('finding-tests', globalTests?.total_test_files);
      this.updateElement('finding-epics', globalTests?.total_epics_found);
      this.updateElement('finding-stories', globalTests?.total_user_stories_found);

      this.attachFindingLinks('finding-commits', filteredCommits);
      this.attachFindingLinks('finding-repos', globalSummary);
      this.attachFindingLinks('finding-contributors', globalContributors);
      this.attachFindingLinks('finding-velocity', globalVelocity);
      this.attachFindingLinks('finding-tests', globalTests);
      this.attachFindingLinks('finding-epics', globalTests);
      this.attachFindingLinks('finding-stories', globalTests);
    } else {
      // Show project-specific metrics - filtered by date if applicable
      const repoData = data.per_repo_metrics[this.selectedProject];
      if (!repoData) {
        this.updateElement('finding-commits', 'N/A');
        this.updateElement('finding-repos', '1');
        this.updateElement('finding-contributors', 'N/A');
        this.updateElement('finding-velocity', 'N/A');
        this.updateElement('finding-tests', 'N/A');
        this.updateElement('finding-epics', 'N/A');
        this.updateElement('finding-stories', 'N/A');
        return;
      }

      const filteredCommits = this.getFilteredMetric(repoData.commits);
      this.updateElement('finding-commits', filteredCommits?.total_commits);
      this.updateElement('finding-repos', '1');
      this.updateElement('finding-contributors', repoData.contributors?.unique_contributors);
      this.updateElement('finding-velocity', filteredCommits?.avg_commits_per_day);
      this.updateElement('finding-tests', repoData.tests?.test_files);
      this.updateElement('finding-epics', repoData.tests?.epics);
      this.updateElement('finding-stories', repoData.tests?.user_stories);

      this.attachFindingLinks('finding-commits', filteredCommits);
      this.attachFindingLinks('finding-repos', { value: 1 });
      this.attachFindingLinks('finding-contributors', repoData.contributors);
      this.attachFindingLinks('finding-velocity', filteredCommits);
      this.attachFindingLinks('finding-tests', repoData.tests);
      this.attachFindingLinks('finding-epics', repoData.tests);
      this.attachFindingLinks('finding-stories', repoData.tests);
    }
  }

  getFilteredMetric(metric) {
    if (!metric || (!this.dateFilterFrom && !this.dateFilterTo)) {
      return metric;
    }

    // If metric has a period_start and period_end, filter based on date range
    if (metric.period_start && metric.period_end) {
      const metricStart = metric.period_start;
      const metricEnd = metric.period_end;

      const filterFrom = this.dateFilterFrom || '1900-01-01';
      const filterTo = this.dateFilterTo || '2100-12-31';

      // Check if metric is within the selected date range
      if (metricEnd < filterFrom || metricStart > filterTo) {
        // Outside range
        return { ...metric, total_commits: 0, avg_commits_per_day: 0 };
      }

      // Partial overlap - show original since we don't have granular data
      return metric;
    }

    return metric;
  }

  getAggregatedCommitsForDateRange() {
    // Aggregate commits from all projects that fall within the date range
    const filterFrom = this.dateFilterFrom || '1900-01-01';
    const filterTo = this.dateFilterTo || '2100-12-31';

    let totalCommits = 0;
    let totalDays = 0;
    let projectsInRange = 0;

    for (const repo of Object.keys(this.manifest.per_repo_metrics)) {
      const repoData = this.manifest.per_repo_metrics[repo];
      if (!repoData.commits) continue;

      const repoStart = repoData.commits.period_start;
      const repoEnd = repoData.commits.period_end;

      // Check if repo data overlaps with date range
      if (repoEnd >= filterFrom && repoStart <= filterTo) {
        totalCommits += repoData.commits.total_commits || 0;
        totalDays += repoData.commits.days_active || 1;
        projectsInRange++;
      }
    }

    const avgCommitsPerDay = totalDays > 0 ? (totalCommits / totalDays) : 0;

    return {
      total_commits: totalCommits,
      avg_commits_per_day: Math.round(avgCommitsPerDay * 100) / 100,
      period_start: filterFrom,
      period_end: filterTo,
      method: `Aggregated from ${projectsInRange} project(s) in date range`
    };
  }

  getUncoveredEpics(repo) {
    /**Calculate which epics don't have test coverage */
    const scanData = this.manifest.github_scan_artifacts || {};
    const allEpics = scanData.epics?.[repo] || [];
    const coveredEpics = scanData.epic_coverage?.[repo] || [];

    if (!allEpics || allEpics.length === 0) return [];

    return allEpics.filter(epic => !coveredEpics.includes(epic));
  }

  renderRepositories() {
    const container = document.getElementById('repos-container');
    if (!container) return;

    const repoData = this.manifest.per_repo_metrics;
    let repoNames;

    if (this.selectedProject === 'all') {
      repoNames = Object.keys(repoData).sort();
    } else {
      repoNames = [this.selectedProject];
    }

    if (repoNames.length === 0) {
      container.innerHTML = '<p>No repositories found.</p>';
      return;
    }

    let html = '';
    for (const repo of repoNames) {
      const data = repoData[repo];
      if (!data) continue;

      const tests = data.tests || {};
      const uncoveredEpics = this.getUncoveredEpics(repo);
      const dropdownId = `uncovered-${repo.replace(/\s+/g, '-')}`;

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
            <tr>
              <td>Uncovered Epics</td>
              <td>
                ${uncoveredEpics.length > 0
                  ? `<details><summary>${uncoveredEpics.length} epic(s) not covered by tests</summary><ul style="margin: 0.5rem 0; padding-left: 1.5rem;">${uncoveredEpics.map(e => `<li>${e}</li>`).join('')}</ul></details>`
                  : '<span style="color: #28a745;">✓ All epics have test coverage</span>'}
              </td>
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

  async renderEvolutionMetrics() {
    const container = document.getElementById('evolution-container');
    if (!container) {
      // Create container if it doesn't exist
      const reposContainer = document.getElementById('repos-container');
      if (!reposContainer) return;

      const evolutionDiv = document.createElement('div');
      evolutionDiv.id = 'evolution-container';
      evolutionDiv.style.marginTop = '3rem';
      reposContainer.parentNode.insertBefore(evolutionDiv, reposContainer.nextSibling);
    }

    const repoData = this.manifest.per_repo_metrics;
    let repoNames;

    if (this.selectedProject === 'all') {
      repoNames = Object.keys(repoData).sort();
    } else {
      repoNames = [this.selectedProject];
    }

    let html = '<div style="background: #f5f5f5; padding: 2rem; border-radius: 8px; margin-top: 2rem;">';
    html += '<h2 style="margin-top: 0;">Project Evolution & Analysis</h2>';

    for (const repo of repoNames) {
      const data = repoData[repo];
      if (!data) continue;

      html += `<div style="background: white; padding: 1.5rem; margin: 1rem 0; border-radius: 6px; border-left: 4px solid #007acc;">`;
      html += `<h3 style="margin-top: 0;">${repo} - Evolution Metrics</h3>`;

      // Load evolution metrics files
      let velocity, contributors, refactor, quality, aiAnalysis;

      try {
        // Try to load velocity trend
        if (data['velocity_trend.json'] || data.velocity_trend) {
          const velocityPath = data['velocity_trend.json']?.file || `./calculations/per_repo/${repo}/velocity_trend.json`;
          velocity = await this.loadJSON(velocityPath);
        }

        // Try to load refactorization activity
        if (data['refactorization_activity.json'] || data.refactorization_activity) {
          const refactorPath = data['refactorization_activity.json']?.file || `./calculations/per_repo/${repo}/refactorization_activity.json`;
          refactor = await this.loadJSON(refactorPath);
        }

        // Try to load code quality evolution
        if (data['code_quality_evolution.json'] || data.code_quality_evolution) {
          const qualityPath = data['code_quality_evolution.json']?.file || `./calculations/per_repo/${repo}/code_quality_evolution.json`;
          quality = await this.loadJSON(qualityPath);
        }

        // Try to load AI indicators
        if (data['ai_usage_indicators.json'] || data.ai_usage_indicators) {
          const aiPath = data['ai_usage_indicators.json']?.file || `./calculations/per_repo/${repo}/ai_usage_indicators.json`;
          aiAnalysis = await this.loadJSON(aiPath);
        }
      } catch (err) {
        console.warn(`Error loading evolution metrics for ${repo}:`, err);
      }

      // Velocity Trends
      if (velocity) {
        html += this.renderVelocityTrend(velocity);
      }

      // Contributor Growth
      if (contributors) {
        html += this.renderContributorGrowth(contributors);
      }

      // Refactorization Activity
      if (refactor) {
        html += this.renderRefactorizationActivity(refactor);
      }

      // Code Quality Evolution
      if (quality) {
        html += this.renderQualityEvolution(quality);
      }

      // AI Analysis
      if (aiAnalysis) {
        html += this.renderAIAnalysis(aiAnalysis);
      }

      html += `</div>`;
    }

    // Global AI Analysis
    const globalAI = this.manifest.global_metrics['ai_usage_analysis.json'];
    if (globalAI && this.selectedProject === 'all') {
      html += `<div style="background: #fff3cd; padding: 1.5rem; margin: 1rem 0; border-radius: 6px; border-left: 4px solid #ff9800;">`;
      html += `<h3 style="margin-top: 0;">🤖 Organization-Wide AI Usage Analysis</h3>`;
      html += this.renderGlobalAIAnalysis(globalAI);
      html += `</div>`;
    }

    html += '</div>';
    document.getElementById('evolution-container').innerHTML = html;
  }

  async loadJSON(path) {
    // Extract just the calculation path (remove ./calculations/ or calculations/ prefix)
    let calcPath = path;
    if (path.startsWith('./calculations/')) {
      calcPath = path.replace('./calculations/', '');
    } else if (path.startsWith('calculations/')) {
      calcPath = path.replace('calculations/', '');
    } else if (path.startsWith('/calculations/')) {
      calcPath = path.replace('/calculations/', '');
    }

    // Build paths using absolute base path first (most reliable)
    const paths = [
      this.basePath + 'calculations/' + calcPath,     // Absolute path (PRIMARY - MOST RELIABLE)
      '../calculations/' + calcPath,                   // Relative path from public folder
      './calculations/' + calcPath,                    // Same directory
      path                                             // Original path as fallback
    ];

    // Remove duplicates and empty paths
    const uniquePaths = [...new Set(paths)].filter(p => p && p.trim());

    for (const p of uniquePaths) {
      try {
        const response = await fetch(p, { cache: 'no-cache' });
        if (response.ok) {
          console.log(`✅ Loaded from: ${p}`);
          return await response.json();
        }
      } catch (err) {
        // Silent fail, try next path
        continue;
      }
    }
    console.warn(`⚠️ Could not load: ${path} from paths: ${uniquePaths.join(', ')}`);
    return null;
  }

  renderVelocityTrend(velocity) {
    const weeksActive = velocity.weeks_active || 0;
    const avgPerWeek = velocity.avg_commits_per_week || 0;
    const total = velocity.total_commits || 0;

    return `
      <div style="margin: 1rem 0; padding: 1rem; background: #f9f9f9; border-radius: 4px;">
        <h4>📈 Velocity Trends</h4>
        <ul style="margin: 0.5rem 0; line-height: 1.8;">
          <li><strong>Total Commits:</strong> ${total}</li>
          <li><strong>Weeks Active:</strong> ${weeksActive}</li>
          <li><strong>Avg Commits/Week:</strong> ${avgPerWeek}</li>
          <li><strong>Period:</strong> ${velocity.time_range.start} to ${velocity.time_range.end}</li>
        </ul>
      </div>
    `;
  }

  renderContributorGrowth(contributors) {
    const total = contributors.total_contributors || 0;
    const monthlyAvg = contributors.avg_new_contributors_per_month || 0;
    const start = contributors.first_contributor_date || 'N/A';
    const end = contributors.latest_contributor_date || 'N/A';

    return `
      <div style="margin: 1rem 0; padding: 1rem; background: #f9f9f9; border-radius: 4px;">
        <h4>👥 Team Growth</h4>
        <ul style="margin: 0.5rem 0; line-height: 1.8;">
          <li><strong>Total Contributors:</strong> ${total}</li>
          <li><strong>Avg New/Month:</strong> ${monthlyAvg}</li>
          <li><strong>First Contributor:</strong> ${start}</li>
          <li><strong>Latest Contributor:</strong> ${end}</li>
        </ul>
      </div>
    `;
  }

  renderRefactorizationActivity(refactor) {
    const totalRefactor = refactor.total_refactor_commits || 0;
    const percentage = refactor.refactor_percentage || 0;
    const events = refactor.refactor_events || {};

    let eventsList = '';
    for (const [key, count] of Object.entries(events)) {
      if (count > 0) {
        eventsList += `<li>${key}: ${count}</li>`;
      }
    }

    return `
      <div style="margin: 1rem 0; padding: 1rem; background: #f9f9f9; border-radius: 4px;">
        <h4>🔧 Refactorization Activity</h4>
        <ul style="margin: 0.5rem 0; line-height: 1.8;">
          <li><strong>Refactor Commits:</strong> ${totalRefactor} (${percentage}%)</li>
          <li><strong>Activities:</strong></li>
          <ul style="margin-left: 1.5rem;">${eventsList || '<li>None detected</li>'}</ul>
        </ul>
      </div>
    `;
  }

  renderQualityEvolution(quality) {
    const grade = quality.quality_grade || 'N/A';
    const status = quality.quality_status || 'Unknown';
    const coverage = quality.coverage_percentage || 0;
    const commits = quality.total_commits || 0;
    const maturity = quality.maturity_score || 0;

    const gradeColor = {
      'A': '#28a745',
      'B': '#17a2b8',
      'C': '#ffc107',
      'D': '#fd7e14',
      'F': '#dc3545'
    }[grade] || '#6c757d';

    return `
      <div style="margin: 1rem 0; padding: 1rem; background: #f9f9f9; border-radius: 4px;">
        <h4>📊 Code Quality Evolution</h4>
        <ul style="margin: 0.5rem 0; line-height: 1.8;">
          <li><strong>Quality Grade:</strong> <span style="background: ${gradeColor}; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">${grade}</span></li>
          <li><strong>Status:</strong> ${status}</li>
          <li><strong>Coverage:</strong> ${coverage}%</li>
          <li><strong>Active Commits:</strong> ${commits}</li>
          <li><strong>Maturity Score:</strong> ${maturity}/100</li>
        </ul>
      </div>
    `;
  }

  renderAIAnalysis(aiAnalysis) {
    const score = aiAnalysis.ai_probability_score || 0;
    const interpretation = aiAnalysis.ai_score_interpretation || 'Unknown';
    const aiCommits = aiAnalysis.ai_attributed_commits || 0;
    const percentage = aiAnalysis.ai_commits_percentage || 0;
    const mentions = aiAnalysis.explicit_ai_mentions || {};
    const patterns = aiAnalysis.code_pattern_analysis || {};

    let mentionsHTML = '';
    for (const [framework, count] of Object.entries(mentions)) {
      if (count > 0) {
        mentionsHTML += `<li>${framework}: ${count} commit${count > 1 ? 's' : ''}</li>`;
      }
    }

    let patternsHTML = '';
    for (const [pattern, count] of Object.entries(patterns)) {
      if (count > 0) {
        patternsHTML += `<li>${pattern}: ${count}</li>`;
      }
    }

    const scoreColor = score < 20 ? '#28a745' : score < 40 ? '#17a2b8' : score < 60 ? '#ffc107' : score < 80 ? '#fd7e14' : '#dc3545';

    return `
      <div style="margin: 1rem 0; padding: 1rem; background: #f0f4ff; border-radius: 4px;">
        <h4>🤖 AI Usage Indicators</h4>
        <ul style="margin: 0.5rem 0; line-height: 1.8;">
          <li><strong>AI Probability Score:</strong> <span style="background: ${scoreColor}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">${score}/100</span></li>
          <li><strong>Interpretation:</strong> ${interpretation}</li>
          <li><strong>AI-Attributed Commits:</strong> ${aiCommits} (${percentage}%)</li>
          ${mentionsHTML ? `<li><strong>AI Frameworks Mentioned:</strong><ul style="margin-left: 1.5rem;">${mentionsHTML}</ul></li>` : ''}
          ${patternsHTML ? `<li><strong>Code Patterns Detected:</strong><ul style="margin-left: 1.5rem;">${patternsHTML}</ul></li>` : ''}
        </ul>
      </div>
    `;
  }

  renderGlobalAIAnalysis(globalAI) {
    const score = globalAI.ai_probability_score || 0;
    const interpretation = globalAI.score_interpretation || 'Unknown';
    const aiCommits = globalAI.total_ai_commits || 0;
    const percentage = globalAI.global_ai_percentage || 0;
    const rankings = globalAI.repositories_ranked || [];

    const scoreColor = score < 20 ? '#28a745' : score < 40 ? '#17a2b8' : score < 60 ? '#ffc107' : score < 80 ? '#fd7e14' : '#dc3545';

    let rankingsHTML = '';
    for (const rank of rankings) {
      rankingsHTML += `<li>${rank.repo}: ${rank.score}/100 (${rank.ai_commits} commits)</li>`;
    }

    return `
      <ul style="margin: 0.5rem 0; line-height: 1.8;">
        <li><strong>Organization AI Score:</strong> <span style="background: ${scoreColor}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">${score}/100</span></li>
        <li><strong>Assessment:</strong> ${interpretation}</li>
        <li><strong>Total AI Commits:</strong> ${aiCommits} (${percentage}% of all commits)</li>
        ${rankingsHTML ? `<li><strong>Repository Rankings (by AI usage):</strong><ul style="margin-left: 1.5rem;">${rankingsHTML}</ul></li>` : ''}
      </ul>
    `;
  }

  showError(message) {
    const container = document.getElementById('repos-container');
    if (container) {
      container.innerHTML = `<p style="color: red;">Error: ${message}</p>`;
    }
  }

  async loadJSON(path) {
    const response = await fetch(path, { cache: 'no-cache' });
    if (!response.ok) throw new Error(`Failed to load ${path}: ${response.status}`);
    return await response.json();
  }

  async renderCharts() {
    try {
      console.log('📊 Loading real data for charts from calculations/');

      // Load real data from calculations
      const velocityData = await this.loadJSON(this.basePath + 'calculations/global/velocity.json').catch(e => {
        console.warn('⚠️ Velocity data not available:', e.message);
        return null;
      });

      const globalContributorsData = await this.loadJSON(this.basePath + 'calculations/global/contributors.json').catch(e => {
        console.warn('⚠️ Global contributors count not available:', e.message);
        return null;
      });

      const commitsData = await this.loadJSON(this.basePath + 'calculations/global/commits.json').catch(e => {
        console.warn('⚠️ Commits data not available:', e.message);
        return null;
      });

      // Load per-repo contributor data to get individual contributor breakdown
      let perRepoContributorsData = [];
      const repos = ['RnDMetrics', 'TrailEquip', 'TrailWaze'];
      for (const repo of repos) {
        const repoContribData = await this.loadJSON(this.basePath + `calculations/per_repo/${repo}/contributors.json`).catch(e => {
          console.warn(`⚠️ Contributor data for ${repo} not available:`, e.message);
          return null;
        });
        if (repoContribData) {
          perRepoContributorsData.push({ repo, data: repoContribData });
        }
      }

      // Render velocity trend chart (Line Chart) - from real data
      this.renderVelocityChart(velocityData);

      // Render test coverage chart (Donut Chart) - from real data or N/A
      this.renderCoverageChart(commitsData);

      // Render contributors chart (Bar Chart) - from real per-repo data
      this.renderContributorsChart(globalContributorsData, perRepoContributorsData);
    } catch (err) {
      console.warn('Chart rendering error:', err);
      // Charts are optional, don't fail the whole report
    }
  }

  renderVelocityChart(velocityData) {
    const ctx = document.getElementById('velocityChart');
    const container = ctx?.parentElement;
    if (!ctx || !container) return;

    if (!velocityData || !velocityData.weekly_data) {
      container.innerHTML = '<p style="color: #999; padding: 2rem;">📊 N/A - Velocity data not available</p>';
      this.addDataSourceNote(container, 'No data available', 'calculations/global/velocity.json');
      return;
    }

    // Extract real weekly data from calculations
    const weeklyData = velocityData.weekly_data;
    const labels = Object.keys(weeklyData).sort();
    const data = labels.map(week => weeklyData[week]);

    console.log('✅ Velocity Chart - Real data loaded:', { weeks: labels.length, dataPoints: data });

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Commits/Week',
          data: data,
          borderColor: '#0366d6',
          backgroundColor: 'rgba(3, 102, 214, 0.05)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#0366d6',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: function(context) {
                return 'Week: ' + context[0].label;
              },
              label: function(context) {
                return 'Commits: ' + context.parsed.y;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { color: '#666' },
            grid: { color: 'rgba(0, 0, 0, 0.05)' }
          },
          x: {
            ticks: { color: '#666' },
            grid: { display: false }
          }
        }
      }
    });

    this.addDataSourceNote(container, `Data from ${labels.length} weeks`, 'calculations/global/velocity.json');
  }

  renderCoverageChart(commitsData) {
    const ctx = document.getElementById('coverageChart');
    const container = ctx?.parentElement;
    if (!ctx || !container) return;

    // Try to get coverage data
    let coveragePercentage = null;
    if (commitsData && commitsData.coverage_percentage !== undefined) {
      coveragePercentage = commitsData.coverage_percentage;
    }

    if (coveragePercentage === null || coveragePercentage === undefined) {
      container.innerHTML = '<p style="color: #999; padding: 2rem;">🎯 N/A - Test coverage data not available (requires local test run)</p>';
      this.addDataSourceNote(container, 'No data available', 'calculations/global/commits.json');
      return;
    }

    const testedPercentage = coveragePercentage;
    const unterstedPercentage = 100 - coveragePercentage;

    console.log('✅ Coverage Chart - Real data loaded:', { tested: testedPercentage + '%', untested: unterstedPercentage + '%' });

    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Tested Code', 'Untested Code'],
        datasets: [{
          data: [testedPercentage, unterstedPercentage],
          backgroundColor: ['#28a745', '#dc3545'],
          borderColor: '#fff',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: '#666', font: { size: 12 } }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.label + ': ' + context.parsed + '%';
              }
            }
          }
        }
      }
    });

    this.addDataSourceNote(container, `${testedPercentage}% tested`, 'calculations/global/commits.json');
  }

  renderContributorsChart(globalContributorsData, perRepoContributorsData) {
    const ctx = document.getElementById('contributorsChart');
    const container = ctx?.parentElement;
    if (!ctx || !container) return;

    // Build chart data from per-repo contributor counts
    const repoContributors = [];

    for (const { repo, data } of perRepoContributorsData) {
      if (data && data.unique_contributors !== undefined) {
        repoContributors.push({
          repo: repo,
          contributors: data.unique_contributors,
          timeRange: data.time_range
        });
      }
    }

    if (repoContributors.length === 0) {
      // Show total count if we have it
      if (globalContributorsData && globalContributorsData.unique_contributors) {
        container.innerHTML = `<p style="color: #999; padding: 2rem;">👥 ${globalContributorsData.unique_contributors} total contributors (breakdown not available)</p>`;
        this.addDataSourceNote(container, `${globalContributorsData.unique_contributors} unique contributors total`, 'calculations/global/contributors.json');
      } else {
        container.innerHTML = '<p style="color: #999; padding: 2rem;">👥 N/A - No contributor data available</p>';
        this.addDataSourceNote(container, 'No breakdown data', 'calculations/per_repo/*/contributors.json');
      }
      return;
    }

    // Sort by repository name for consistent display
    repoContributors.sort((a, b) => a.repo.localeCompare(b.repo));

    // Prepare chart data
    const labels = repoContributors.map(r => r.repo);
    const data = repoContributors.map(r => r.contributors);

    console.log('✅ Contributors Chart - Real data loaded from GitHub:', { repositories: labels, contributors: data });

    // Determine colors based on contributor count (green for 2+, orange for 1)
    const backgroundColor = data.map(count => {
      if (count >= 2) return 'rgba(40, 167, 69, 0.8)';  // Green - good
      return 'rgba(255, 193, 7, 0.8)';  // Yellow - warning
    });

    const borderColor = data.map(count => {
      if (count >= 2) return '#28a745';  // Green
      return '#ffc107';  // Yellow
    });

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Number of Contributors',
          data: data,
          backgroundColor: backgroundColor,
          borderColor: borderColor,
          borderWidth: 2
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(context) {
                const count = context.parsed.x;
                const status = count >= 2 ? '✓ Good' : '⚠️ Warning - Single contributor';
                return `Contributors: ${count} (${status})`;
              }
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: {
              color: '#666',
              stepSize: 1
            },
            grid: { color: 'rgba(0, 0, 0, 0.05)' },
            title: {
              display: true,
              text: 'Number of Contributors'
            }
          },
          y: {
            ticks: { color: '#666' },
            grid: { display: false }
          }
        }
      }
    });

    const totalContributors = data.reduce((a, b) => a + b, 0);
    this.addDataSourceNote(container, `${labels.length} projects, ${totalContributors} total contributors`, 'calculations/per_repo/*/contributors.json');
  }

  addDataSourceNote(container, description, source) {
    if (!container) return;
    const sourceNote = document.createElement('div');
    sourceNote.className = 'chart-data-source';
    sourceNote.innerHTML = `<small>📊 Data: ${description} | Source: <code>${source}</code></small>`;
    container.appendChild(sourceNote);
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  new MetricsReport();
});
