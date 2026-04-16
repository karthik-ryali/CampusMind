const API_CONFIG = {
    BASE_URL: 'https://campusmind-sife.onrender.com',
    ENDPOINTS: {
        LOGIN: '/auth/login',
        USERS: '/users',
        USER: '/users/{id}',
        ISSUES: '/issues',
        ISSUE: '/issues/{id}',
        ISSUES_FOR_USER: '/issues/for_user/{id}',
        CREATE_ISSUE: '/issues',
        FORWARD_ISSUE: '/issues/{id}/forward',
        VERIFY_ISSUE: '/issues/{id}/verify',
        CLASSIFY_ISSUE: '/issues/{id}/classify',
        ADMIN_STATS: '/admin/stats',
        ADMIN_ISSUES: '/admin/issues',
        DEPARTMENT: '/departments/{id}',
        SECTION: '/sections/{id}'
    },
    TIMEOUT: 10000,
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000
};

(function () {
    const metaTag = document.querySelector('meta[name="api-url"]');
    if (metaTag && metaTag.content) {
        API_CONFIG.BASE_URL = metaTag.content.replace(/\/$/, '');
    } else if (window.API_URL) {
        API_CONFIG.BASE_URL = window.API_URL.replace(/\/$/, '');
    }
})();