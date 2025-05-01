// Main JS file for Bob the Whisky Expert

document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const usernameForm = document.getElementById('username-form');
    if (usernameForm) {
        usernameForm.addEventListener('submit', function(event) {
            const usernameInput = document.getElementById('username');
            if (!usernameInput.value.trim()) {
                event.preventDefault();
                alert('Please enter a BAXUS username');
                return;
            }
            
            // Show loading spinner
            const loadingSpinner = document.getElementById('loading-spinner');
            if (loadingSpinner) {
                loadingSpinner.style.display = 'block';
            }
            
            // Hide the form
            usernameForm.style.display = 'none';
        });
    }
    
    // Bootstrap tooltips initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Flavor profile visualization
    const flavorContainers = document.querySelectorAll('.flavor-profile-container');
    flavorContainers.forEach(container => {
        const flavorData = JSON.parse(container.dataset.flavors || '{}');
        const flavorProfileDiv = document.createElement('div');
        flavorProfileDiv.className = 'flavor-profile';
        
        for (const [flavor, value] of Object.entries(flavorData)) {
            if (value > 0) {
                const flavorDiv = document.createElement('div');
                flavorDiv.className = 'flavor-item';
                
                const label = document.createElement('small');
                label.className = 'text-muted';
                label.textContent = flavor;
                
                const barContainer = document.createElement('div');
                barContainer.className = 'progress w-100';
                barContainer.style.height = '8px';
                
                const bar = document.createElement('div');
                bar.className = 'progress-bar';
                bar.style.width = `${Math.min(100, value)}%`;
                bar.setAttribute('title', `${flavor}: ${Math.round(value)}%`);
                
                // Set different colors for different flavors
                switch(flavor.toLowerCase()) {
                    case 'peated':
                    case 'smoky':
                        bar.classList.add('bg-danger');
                        break;
                    case 'sherried':
                    case 'fruity':
                        bar.classList.add('bg-success');
                        break;
                    case 'spicy':
                        bar.classList.add('bg-warning');
                        break;
                    case 'vanilla':
                    case 'caramel':
                        bar.classList.add('bg-info');
                        break;
                    default:
                        bar.classList.add('bg-primary');
                }
                
                barContainer.appendChild(bar);
                flavorDiv.appendChild(label);
                flavorDiv.appendChild(barContainer);
                flavorProfileDiv.appendChild(flavorDiv);
            }
        }
        
        container.appendChild(flavorProfileDiv);
    });
});
