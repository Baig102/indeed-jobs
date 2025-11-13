if (window.location.pathname === '/') {
    loadStats();
}

async function loadStats() {
    try {
        const response = await fetch('/stats');
        const data = await response.json();
        
        // Update CSV status
        const csvStatus = document.getElementById('csv-status');
        if (csvStatus) {
            csvStatus.innerHTML = data.csv_exists 
                ? '<span class="badge bg-success"><i class="fas fa-check"></i> CSV File Ready</span>'
                : '<span class="badge bg-secondary"><i class="fas fa-times"></i> No CSV File</span>';
        }
        
        // Update DB status
        const dbStatus = document.getElementById('db-status');
        if (dbStatus) {
            dbStatus.innerHTML = data.db_exists 
                ? '<span class="badge bg-success"><i class="fas fa-check"></i> Database Ready</span>'
                : '<span class="badge bg-secondary"><i class="fas fa-times"></i> No Database</span>';
        }
        
        // Update total jobs
        const totalJobs = document.getElementById('total-jobs');
        if (totalJobs) {
            totalJobs.textContent = data.total_jobs;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Utility function to show toast notifications
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    toast.style.zIndex = '9999';
    toast.innerHTML = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
