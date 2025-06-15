class SeriesFilter {
    constructor() {
        this.allSeries = [];
        this.filteredSeries = [];
        this.filters = {
            search: '',
            type: '',
            genre: '',
            language: ''
        };
        this.init();
    }

    async init() {
        await this.loadSeries();
        this.bindEvents();
        this.renderSeries();
    }

    async loadSeries() {
        try {
            const response = await fetch('/api/series/');
            const data = await response.json();
            this.allSeries = data.series;
            this.filteredSeries = [...this.allSeries];
        } catch (error) {
            console.error('Error loading series:', error);
        }
    }

    bindEvents() {
        document.getElementById('search-input').addEventListener('input', (e) => {
            this.filters.search = e.target.value;
            this.applyFilters();
        });

        document.getElementById('clear-button').addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('search-input').value = '';
            this.filters.search = '';
            this.applyFilters();
        });

        document.getElementsByName('type-select').forEach(radio => {
            radio.addEventListener('change', (e) => {
            this.filters.type = e.target.value;
            this.applyFilters();
            });
        });

        document.getElementById('genre-select').addEventListener('change', (e) => {
            this.filters.genre = e.target.value;
            this.applyFilters();
        });

        document.getElementById('language-select').addEventListener('change', (e) => {
            this.filters.language = e.target.value;
            this.applyFilters();
        });

        document.getElementById('reset-button').addEventListener('click', (e) => {
            e.preventDefault();
            this.resetAllFilters();
        });
    }

    applyFilters() {
        this.filteredSeries = this.allSeries.filter(series => {
            // Search filter
            if (this.filters.search) {
                const searchTerm = this.filters.search.toLowerCase();
                const nameMatch = series.name.toLowerCase().includes(searchTerm);
                const authorMatch = series.authors.some(author =>
                    author.toLowerCase().includes(searchTerm)
                );
                if (!nameMatch && !authorMatch) return false;
            }
            // Type filter
            if (this.filters.type && series.type !== this.filters.type) {
                return false;
            }
            // Genre filter
            if (this.filters.genre && series.genre !== this.filters.genre) {
                return false;
            }
            // Language filter
            if (this.filters.language && series.language !== this.filters.language) {
                return false;
            }
            return true;
        });

        this.renderSeries();
    }

    renderSeries() {
        const container = document.getElementById('series-list-container');
        if (!container) return;

        const resultCount = this.filteredSeries.length;
        const pluralSuffix = resultCount > 1 ? 's' : '';
        document.getElementById('results-count').innerText = `${resultCount} résultat${pluralSuffix}`;

        let html = '';
        this.filteredSeries.forEach(series => {
            html += `
                <div class="col-12 col-md-6 col-xxl-4">
                    <div class="card book-card h-100">
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title">${this.escapeHtml(series.name)}</h5>
                            <p class="card-text mb-1">${this.escapeHtml(series.authors.join(', '))}</p>
                            <p class="card-text mb-2">${this.escapeHtml(series.type_display)} - ${this.escapeHtml(series.genre_display)}</p>
                            <a class="card-link stretched-link link-primary mt-auto" href="${series.url}">Détails</a>
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    resetAllFilters() {
        this.filters = {
            search: '',
            type: '',
            genre: '',
            language: ''
        };
    
        document.getElementById('search-input').value = '';
        document.getElementsByName('type-select').forEach(radio => radio.checked = radio.value === '');
        document.getElementById('genre-select').value = '';
        document.getElementById('language-select').value = '';
    
        this.applyFilters();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new SeriesFilter();
});