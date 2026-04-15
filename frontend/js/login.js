// Login & Registration Logic

document.addEventListener('DOMContentLoaded', () => {
    console.log('Login Script Initialized');

    // Explicitly grab api from window to be 100% sure
    const api = window.api;
    if (!api) {
        console.error('API Client not found! Make sure api.js is loaded correctly.');
        alert('Критическая ошибка: API клиент не загружен. Пожалуйста, обновите страницу.');
        return;
    }

    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const showRegisterBtn = document.getElementById('showRegister');
    const showLoginBtn = document.getElementById('showLogin');

    console.log('API Token status:', api.token ? 'Present' : 'Not found');

    // Check if already logged in
    async function checkSession() {
        if (api.token) {
            try {
                const user = await api.getMe();
                redirectUser(user);
            } catch (e) {
                console.error('Session validation failed:', e);
                api.clearToken();
            }
        }
    }

    function redirectUser(user) {
        if (user.role === 'client') {
            window.location.href = 'client.html';
        } else if (user.role === 'manager') {
            window.location.href = 'manager.html';
        } else {
            window.location.href = 'agent.html';
        }
    }

    checkSession();

    // Toggle Forms
    if (showRegisterBtn) {
        showRegisterBtn.addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('loginPage').classList.add('hidden');
            document.getElementById('registerPage').classList.remove('hidden');
        });
    }

    if (showLoginBtn) {
        showLoginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('registerPage').classList.add('hidden');
            document.getElementById('loginPage').classList.remove('hidden');
        });
    }

    // Login Handle
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = loginForm.querySelector('button');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
            btn.disabled = true;

            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;

            try {
                await api.login(email, password);
                const user = await api.getMe();
                redirectUser(user);
            } catch (error) {
                alert('Ошибка входа: ' + error.message);
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        });
    }

    // Register Handle
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = registerForm.querySelector('button');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
            btn.disabled = true;

            const name = document.getElementById('regName').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;

            try {
                await api.register(email, password, name);
                const user = await api.getMe();
                redirectUser(user);
            } catch (error) {
                alert('Ошибка регистрации: ' + error.message);
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        });
    }
});
