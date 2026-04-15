class NotificationCenter {
    constructor() {
        this.lastId = 0;
        this.pollInterval = 15000; // 15s
        this.init();
    }

    async init() {
        if (!api.token) return;

        // Initial Fetch (to set baseline)
        await this.checkNotifications(true);

        setInterval(() => this.checkNotifications(), this.pollInterval);
    }

    async checkNotifications(silent = false) {
        try {
            const notifs = await api.request('/notifications/?limit=5');
            if (notifs.length > 0) {
                // Determine new ones. For simplicity in MVP, we track max ID seen locally.
                // In production, backend should support ?since_id=...

                const newest = notifs[0];
                if (!silent && newest.id > this.lastId) {
                    // Show toasts for all new
                    const newOnes = notifs.filter(n => n.id > this.lastId);
                    newOnes.reverse().forEach(n => this.showToast(n));
                }

                this.lastId = newest.id;
            }
        } catch (e) {
            console.error("Notification Poll Error", e);
        }
    }

    showToast(notification) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerHTML = `
            <div style="font-weight:600; margin-bottom:0.25rem">${notification.title}</div>
            <div style="font-size:0.9rem; opacity:0.9">${notification.message}</div>
        `;

        document.body.appendChild(toast);

        // Auto remove
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    window.notifications = new NotificationCenter();
});
