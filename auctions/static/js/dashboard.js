// Dashboard Charts JavaScript

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get data from HTML data attributes
    const dataContainer = document.getElementById('dashboard-data');
    const categoryData = JSON.parse(dataContainer.dataset.categoryStats || '[]');
    const monthlyListingsData = JSON.parse(dataContainer.dataset.monthlyListings || '[]');
    const monthlyBidsData = JSON.parse(dataContainer.dataset.monthlyBids || '[]');

    // Category Distribution Chart
    if (categoryData.length > 0) {
        const categoryLabels = categoryData.map(item => item.category || 'Sin categoría');
        const categoryCounts = categoryData.map(item => item.count);

        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        const categoryChart = new Chart(categoryCtx, {
            type: 'doughnut',
            data: {
                labels: categoryLabels,
                datasets: [{
                    data: categoryCounts,
                    backgroundColor: [
                        '#4e73df',
                        '#1cc88a',
                        '#36b9cc',
                        '#f6c23e',
                        '#e74a3b'
                    ],
                    hoverBackgroundColor: [
                        '#2e59d9',
                        '#17a673',
                        '#2c9faf',
                        '#f4b619',
                        '#e02d1b'
                    ],
                    hoverBorderColor: "rgba(234, 236, 244, 1)"
                }]
            },
            options: {
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Monthly Trends Chart
    if (monthlyListingsData.length > 0 || monthlyBidsData.length > 0) {
        // Create a complete month range for the last 6 months
        const months = [];
        const listingCounts = [];
        const bidCounts = [];

        for (let i = 5; i >= 0; i--) {
            const date = new Date();
            date.setMonth(date.getMonth() - i);
            const monthKey = date.getFullYear() + '-' + String(date.getMonth() + 1).padStart(2, '0');
            months.push(date.toLocaleDateString('es-ES', { month: 'short', year: 'numeric' }));
            
            const listingData = monthlyListingsData.find(item => item.month === monthKey);
            const bidData = monthlyBidsData.find(item => item.month === monthKey);
            
            listingCounts.push(listingData ? listingData.count : 0);
            bidCounts.push(bidData ? bidData.count : 0);
        }

        const trendsCtx = document.getElementById('trendsChart').getContext('2d');
        const trendsChart = new Chart(trendsCtx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Nuevas Subastas',
                    data: listingCounts,
                    borderColor: '#4e73df',
                    backgroundColor: 'rgba(78, 115, 223, 0.1)',
                    borderWidth: 2,
                    fill: true
                }, {
                    label: 'Nuevas Pujas',
                    data: bidCounts,
                    borderColor: '#1cc88a',
                    backgroundColor: 'rgba(28, 200, 138, 0.1)',
                    borderWidth: 2,
                    fill: true
                }]
            },
            options: {
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }
});