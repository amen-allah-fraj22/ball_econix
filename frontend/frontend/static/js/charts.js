// frontend/static/js/charts.js
class EconomicCharts {
    constructor() {
        this.charts = {}; // To store chart instances for updates later
        this.map = null; // To store map instance
        // Ensure CSRF token is available for potential POST requests if any were planned
        // this.csrftoken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';
    }

    async fetchData(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                console.error(`Error fetching data from ${url}: ${response.statusText}`);
                return null;
            }
            return await response.json();
        } catch (error) {
            console.error(`Exception when fetching data from ${url}:`, error);
            return null;
        }
    }

    // Method to get a color based on happiness score
    getHappinessColor(score) {
        if (score === null || score === undefined) return '#ccc'; // Default for no data
        if (score > 7) return '#28a745'; // Very Happy (Green)
        if (score > 6) return '#8fbc8f'; // Happy (Dark Sea Green)
        if (score > 5) return '#ffc107'; // Neutral (Yellow)
        if (score > 4) return '#fd7e14'; // Less Happy (Orange)
        return '#dc3545';       // Unhappy (Red)
    }

    async initWorldMap(containerId = 'worldMap') {
        const mapContainer = document.getElementById(containerId);
        if (!mapContainer) {
            console.error(`Map container with ID '${containerId}' not found.`);
            return;
        }
        mapContainer.innerHTML = ''; // Clear previous content if any

        const data = await this.fetchData('/api/analytics/global-dashboard-data/');
        if (!data || data.length === 0) {
            mapContainer.innerHTML = '<p>No data available to display on the map.</p>';
            console.warn('No data for world map.');
            return;
        }

        // Initialize Leaflet map
        if (this.map) { // If map already exists, remove it before re-initializing
            this.map.remove();
        }
        this.map = L.map(containerId).setView([20, 0], 2); // Default view

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(this.map);

        data.forEach(country => {
            if (country.lat != null && country.lng != null) {
                const color = this.getHappinessColor(country.happiness);
                const circle = L.circleMarker([country.lat, country.lng], {
                    radius: 8,
                    fillColor: color,
                    color: '#000',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                }).addTo(this.map);

                circle.bindTooltip(`
                    <strong>${country.country} (${country.code})</strong><br>
                    Happiness Score: ${country.happiness !== null ? country.happiness.toFixed(2) : 'N/A'}
                `);
                // Later: circle.on('click', () => { window.location.href = `/countries/${country.code}/`; });
            }
        });
        console.log('World map initialized.');
    }

    async initInflationTrends(containerId = 'inflationChart') {
        const canvas = document.getElementById(containerId);
        if (!canvas) {
            console.error(`Canvas with ID '${containerId}' not found.`);
            return;
        }

        const data = await this.fetchData('/api/analytics/inflation-trends/');
        if (!data || data.length === 0) {
            canvas.getContext('2d').fillText('No inflation data available.', 10, 50);
            console.warn('No data for inflation trends chart.');
            return;
        }

        const years = data.map(item => item.year);
        const headlineInflation = data.map(item => item.avg_headline_inflation);
        const foodInflation = data.map(item => item.avg_food_inflation);
        const energyInflation = data.map(item => item.avg_energy_inflation);

        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        this.charts[containerId] = new Chart(canvas, {
            type: 'line',
            data: {
                labels: years,
                datasets: [
                    {
                        label: 'Headline Inflation',
                        data: headlineInflation,
                        borderColor: 'rgba(239, 68, 68, 1)', // Tailwind red-500
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        fill: false,
                        tension: 0.1
                    },
                    {
                        label: 'Food Inflation',
                        data: foodInflation,
                        borderColor: 'rgba(245, 158, 11, 1)', // Tailwind amber-500
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        fill: false,
                        tension: 0.1
                    },
                    {
                        label: 'Energy Inflation',
                        data: energyInflation,
                        borderColor: 'rgba(37, 99, 235, 1)', // Tailwind blue-600
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        fill: false,
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toFixed(2) + '%';
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Year'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Average Inflation Rate (%)'
                        },
                        beginAtZero: false // Inflation can be negative
                    }
                }
            }
        });
        console.log('Inflation trends chart initialized.');
    }

    // Placeholder for initCorrelationChart and updateCharts
    async initCorrelationChart(containerId = 'happinessGdpChart') {
        const canvas = document.getElementById(containerId);
        if (!canvas) {
            console.error(`Canvas with ID '${containerId}' not found for correlation chart.`);
            return;
        }

        const correlationData = await this.fetchData('/api/analytics/correlation-analysis/');
        if (!correlationData || !correlationData.pca_loadings) { // Check for pca_loadings specifically
            canvas.getContext('2d').fillText('Correlation data (PCA) not available.', 10, 50);
            console.warn('No PCA data for correlation chart.');
            return;
        }

        // For this chart, we'll visualize the PCA components' impact.
        // A true scatter plot of individual data points (e.g., country happiness vs inflation)
        // would require a different data structure from the API or more client-side processing.
        // Here, we'll create a bar chart of PC1 loadings as an example of using the PCA data.

        const pc1_loadings = correlationData.pca_loadings.PC1;
        if (!pc1_loadings) {
            canvas.getContext('2d').fillText('PCA PC1 loadings not available.', 10, 50);
            console.warn('PCA PC1 loadings missing in data for correlation chart.');
            return;
        }

        const labels = Object.keys(pc1_loadings);
        const dataValues = Object.values(pc1_loadings);

        // Prepare background colors based on positive/negative loading
        const backgroundColors = dataValues.map(value => value >= 0 ? 'rgba(75, 192, 192, 0.6)' : 'rgba(255, 99, 132, 0.6)');
        const borderColors = dataValues.map(value => value >= 0 ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)');


        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        this.charts[containerId] = new Chart(canvas, {
            type: 'bar', // Changed to bar chart to show PCA loadings effectively
            data: {
                labels: labels,
                datasets: [{
                    label: 'PC1 Loadings',
                    data: dataValues,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y', // Display feature names on Y-axis for better readability
                plugins: {
                    legend: {
                        display: false // Typically false for a single dataset bar chart like this
                    },
                    title: {
                        display: true,
                        text: 'Factor Loadings on Principal Component 1 (PC1)'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.x !== null) { // x is the value for horizontal bar
                                    label += context.parsed.x.toFixed(3);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Loading Value'
                        },
                        beginAtZero: true // Or false if negative loadings are significant and you want to center
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Economic Indicator'
                        }
                    }
                }
            }
        });
        console.log('Correlation chart (PCA Loadings) initialized using ID: ' + containerId);
    }

    updateCharts(newData) {
        // Implementation for dynamic updates later
        console.log('updateCharts called with:', newData);
    }
}
