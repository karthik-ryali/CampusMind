class AuthService {
    constructor() {
        this.currentUser = null;
        this.usersCache = null;
    }

    loadUser() {
        const userStr = localStorage.getItem('campusmind_user');
        if (userStr) {
            this.currentUser = JSON.parse(userStr);
            return this.currentUser;
        }
        return null;
    }

    saveUser(user) {
        this.currentUser = user;
        localStorage.setItem('campusmind_user', JSON.stringify(user));
    }

    clearUser() {
        this.currentUser = null;
        this.usersCache = null;
        localStorage.removeItem('campusmind_user');
    }

    isAuthenticated() {
        return this.currentUser !== null;
    }

    getUser() {
        return this.currentUser;
    }

    async loadUsersCache() {
        try {
            this.usersCache = await api.getUsers();
            return this.usersCache;
        } catch (error) {
            console.error('Failed to load users cache:', error);
            return [];
        }
    }

    getUserById(id) {
        if (!this.usersCache) return null;
        return this.usersCache.find(u => u.id === id) || null;
    }

    async getDepartmentName(id) {
        if (!id) return '-';
        try {
            const dept = await api.getDepartment(id);
            return dept.name || `ID:${id}`;
        } catch (error) {
            return `ID:${id}`;
        }
    }

    async getSectionName(id) {
        if (!id) return '-';
        try {
            const section = await api.getSection(id);
            return section.name || `ID:${id}`;
        } catch (error) {
            return `ID:${id}`;
        }
    }
}

const auth = new AuthService();
