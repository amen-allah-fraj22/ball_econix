// Ball Econix - Dashboard Specific JavaScript
// Enhanced dashboard functionality with modern interactions

class DashboardManager {
  constructor() {
    this.charts = new Map();
    this.widgets = new Map();
    this.filters = new Map();
    this.init();
  }

  init() {
    this.initializeWidgets();
    this.setupEventListeners();
    this.loadDashboardData();
    this.initializeCharts();
    this.setupRealTimeUpdates();
    
    console.log('Dashboard Manager initialized');
  }

  initializeWidgets() {
    // Initialize metric cards with animations
    this.initMetricCards();
    
    // Initialize search functionality
    this.initSearchWidget();
    
    // Initialize filter controls
    this.initFilterControls();
    
    // Initialize data tables
    this.initDataTables();
  }

  initMetricCards() {
    const metricCards = document.querySelectorAll('.metric-card, .stat-card');
    
    metricCards.forEach((card, index) => {
      // Add staggered animation delay
      card.style.animationDelay = `${index * 0.1}s`;
      
      // Add hover effects
      card.addEventListener('mouseenter', () => {
        this.animateMetricCard(card, 'hover');
      });
      
      card.addEventListener('mouseleave', () => {
        this.animateMetricCard(card, 'normal');
      });
      
      // Initialize counter animation if data-counter exists
      const counterElement = card.querySelector('[data-counter]');
      if (counterElement) {
        this.observeCounter(counterElement);
      }
    });
  }

  animateMetricCard(card, state) {
    const icon = card.querySelector('.metric-icon, .stat-icon');
    const value = card.querySelector('.metric-value, .stat-value');
    
    if (state === 'hover') {
      if (icon) icon.style.transform = 'scale(1.1) rotate(5deg)';
      if (value) value.style.transform = 'scale(1.05)';
      card.style.transform = 'translateY(-8px)';
    } else {
      if (icon) icon.style.transform = 'scale(1) rotate(0deg)';
      if (value) value.style.transform = 'scale(1)';
      card.style.transform = 'translateY(0)';
    }
  }

  observeCounter(element) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !element.dataset.animated) {
          this.animateCounter(element);
          element.dataset.animated = 'true';
        }
      });
    }, { threshold: 0.5 });
    
    observer.observe(element);
  }

  animateCounter(element) {
    const target = parseFloat(element.dataset.counter);
    const duration = parseInt(element.dataset.duration) || 2000;
    const isPercentage = element.dataset.type === 'percentage';
    const isCurrency = element.dataset.type === 'currency';
    const decimals = parseInt(element.dataset.decimals) || 0;
    
    const increment = target / (duration / 16);
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      
      let displayValue = current.toFixed(decimals);
      
      if (isCurrency) {
        displayValue = new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD'
        }).format(current);
      } else if (isPercentage) {
        displayValue = current.toFixed(1) + '%';
      } else {
        displayValue = Math.floor(current).toLocaleString();
      }
      
      element.textContent = displayValue;
    }, 16);
  }

  initSearchWidget() {
    const searchInput = document.querySelector('#countrySearch, .search-input');
    const searchResults = document.querySelector('#searchResults, .search-results');
    
    if (!searchInput || !searchResults) return;

    let searchTimeout;
    
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      const query = e.target.value.trim();
      
      if (query.length < 2) {
        searchResults.innerHTML = '';
        searchResults.style.display = 'none';
        return;
      }
      
      // Show loading state
      searchResults.innerHTML = '<div class="search-loading">Searching...</div>';
      searchResults.style.display = 'block';
      
      searchTimeout = setTimeout(() => {
        this.performSearch(query, searchResults);
      }, 300);
    });
    
    // Hide results when clicking outside
    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.style.display = 'none';
      }
    });
  }

  async performSearch(query, resultsContainer) {
    try {
      const response = await fetch(`/api/analytics/search-countries/?q=${encodeURIComponent(query)}`);
      
      if (!response.ok) {
        throw new Error('Search failed');
      }
      
      const results = await response.json();
      this.displaySearchResults(results, resultsContainer);
      
    } catch (error) {
      console.error('Search error:', error);
      resultsContainer.innerHTML = '<div class="search-error">Search failed. Please try again.</div>';
    }
  }

  displaySearchResults(results, container) {
    if (!results || results.length === 0) {
      container.innerHTML = '<div class="search-no-results">No countries found</div>';
      return;
    }
    
    const resultsList = results.map(country => `
      <div class="search-result-item" data-country="${country.name}">
        <div class="search-result-content">
          <div class="search-result-name">${country.name}</div>
          <div class="search-result-details">${country.continent || ''} ${country.region ? '- ' + country.region : ''}</div>
        </div>
        <div class="search-result-score">
          ${country.happiness_score !== null ? country.happiness_score.toFixed(1) : 'N/A'}
        </div>
      </div>
    `).join('');
    
    container.innerHTML = resultsList;
    
    // Add click handlers
    container.querySelectorAll('.search-result-item').forEach(item => {
      item.addEventListener('click', () => {
        const countryName = item.dataset.country;
        this.navigateToCountry(countryName);
        container.style.display = 'none';
      });
    });
  }

  navigateToCountry(countryName) {
    window.location.href = `/countries/${encodeURIComponent(countryName)}/`;
  }

  initFilterControls() {
    const filterControls = document.querySelectorAll('.filter-control, .form-select');
    
    filterControls.forEach(control => {
      control.addEventListener('change', (e) => {
        const filterType = e.target.dataset.filter || e.target.name;
        const filterValue = e.target.value;
        
        this.applyFilter(filterType, filterValue);
      });
    });
  }

  applyFilter(type, value) {
    this.filters.set(type, value);
    
    // Update charts and data based on filters
    this.updateChartsWithFilters();
    
    // Update URL parameters
    this.updateURLParams();
  }

  updateChartsWithFilters() {
    const filters = Object.fromEntries(this.filters);
    
    this.charts.forEach((chart, chartId) => {
      this.updateChart(chartId, filters);
    });
  }

  updateURLParams() {
    const params = new URLSearchParams();
    this.filters.forEach((value, key) => {
      if (value) params.set(key, value);
    });
    
    const newURL = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, '', newURL);
  }

  initDataTables() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
      this.enhanceTable(table);
    });
  }

  enhanceTable(table) {
    // Add sorting functionality
    const headers = table.querySelectorAll('th[data-sortable]');
    
    headers.forEach(header => {
      header.style.cursor = 'pointer';
      header.addEventListener('click', () => {
        this.sortTable(table, header);
      });
    });
    
    // Add row hover effects
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
      row.addEventListener('mouseenter', () => {
        row.style.transform = 'scale(1.01)';
      });
      
      row.addEventListener('mouseleave', () => {
        row.style.transform = 'scale(1)';
      });
    });
  }

  sortTable(table, header) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const isNumeric = header.dataset.type === 'numeric';
    const currentSort = header.dataset.sort || 'asc';
    const newSort = currentSort === 'asc' ? 'desc' : 'asc';
    
    // Clear all sort indicators
    table.querySelectorAll('th').forEach(th => {
      th.classList.remove('sort-asc', 'sort-desc');
      delete th.dataset.sort;
    });
    
    // Set new sort indicator
    header.classList.add(`sort-${newSort}`);
    header.dataset.sort = newSort;
    
    // Sort rows
    rows.sort((a, b) => {
      const aValue = a.children[columnIndex].textContent.trim();
      const bValue = b.children[columnIndex].textContent.trim();
      
      let comparison = 0;
      
      if (isNumeric) {
        const aNum = parseFloat(aValue.replace(/[^0-9.-]/g, ''));
        const bNum = parseFloat(bValue.replace(/[^0-9.-]/g, ''));
        comparison = aNum - bNum;
      } else {
        comparison = aValue.localeCompare(bValue);
      }
      
      return newSort === 'asc' ? comparison : -comparison;
    });
    
    // Reorder rows in DOM
    rows.forEach(row => tbody.appendChild(row));
  }

  setupEventListeners() {
    // Tab switching
    document.addEventListener('click', (e) => {
      if (e.target.matches('.tab-button')) {
        this.handleTabSwitch(e.target);
      }
    });
    
    // Chart controls
    document.addEventListener('click', (e) => {
      if (e.target.matches('.chart-control-btn')) {
        this.handleChartControl(e.target);
      }
    });
    
    // Export buttons
    document.addEventListener('click', (e) => {
      if (e.target.matches('.chart-export-btn')) {
        this.handleChartExport(e.target);
      }
    });
    
    // Refresh buttons
    document.addEventListener('click', (e) => {
      if (e.target.matches('.refresh-btn')) {
        this.handleRefresh(e.target);
      }
    });
  }

  handleTabSwitch(tabButton) {
    const tabContainer = tabButton.closest('.tab-container');
    const targetId = tabButton.dataset.target;
    const targetPane = document.querySelector(targetId);
    
    if (!targetPane) return;
    
    // Update active states
    tabContainer.querySelectorAll('.tab-button').forEach(btn => {
      btn.classList.remove('active');
    });
    tabContainer.querySelectorAll('.tab-pane').forEach(pane => {
      pane.classList.remove('active');
    });
    
    tabButton.classList.add('active');
    targetPane.classList.add('active');
    
    // Trigger chart resize if needed
    setTimeout(() => {
      this.resizeChartsInPane(targetPane);
    }, 300);
  }

  resizeChartsInPane(pane) {
    const charts = pane.querySelectorAll('canvas');
    charts.forEach(canvas => {
      const chartInstance = Chart.getChart(canvas);
      if (chartInstance) {
        chartInstance.resize();
      }
    });
  }

  handleChartControl(button) {
    const chartContainer = button.closest('.chart-wrapper, .chart-card');
    const chartId = chartContainer.dataset.chartId;
    const action = button.dataset.action;
    
    switch (action) {
      case 'refresh':
        this.refreshChart(chartId);
        break;
      case 'fullscreen':
        this.toggleChartFullscreen(chartContainer);
        break;
      case 'settings':
        this.openChartSettings(chartId);
        break;
    }
  }

  handleChartExport(button) {
    const chartContainer = button.closest('.chart-wrapper, .chart-card');
    const canvas = chartContainer.querySelector('canvas');
    const format = button.dataset.format || 'png';
    
    if (canvas) {
      this.exportChart(canvas, format);
    }
  }

  exportChart(canvas, format) {
    const link = document.createElement('a');
    link.download = `chart-${Date.now()}.${format}`;
    
    if (format === 'png') {
      link.href = canvas.toDataURL('image/png');
    } else if (format === 'jpg') {
      link.href = canvas.toDataURL('image/jpeg', 0.9);
    }
    
    link.click();
  }

  handleRefresh(button) {
    const container = button.closest('[data-refresh-target]');
    const target = container.dataset.refreshTarget;
    
    button.classList.add('loading');
    
    setTimeout(() => {
      this.refreshData(target);
      button.classList.remove('loading');
    }, 1000);
  }

  async loadDashboardData() {
    try {
      // Load global stats
      await this.loadGlobalStats();
      
      // Load chart data
      await this.loadChartData();
      
      // Load recent activity
      await this.loadRecentActivity();
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      this.showError('Failed to load dashboard data');
    }
  }

  async loadGlobalStats() {
    try {
      const response = await fetch('/api/analytics/global-stats/');
      if (response.ok) {
        const stats = await response.json();
        this.updateGlobalStats(stats);
      }
    } catch (error) {
      console.error('Error loading global stats:', error);
    }
  }

  updateGlobalStats(stats) {
    // Update metric cards with new data
    Object.entries(stats).forEach(([key, value]) => {
      const element = document.querySelector(`[data-stat="${key}"]`);
      if (element) {
        this.animateValueChange(element, value);
      }
    });
  }

  animateValueChange(element, newValue) {
    const currentValue = parseFloat(element.textContent.replace(/[^0-9.-]/g, ''));
    const difference = newValue - currentValue;
    const steps = 30;
    const stepValue = difference / steps;
    let step = 0;
    
    const animation = setInterval(() => {
      step++;
      const value = currentValue + (stepValue * step);
      element.textContent = this.formatValue(value, element.dataset.format);
      
      if (step >= steps) {
        clearInterval(animation);
        element.textContent = this.formatValue(newValue, element.dataset.format);
      }
    }, 50);
  }

  formatValue(value, format) {
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD'
        }).format(value);
      case 'percentage':
        return value.toFixed(1) + '%';
      case 'number':
        return Math.round(value).toLocaleString();
      default:
        return value.toString();
    }
  }

  async loadChartData() {
    // This will be implemented based on specific chart requirements
    console.log('Loading chart data...');
  }

  async loadRecentActivity() {
    // Load recent activity data
    console.log('Loading recent activity...');
  }

  initializeCharts() {
    // Initialize charts based on canvas elements found
    const chartCanvases = document.querySelectorAll('canvas[data-chart]');
    
    chartCanvases.forEach(canvas => {
      const chartType = canvas.dataset.chart;
      const chartId = canvas.id || `chart-${Date.now()}`;
      
      this.createChart(chartId, canvas, chartType);
    });
  }

  createChart(chartId, canvas, type) {
    // This will be overridden by specific chart implementations
    console.log(`Creating chart: ${chartId} of type: ${type}`);
  }

  async updateChart(chartId, filters = {}) {
    const chart = this.charts.get(chartId);
    if (!chart) return;
    
    try {
      // Fetch new data based on filters
      const data = await this.fetchChartData(chartId, filters);
      
      // Update chart data
      chart.data = data;
      chart.update('active');
      
    } catch (error) {
      console.error(`Error updating chart ${chartId}:`, error);
    }
  }

  async fetchChartData(chartId, filters) {
    // This will be implemented based on specific chart requirements
    return {};
  }

  refreshChart(chartId) {
    this.updateChart(chartId, Object.fromEntries(this.filters));
  }

  setupRealTimeUpdates() {
    // Set up periodic updates for real-time data
    setInterval(() => {
      this.updateRealTimeData();
    }, 30000); // Update every 30 seconds
  }

  async updateRealTimeData() {
    try {
      // Update only real-time metrics
      await this.loadGlobalStats();
      
    } catch (error) {
      console.error('Error updating real-time data:', error);
    }
  }

  showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-error';
    alert.innerHTML = `
      <div class="alert-icon">
        <i class="fas fa-exclamation-triangle"></i>
      </div>
      <div class="alert-content">
        <div class="alert-message">${message}</div>
      </div>
    `;
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
      alert.classList.add('show');
    }, 10);
    
    setTimeout(() => {
      alert.classList.remove('show');
      setTimeout(() => alert.remove(), 300);
    }, 5000);
  }

  // Utility methods
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }
}

// Initialize Dashboard Manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.dashboardManager = new DashboardManager();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DashboardManager;
}