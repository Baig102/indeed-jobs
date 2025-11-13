let currentJobs = [];

document.addEventListener('DOMContentLoaded', () => {
    loadJobs();
    
    document.getElementById('addJobForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await addJob();
    });
    
    document.getElementById('editJobForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await updateJob();
    });
});

async function loadJobs() {
    const city = document.getElementById('filterCity').value;
    const position = document.getElementById('filterPosition').value;
    
    let url = '/api/jobs?';
    if (city) url += `city=${encodeURIComponent(city)}&`;
    if (position) url += `position=${encodeURIComponent(position)}`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            currentJobs = data.jobs;
            displayJobs(data.jobs);
            document.getElementById('jobsCount').textContent = data.count;
        } else {
            showError('Failed to load jobs: ' + data.error);
        }
    } catch (error) {
        showError('Error loading jobs: ' + error.message);
    }
}

function displayJobs(jobs) {
    const jobsList = document.getElementById('jobsList');
    
    if (jobs.length === 0) {
        jobsList.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-info-circle"></i> No jobs found. Try different filters or add new jobs.
            </div>
        `;
        return;
    }
    
    jobsList.innerHTML = jobs.map(job => `
        <div class="card job-card shadow-sm mb-3">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-9">
                        <h5 class="card-title text-primary">
                            <i class="fas fa-briefcase"></i> ${job.title}
                        </h5>
                        <p class="mb-1">
                            <strong><i class="fas fa-building"></i> ${job.company}</strong>
                        </p>
                        <p class="mb-1">
                            <i class="fas fa-map-marker-alt text-danger"></i> ${job.location}
                            ${job.salary !== 'N/A' ? ` | <i class="fas fa-dollar-sign text-success"></i> ${job.salary}` : ''}
                        </p>
                        <p class="mb-1">
                            <i class="fas fa-calendar text-info"></i> ${job.posted_date}
                            ${job.job_type !== 'N/A' ? ` | <i class="fas fa-briefcase"></i> ${job.job_type}` : ''}
                        </p>
                        <p class="text-muted small mb-2">${job.description}</p>
                        ${job.job_url !== 'N/A' ? `
                            <a href="${job.job_url}" target="_blank" class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-external-link-alt"></i> View Job
                            </a>
                        ` : ''}
                    </div>
                    <div class="col-md-3 text-end">
                        <button class="btn btn-sm btn-info mb-2" onclick="editJobModal(${job.id})">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteJobConfirm(${job.id})">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

async function addJob() {
    const jobData = {
        title: document.getElementById('newTitle').value,
        company: document.getElementById('newCompany').value,
        location: document.getElementById('newLocation').value || 'N/A',
        salary: document.getElementById('newSalary').value || 'N/A',
        job_type: document.getElementById('newJobType').value || 'N/A',
        description: document.getElementById('newDescription').value || 'N/A',
        posted_date: document.getElementById('newDate').value || 'N/A',
        job_url: document.getElementById('newUrl').value || 'N/A'
    };
    
    try {
        const response = await fetch('/api/jobs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(jobData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Job added successfully!');
            document.getElementById('addJobForm').reset();
            bootstrap.Modal.getInstance(document.getElementById('addJobModal')).hide();
            loadJobs();
        } else {
            showError('Failed to add job: ' + data.error);
        }
    } catch (error) {
        showError('Error adding job: ' + error.message);
    }
}

// Show edit modal
function editJobModal(jobId) {
    const job = currentJobs.find(j => j.id === jobId);
    if (!job) return;
    
    document.getElementById('editJobId').value = job.id;
    document.getElementById('editTitle').value = job.title;
    document.getElementById('editCompany').value = job.company;
    document.getElementById('editLocation').value = job.location;
    document.getElementById('editSalary').value = job.salary;
    document.getElementById('editJobType').value = job.job_type;
    document.getElementById('editDescription').value = job.description;
    document.getElementById('editDate').value = job.posted_date;
    
    new bootstrap.Modal(document.getElementById('editJobModal')).show();
}

// Update job
async function updateJob() {
    const jobId = document.getElementById('editJobId').value;
    const jobData = {
        title: document.getElementById('editTitle').value,
        company: document.getElementById('editCompany').value,
        location: document.getElementById('editLocation').value,
        salary: document.getElementById('editSalary').value,
        job_type: document.getElementById('editJobType').value,
        description: document.getElementById('editDescription').value,
        posted_date: document.getElementById('editDate').value
    };
    
    try {
        const response = await fetch(`/api/jobs/${jobId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(jobData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Job updated successfully!');
            bootstrap.Modal.getInstance(document.getElementById('editJobModal')).hide();
            loadJobs();
        } else {
            showError('Failed to update job: ' + data.error);
        }
    } catch (error) {
        showError('Error updating job: ' + error.message);
    }
}

// Delete job confirmation
function deleteJobConfirm(jobId) {
    if (confirm('Are you sure you want to delete this job?')) {
        deleteJob(jobId);
    }
}

// Delete job
async function deleteJob(jobId) {
    try {
        const response = await fetch(`/api/jobs/${jobId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Job deleted successfully!');
            loadJobs();
        } else {
            showError('Failed to delete job: ' + data.error);
        }
    } catch (error) {
        showError('Error deleting job: ' + error.message);
    }
}

// Helper functions
function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'danger');
}

function showNotification(message, type) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 3000);
}
