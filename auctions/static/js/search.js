// Advanced Search JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize search functionality
    initializeSearch();
    initializeAutocomplete();
    initializeViewToggle();
    initializePriceRange();
    initializeFilters();
});

function initializeSearch() {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchQuery');
    const clearBtn = document.getElementById('clearSearch');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            performSearch();
        });
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            clearSearch();
        });
    }
    
    // Auto-search on input change (debounced)
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length >= 2) {
                    performSearch();
                }
            }, 500);
        });
    }
}

function initializeAutocomplete() {
    const searchInput = document.getElementById('searchQuery');
    const autocompleteContainer = document.getElementById('autocompleteResults');
    
    if (!searchInput || !autocompleteContainer) return;
    
    let autocompleteTimeout;
    let currentFocus = -1;
    
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        clearTimeout(autocompleteTimeout);
        
        if (query.length < 2) {
            hideAutocomplete();
            return;
        }
        
        autocompleteTimeout = setTimeout(() => {
            fetchAutocompleteResults(query);
        }, 300);
    });
    
    searchInput.addEventListener('keydown', function(e) {
        const items = autocompleteContainer.querySelectorAll('.autocomplete-item');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            currentFocus++;
            if (currentFocus >= items.length) currentFocus = 0;
            setActiveItem(items, currentFocus);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            currentFocus--;
            if (currentFocus < 0) currentFocus = items.length - 1;
            setActiveItem(items, currentFocus);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (currentFocus > -1 && items[currentFocus]) {
                selectAutocompleteItem(items[currentFocus]);
            } else {
                performSearch();
            }
        } else if (e.key === 'Escape') {
            hideAutocomplete();
        }
    });
    
    // Hide autocomplete when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !autocompleteContainer.contains(e.target)) {
            hideAutocomplete();
        }
    });
    
    function fetchAutocompleteResults(query) {
        fetch(`/search/autocomplete/?q=${encodeURIComponent(query)}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            displayAutocompleteResults(data.suggestions);
        })
        .catch(error => {
            console.error('Autocomplete error:', error);
            hideAutocomplete();
        });
    }
    
    function displayAutocompleteResults(suggestions) {
        autocompleteContainer.innerHTML = '';
        currentFocus = -1;
        
        if (suggestions.length === 0) {
            hideAutocomplete();
            return;
        }
        
        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.innerHTML = `
                <div class="item-title">${escapeHtml(suggestion.title)}</div>
                ${suggestion.category ? `<div class="item-category">${escapeHtml(suggestion.category)}</div>` : ''}
            `;
            
            item.addEventListener('click', function() {
                selectAutocompleteItem(this);
            });
            
            autocompleteContainer.appendChild(item);
        });
        
        showAutocomplete();
    }
    
    function setActiveItem(items, index) {
        items.forEach(item => item.classList.remove('active'));
        if (items[index]) {
            items[index].classList.add('active');
        }
    }
    
    function selectAutocompleteItem(item) {
        const title = item.querySelector('.item-title').textContent;
        searchInput.value = title;
        hideAutocomplete();
        performSearch();
    }
    
    function showAutocomplete() {
        autocompleteContainer.style.display = 'block';
    }
    
    function hideAutocomplete() {
        autocompleteContainer.style.display = 'none';
        currentFocus = -1;
    }
}

function initializeViewToggle() {
    const gridBtn = document.getElementById('gridView');
    const listBtn = document.getElementById('listView');
    const resultsContainer = document.getElementById('searchResults');
    
    if (!gridBtn || !listBtn || !resultsContainer) return;
    
    gridBtn.addEventListener('click', function() {
        setView('grid');
    });
    
    listBtn.addEventListener('click', function() {
        setView('list');
    });
    
    function setView(view) {
        if (view === 'grid') {
            gridBtn.classList.add('active');
            listBtn.classList.remove('active');
            resultsContainer.className = 'listings-grid';
        } else {
            listBtn.classList.add('active');
            gridBtn.classList.remove('active');
            resultsContainer.className = 'listings-list';
        }
        
        // Save preference
        localStorage.setItem('searchView', view);
    }
    
    // Load saved preference
    const savedView = localStorage.getItem('searchView') || 'grid';
    setView(savedView);
}

function initializePriceRange() {
    const minPriceInput = document.getElementById('minPrice');
    const maxPriceInput = document.getElementById('maxPrice');
    
    if (!minPriceInput || !maxPriceInput) return;
    
    function validatePriceRange() {
        const minPrice = parseFloat(minPriceInput.value) || 0;
        const maxPrice = parseFloat(maxPriceInput.value) || 0;
        
        if (maxPrice > 0 && minPrice > maxPrice) {
            maxPriceInput.value = minPrice;
        }
    }
    
    minPriceInput.addEventListener('change', validatePriceRange);
    maxPriceInput.addEventListener('change', validatePriceRange);
}

function initializeFilters() {
    const sortSelect = document.getElementById('sortBy');
    
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            performSearch();
        });
    }
    
    // Initialize active filters display
    updateActiveFilters();
}

function performSearch() {
    const form = document.getElementById('searchForm');
    const resultsContainer = document.getElementById('searchResults');
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    if (!form || !resultsContainer) return;
    
    // Show loading state
    if (loadingSpinner) {
        loadingSpinner.style.display = 'block';
    }
    resultsContainer.style.opacity = '0.5';
    
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);
    
    fetch(`/search/?${params.toString()}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        // Parse the response and update results
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newResults = doc.getElementById('searchResults');
        const newResultsHeader = doc.querySelector('.results-header');
        
        if (newResults) {
            resultsContainer.innerHTML = newResults.innerHTML;
        }
        
        if (newResultsHeader) {
            const currentHeader = document.querySelector('.results-header');
            if (currentHeader) {
                currentHeader.innerHTML = newResultsHeader.innerHTML;
            }
        }
        
        // Update URL without page reload
        const newUrl = `/search/?${params.toString()}`;
        window.history.pushState({}, '', newUrl);
        
        // Update active filters
        updateActiveFilters();
    })
    .catch(error => {
        console.error('Search error:', error);
        showErrorMessage('An error occurred while searching. Please try again.');
    })
    .finally(() => {
        // Hide loading state
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }
        resultsContainer.style.opacity = '1';
    });
}

function clearSearch() {
    const form = document.getElementById('searchForm');
    if (!form) return;
    
    // Reset form fields
    form.reset();
    
    // Clear URL parameters
    window.history.pushState({}, '', '/search/');
    
    // Perform empty search to show all results
    performSearch();
}

function updateActiveFilters() {
    const activeFiltersContainer = document.getElementById('activeFilters');
    if (!activeFiltersContainer) return;
    
    const filters = [];
    const form = document.getElementById('searchForm');
    if (!form) return;
    
    const formData = new FormData(form);
    
    // Check each filter
    if (formData.get('q')) {
        filters.push({
            label: `Search: "${formData.get('q')}"`,
            param: 'q'
        });
    }
    
    if (formData.get('category')) {
        const categorySelect = document.getElementById('category');
        const categoryText = categorySelect.options[categorySelect.selectedIndex].text;
        filters.push({
            label: `Category: ${categoryText}`,
            param: 'category'
        });
    }
    
    if (formData.get('min_price')) {
        filters.push({
            label: `Min Price: $${formData.get('min_price')}`,
            param: 'min_price'
        });
    }
    
    if (formData.get('max_price')) {
        filters.push({
            label: `Max Price: $${formData.get('max_price')}`,
            param: 'max_price'
        });
    }
    
    // Display filters
    if (filters.length > 0) {
        activeFiltersContainer.innerHTML = filters.map(filter => `
            <span class="filter-badge">
                ${escapeHtml(filter.label)}
                <button type="button" class="remove-filter" onclick="removeFilter('${filter.param}')">
                    <i class="fas fa-times"></i>
                </button>
            </span>
        `).join('');
        activeFiltersContainer.style.display = 'block';
    } else {
        activeFiltersContainer.style.display = 'none';
    }
}

function removeFilter(param) {
    const form = document.getElementById('searchForm');
    if (!form) return;
    
    const input = form.querySelector(`[name="${param}"]`);
    if (input) {
        if (input.type === 'select-one') {
            input.selectedIndex = 0;
        } else {
            input.value = '';
        }
    }
    
    performSearch();
}

function showErrorMessage(message) {
    const resultsContainer = document.getElementById('searchResults');
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${escapeHtml(message)}
        </div>
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Handle browser back/forward buttons
window.addEventListener('popstate', function(e) {
    // Reload the page to handle back/forward navigation
    window.location.reload();
});

// Initialize search suggestions
function initializeSearchSuggestions() {
    const suggestionsContainer = document.getElementById('searchSuggestions');
    if (!suggestionsContainer) return;
    
    const suggestions = suggestionsContainer.querySelectorAll('.suggestion-chip');
    suggestions.forEach(suggestion => {
        suggestion.addEventListener('click', function(e) {
            e.preventDefault();
            const searchInput = document.getElementById('searchQuery');
            if (searchInput) {
                searchInput.value = this.textContent.trim();
                performSearch();
            }
        });
    });
}

// Call after DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeSearchSuggestions();
});