class StudentDashboard {
    static async render(container) {
        const user = auth.getUser();
        if (!user) return;

        try {
            const [activeIssues, resolvedIssues, proctor] = await Promise.all([
                api.getIssuesForUser(user.id, false),
                api.getIssuesForUser(user.id, true),
                user.reports_to ? api.getUser(user.reports_to) : null
            ]);

            const resolvedOnly = (resolvedIssues || []).filter(i => i.status === 'closed');

            container.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Active Complaints</div>
                        <div class="stat-value">${(activeIssues || []).length}</div>
                    </div>
                    <div class="stat-card resolved">
                        <div class="stat-label">Resolved</div>
                        <div class="stat-value">${resolvedOnly.length}</div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Raise a Complaint</h2>
                    </div>
                    <form id="raise-complaint-form" class="form-card">
                        <div class="form-group-full">
                            <label for="complaint-title">Title</label>
                            <input type="text" id="complaint-title" placeholder="Brief title of your complaint" required>
                        </div>
                        <div class="form-group-full">
                            <label for="complaint-description">Description</label>
                            <textarea id="complaint-description" placeholder="Describe your complaint in detail..." required></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-paper-plane"></i> Submit Complaint
                        </button>
                    </form>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Your Complaints</h2>
                    </div>
                    ${this.renderIssuesTable(activeIssues, 'active')}
                </div>

                ${resolvedOnly.length > 0 ? `
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Resolved Complaints</h2>
                    </div>
                    ${this.renderIssuesTable(resolvedOnly, 'resolved')}
                </div>
                ` : ''}
            `;

            // Setup form handler
            const form = document.getElementById('raise-complaint-form');
            if (form) {
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    await this.handleSubmitComplaint();
                });
            }
        } catch (error) {
            console.error('Error loading student dashboard:', error);
            container.innerHTML = '<div class="error-message show">Failed to load dashboard</div>';
        }
    }

    static async handleSubmitComplaint() {
        const user = auth.getUser();
        const title = document.getElementById('complaint-title').value;
        const description = document.getElementById('complaint-description').value;

        if (!title || !description) {
            showToast('Title and description are required', 'error');
            return;
        }

        try {
            await api.createIssue({
                student_id: user.id,
                title: title,
                description: description
            });

            showToast('Complaint submitted successfully!', 'success');
            document.getElementById('raise-complaint-form').reset();
            
            // Reload dashboard
            setTimeout(() => {
                StudentDashboard.render(document.getElementById('dashboard-content'));
            }, 1000);
        } catch (error) {
            showToast('Failed to submit complaint', 'error');
        }
    }

    static renderIssuesTable(issues, type) {
        if (!issues || issues.length === 0) {
            return '<div class="empty-state"><div class="empty-state-icon">📋</div><h3>No Complaints</h3><p>You don\'t have any ' + type + ' complaints.</p></div>';
        }

        const rows = issues.map(issue => {
            const priority = issue.priority || 'N/A';
            const status = issue.status || 'open';
            const raisedBy = auth.getUserById(issue.student_id)?.name || 'Unknown';
            const assignedTo = issue.assigned_to ? (auth.getUserById(issue.assigned_to)?.name || 'Unassigned') : 'Unassigned';
            const verifiedBy = issue.verified_by ? (auth.getUserById(issue.verified_by)?.name || '-') : '-';
            const verifiedAt = issue.verified_at ? new Date(issue.verified_at).toLocaleString() : '-';

            let row = `
                <tr>
                    <td>${issue.id}</td>
                    <td><strong>${issue.title}</strong></td>
                    <td>${issue.category || 'N/A'}</td>
                    <td><span class="badge badge-${priority.toLowerCase()}">${priority}</span></td>
                    <td><span class="badge badge-${status.toLowerCase()}">${status}</span></td>
            `;

            if (type === 'resolved') {
                row += `
                    <td>${raisedBy}</td>
                    <td>${verifiedBy}</td>
                    <td>${verifiedAt}</td>
                `;
            } else {
                row += `
                    <td>${raisedBy}</td>
                    <td>${assignedTo}</td>
                    <td>${new Date(issue.created_at).toLocaleString()}</td>
                `;
            }

            row += '</tr>';
            return row;
        }).join('');

        const headers = type === 'resolved' 
            ? '<th>ID</th><th>Title</th><th>Category</th><th>Priority</th><th>Status</th><th>Raised By</th><th>Verified By</th><th>Verified At</th>'
            : '<th>ID</th><th>Title</th><th>Category</th><th>Priority</th><th>Status</th><th>Raised By</th><th>Assigned To</th><th>Created At</th>';

        return `
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>${headers}</tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            </div>
        `;
    }
}
