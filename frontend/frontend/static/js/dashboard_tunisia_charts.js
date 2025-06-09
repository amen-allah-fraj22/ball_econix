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
        console.log("DEBUG: Real Estate Chart - chartData received:", chartData); // Debug print
        
        // Ensure data arrays are pure, by mapping them
        const years = chartData.years ? chartData.years.map(y => y) : [];
        const residential_prices = chartData.residential_prices ? chartData.residential_prices.map(p => p) : [];
        const commercial_prices = chartData.commercial_prices ? chartData.commercial_prices.map(p => p) : [];
        const land_prices = chartData.land_prices ? chartData.land_prices.map(p => p) : [];

        const data = {
            labels: years,
            datasets: [
                {
                    label: 'Residential Price (€/m²)',
                    data: residential_prices,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: false,
                    tension: 0.1
                },
                {
                    label: 'Commercial Price (€/m²)',
                    data: commercial_prices,
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    fill: false,
                    tension: 0.1
                },
                {
                    label: 'Land Price (€/m²)',
                    data: land_prices,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: false,
                    tension: 0.1
                }
            ]
        };
        const chartTitle = chartData.governorate_name ? `Real Estate Price Trends in ${chartData.governorate_name}` : 'Real Estate Price Trends';

        if (realEstateChartInstance) {
            realEstateChartInstance.destroy(); // Destroy previous instance
        }

        if (realEstateChartCanvas) {
            realEstateChartCanvas.style.height = '250px'; // Explicitly set CSS height
            realEstateChartInstance = new Chart(realEstateChartCanvas.getContext('2d'), {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: { y: { beginAtZero: false, ticks: { callback: function(value) { return '€' + value.toLocaleString(); } } } },
                    plugins: { title: { display: true, text: chartTitle }, legend: { display: true, position: 'top' }, tooltip: { mode: 'index', intersect: false, callbacks: { label: function(context) { let label = context.dataset.label || ''; if (label) { label += ': '; } if (context.parsed.y !== null) { label += '€' + context.parsed.y.toLocaleString(); } return label; } } } }
                }
            });
        } else { console.error("Real Estate Chart canvas not found!"); }
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
            console.log("DEBUG: Real Estate API - fetchedData:", fetchedData); // Debug print
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
        console.log("DEBUG: Labor Market Chart - chartData received:", chartData); // Debug print
        
        // Ensure data arrays are pure, by mapping them
        const years = chartData.years ? chartData.years.map(y => y) : [];
        const unemployment_rate = chartData.unemployment_rate ? chartData.unemployment_rate.map(u => u) : [];
        const youth_unemployment = chartData.youth_unemployment ? chartData.youth_unemployment.map(y => y) : [];
        const female_unemployment = chartData.female_unemployment ? chartData.female_unemployment.map(f => f) : [];
        const labor_force_participation = chartData.labor_force_participation ? chartData.labor_force_participation.map(l => l) : [];
        const average_wage = chartData.average_wage ? chartData.average_wage.map(a => a) : [];
        const job_creation_rate = chartData.job_creation_rate ? chartData.job_creation_rate.map(j => j) : [];

        const data = {
            labels: years,
            datasets: [
                { label: 'Unemployment Rate (%)', data: unemployment_rate, borderColor: 'rgba(255, 99, 132, 1)', backgroundColor: 'rgba(255, 99, 132, 0.2)', fill: false, tension: 0.1, yAxisID: 'y-axis-percentage' },
                { label: 'Youth Unemployment (%)', data: youth_unemployment, borderColor: 'rgba(54, 162, 235, 1)', backgroundColor: 'rgba(54, 162, 235, 0.2)', fill: false, tension: 0.1, yAxisID: 'y-axis-percentage' },
                { label: 'Female Unemployment (%)', data: female_unemployment, borderColor: 'rgba(255, 206, 86, 1)', backgroundColor: 'rgba(255, 206, 86, 0.2)', fill: false, tension: 0.1, yAxisID: 'y-axis-percentage' },
                { label: 'Labor Force Participation (%)', data: labor_force_participation, borderColor: 'rgba(75, 192, 192, 1)', backgroundColor: 'rgba(75, 192, 192, 0.2)', fill: false, tension: 0.1, yAxisID: 'y-axis-percentage' },
                { label: 'Average Wage (TND)', data: average_wage, borderColor: 'rgba(153, 102, 255, 1)', backgroundColor: 'rgba(153, 102, 255, 0.2)', fill: false, tension: 0.1, yAxisID: 'y-axis-wage' },
                { label: 'Job Creation Rate (%)', data: job_creation_rate, borderColor: 'rgba(255, 159, 64, 1)', backgroundColor: 'rgba(255, 159, 64, 0.2)', fill: false, tension: 0.1, yAxisID: 'y-axis-percentage' }
            ]
        };
        const chartTitle = chartData.governorate_name ? `Labor Market Trends in ${chartData.governorate_name}` : 'Labor Market Trends';

        if (laborMarketChartInstance) {
            laborMarketChartInstance.destroy(); // Destroy previous instance
        }

        if (laborMarketChartCanvas) {
            laborMarketChartCanvas.style.height = '250px'; // Explicitly set CSS height
            laborMarketChartInstance = new Chart(laborMarketChartCanvas.getContext('2d'), {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
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

    async function fetchAndRenderLaborMarketData(governorateId) {
        console.log(`Fetching labor market data for governorate ID: ${governorateId}`); // Detailed logging
        
        if (!governorateId) {
            console.warn('No governorate ID provided');
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
            console.log('Fetch response status:', response.status); // Log response status
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`HTTP error! status: ${response.status}, message: ${errorText}`);
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const fetchedData = await response.json();
            console.log("DEBUG: Labor Market API - fetchedData:", fetchedData); // Detailed debug print
            
            if (fetchedData.years && fetchedData.years.length > 0) { 
                initOrUpdateLaborMarketChart(fetchedData); 
            }
            else {
                const name = fetchedData.governorate_name || 'selected area';
                console.warn(`No data available for ${name}`);
                initOrUpdateLaborMarketChart({ 
                    years: [], 
                    unemployment_rate: [], 
                    youth_unemployment: [], 
                    female_unemployment: [], 
                    labor_force_participation: [], 
                    average_wage: [], 
                    job_creation_rate: [], 
                    governorate_name: `No data for ${name}` 
                });
            }
        } catch (error) {
            console.error('Error fetching labor market data:', error);
            initOrUpdateLaborMarketChart({ 
                years: [], 
                unemployment_rate: [], 
                youth_unemployment: [], 
                female_unemployment: [], 
                labor_force_participation: [], 
                average_wage: [], 
                job_creation_rate: [], 
                governorate_name: 'Error Loading Data' 
            });
        }
    }

    // Function to initialize the chart with the first governorate
    function initializeLaborMarketChart() {
        if (governorateLaborMarketSelect && governorateLaborMarketSelect.options.length > 0) {
            // Select the first governorate by default
            const firstGovernorateId = governorateLaborMarketSelect.options[0].value;
            governorateLaborMarketSelect.value = firstGovernorateId;
            
            // Fetch and render data for the first governorate
            fetchAndRenderLaborMarketData(firstGovernorateId);
        }
    }

    // Add event listener for governorate selection
    if (governorateLaborMarketSelect) {
        governorateLaborMarketSelect.addEventListener('change', function() {
            const selectedGovernorateId = this.value;
            fetchAndRenderLaborMarketData(selectedGovernorateId);
        });
    }

    // Initialize the chart when the page loads
    initializeLaborMarketChart();

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

});

// Investment Recommendation Logic - Defined globally for access from HTML onclick
window.getInvestmentRecommendation = async function() {
    const sectorSelect = document.getElementById('sectorSelect');
    const recommendationResult = document.getElementById('recommendationResult');
    const selectedSector = sectorSelect.value;

    if (!selectedSector) {
        recommendationResult.innerHTML = `<p class="text-danger">Please select a sector.</p>`;
        return;
    }

    recommendationResult.innerHTML = `<p class="text-info"><i>Fetching recommendation for ${selectedSector}...</i></p>`;

    try {
        // Redirect to the new recommendations page
        window.location.href = `/api/analytics/investment-recommendations-page/${encodeURIComponent(selectedSector)}/`;

    } catch (error) {
        console.error('Error in getInvestmentRecommendation:', error);
        recommendationResult.innerHTML = `<div class="alert alert-danger">Error fetching recommendation. Please try again.</div>`;
    }
};
