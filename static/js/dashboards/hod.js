class HODDashboard {
    static async render(container) {
        const user = auth.getUser();
        if (!user) return;

        try {
            const issues = await api.getIssuesForUser(user.id, false);
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
                </div>

                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Active Complaints</h2>
                    </div>
                    ${ProctorDashboard.renderIssuesTable(activeIssues, 'active')}
                    ${activeIssues.length > 0 ? this.renderActions(activeIssues) : ''}
                </div>

                ${escalatedIssues.length > 0 ? `
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Escalated Complaints</h2>
                    </div>
                    ${ProctorDashboard.renderIssuesTable(escalatedIssues, 'escalated')}
                </div>
                ` : ''}

                ${resolvedIssues.length > 0 ? `
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Resolved Complaints</h2>
                    </div>
                    ${ProctorDashboard.renderIssuesTable(resolvedIssues, 'resolved')}
                </div>
                ` : ''}
            `;

            // Setup action handlers
            this.setupActionHandlers();
        } catch (error) {
            console.error('Error loading HOD dashboard:', error);
            container.innerHTML = '<div class="error-message show">Failed to load dashboard</div>';
        }
    }

    static renderActions(issues) {
        const issueIds = issues.map(i => i.id);
        
        return `
            <div class="form-card" style="margin-top: 24px;">
                <h3 style="margin-bottom: 16px;">Actions</h3>
                <div class="form-row">
                    <div class="form-group-full">
                        <label>Select Issue ID</label>
                        <select id="hod-issue-select" class="form-group-full">
                            ${issueIds.map(id => `<option value="${id}">Issue #${id}</option>`).join('')}
                        </select>
                    </div>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-success" onclick="HODDashboard.handleResolve()">
                        <i class="fas fa-check"></i> Resolve
                    </button>
                    <button class="btn btn-warning" onclick="HODDashboard.handleEscalate()">
                        <i class="fas fa-arrow-up"></i> Escalate
                    </button>
                    <button class="btn btn-info" onclick="HODDashboard.handleReclassify()">
                        <i class="fas fa-redo"></i> Re-classify
                    </button>
                </div>
            </div>
        `;
    }

    static setupActionHandlers() {
        // Handlers are set up via onclick in renderActions
    }

    static async handleResolve() {
        const user = auth.getUser();
        const select = document.getElementById('hod-issue-select');
        if (!select) return;

        const issueId = parseInt(select.value);
        try {
            await api.verifyIssue(issueId, user.id, true);
            showToast('Issue resolved successfully!', 'success');
            setTimeout(() => {
                HODDashboard.render(document.getElementById('dashboard-content'));
            }, 1000);
        } catch (error) {
            showToast('Failed to resolve issue', 'error');
        }
    }

    static async handleEscalate() {
        const user = auth.getUser();
        const select = document.getElementById('hod-issue-select');
        if (!select) return;

        const issueId = parseInt(select.value);
        try {
            await api.forwardIssue(issueId, user.id);
            showToast('Issue escalated successfully!', 'success');
            setTimeout(() => {
                HODDashboard.render(document.getElementById('dashboard-content'));
            }, 1000);
        } catch (error) {
            showToast('Failed to escalate issue', 'error');
        }
    }

    static async handleReclassify() {
        const select = document.getElementById('hod-issue-select');
        if (!select) return;

        const issueId = parseInt(select.value);
        try {
            await api.classifyIssue(issueId);
            showToast('Issue re-classified successfully!', 'success');
            setTimeout(() => {
                HODDashboard.render(document.getElementById('dashboard-content'));
            }, 1000);
        } catch (error) {
            showToast('Failed to re-classify issue', 'error');
        }
    }
}