// Ball Econix - Main JavaScript
// Modern Dark Theme Interactive Features

class BallEconix {
  constructor() {
    this.init();
    this.setupEventListeners();
    this.initializeComponents();
  }

  init() {
    // Initialize theme
    this.setTheme();
    
    // Initialize mobile menu
    this.initMobileMenu();
    
    // Initialize smooth scrolling
    this.initSmoothScrolling();
    
    // Initialize loading states
    this.initLoadingStates();
    
    // Initialize animations
    this.initAnimations();
    
    console.log('Ball Econix initialized');
  }

  setTheme() {
    // Ensure dark theme is applied
    document.documentElement.setAttribute('data-theme', 'dark');
    
    // Apply theme colors to Chart.js defaults if available
    if (typeof Chart !== 'undefined') {
      Chart.defaults.color = '#b0b0b0';
      Chart.defaults.borderColor = '#333333';
      Chart.defaults.backgroundColor = 'rgba(84, 215, 241, 0.1)';
      
      // Set default font
      Chart.defaults.font.family = 'Inter, Segoe UI, system-ui, -apple-system, sans-serif';
      Chart.defaults.font.size = 12;
      
      // Set default colors for different chart types
      Chart.defaults.datasets.line.borderColor = '#54d7f1';
      Chart.defaults.datasets.line.backgroundColor = 'rgba(84, 215, 241, 0.1)';
      Chart.defaults.datasets.bar.backgroundColor = '#54d7f1';
      Chart.defaults.datasets.bar.borderColor = '#3bc5e8';
    }
  }

  initMobileMenu() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    const menuToggle = document.querySelector('.menu-toggle');
    const overlay = document.querySelector('.mobile-overlay');

    if (menuToggle) {
      menuToggle.addEventListener('click', () => {
        sidebar?.classList.toggle('open');
        mainContent?.classList.toggle('sidebar-open');
        overlay?.classList.toggle('active');
      });
    }

    if (overlay) {
      overlay.addEventListener('click', () => {
        sidebar?.classList.remove('open');
        mainContent?.classList.remove('sidebar-open');
        overlay.classList.remove('active');
      });
    }

    // Close mobile menu on window resize
    window.addEventListener('resize', () => {
      if (window.innerWidth > 1024) {
        sidebar?.classList.remove('open');
        mainContent?.classList.remove('sidebar-open');
        overlay?.classList.remove('active');
      }
    });
  }

  initSmoothScrolling() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  }

  initLoadingStates() {
    // Add loading states to buttons
    document.querySelectorAll('.btn').forEach(btn => {
      btn.addEventListener('click', function(e) {
        if (this.classList.contains('loading')) return;
        
        // Add loading state
        this.classList.add('loading');
        const originalText = this.innerHTML;
        this.innerHTML = '<span class="loading-spinner"></span> Loading...';
        
        // Remove loading state after 2 seconds (adjust as needed)
        setTimeout(() => {
          this.classList.remove('loading');
          this.innerHTML = originalText;
        }, 2000);
      });
    });
  }

  initAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-fade-in');
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    // Observe cards and charts
    document.querySelectorAll('.card, .chart-wrapper, .metric-card').forEach(el => {
      observer.observe(el);
    });
  }

  setupEventListeners() {
    // Global event listeners
    document.addEventListener('DOMContentLoaded', () => {
      this.initializeComponents();
    });

    // Handle form submissions
    document.addEventListener('submit', (e) => {
      this.handleFormSubmit(e);
    });

    // Handle modal triggers
    document.addEventListener('click', (e) => {
      if (e.target.matches('[data-modal-trigger]')) {
        this.openModal(e.target.dataset.modalTrigger);
      }
      if (e.target.matches('[data-modal-close]')) {
        this.closeModal();
      }
    });

    // Handle dropdown toggles
    document.addEventListener('click', (e) => {
      if (e.target.matches('.dropdown-toggle')) {
        this.toggleDropdown(e.target.closest('.dropdown'));
      } else {
        // Close all dropdowns when clicking outside
        document.querySelectorAll('.dropdown.active').forEach(dropdown => {
          dropdown.classList.remove('active');
        });
      }
    });

    // Handle tab switching
    document.addEventListener('click', (e) => {
      if (e.target.matches('.tab-button')) {
        this.switchTab(e.target);
      }
    });

    // Handle accordion toggles
    document.addEventListener('click', (e) => {
      if (e.target.matches('.accordion-header')) {
        this.toggleAccordion(e.target.closest('.accordion-item'));
      }
    });
  }

  initializeComponents() {
    // Initialize tooltips
    this.initTooltips();
    
    // Initialize progress bars
    this.initProgressBars();
    
    // Initialize counters
    this.initCounters();
    
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
      this.initChartDefaults();
    }
  }

  initTooltips() {
    // Simple tooltip implementation
    document.querySelectorAll('[data-tooltip]').forEach(element => {
      element.addEventListener('mouseenter', (e) => {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip-popup';
        tooltip.textContent = e.target.dataset.tooltip;
        document.body.appendChild(tooltip);
        
        const rect = e.target.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        
        setTimeout(() => tooltip.classList.add('show'), 10);
      });
      
      element.addEventListener('mouseleave', () => {
        document.querySelectorAll('.tooltip-popup').forEach(tooltip => {
          tooltip.remove();
        });
      });
    });
  }

  initProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    const progressObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const progressBar = entry.target;
          const targetWidth = progressBar.dataset.progress || '0';
          
          setTimeout(() => {
            progressBar.style.width = targetWidth + '%';
          }, 200);
          
          progressObserver.unobserve(progressBar);
        }
      });
    });

    progressBars.forEach(bar => progressObserver.observe(bar));
  }

  initCounters() {
    const counters = document.querySelectorAll('[data-counter]');
    
    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.animateCounter(entry.target);
          counterObserver.unobserve(entry.target);
        }
      });
    });

    counters.forEach(counter => counterObserver.observe(counter));
  }

  animateCounter(element) {
    const target = parseInt(element.dataset.counter);
    const duration = parseInt(element.dataset.duration) || 2000;
    const increment = target / (duration / 16);
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      element.textContent = Math.floor(current).toLocaleString();
    }, 16);
  }

  initChartDefaults() {
    // Set global Chart.js defaults for dark theme
    Chart.defaults.plugins.legend.labels.color = '#b0b0b0';
    Chart.defaults.plugins.legend.labels.font = {
      family: 'Inter, Segoe UI, system-ui, -apple-system, sans-serif',
      size: 12
    };
    
    Chart.defaults.scales.linear.grid.color = '#333333';
    Chart.defaults.scales.linear.ticks.color = '#b0b0b0';
    Chart.defaults.scales.category.grid.color = '#333333';
    Chart.defaults.scales.category.ticks.color = '#b0b0b0';
    
    // Custom tooltip styling
    Chart.defaults.plugins.tooltip.backgroundColor = '#2a2a2a';
    Chart.defaults.plugins.tooltip.titleColor = '#ffffff';
    Chart.defaults.plugins.tooltip.bodyColor = '#b0b0b0';
    Chart.defaults.plugins.tooltip.borderColor = '#333333';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
  }

  // Modal functionality
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  }

  closeModal() {
    document.querySelectorAll('.modal-overlay.active').forEach(modal => {
      modal.classList.remove('active');
    });
    document.body.style.overflow = '';
  }

  // Dropdown functionality
  toggleDropdown(dropdown) {
    dropdown.classList.toggle('active');
  }

  // Tab functionality
  switchTab(tabButton) {
    const tabContainer = tabButton.closest('.tab-container');
    const targetPane = tabContainer.querySelector(tabButton.dataset.target);
    
    if (!targetPane) return;

    // Remove active class from all tabs and panes
    tabContainer.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    tabContainer.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    
    // Add active class to clicked tab and target pane
    tabButton.classList.add('active');
    targetPane.classList.add('active');
  }

  // Accordion functionality
  toggleAccordion(accordionItem) {
    const isActive = accordionItem.classList.contains('active');
    
    // Close all accordion items in the same accordion
    const accordion = accordionItem.closest('.accordion');
    accordion.querySelectorAll('.accordion-item').forEach(item => {
      item.classList.remove('active');
    });
    
    // Toggle the clicked item
    if (!isActive) {
      accordionItem.classList.add('active');
    }
  }

  // Form handling
  handleFormSubmit(e) {
    const form = e.target;
    if (form.classList.contains('ajax-form')) {
      e.preventDefault();
      this.submitFormAjax(form);
    }
  }

  async submitFormAjax(form) {
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Add loading state
    if (submitButton) {
      submitButton.classList.add('loading');
      submitButton.disabled = true;
    }

    try {
      const response = await fetch(form.action, {
        method: form.method,
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': this.getCSRFToken()
        }
      });

      const result = await response.json();
      
      if (response.ok) {
        this.showAlert('success', result.message || 'Form submitted successfully!');
        form.reset();
      } else {
        this.showAlert('error', result.error || 'An error occurred. Please try again.');
      }
    } catch (error) {
      this.showAlert('error', 'Network error. Please check your connection and try again.');
    } finally {
      // Remove loading state
      if (submitButton) {
        submitButton.classList.remove('loading');
        submitButton.disabled = false;
      }
    }
  }

  // Utility functions
  getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
  }

  showAlert(type, message) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
      <div class="alert-icon">
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
      </div>
      <div class="alert-content">
        <div class="alert-message">${message}</div>
      </div>
    `;
    
    document.body.appendChild(alert);
    
    setTimeout(() => alert.classList.add('show'), 10);
    setTimeout(() => {
      alert.classList.remove('show');
      setTimeout(() => alert.remove(), 300);
    }, 5000);
  }

  // Data formatting utilities
  formatNumber(num, decimals = 0) {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(num);
  }

  formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount);
  }

  formatPercentage(value, decimals = 1) {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value / 100);
  }

  // API utilities
  async fetchData(url, options = {}) {
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': this.getCSRFToken()
      }
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Fetch error:', error);
      throw error;
    }
  }

  // Chart utilities
  createChart(canvas, config) {
    if (typeof Chart === 'undefined') {
      console.error('Chart.js is not loaded');
      return null;
    }

    // Apply dark theme defaults to config
    const darkConfig = this.applyDarkThemeToChart(config);
    
    return new Chart(canvas, darkConfig);
  }

  applyDarkThemeToChart(config) {
    // Deep clone the config to avoid modifying the original
    const darkConfig = JSON.parse(JSON.stringify(config));
    
    // Apply dark theme colors
    if (darkConfig.data && darkConfig.data.datasets) {
      darkConfig.data.datasets.forEach((dataset, index) => {
        if (!dataset.backgroundColor) {
          dataset.backgroundColor = this.getChartColor(index, 0.2);
        }
        if (!dataset.borderColor) {
          dataset.borderColor = this.getChartColor(index, 1);
        }
      });
    }
    
    return darkConfig;
  }

  getChartColor(index, alpha = 1) {
    const colors = [
      '#54d7f1', '#0C0D49', '#3bc5e8', '#1a1f7a',
      '#7dd3fc', '#0f172a', '#38bdf8', '#1e293b'
    ];
    
    const color = colors[index % colors.length];
    
    if (alpha < 1) {
      // Convert hex to rgba
      const r = parseInt(color.slice(1, 3), 16);
      const g = parseInt(color.slice(3, 5), 16);
      const b = parseInt(color.slice(5, 7), 16);
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    
    return color;
  }

  // Performance monitoring
  measurePerformance(name, fn) {
    const start = performance.now();
    const result = fn();
    const end = performance.now();
    console.log(`${name} took ${end - start} milliseconds`);
    return result;
  }

  // Debounce utility
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

  // Throttle utility
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

// Initialize Ball Econix when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.ballEconix = new BallEconix();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = BallEconix;
}