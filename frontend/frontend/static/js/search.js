// frontend/static/js/search.js
class CountrySearch {
    constructor(inputId = 'countrySearch', resultsId = 'searchResults') {
        this.searchInput = document.getElementById(inputId);
        this.resultsContainer = document.getElementById(resultsId);
        this.debounceTimer = null;
        this.debounceDelay = 300; // milliseconds

        if (!this.searchInput) {
            console.error(`Search input with ID '${inputId}' not found.`);
            return;
        }
        if (!this.resultsContainer) {
            console.error(`Results container with ID '${resultsId}' not found.`);
            return;
        }
    }

    async fetchData(query) {
        if (!query || query.trim() === '') {
            this.handleSearchResults([]); // Clear results if query is empty
            return null;
        }
        try {
            const response = await fetch(`/api/analytics/search-countries/?q=${encodeURIComponent(query)}`);
            if (!response.ok) {
                console.error(`Error fetching search results: ${response.statusText}`);
                this.resultsContainer.innerHTML = '<p class="text-danger">Error fetching results.</p>';
                return null;
            }
            return await response.json();
        } catch (error) {
            console.error('Exception during search data fetch:', error);
            this.resultsContainer.innerHTML = '<p class="text-danger">Error fetching results.</p>';
            return null;
        }
    }

    handleSearchResults(results) {
        this.resultsContainer.innerHTML = ''; // Clear previous results

        if (!results || results.length === 0) {
            this.resultsContainer.innerHTML = '<p class="text-muted">No countries found.</p>';
            return;
        }

        const ul = document.createElement('ul');
        ul.className = 'list-group'; // Bootstrap styling

        results.forEach(country => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center list-group-item-action'; // Added list-group-item-action for hover/click

            const flagPlaceholder = `<span class="me-2">🌍</span>`;

            li.innerHTML = `
                <div>
                    ${flagPlaceholder}
                    <strong>${country.name}</strong> (${country.code})
                    <small class="d-block text-muted">${country.continent || ''}${country.region ? ' - ' + country.region : ''}</small>
                </div>
                <span class="badge bg-primary rounded-pill">
                    ${country.happiness_score !== null ? country.happiness_score.toFixed(2) : 'N/A'}
                </span>
            `;
            li.style.cursor = 'pointer';
            li.addEventListener('click', () => {
                // Navigate to country detail page
                window.location.href = `/countries/${encodeURIComponent(country.name)}/`;
                this.resultsContainer.innerHTML = ''; // Clear results after click
            });
            ul.appendChild(li);
        });
        this.resultsContainer.appendChild(ul);
    }

    initSearch() {
        if (!this.searchInput) return;

        this.searchInput.addEventListener('input', () => {
            clearTimeout(this.debounceTimer);
            const query = this.searchInput.value;

            if (!query.trim()) {
                this.resultsContainer.innerHTML = '';
                return;
            }

            this.resultsContainer.innerHTML = '<p class="text-muted"><i>Searching...</i></p>';


            this.debounceTimer = setTimeout(async () => {
                const results = await this.fetchData(query);
                if (results !== null) {
                    this.handleSearchResults(results);
                } else if (query.trim()) {
                    // Error message is already set by fetchData in this case.
                }
            }, this.debounceDelay);
        });

        document.addEventListener('click', (event) => {
            if (this.searchInput && this.resultsContainer) {
                const isClickInsideSearch = this.searchInput.contains(event.target);
                const isClickInsideResults = this.resultsContainer.contains(event.target);
                if (!isClickInsideSearch && !isClickInsideResults) {
                    this.resultsContainer.innerHTML = '';
                }
            }
        });
        console.log('Country search initialized.');
    }
}
