class Router {
    constructor() {
        this.currentPage = 'dashboard';
        this.init();
    }

    init() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.dataset.page;
                if (page) {
                    this.navigate(page);
                }
            });
        });
    }

    navigate(page) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.page === page) {
                item.classList.add('active');
            }
        });

        document.querySelectorAll('.content-page').forEach(p => {
            p.classList.remove('active');
        });

        const targetPage = document.getElementById(`${page}-page`);
        if (targetPage) {
            targetPage.classList.add('active');
            this.currentPage = page;
            
            window.dispatchEvent(new CustomEvent('pagechange', { detail: { page } }));
        }
    }

    getCurrentPage() {
        return this.currentPage;
    }
}

const router = new Router();
