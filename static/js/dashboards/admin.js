class AdminDashboard {
    static async render(container) {
        try {
            const [stats, issues] = await Promise.all([
                api.getAdminStats(),
                api.getAdminIssues()
            ]);

            container.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card total">
                        <div class="stat-label">Total Issues</div>
                        <div class="stat-value">${stats.total || 0}</div>
                    </div>
                    <div class="stat-card active">
                        <div class="stat-label">Active Issues</div>
                        <div class="stat-value">${stats.active || 0}</div>
                    </div>
                    <div class="stat-card resolved">
                        <div class="stat-label">Resolved Issues</div>
                        <div class="stat-value">${stats.resolved || 0}</div>
                    </div>
                </div>

                ${stats.by_department && stats.by_department.length > 0 ? `
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Department Breakdown</h2>
                    </div>
                    ${this.renderDepartmentStats(stats.by_department)}
                </div>
                ` : ''}

                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">All Issues</h2>
                    </div>
                    ${this.renderIssuesTable(issues)}
                </div>
            `;
        } catch (error) {
            console.error('Error loading admin dashboard:', error);
            container.innerHTML = '<div class="error-message show">Failed to load dashboard</div>';
        }
    }

    static renderDepartmentStats(departments) {
        const rows = departments.map(dept => `
            <tr>
                <td><strong>${dept.department_name}</strong></td>
                <td>${dept.total}</td>
                <td>${dept.active}</td>
                <td>${dept.resolved}</td>
            </tr>
        `).join('');

        return `
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Department</th>
                            <th>Total</th>
                            <th>Active</th>
                            <th>Resolved</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            </div>
        `;
    }

    static renderIssuesTable(issues) {
        if (!issues || issues.length === 0) {
            return '<div class="empty-state"><div class="empty-state-icon">📊</div><h3>No Issues</h3><p>No issues found in the system.</p></div>';
        }

        const rows = issues.map(issue => {
            const status = issue.status || 'open';
            const raisedBy = auth.getUserById(issue.student_id)?.name || 'Unknown';
            
            return `
                <tr>
                    <td>${issue.id}</td>
                    <td><strong>${issue.title}</strong></td>
                    <td><span class="badge badge-${status.toLowerCase()}">${status}</span></td>
                    <td>${raisedBy}</td>
                    <td>${new Date(issue.created_at).toLocaleString()}</td>
                </tr>
            `;
        }).join('');

        return `
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Status</th>
                            <th>Raised By</th>
                            <th>Created At</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            </div>
        `;
    }
}
