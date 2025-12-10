class ProctorDashboard {
    static async render(container) {
        const user = auth.getUser();
        if (!user) return;

        try {
            const [issues, allUsers] = await Promise.all([
                api.getIssuesForUser(user.id, false),
                auth.loadUsersCache()
            ]);

            const students = (allUsers || []).filter(u => u.reports_to === user.id && u.role === 'student');
            const activeIssues = (issues || []).filter(i => i.status !== 'closed' && i.forwarded_by !== user.id);
            const escalatedIssues = (issues || []).filter(i => i.forwarded_by === user.id);
            const allResolved = await api.getIssuesForUser(user.id, true);
            const resolvedIssues = (allResolved || []).filter(i => i.status === 'closed');

            container.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card active">
                        <div class="stat-label">Active Complaints</div>
                        <div class="stat-value">${activeIssues.length}</div>
                    </div>
                    <div class="stat-card escalated">
                        <div class="stat-label">Escalated</div>
                        <div class="stat-value">${escalatedIssues.length}</div>
                    </div>
                    <div class="stat-card resolved">
                        <div class="stat-label">Resolved</div>
                        <div class="stat-value">${resolvedIssues.length}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Students</div>
                        <div class="stat-value">${students.length}</div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Active Complaints</h2>
                    </div>
                    ${this.renderIssuesTable(activeIssues, 'active')}
                    ${activeIssues.length > 0 ? this.renderActions(activeIssues, 'proctor') : ''}
                </div>

                ${escalatedIssues.length > 0 ? `
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Escalated Complaints</h2>
                    </div>
                    ${this.renderIssuesTable(escalatedIssues, 'escalated')}
                </div>
                ` : ''}

                ${resolvedIssues.length > 0 ? `
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Resolved Complaints</h2>
                    </div>
                    ${this.renderIssuesTable(resolvedIssues, 'resolved')}
                </div>
                ` : ''}
            `;

            // Setup action handlers
            this.setupActionHandlers('proctor');
        } catch (error) {
            console.error('Error loading proctor dashboard:', error);
            container.innerHTML = '<div class="error-message show">Failed to load dashboard</div>';
        }
    }

    static renderIssuesTable(issues, type) {
        if (!issues || issues.length === 0) {
            return '<div class="empty-state"><div class="empty-state-icon">✅</div><h3>No Complaints</h3><p>No ' + type + ' complaints found.</p></div>';
        }

        const rows = issues.map(issue => {
            const priority = issue.priority || 'N/A';
            const status = issue.status || 'open';
            const raisedBy = auth.getUserById(issue.student_id)?.name || 'Unknown';
            const assignedTo = issue.assigned_to ? (auth.getUserById(issue.assigned_to)?.name || 'Unassigned') : 'Unassigned';
            const forwardedTo = issue.assigned_to ? (auth.getUserById(issue.assigned_to)?.name || 'Unassigned') : 'Unassigned';
            const verifiedBy = issue.verified_by ? (auth.getUserById(issue.verified_by)?.name || '-') : '-';
            const verifiedAt = issue.verified_at ? new Date(issue.verified_at).toLocaleString() : '-';

            if (type === 'resolved') {
                return `
                    <tr>
                        <td>${issue.id}</td>
                        <td><strong>${issue.title}</strong></td>
                        <td>${issue.category || 'N/A'}</td>
                        <td><span class="badge badge-${priority.toLowerCase()}">${priority}</span></td>
                        <td><span class="badge badge-${status.toLowerCase()}">${status}</span></td>
                        <td>${raisedBy}</td>
                        <td>${verifiedBy}</td>
                        <td>${verifiedAt}</td>
                    </tr>
                `;
            } else if (type === 'escalated') {
                return `
                    <tr>
                        <td>${issue.id}</td>
                        <td><strong>${issue.title}</strong></td>
                        <td>${issue.category || 'N/A'}</td>
                        <td><span class="badge badge-${priority.toLowerCase()}">${priority}</span></td>
                        <td><span class="badge badge-${status.toLowerCase()}">${status}</span></td>
                        <td>${raisedBy}</td>
                        <td>${forwardedTo}</td>
                        <td>${new Date(issue.created_at).toLocaleString()}</td>
                    </tr>
                `;
            } else {
                return `
                    <tr>
                        <td>${issue.id}</td>
                        <td><strong>${issue.title}</strong></td>
                        <td>${issue.category || 'N/A'}</td>
                        <td><span class="badge badge-${priority.toLowerCase()}">${priority}</span></td>
                        <td><span class="badge badge-${status.toLowerCase()}">${status}</span></td>
                        <td>${raisedBy}</td>
                        <td>${assignedTo}</td>
                        <td>${new Date(issue.created_at).toLocaleString()}</td>
                    </tr>
                `;
            }
        }).join('');

        let headers;
        if (type === 'resolved') {
            headers = '<th>ID</th><th>Title</th><th>Category</th><th>Priority</th><th>Status</th><th>Raised By</th><th>Verified By</th><th>Verified At</th>';
        } else if (type === 'escalated') {
            headers = '<th>ID</th><th>Title</th><th>Category</th><th>Priority</th><th>Status</th><th>Raised By</th><th>Forwarded To</th><th>Created At</th>';
        } else {
            headers = '<th>ID</th><th>Title</th><th>Category</th><th>Priority</th><th>Status</th><th>Raised By</th><th>Assigned To</th><th>Created At</th>';
        }

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

    static renderActions(issues, prefix) {
        const issueIds = issues.map(i => i.id);
        
        return `
            <div class="form-card" style="margin-top: 24px;">
                <h3 style="margin-bottom: 16px;">Actions</h3>
                <div class="form-row">
                    <div class="form-group-full">
                        <label>Select Issue ID</label>
                        <select id="${prefix}-issue-select" class="form-group-full">
                            ${issueIds.map(id => `<option value="${id}">Issue #${id}</option>`).join('')}
                        </select>
                    </div>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-success" onclick="ProctorDashboard.handleResolve('${prefix}')">
                        <i class="fas fa-check"></i> Resolve
                    </button>
                    <button class="btn btn-warning" onclick="ProctorDashboard.handleEscalate('${prefix}')">
                        <i class="fas fa-arrow-up"></i> Escalate
                    </button>
                    <button class="btn btn-info" onclick="ProctorDashboard.handleReclassify('${prefix}')">
                        <i class="fas fa-redo"></i> Re-classify
                    </button>
                </div>
            </div>
        `;
    }

    static setupActionHandlers(prefix) {
        // Handlers are set up via onclick in renderActions
    }

    static async handleResolve(prefix) {
        const user = auth.getUser();
        const select = document.getElementById(`${prefix}-issue-select`);
        if (!select) return;

        const issueId = parseInt(select.value);
        try {
            await api.verifyIssue(issueId, user.id, true);
            showToast('Issue resolved successfully!', 'success');
            setTimeout(() => {
                ProctorDashboard.render(document.getElementById('dashboard-content'));
            }, 1000);
        } catch (error) {
            showToast('Failed to resolve issue', 'error');
        }
    }

    static async handleEscalate(prefix) {
        const user = auth.getUser();
        const select = document.getElementById(`${prefix}-issue-select`);
        if (!select) return;

        const issueId = parseInt(select.value);
        try {
            await api.forwardIssue(issueId, user.id);
            showToast('Issue escalated successfully!', 'success');
            setTimeout(() => {
                ProctorDashboard.render(document.getElementById('dashboard-content'));
            }, 1000);
        } catch (error) {
            showToast('Failed to escalate issue', 'error');
        }
    }

    static async handleReclassify(prefix) {
        const select = document.getElementById(`${prefix}-issue-select`);
        if (!select) return;

        const issueId = parseInt(select.value);
        try {
            await api.classifyIssue(issueId);
            showToast('Issue re-classified successfully!', 'success');
            setTimeout(() => {
                ProctorDashboard.render(document.getElementById('dashboard-content'));
            }, 1000);
        } catch (error) {
            showToast('Failed to re-classify issue', 'error');
        }
    }
}
