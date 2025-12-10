class VCDashboard {
    static async render(container) {
        const user = auth.getUser();
        if (!user) return;

        try {
            const issues = await api.getIssuesForUser(user.id, false);
            const allResolved = await api.getIssuesForUser(user.id, true);
            const resolvedIssues = (allResolved || []).filter(i => i.status === 'closed');

            container.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card active">
                        <div class="stat-label">Escalated Complaints</div>
                        <div class="stat-value">${(issues || []).length}</div>
                    </div>
                    <div class="stat-card resolved">
                        <div class="stat-label">Resolved</div>
                        <div class="stat-value">${resolvedIssues.length}</div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Escalated Complaints</h2>
                    </div>
                    ${this.renderIssuesTable(issues)}
                    ${issues && issues.length > 0 ? this.renderActions(issues) : ''}
                </div>

                ${resolvedIssues.length > 0 ? `
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Resolved Complaints</h2>
                    </div>
                    ${this.renderResolvedTable(resolvedIssues)}
                </div>
                ` : ''}
            `;

            // Setup action handler
            const resolveBtn = document.getElementById('vc-resolve-btn');
            if (resolveBtn) {
                resolveBtn.addEventListener('click', () => this.handleResolve());
            }
        } catch (error) {
            console.error('Error loading VC dashboard:', error);
            container.innerHTML = '<div class="error-message show">Failed to load dashboard</div>';
        }
    }

    static renderIssuesTable(issues) {
        if (!issues || issues.length === 0) {
            return '<div class="empty-state"><div class="empty-state-icon">✅</div><h3>No Escalated Complaints</h3><p>No complaints have been escalated to your level.</p></div>';
        }

        const rows = issues.map(issue => {
            const priority = issue.priority || 'N/A';
            const raisedBy = auth.getUserById(issue.student_id)?.name || 'Unknown';
            
            return `
                <tr>
                    <td>${issue.id}</td>
                    <td><strong>${issue.title}</strong></td>
                    <td>${issue.category || 'N/A'}</td>
                    <td><span class="badge badge-${priority.toLowerCase()}">${priority}</span></td>
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
                            <th>Category</th>
                            <th>Priority</th>
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

    static renderResolvedTable(issues) {
        const rows = issues.map(issue => {
            const priority = issue.priority || 'N/A';
            const raisedBy = auth.getUserById(issue.student_id)?.name || 'Unknown';
            const verifiedBy = issue.verified_by ? (auth.getUserById(issue.verified_by)?.name || '-') : '-';
            const verifiedAt = issue.verified_at ? new Date(issue.verified_at).toLocaleString() : '-';

            return `
                <tr>
                    <td>${issue.id}</td>
                    <td><strong>${issue.title}</strong></td>
                    <td>${raisedBy}</td>
                    <td>${verifiedBy}</td>
                    <td>${verifiedAt}</td>
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
                            <th>Raised By</th>
                            <th>Verified By</th>
                            <th>Verified At</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            </div>
        `;
    }

    static renderActions(issues) {
        const issueIds = issues.map(i => i.id);
        
        return `
            <div class="form-card" style="margin-top: 24px;">
                <h3 style="margin-bottom: 16px;">Actions</h3>
                <div class="form-row">
                    <div class="form-group-full">
                        <label>Select Issue ID</label>
                        <select id="vc-issue-select" class="form-group-full">
                            ${issueIds.map(id => `<option value="${id}">Issue #${id}</option>`).join('')}
                        </select>
                    </div>
                </div>
                <div class="action-buttons">
                    <button id="vc-resolve-btn" class="btn btn-success">
                        <i class="fas fa-check"></i> Resolve (Close)
                    </button>
                </div>
            </div>
        `;
    }

    static async handleResolve() {
        const user = auth.getUser();
        const select = document.getElementById('vc-issue-select');
        if (!select) return;

        const issueId = parseInt(select.value);
        try {
            await api.verifyIssue(issueId, user.id, true);
            showToast('Issue resolved successfully!', 'success');
            setTimeout(() => {
                VCDashboard.render(document.getElementById('dashboard-content'));
            }, 1000);
        } catch (error) {
            showToast('Failed to resolve issue', 'error');
        }
    }
}
