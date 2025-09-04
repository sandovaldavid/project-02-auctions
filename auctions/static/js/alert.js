// Alert Auto-Dismiss JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeAlerts();
});

function initializeAlerts() {
    // Get all alert elements
    const alerts = document.querySelectorAll('.custom-alert');
    
    alerts.forEach(function(alert) {
        // Set auto-dismiss timer for 5 seconds (matching CSS animation)
        setTimeout(function() {
            dismissAlert(alert);
        }, 5000);
        
        // Handle manual close button
        const closeBtn = alert.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                dismissAlert(alert);
            });
        }
    });
}

function dismissAlert(alert) {
    if (!alert || !alert.parentElement) return;
    
    const alertWrapper = alert.closest('.alert-wrapper');
    if (!alertWrapper) return;
    
    // Add fade out animation
    alertWrapper.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
    alertWrapper.style.opacity = '0';
    alertWrapper.style.transform = 'translateX(100%)';
    
    // Remove element after animation
    setTimeout(function() {
        if (alertWrapper.parentElement) {
            alertWrapper.parentElement.removeChild(alertWrapper);
        }
    }, 300);
}

// Function to manually dismiss all alerts
function dismissAllAlerts() {
    const alerts = document.querySelectorAll('.custom-alert');
    alerts.forEach(function(alert) {
        dismissAlert(alert);
    });
}

// Export functions for external use
window.AlertManager = {
    dismissAlert: dismissAlert,
    dismissAllAlerts: dismissAllAlerts,
    initializeAlerts: initializeAlerts
};