class APIService {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
    }

    async request(url, options = {}) {
        const headers = {};
        if (options.body) {
            headers['Content-Type'] = 'application/json';
        }
        
        const config = {
            ...options,
            headers: {
                ...headers,
                ...options.headers
            }
        };

        try {
            console.log('API Request:', `${this.baseURL}${url}`, config);
            const response = await fetch(`${this.baseURL}${url}`, config);
            
            if (!response.ok) {
                let errorMessage = `HTTP error! status: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch {
                    const errorText = await response.text();
                    if (errorText) {
                        try {
                            const errorData = JSON.parse(errorText);
                            errorMessage = errorData.detail || errorMessage;
                        } catch {
                            errorMessage = errorText || errorMessage;
                        }
                    }
                }
                throw new Error(errorMessage);
            }
            
            const data = await response.json();
            console.log('API Response:', data);
            return data;
        } catch (error) {
            console.error('API Error:', error);
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Failed to fetch - Backend server is not running or CORS error');
            }
            throw error;
        }
    }

    async get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        return this.request(fullUrl, { method: 'GET' });
    }

    async post(url, data = {}, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        // For login, we don't send body, only query params
        const body = Object.keys(data).length > 0 ? JSON.stringify(data) : undefined;
        const options = {
            method: 'POST'
        };
        if (body) {
            options.body = body;
        }
        return this.request(fullUrl, options);
    }

    async login(email, password) {
        return this.post(API_CONFIG.ENDPOINTS.LOGIN, {}, { email, password });
    }

    async getUsers() {
        return this.get(API_CONFIG.ENDPOINTS.USERS);
    }

    async getUser(id) {
        return this.get(API_CONFIG.ENDPOINTS.USER.replace('{id}', id));
    }

    async getIssues(params = {}) {
        return this.get(API_CONFIG.ENDPOINTS.ISSUES, params);
    }

    async getIssue(id) {
        return this.get(API_CONFIG.ENDPOINTS.ISSUE.replace('{id}', id));
    }

    async getIssuesForUser(userId, showResolved = false) {
        return this.get(
            API_CONFIG.ENDPOINTS.ISSUES_FOR_USER.replace('{id}', userId),
            { show_resolved: showResolved }
        );
    }

    async createIssue(data) {
        return this.post(API_CONFIG.ENDPOINTS.CREATE_ISSUE, data);
    }

    async forwardIssue(issueId, byUserId) {
        return this.post(
            API_CONFIG.ENDPOINTS.FORWARD_ISSUE.replace('{id}', issueId),
            {},
            { by_user_id: byUserId }
        );
    }

    async verifyIssue(issueId, verifierId, resolved = true) {
        return this.post(
            API_CONFIG.ENDPOINTS.VERIFY_ISSUE.replace('{id}', issueId),
            {},
            { verifier_id: verifierId, resolved: resolved }
        );
    }

    async classifyIssue(issueId) {
        return this.post(API_CONFIG.ENDPOINTS.CLASSIFY_ISSUE.replace('{id}', issueId));
    }

    async getAdminStats() {
        return this.get(API_CONFIG.ENDPOINTS.ADMIN_STATS);
    }

    async getAdminIssues(params = {}) {
        return this.get(API_CONFIG.ENDPOINTS.ADMIN_ISSUES, params);
    }

    async getDepartment(id) {
        return this.get(API_CONFIG.ENDPOINTS.DEPARTMENT.replace('{id}', id));
    }

    async getSection(id) {
        return this.get(API_CONFIG.ENDPOINTS.SECTION.replace('{id}', id));
    }
}

const api = new APIService();