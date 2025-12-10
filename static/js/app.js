class App {
    constructor() {
        this.init();
    }

    async init() {
        this.showLogin();
        
        const user = auth.loadUser();
        
        if (user && user.id) {
            try {
                await auth.loadUsersCache();
                this.showDashboard();
                this.updateUI();
                this.loadDashboard();
            } catch (error) {
                console.error('Session verification failed:', error);
                auth.clearUser();
                this.showLogin();
            }
        }

        this.setupEventListeners();
    }

    setupEventListeners() {
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleLogin();
            });
        }

        const togglePassword = document.getElementById('toggle-password');
        if (togglePassword) {
            togglePassword.addEventListener('click', () => {
                const passwordInput = document.getElementById('password');
                const passwordIcon = document.getElementById('password-icon');
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    passwordIcon.classList.remove('fa-eye');
                    passwordIcon.classList.add('fa-eye-slash');
                } else {
                    passwordInput.type = 'password';
                    passwordIcon.classList.remove('fa-eye-slash');
                    passwordIcon.classList.add('fa-eye');
                }
            });
        }

        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                this.handleLogout();
            });
        }

        window.addEventListener('pagechange', (e) => {
            this.loadDashboard();
        });

        setInterval(() => {
            const user = auth.getUser();
            if (user) {
                const lastActivity = localStorage.getItem('last_activity');
                if (lastActivity) {
                    const timeDiff = Date.now() - parseInt(lastActivity);
                    const thirtyMinutes = 30 * 60 * 1000;
                    if (timeDiff > thirtyMinutes) {
                        this.handleLogout();
                        showToast('Session expired. Please login again.', 'warning');
                    }
                }
            }
        }, 60000); 

        ['mousedown', 'keydown', 'scroll', 'touchstart'].forEach(event => {
            document.addEventListener(event, () => {
                if (auth.isAuthenticated()) {
                    localStorage.setItem('last_activity', Date.now().toString());
                }
            });
        });
    }

    async handleLogin() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('login-error');
        const submitBtn = document.querySelector('#login-form button[type="submit"]');

        try {
            errorDiv.classList.remove('show');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span>Logging in...</span><i class="fas fa-spinner fa-spin"></i>';
            
            const user = await api.login(email, password);
            
            if (user && user.id) {
                auth.saveUser(user);
                await auth.loadUsersCache();
                this.showDashboard();
                this.updateUI();
                this.loadDashboard();
                showToast('Login successful!', 'success');
            } else {
                throw new Error('Invalid credentials');
            }
        } catch (error) {
            console.error('Login error:', error);
            let errorMsg = 'Invalid credentials or backend unreachable.';
            if (error.message) {
                errorMsg = error.message;
            }
            if (error.message && error.message.includes('Failed to fetch')) {
                errorMsg = 'Cannot connect to backend. Make sure the server is running on http://127.0.0.1:8000';
            }
            errorDiv.textContent = errorMsg + ' Please check your credentials and ensure the backend is running.';
            errorDiv.classList.add('show');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span>Login</span><i class="fas fa-arrow-right"></i>';
        }
    }

    handleLogout() {
        auth.clearUser();
        this.showLogin();
        document.getElementById('login-form').reset();
    }

    showLogin() {
        const loginPage = document.getElementById('login-page');
        const dashboardContainer = document.getElementById('dashboard-container');
        
        if (loginPage) {
            loginPage.classList.add('active');
            loginPage.style.display = 'block';
        }
        if (dashboardContainer) {
            dashboardContainer.classList.remove('active');
            dashboardContainer.style.display = 'none';
        }
    }

    showDashboard() {
        const loginPage = document.getElementById('login-page');
        const dashboardContainer = document.getElementById('dashboard-container');
        
        if (loginPage) {
            loginPage.classList.remove('active');
            loginPage.style.display = 'none';
        }
        if (dashboardContainer) {
            dashboardContainer.classList.add('active');
            dashboardContainer.style.display = 'flex';
        }
    }

    updateUI() {
        const user = auth.getUser();
        if (!user) return;

        document.getElementById('sidebar-user-name').textContent = user.name;
        document.getElementById('sidebar-user-role').textContent = user.role.toUpperCase();

        const adminNav = document.getElementById('nav-admin');
        if (user.role === 'admin') {
            adminNav.style.display = 'block';
        } else {
            adminNav.style.display = 'none';
        }

        const roleTitles = {
            'student': 'Student Dashboard',
            'proctor': 'Proctor Dashboard',
            'hod': 'HOD Dashboard',
            'vc': 'VC Dashboard',
            'admin': 'Admin Dashboard'
        };

        document.getElementById('dashboard-title').textContent = roleTitles[user.role] || 'Dashboard';
    }

    async loadDashboard() {
        const user = auth.getUser();
        if (!user) return;

        const page = router.getCurrentPage();
        const role = user.role.toLowerCase();

        switch (page) {
            case 'dashboard':
                await this.loadRoleDashboard(role);
                break;
            case 'issues':
                await this.loadIssuesPage(role);
                break;
            case 'profile':
                await this.loadProfilePage();
                break;
            case 'admin':
                if (role === 'admin') {
                    await this.loadAdminDashboard();
                }
                break;
        }
    }

    async loadRoleDashboard(role) {
        const content = document.getElementById('dashboard-content');
        content.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

        try {
            switch (role) {
                case 'student':
                    await StudentDashboard.render(content);
                    break;
                case 'proctor':
                    await ProctorDashboard.render(content);
                    break;
                case 'hod':
                    await HODDashboard.render(content);
                    break;
                case 'vc':
                    await VCDashboard.render(content);
                    break;
                case 'admin':
                    await AdminDashboard.render(content);
                    break;
            }
        } catch (error) {
            console.error('Error loading dashboard:', error);
            content.innerHTML = '<div class="error-message show">Failed to load dashboard</div>';
        }
    }

    async loadIssuesPage(role) {
        const content = document.getElementById('issues-content');
        content.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

        try {
            const user = auth.getUser();
            const issues = await api.getIssuesForUser(user.id, true);
            
            content.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">All Issues</h2>
                    </div>
                    ${this.renderIssuesTable(issues)}
                </div>
            `;
        } catch (error) {
            console.error('Error loading issues:', error);
            content.innerHTML = '<div class="error-message show">Failed to load issues</div>';
        }
    }

    async loadProfilePage() {
        const content = document.getElementById('profile-content');
        const user = auth.getUser();
        
        const deptName = await auth.getDepartmentName(user.department_id);
        const sectName = await auth.getSectionName(user.section_id);

        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Profile Information</h2>
                </div>
                <div class="form-row">
                    <div class="form-group-full">
                        <label>Name</label>
                        <input type="text" value="${user.name}" readonly>
                    </div>
                    <div class="form-group-full">
                        <label>Email</label>
                        <input type="email" value="${user.email}" readonly>
                    </div>
                    <div class="form-group-full">
                        <label>Role</label>
                        <input type="text" value="${user.role.toUpperCase()}" readonly>
                    </div>
                    <div class="form-group-full">
                        <label>Department</label>
                        <input type="text" value="${deptName}" readonly>
                    </div>
                    <div class="form-group-full">
                        <label>Section</label>
                        <input type="text" value="${sectName}" readonly>
                    </div>
                </div>
            </div>
        `;
    }

    async loadAdminDashboard() {
        await AdminDashboard.render(document.getElementById('admin-content'));
    }

    renderIssuesTable(issues) {
        if (!issues || issues.length === 0) {
            return '<div class="empty-state"><div class="empty-state-icon">📋</div><h3>No Issues</h3><p>No issues found.</p></div>';
        }

        const rows = issues.map(issue => {
            const priority = issue.priority || 'N/A';
            const status = issue.status || 'open';
            return `
                <tr>
                    <td>${issue.id}</td>
                    <td>${issue.title}</td>
                    <td>${issue.category || 'N/A'}</td>
                    <td><span class="badge badge-${priority.toLowerCase()}">${priority}</span></td>
                    <td><span class="badge badge-${status.toLowerCase()}">${status}</span></td>
                    <td>${new Date(issue.created_at).toLocaleDateString()}</td>
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
                            <th>Status</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            </div>
        `;
    }

    showToast(message, type = 'info') {
        const container = document.querySelector('.toast-container') || this.createToastContainer();
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: '✓',
            error: '✕',
            info: 'ℹ',
            warning: '⚠'
        };

        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || icons.info}</div>
            <div class="toast-message">${message}</div>
            <button class="toast-close">&times;</button>
        `;

        container.appendChild(toast);

        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.remove();
        });

        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
    window.showToast = (message, type) => window.app.showToast(message, type);
});