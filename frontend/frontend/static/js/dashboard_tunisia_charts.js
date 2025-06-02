document.addEventListener('DOMContentLoaded', function () {
    // Governorates data is expected to be set by the Django template in a global variable
    // like: <script>window.governoratesData = JSON.parse('{{ governorates_data|escapejs|default:"[]" }}');</script>
    // This script will be loaded after that global variable is set.

    const governorates = window.governoratesData || [];

    // Populate Governorate Select Dropdowns
    const governorateRealEstateSelect = document.getElementById('governorateRealEstateSelect');
    const governorateLaborMarketSelect = document.getElementById('governorateLaborMarketSelect');

    function populateSelect(selectElement, data) {
        if (selectElement) {
            selectElement.innerHTML = ''; // Clear existing options
            if (data.length === 0) {
                selectElement.innerHTML = '<option value="">No governorates found</option>';
                return;
            }
            let defaultSelected = false;
            data.forEach(gov => {
                const option = document.createElement('option');
                option.value = gov.id;
                option.textContent = gov.name;
                selectElement.appendChild(option);
                if (gov.name.toLowerCase() === 'tunis') {
                    selectElement.value = gov.id;
                    defaultSelected = true;
                }
            });
            if (!defaultSelected && selectElement.options.length > 0) {
                selectElement.value = selectElement.options[0].value;
            }
        }
    }

    populateSelect(governorateRealEstateSelect, governorates);
    populateSelect(governorateLaborMarketSelect, governorates);

    // Real Estate Chart Logic
    const realEstateChartCanvas = document.getElementById('realEstateChart');
    let realEstateChartInstance;

    function initOrUpdateRealEstateChart(chartData) {
        const data = {
            labels: chartData.years,
            datasets: [
                {
                    label: 'Residential Price (€/m²)',
                    data: chartData.residential_prices,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: false,
                    tension: 0.1
                },
                {
                    label: 'Commercial Price (€/m²)',
                    data: chartData.commercial_prices,
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    fill: false,
                    tension: 0.1
                },
                {
                    label: 'Land Price (€/m²)',
                    data: chartData.land_prices,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: false,
                    tension: 0.1
                }
            ]
        };
        const chartTitle = chartData.governorate_name ? `Real Estate Price Trends in ${chartData.governorate_name}` : 'Real Estate Price Trends';

        if (realEstateChartInstance) {
            realEstateChartInstance.data.labels = chartData.years;
            realEstateChartInstance.data.datasets[0].data = chartData.residential_prices;
            realEstateChartInstance.data.datasets[1].data = chartData.commercial_prices;
            realEstateChartInstance.data.datasets[2].data = chartData.land_prices;
            realEstateChartInstance.options.plugins.title.text = chartTitle;
            realEstateChartInstance.update();
        } else {
            if (realEstateChartCanvas) {
                realEstateChartInstance = new Chart(realEstateChartCanvas.getContext('2d'), {
                    type: 'line',
                    data: data,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: { y: { beginAtZero: false, ticks: { callback: function(value) { return '€' + value.toLocaleString(); } } } },
                        plugins: { title: { display: true, text: chartTitle }, legend: { display: true, position: 'top' }, tooltip: { mode: 'index', intersect: false, callbacks: { label: function(context) { let label = context.dataset.label || ''; if (label) { label += ': '; } if (context.parsed.y !== null) { label += '€' + context.parsed.y.toLocaleString(); } return label; } } } }
                    }
                });
            } else { console.error("Real Estate Chart canvas not found!"); }
        }
    }

    async function fetchAndRenderRealEstateData(governorateId) {
        if (!governorateId) {
            if(realEstateChartInstance) {
                realEstateChartInstance.data.labels = [];
                realEstateChartInstance.data.datasets.forEach(dataset => dataset.data = []);
                realEstateChartInstance.options.plugins.title.text = 'Select a Governorate';
                realEstateChartInstance.update();
            }
            return;
        }
        try {
            const response = await fetch(`/api/analytics/real-estate-trends/${governorateId}/`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const fetchedData = await response.json();
             if (fetchedData.years && fetchedData.years.length > 0) { initOrUpdateRealEstateChart(fetchedData); }
            else {
                const name = fetchedData.governorate_name || 'selected area';
                initOrUpdateRealEstateChart({ years: [], residential_prices: [], commercial_prices: [], land_prices: [], governorate_name: `No data for ${name}` });
            }
        } catch (error) {
            console.error('Error fetching real estate data:', error);
            initOrUpdateRealEstateChart({ years: [], residential_prices: [], commercial_prices: [], land_prices: [], governorate_name: 'Error Loading Data' });
        }
    }

    if (governorateRealEstateSelect) {
        governorateRealEstateSelect.addEventListener('change', function() { fetchAndRenderRealEstateData(this.value); });
        if (governorateRealEstateSelect.value) {
             fetchAndRenderRealEstateData(governorateRealEstateSelect.value);
        } else { // Fallback if no governorates were populated or none selected
            initOrUpdateRealEstateChart({ years: [], residential_prices: [], commercial_prices: [], land_prices: [], governorate_name: 'Select Governorate' });
        }
    } else { console.error("Governorate select dropdown 'governorateRealEstateSelect' not found!"); }

    // Labor Market Chart Logic
    const laborMarketChartCanvas = document.getElementById('laborChart');
    let laborMarketChartInstance;

    function initOrUpdateLaborMarketChart(chartData) {
        const data = {
            labels: chartData.years,
            datasets: [
                { label: 'Unemployment Rate (%)', data: chartData.unemployment_rate, borderColor: 'rgba(255, 99, 132, 1)', backgroundColor: 'rgba(255, 99, 132, 0.2)', fill: false, tension: 0.1, yAxisID: 'y-axis-percentage' },
                { label: 'Youth Unemployment (%)', data: chartData.youth_unemployment, borderColor: 'rgba(54, 162, 235, 1)', backgroundColor: 'rgba(54, 162, 235, 0.2)', fill: false, tension: 0.1, yAxisID: 'y-axis-percentage' },
                { label: 'Female Unemployment (%)', data: chartData.female_unemployment, borderColor: 'rgba(255, 206, 86, 1)', backgroundColor: 'rgba(255, 206, 86, 0.2)', fill: false, tension: 0.1, yAxisID: 'y-axis-percentage' },
                { label: 'Labor Force Participation (%)', data: chartData.labor_force_participation, borderColor: 'rgba(75, 192, 192, 1)', backgroundColor: 'rgba(75, 192, 192, 0.2)', fill: false, tension: 0.1, yAxisID: 'y-axis-percentage' },
                { label: 'Average Wage (TND)', data: chartData.average_wage, borderColor: 'rgba(153, 102, 255, 1)', backgroundColor: 'rgba(153, 102, 255, 0.2)', fill: false, tension: 0.1, yAxisID: 'y-axis-wage' },
                { label: 'Job Creation Rate (%)', data: chartData.job_creation_rate, borderColor: 'rgba(255, 159, 64, 1)', backgroundColor: 'rgba(255, 159, 64, 0.2)', fill: false, tension: 0.1, yAxisID: 'y-axis-percentage' }
            ]
        };
        const chartTitle = chartData.governorate_name ? `Labor Market Trends in ${chartData.governorate_name}` : 'Labor Market Trends';

        if (laborMarketChartInstance) {
            laborMarketChartInstance.data = data;
            laborMarketChartInstance.options.plugins.title.text = chartTitle;
            laborMarketChartInstance.update();
        } else {
            if (laborMarketChartCanvas) {
                laborMarketChartInstance = new Chart(laborMarketChartCanvas.getContext('2d'), {
                    type: 'line',
                    data: data,
                    options: {
                        responsive: true, maintainAspectRatio: false,
                        scales: {
                            'y-axis-percentage': { type: 'linear', position: 'left', title: { display: true, text: 'Percentage (%)' }, beginAtZero: true },
                            'y-axis-wage': { type: 'linear', position: 'right', title: { display: true, text: 'Average Wage (TND)' }, beginAtZero: false, grid: { drawOnChartArea: false } }
                        },
                        plugins: {
                            title: { display: true, text: chartTitle },
                            legend: { display: true, position: 'top' },
                            tooltip: { mode: 'index', intersect: false, callbacks: { label: function(context) { let label = context.dataset.label || ''; if (label) { label += ': '; } if (context.parsed.y !== null) { if (context.dataset.yAxisID === 'y-axis-wage') { label += 'TND ' + context.parsed.y.toLocaleString(); } else { label += context.parsed.y.toFixed(2) + '%'; } } return label; } } }
                        }
                    }
                });
            } else { console.error("Labor Market Chart canvas not found!"); }
        }
    }

    async function fetchAndRenderLaborMarketData(governorateId) {
        if (!governorateId) {
             if(laborMarketChartInstance) {
                laborMarketChartInstance.data.labels = [];
                laborMarketChartInstance.data.datasets.forEach(dataset => dataset.data = []);
                laborMarketChartInstance.options.plugins.title.text = 'Select a Governorate';
                laborMarketChartInstance.update();
             }
            return;
        }
        try {
            const response = await fetch(`/api/analytics/labor-market-trends/${governorateId}/`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const fetchedData = await response.json();
            if (fetchedData.years && fetchedData.years.length > 0) { initOrUpdateLaborMarketChart(fetchedData); }
            else {
                const name = fetchedData.governorate_name || 'selected area';
                initOrUpdateLaborMarketChart({ years: [], unemployment_rate: [], youth_unemployment: [], female_unemployment: [], labor_force_participation: [], average_wage: [], job_creation_rate: [], governorate_name: `No data for ${name}` });
            }
        } catch (error) {
            console.error('Error fetching labor market data:', error);
            initOrUpdateLaborMarketChart({ years: [], unemployment_rate: [], youth_unemployment: [], female_unemployment: [], labor_force_participation: [], average_wage: [], job_creation_rate: [], governorate_name: 'Error Loading Data' });
        }
    }

    if (governorateLaborMarketSelect) {
        governorateLaborMarketSelect.addEventListener('change', function() { fetchAndRenderLaborMarketData(this.value); });
        if (governorateLaborMarketSelect.value) {
            fetchAndRenderLaborMarketData(governorateLaborMarketSelect.value);
        } else {
             initOrUpdateLaborMarketChart({ years: [], unemployment_rate: [], youth_unemployment: [], female_unemployment: [], labor_force_participation: [], average_wage: [], job_creation_rate: [], governorate_name: 'Select Governorate' });
        }
    } else { console.error("Governorate select dropdown 'governorateLaborMarketSelect' not found!"); }

    // Tunisia Map Logic (for the map in the main dashboard, if it were not an iframe)
    // Since tunisiaMap is now in an iframe, this logic is primarily for tunisia_map.html,
    // but the governoratesData is available here if needed for other purposes.
    // The map initialization specific to the main dashboard's #tunisiaMap div is removed
    // as it's now an iframe.
    const tunisiaMapDiv = document.getElementById('tunisiaMap'); // This is the iframe's parent div
    if (tunisiaMapDiv) {
        // The map itself is inside the iframe src="{% url 'analytics_api:tunisia_map_view' %}"
        // and will be initialized by frontend/frontend/templates/analytics/tunisia_map.html
        console.log("Tunisia map iframe container is present.");
    }

    // Investment Advisor Logic
    // Note: The getInvestmentRecommendation function needs to be available globally if called by an inline onclick
    // If this script is included at the end of the body, it should be fine.
    // Otherwise, explicitly attach it to window: window.getInvestmentRecommendation = async function() { ... }
    // For now, assuming it's fine as a non-window function due to script placement or if the button's onclick is also set via JS.
    // If the button is <button onclick="getInvestmentRecommendation()">, then this function MUST be global.
    // To make it global from within this event listener, assign it to window.
    window.getInvestmentRecommendation = async function() {
        const sectorSelect = document.getElementById('sectorSelect');
        const recommendationResultDiv = document.getElementById('recommendationResult');

        if (!sectorSelect || !recommendationResultDiv) {
            console.error('Sector select or recommendation result div not found.');
            if (recommendationResultDiv) recommendationResultDiv.innerHTML = '<p class="text-danger">Error: UI elements missing.</p>';
            return;
        }

        const selectedSector = sectorSelect.value;
        recommendationResultDiv.innerHTML = '<p class="text-info">Loading recommendation...</p>';

        try {
            const response = await fetch(`/api/tunisia/investment-advisor/?sector=${selectedSector}`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: `HTTP error! status: ${response.status}` }));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            
            const recommendations = await response.json();

            if (recommendations.length === 0) {
                recommendationResultDiv.innerHTML = '<p class="text-muted">No specific recommendations found for this sector. Consider general economic factors.</p>';
                return;
            }

            let htmlResult = '<ul class="list-group">';
            recommendations.forEach(rec => {
                htmlResult += `
                    <li class="list-group-item">
                        <h5>${rec.governorate_name}</h5>
                        <p><strong>Sector:</strong> ${rec.sector}</p>
                        <p><strong>Overall Score:</strong> <span class="badge bg-primary">${rec.overall_score.toFixed(2)}</span></p>
                        <p class="mb-1"><strong>Reasoning:</strong> ${rec.reasoning || 'N/A'}</p>
                        <small class="text-muted">Labor: ${rec.labor_score.toFixed(2)}, Infra: ${rec.infrastructure_score.toFixed(2)}, Tax: ${rec.tax_incentive_score.toFixed(2)}, Market: ${rec.market_access_score.toFixed(2)}</small>
                    </li>`;
            });
            htmlResult += '</ul>';
            recommendationResultDiv.innerHTML = htmlResult;

        } catch (error) {
            console.error('Error fetching investment recommendation:', error);
            recommendationResultDiv.innerHTML = `<p class="text-danger">Failed to load recommendations: ${error.message}</p>`;
        }
    }
    // If the button is already in main.html with an onclick, the above function must be global.
    // If we were to add the event listener programmatically:
    // const getRecommendationButton = document.getElementById('getRecommendationButton'); // Assuming a button with this ID
    // if (getRecommendationButton) {
    //     getRecommendationButton.addEventListener('click', getInvestmentRecommendation);
    // }
});
</script>
{% endblock %}
