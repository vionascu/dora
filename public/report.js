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
    // Store chart instances so we can destroy and recreate them
    this.charts = {
      velocity: null,
      coverage: null,
      contributors: null
    };
    // Detect base path for GitHub Pages deployment
    // window.location.pathname = /dora/public/ or /dora/public/index.html
    this.basePath = this.detectBasePath();
    this.init();
  }

  detectBasePath() {
    // Determine base path based on deployment context
    const pathname = window.location.pathname;
    const hostname = window.location.hostname;
    console.log('Current pathname:', pathname, 'hostname:', hostname);

    // GitLab Artifact Preview: /-/dora/-/jobs/JOBID/artifacts/public/index.html
    // Files are relative to public/ folder, so calculations/ is at ./calculations/
    if (pathname.includes('/-/') && pathname.includes('/artifacts/')) {
      console.log('🔧 Detected GitLab artifact preview URL');
      return './';
    }
    // GitHub Pages: /dora/public/index.html -> /dora/
    if (pathname.includes('/dora/public')) {
      return '/dora/';
    }
    // GitLab Pages: /public/index.html -> /
    if (pathname.includes('/public') && !hostname.includes('localhost')) {
      return '/';
    }
    // Local development (localhost or 127.0.0.1): served from project root via http.server
    // URL is http://localhost:8002/public/index.html
    // So pathname = /public/index.html, but calculations are at /calculations/
    // We need to use ../calculations/ which resolves correctly from /public/
    if (hostname.includes('localhost') || hostname === '127.0.0.1') {
      return '../';
    }
    // Default
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
      const filterBtn = document.getElementById('apply-date-filter');
      filterBtn.textContent = 'Apply Filter';
      filterBtn.style.background = '#28a745';
      this.render();
      // Re-render charts with reset date filter
      setTimeout(() => this.renderCharts(), 500);
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

    // Re-render charts for the selected project
    console.log('📊 Project selected:', project);
    setTimeout(() => this.renderCharts(), 500);
  }

  applyDateFilter(from, to) {
    this.dateFilterFrom = from || null;
    this.dateFilterTo = to || null;

    console.log('🗓️  DATE FILTER APPLIED:', { from: this.dateFilterFrom, to: this.dateFilterTo });

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
    // Re-render charts with new date filter
    console.log('📊 Re-rendering charts in 500ms...');
    setTimeout(() => this.renderCharts(), 500);
  }

  render() {
    this.renderFindings().catch(err => console.error('Findings render error:', err));
    this.renderRepositories().catch(err => console.error('Repositories render error:', err));
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

  async renderFindings() {
    const data = this.manifest;

    if (this.selectedProject === 'all') {
      // Show global metrics - with date filtering if applicable
      let filteredCommits;

      if (this.dateFilterFrom || this.dateFilterTo) {
        // Aggregate commits from projects that fall within date range
        filteredCommits = await this.getAggregatedCommitsForDateRange();
        console.log('📊 Metrics updated for date range:', { from: this.dateFilterFrom, to: this.dateFilterTo, commits: filteredCommits.total_commits, avgPerDay: filteredCommits.avg_commits_per_day });
      } else {
        filteredCommits = data.global_metrics['commits.json'];
      }

      this.updateElement('finding-commits', filteredCommits?.total_commits);

      const globalSummary = data.global_metrics['summary.json'];
      this.updateElement('finding-repos', globalSummary?.repos_analyzed?.length);

      const globalContributors = data.global_metrics['contributors.json'];
      const contributorCount = globalContributors?.unique_contributors;

      if (!contributorCount) {
        console.warn('⚠️ Contributors data not available in manifest:', { globalContributors });
      } else {
        console.log('✅ Team Size (Global Contributors):', contributorCount);
      }

      this.updateElement('finding-contributors', contributorCount || 'N/A');

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

      // Calculate total LOC across all repos
      let totalLOC = 0;
      for (const repo of Object.keys(data.per_repo_metrics)) {
        const locMetric = data.per_repo_metrics[repo].loc;
        if (locMetric && locMetric.total_lines_of_code) {
          totalLOC += locMetric.total_lines_of_code;
        }
      }
      this.updateElement('finding-loc', totalLOC > 0 ? totalLOC : 'N/A');

      this.attachFindingLinks('finding-commits', filteredCommits);
      this.attachFindingLinks('finding-repos', globalSummary);
      this.attachFindingLinks('finding-contributors', globalContributors);
      this.attachFindingLinks('finding-velocity', globalVelocity);
      this.attachFindingLinks('finding-tests', globalTests);
      this.attachFindingLinks('finding-epics', globalTests);
      this.attachFindingLinks('finding-stories', globalTests);
      this.attachFindingLinks('finding-loc', { value: totalLOC > 0 ? totalLOC : 'N/A' });
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
        this.updateElement('finding-loc', 'N/A');
        return;
      }

      const filteredCommits = this.getFilteredMetric(repoData.commits);
      this.updateElement('finding-commits', filteredCommits?.total_commits);
      this.updateElement('finding-repos', '1');

      const repoContributorCount = repoData.contributors?.unique_contributors;
      if (!repoContributorCount) {
        console.warn(`⚠️ Contributor data not available for ${this.selectedProject}:`, { contributors: repoData.contributors });
      } else {
        console.log(`✅ Contributors for ${this.selectedProject}:`, repoContributorCount);
      }
      this.updateElement('finding-contributors', repoContributorCount || 'N/A');

      this.updateElement('finding-velocity', filteredCommits?.avg_commits_per_day);
      this.updateElement('finding-tests', repoData.tests?.test_files);
      this.updateElement('finding-epics', repoData.tests?.epics);
      this.updateElement('finding-stories', repoData.tests?.user_stories);
      this.updateElement('finding-loc', repoData.loc?.total_lines_of_code || 'N/A');

      this.attachFindingLinks('finding-commits', filteredCommits);
      this.attachFindingLinks('finding-repos', { value: 1 });
      this.attachFindingLinks('finding-contributors', repoData.contributors);
      this.attachFindingLinks('finding-velocity', filteredCommits);
      this.attachFindingLinks('finding-tests', repoData.tests);
      this.attachFindingLinks('finding-epics', repoData.tests);
      this.attachFindingLinks('finding-stories', repoData.tests);
      this.attachFindingLinks('finding-loc', repoData.loc);
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

  async getAggregatedCommitsForDateRange() {
    // Aggregate ACTUAL commits from projects within date range using velocity data
    const filterFrom = this.dateFilterFrom || '1900-01-01';
    const filterTo = this.dateFilterTo || '2100-12-31';

    const filterFromDate = new Date(filterFrom);
    const filterToDate = new Date(filterTo);

    let totalCommits = 0;
    let activeDays = new Set();
    let projectsInRange = 0;

    for (const repo of Object.keys(this.manifest.per_repo_metrics)) {
      const repoData = this.manifest.per_repo_metrics[repo];
      if (!repoData.commits) continue;

      const repoStart = repoData.commits.period_start;
      const repoEnd = repoData.commits.period_end;

      // Check if repo data overlaps with date range
      if (repoEnd >= filterFrom && repoStart <= filterTo) {
        projectsInRange++;

        // Try to load velocity_trend for accurate filtered counts
        try {
          const velocityPath = this.basePath + `calculations/per_repo/${repo}/velocity_trend.json`;
          const velocityData = await this.loadJSON(velocityPath);

          if (velocityData && velocityData.weekly_data) {
            // Filter weekly data by date range
            const filteredWeeks = this.filterWeeklyDataByDateRange(velocityData.weekly_data);
            const weeklyCommits = Object.values(filteredWeeks).reduce((sum, val) => sum + val, 0);
            totalCommits += weeklyCommits;

            // Count unique weeks (approximate days)
            activeDays.add(Object.keys(filteredWeeks).length * 7);
          }
        } catch (err) {
          // If velocity data unavailable, fall back to basic calculation
          console.warn(`Could not load velocity for ${repo}, using basic calculation`);
          totalCommits += repoData.commits.total_commits || 0;
          activeDays.add(repoData.commits.days_active || 1);
        }
      }
    }

    const totalDays = Array.from(activeDays).reduce((a, b) => a + b, 0) || 1;
    const avgCommitsPerDay = totalDays > 0 ? (totalCommits / totalDays) : 0;

    return {
      total_commits: totalCommits,
      avg_commits_per_day: Math.round(avgCommitsPerDay * 100) / 100,
      period_start: filterFrom,
      period_end: filterTo,
      method: `Filtered from ${projectsInRange} project(s) within selected date range`
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

  async renderRepositories() {
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

      // Apply date filtering to commits data if filter is active
      let filteredCommits = data.commits;
      let hasDateFilter = this.dateFilterFrom || this.dateFilterTo;

      // If date filter is active, try to load velocity data for accurate filtering
      if (hasDateFilter) {
        try {
          const velocityPath = this.basePath + `calculations/per_repo/${repo}/velocity_trend.json`;
          const velocityData = await this.loadJSON(velocityPath);
          if (velocityData && velocityData.weekly_data) {
            const filteredWeeks = this.filterWeeklyDataByDateRange(velocityData.weekly_data);
            const weeklyCommits = Object.values(filteredWeeks).reduce((sum, val) => sum + val, 0);
            const weeksCount = Object.keys(filteredWeeks).length;
            const avgPerDay = weeksCount > 0 ? (weeklyCommits / (weeksCount * 7)) : 0;

            filteredCommits = {
              ...data.commits,
              total_commits: weeklyCommits,
              avg_commits_per_day: Math.round(avgPerDay * 100) / 100,
              period_start: this.dateFilterFrom || data.commits.period_start,
              period_end: this.dateFilterTo || data.commits.period_end,
              days_active: weeksCount * 7,
              _isFiltered: true
            };
          }
        } catch (err) {
          // Fall back to base filtering
          filteredCommits = this.getFilteredMetric(data.commits);
        }
      }

      html += `
        <div class="repo-detail-card">
          <div class="repo-detail-name">${repo}</div>
          <table class="repo-metrics-table">
            <tr>
              <td>Total Commits</td>
              <td>${this.formatValue(filteredCommits?.total_commits)}${this.renderMetricLinks(filteredCommits)}${hasDateFilter && filteredCommits?._isFiltered ? ' <span style="color: #ff9800; font-size: 0.9em;">(filtered)</span>' : ''}</td>
            </tr>
            <tr>
              <td>Contributors</td>
              <td>${this.formatValue(data.contributors?.unique_contributors)}${this.renderMetricLinks(data.contributors)}</td>
            </tr>
            <tr>
              <td>Daily Activity</td>
              <td>${this.formatValue(filteredCommits?.avg_commits_per_day, 'commits/day')}${this.renderMetricLinks(filteredCommits)}${hasDateFilter && filteredCommits?._isFiltered ? ' <span style="color: #ff9800; font-size: 0.9em;">(filtered)</span>' : ''}</td>
            </tr>
            <tr>
              <td>Active Period</td>
              <td>${this.formatRange(filteredCommits?.period_start, filteredCommits?.period_end)}${this.renderMetricLinks(filteredCommits)}</td>
            </tr>
            <tr>
              <td>Days Active</td>
              <td>${this.formatValue(filteredCommits?.days_active)}${this.renderMetricLinks(filteredCommits)}${hasDateFilter && filteredCommits?._isFiltered ? ' <span style="color: #ff9800; font-size: 0.9em;">(filtered)</span>' : ''}</td>
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
          const velocityPath = data['velocity_trend.json']?.file || this.basePath + `calculations/per_repo/${repo}/velocity_trend.json`;
          velocity = await this.loadJSON(velocityPath);
        }

        // Try to load refactorization activity
        if (data['refactorization_activity.json'] || data.refactorization_activity) {
          const refactorPath = data['refactorization_activity.json']?.file || this.basePath + `calculations/per_repo/${repo}/refactorization_activity.json`;
          refactor = await this.loadJSON(refactorPath);
        }

        // Try to load code quality evolution
        if (data['code_quality_evolution.json'] || data.code_quality_evolution) {
          const qualityPath = data['code_quality_evolution.json']?.file || this.basePath + `calculations/per_repo/${repo}/code_quality_evolution.json`;
          quality = await this.loadJSON(qualityPath);
        }

        // Try to load AI indicators
        if (data['ai_usage_indicators.json'] || data.ai_usage_indicators) {
          const aiPath = data['ai_usage_indicators.json']?.file || this.basePath + `calculations/per_repo/${repo}/ai_usage_indicators.json`;
          aiAnalysis = await this.loadJSON(aiPath);
        }
      } catch (err) {
        console.warn(`Error loading evolution metrics for ${repo}:`, err.message);
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

  async renderCharts() {
    try {
      console.log('📊 Loading real data for charts - Project:', this.selectedProject);

      // Determine if we're showing global or per-repo data
      if (this.selectedProject === 'all') {
        // Global view - aggregate from all repos
        const globalContributorsData = await this.loadJSON(this.basePath + 'calculations/global/contributors.json').catch(e => {
          console.warn('⚠️ Global contributors count not available:', e.message);
          return null;
        });

        const commitsData = await this.loadJSON(this.basePath + 'calculations/global/commits.json').catch(e => {
          console.warn('⚠️ Commits data not available:', e.message);
          return null;
        });

        // For global view, aggregate velocity from all repos in MANIFEST
        let aggregatedWeeklyData = {};
        if (this.manifest && this.manifest.per_repo_metrics) {
          for (const repo of Object.keys(this.manifest.per_repo_metrics)) {
            const repoVelocity = await this.loadJSON(this.basePath + `calculations/per_repo/${repo}/velocity_trend.json`).catch(e => {
              console.warn(`⚠️ Velocity data for ${repo} not available:`, e.message);
              return null;
            });
            if (repoVelocity && repoVelocity.weekly_data) {
              // Aggregate weekly data
              for (const [week, count] of Object.entries(repoVelocity.weekly_data)) {
                aggregatedWeeklyData[week] = (aggregatedWeeklyData[week] || 0) + count;
              }
            }
          }
        }

        const aggregatedVelocityData = Object.keys(aggregatedWeeklyData).length > 0
          ? { weekly_data: aggregatedWeeklyData }
          : null;

        // Load per-repo contributor data
        let perRepoContributorsData = [];
        if (this.manifest && this.manifest.per_repo_metrics) {
          for (const repo of Object.keys(this.manifest.per_repo_metrics)) {
            const repoContribData = await this.loadJSON(this.basePath + `calculations/per_repo/${repo}/contributors.json`).catch(e => {
              console.warn(`⚠️ Contributor data for ${repo} not available:`, e.message);
              return null;
            });
            if (repoContribData) {
              perRepoContributorsData.push({ repo, data: repoContribData });
            }
          }
        }

        // Render global charts
        this.renderVelocityChart(aggregatedVelocityData);
        this.renderCoverageChart(commitsData);
        await this.renderContributorsChart(globalContributorsData, perRepoContributorsData);
      } else {
        // Per-repo view - load specific project data
        const repoVelocity = await this.loadJSON(this.basePath + `calculations/per_repo/${this.selectedProject}/velocity_trend.json`).catch(e => {
          console.warn(`⚠️ Velocity data for ${this.selectedProject}:`, e.message);
          return null;
        });

        const repoCoverage = await this.loadJSON(this.basePath + `calculations/per_repo/${this.selectedProject}/coverage.json`).catch(e => {
          console.warn(`⚠️ Coverage data for ${this.selectedProject}:`, e.message);
          return null;
        });

        const repoContributors = await this.loadJSON(this.basePath + `calculations/per_repo/${this.selectedProject}/contributors.json`).catch(e => {
          console.warn(`⚠️ Contributors data for ${this.selectedProject}:`, e.message);
          return null;
        });

        // Render per-repo charts
        this.renderVelocityChart(repoVelocity);
        this.renderCoverageChart(repoCoverage);
        this.renderContributorsChartPerRepo(repoContributors);
      }
    } catch (err) {
      console.warn('Chart rendering error:', err);
      // Charts are optional, don't fail the whole report
    }
  }

  filterWeeklyDataByDateRange(weeklyData) {
    if (!this.dateFilterFrom && !this.dateFilterTo) {
      return weeklyData;
    }

    const filterFrom = this.dateFilterFrom ? new Date(this.dateFilterFrom) : null;
    const filterTo = this.dateFilterTo ? new Date(this.dateFilterTo) : null;

    const filtered = {};
    for (const [week, value] of Object.entries(weeklyData)) {
      // Parse week format: "2026-W05" -> get Monday of that week
      const match = week.match(/(\d{4})-W(\d{2})/);
      if (!match) continue;

      const year = parseInt(match[1]);
      const weekNum = parseInt(match[2]);

      // Calculate the Monday of that ISO week
      const jan4 = new Date(year, 0, 4);
      const dayOfWeek = (jan4.getDay() || 7) - 1;
      const weekStart = new Date(jan4);
      weekStart.setDate(weekStart.getDate() - dayOfWeek + (weekNum - 1) * 7);

      // Check if week is within date range
      if (filterFrom && weekStart < filterFrom) continue;
      if (filterTo && weekStart > filterTo) continue;

      filtered[week] = value;
    }

    return filtered;
  }

  renderVelocityChart(velocityData) {
    const ctx = document.getElementById('velocityChart');
    const container = ctx?.parentElement;
    if (!ctx || !container) return;

    // Destroy old chart if it exists
    if (this.charts.velocity) {
      this.charts.velocity.destroy();
      this.charts.velocity = null;
    }

    if (!velocityData || !velocityData.weekly_data) {
      container.innerHTML = '<p style="color: #999; padding: 2rem;">📊 N/A - Velocity data not available</p>';
      this.addDataSourceNote(container, 'No data available', 'calculations/global/velocity.json');
      return;
    }

    // Extract real weekly data from calculations
    let weeklyData = velocityData.weekly_data;

    // Apply date filter if active
    if (this.dateFilterFrom || this.dateFilterTo) {
      const beforeCount = Object.keys(weeklyData).length;
      weeklyData = this.filterWeeklyDataByDateRange(weeklyData);
      const afterCount = Object.keys(weeklyData).length;
      console.log('📅 Date filter applied:', { dateFrom: this.dateFilterFrom, dateTo: this.dateFilterTo, before: beforeCount, after: afterCount });
    }

    const labels = Object.keys(weeklyData).sort();
    const data = labels.map(week => weeklyData[week]);

    console.log('✅ Velocity Chart - Real data loaded:', { weeks: labels.length, dataPoints: data, dateFilterFrom: this.dateFilterFrom, dateFilterTo: this.dateFilterTo });

    this.charts.velocity = new Chart(ctx, {
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

    // Destroy old chart if it exists
    if (this.charts.coverage) {
      this.charts.coverage.destroy();
      this.charts.coverage = null;
    }

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

    this.charts.coverage = new Chart(ctx, {
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

  async renderContributorsChart(globalContributorsData, perRepoContributorsData) {
    const ctx = document.getElementById('contributorsChart');
    const container = ctx?.parentElement;
    if (!ctx || !container) return;

    // Destroy old chart if it exists
    if (this.charts.contributors) {
      this.charts.contributors.destroy();
      this.charts.contributors = null;
    }

    // If date filter is active, calculate filtered contributor counts from commits
    let contributors = [];
    const hasDateFilter = this.dateFilterFrom || this.dateFilterTo;

    if (hasDateFilter) {
      // Load commits and count per contributor in the date range
      console.log('📅 Calculating contributors for date range:', { from: this.dateFilterFrom, to: this.dateFilterTo });

      if (this.manifest && this.manifest.per_repo_metrics) {
        for (const repo of Object.keys(this.manifest.per_repo_metrics)) {
          try {
            // Load raw commits from git_artifacts (not the metrics file at calculations/)
            const commitsData = await this.loadJSON(this.basePath + `git_artifacts/${repo}/commits.json`);
            console.log(`📋 Loaded commits for ${repo}:`, commitsData ? `${commitsData.commits?.length || 0} commits` : 'null');

            if (commitsData && commitsData.commits && Array.isArray(commitsData.commits)) {
              const filterFrom = this.dateFilterFrom ? new Date(this.dateFilterFrom) : new Date('1900-01-01');
              const filterTo = this.dateFilterTo ? new Date(this.dateFilterTo) : new Date('2100-12-31');

              console.log(`🔍 Filtering ${commitsData.commits.length} commits between ${filterFrom.toISOString()} and ${filterTo.toISOString()}`);

              // Count commits per author in the date range
              const authorCounts = {};
              let filteredCount = 0;
              commitsData.commits.forEach(commit => {
                const commitDate = new Date(commit.timestamp.split(' ')[0]); // Extract date part
                if (commitDate >= filterFrom && commitDate <= filterTo) {
                  const author = commit.author_email || commit.author_name || 'Unknown';
                  authorCounts[author] = (authorCounts[author] || 0) + 1;
                  filteredCount++;
                }
              });

              console.log(`✅ Found ${filteredCount} commits and ${Object.keys(authorCounts).length} authors in date range`);

              // Add to contributors list
              for (const [author, count] of Object.entries(authorCounts)) {
                const existing = contributors.find(c => c.email === author);
                if (existing) {
                  existing.commit_count = (existing.commit_count || 0) + count;
                } else {
                  contributors.push({ name: author, email: author, commit_count: count });
                }
              }
            }
          } catch (e) {
            console.warn(`⚠️ Commits data for ${repo} not available:`, e.message);
          }
        }
      }
    } else {
      // No date filter - use all-time contributor data from authors.json
      if (this.manifest && this.manifest.per_repo_metrics) {
        for (const repo of Object.keys(this.manifest.per_repo_metrics)) {
          try {
            const authorsData = await this.loadJSON(this.basePath + `git_artifacts/${repo}/authors.json`);
            if (authorsData && authorsData.authors && Array.isArray(authorsData.authors)) {
              contributors = contributors.concat(authorsData.authors);
            }
          } catch (e) {
            console.warn(`⚠️ Authors data for ${repo} not available:`, e.message);
          }
        }
      }
    }

    // If we have individual contributors, show top N by commit count
    if (contributors.length > 0) {
      // Sort by commit count descending
      contributors.sort((a, b) => (b.commit_count || 0) - (a.commit_count || 0));

      // Take top 15 contributors
      const topContributors = contributors.slice(0, 15);

      const labels = topContributors.map(c => c.name || c.email || 'Unknown');
      const commitCounts = topContributors.map(c => c.commit_count || 0);

      console.log('✅ Contributors Chart - Real data from individual contributors:', { contributors: labels, commits: commitCounts, dateFiltered: hasDateFilter });

      // Determine colors based on commit count (gradient)
      const maxCommits = Math.max(...commitCounts, 1);
      const backgroundColor = commitCounts.map(count => {
        const intensity = Math.min(count / maxCommits, 1);
        const hue = Math.floor((1 - intensity) * 120); // Green (120) to Yellow (60)
        return `hsl(${hue}, 70%, 50%)`;
      });

      const borderColor = backgroundColor.map(bg => bg.replace('50%', '40%'));

      this.charts.contributors = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Commits',
            data: commitCounts,
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
                  return `Commits: ${context.parsed.x}`;
                }
              }
            }
          },
          scales: {
            x: {
              beginAtZero: true,
              ticks: {
                color: '#666'
              },
              grid: { color: 'rgba(0, 0, 0, 0.05)' },
              title: {
                display: true,
                text: 'Commits by Contributor'
              }
            },
            y: {
              ticks: { color: '#666' },
              grid: { display: false }
            }
          }
        }
      });

      const filterNote = hasDateFilter ? ` (filtered: ${this.dateFilterFrom || '∞'} to ${this.dateFilterTo || '∞'})` : '';
      this.addDataSourceNote(container, `Top ${labels.length} contributors (${contributors.length} shown)${filterNote}`, 'git_artifacts/*/commits.json');
    } else {
      // Fallback to showing total count if no individual contributors found
      if (globalContributorsData && globalContributorsData.unique_contributors) {
        container.innerHTML = `<p style="color: #999; padding: 2rem;">👥 ${globalContributorsData.unique_contributors} total contributors</p>`;
        this.addDataSourceNote(container, `${globalContributorsData.unique_contributors} unique contributors total`, 'calculations/global/contributors.json');
      } else {
        container.innerHTML = '<p style="color: #999; padding: 2rem;">👥 N/A - No contributor data available</p>';
        this.addDataSourceNote(container, 'No breakdown data', 'git_artifacts/*/authors.json');
      }
    }
  }

  renderContributorsChartPerRepo(repoContributorsData) {
    const ctx = document.getElementById('contributorsChart');
    const container = ctx?.parentElement;
    if (!ctx || !container) return;

    // Destroy old chart if it exists
    if (this.charts.contributors) {
      this.charts.contributors.destroy();
      this.charts.contributors = null;
    }

    if (!repoContributorsData || !repoContributorsData.unique_contributors) {
      container.innerHTML = '<p style="color: #999; padding: 2rem;">👥 N/A - No contributor data available</p>';
      this.addDataSourceNote(container, 'No data', `calculations/per_repo/${this.selectedProject}/contributors.json`);
      return;
    }

    const count = repoContributorsData.unique_contributors;

    // Display as a simple metric for single project
    const statusColor = count >= 2 ? '#28a745' : '#ffc107'; // Green or Yellow
    const statusText = count >= 2 ? '✓ Good' : '⚠️ Risk';

    // Show a simple bar chart with just this project
    this.charts.contributors = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: [this.selectedProject],
        datasets: [{
          label: 'Number of Contributors',
          data: [count],
          backgroundColor: statusColor === '#28a745' ? 'rgba(40, 167, 69, 0.8)' : 'rgba(255, 193, 7, 0.8)',
          borderColor: statusColor,
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
              label: function() {
                return `Contributors: ${count} (${statusText})`;
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
            grid: { color: 'rgba(0, 0, 0, 0.05)' }
          },
          y: {
            ticks: { color: '#666' },
            grid: { display: false }
          }
        }
      }
    });

    this.addDataSourceNote(container, `${count} contributor${count !== 1 ? 's' : ''} in ${this.selectedProject}`, `calculations/per_repo/${this.selectedProject}/contributors.json`);
  }

  addDataSourceNote(container, description, source) {
    if (!container) return;
    // Remove existing data source notes to avoid duplicates
    const existing = container.querySelector('.chart-data-source');
    if (existing) {
      existing.remove();
    }
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
