/**
 * Features for Client Portal
 * CSAT ratings, asset viewing
 */

let currentRatingTicketId = null;
let selectedRating = 0;

// ============================================
// CSAT RATING
// ============================================
// Setup rating stars
document.addEventListener('DOMContentLoaded', () => {
    // Setup CSAT modal stars
    const csatStars = document.querySelectorAll('#csatStars .rating-star');
    csatStars.forEach(star => {
        star.addEventListener('click', () => {
            const rating = parseInt(star.dataset.rating);
            selectCsatRating(rating);
        });
        
        star.addEventListener('mouseenter', () => {
            const rating = parseInt(star.dataset.rating);
            highlightCsatStars(rating);
        });
    });
    
    document.getElementById('csatStars')?.addEventListener('mouseleave', () => {
        highlightCsatStars(selectedRating);
    });
    
    // Setup inline rating stars
    const clientStars = document.querySelectorAll('#clientRatingStars .rating-star');
    clientStars.forEach(star => {
        star.addEventListener('click', () => {
            const rating = parseInt(star.dataset.rating);
            selectClientRating(rating);
        });
        
        star.addEventListener('mouseenter', () => {
            const rating = parseInt(star.dataset.rating);
            highlightClientStars(rating);
        });
    });
    
    document.getElementById('clientRatingStars')?.addEventListener('mouseleave', () => {
        const currentRating = document.getElementById('clientRatingStars').dataset.rating || 0;
        highlightClientStars(parseInt(currentRating));
    });
});

function selectCsatRating(rating) {
    selectedRating = rating;
    highlightCsatStars(rating);
}

function highlightCsatStars(rating) {
    const stars = document.querySelectorAll('#csatStars .rating-star');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

function selectClientRating(rating) {
    document.getElementById('clientRatingStars').dataset.rating = rating;
    highlightClientStars(rating);
}

function highlightClientStars(rating) {
    const stars = document.querySelectorAll('#clientRatingStars .rating-star');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

async function submitCsatRating() {
    if (selectedRating === 0) {
        showClientToast('Пожалуйста, выберите оценку', 'warning');
        return;
    }
    
    try {
        const comment = document.getElementById('csatComment').value;
        await featuresAPI.rateTicket(currentRatingTicketId, selectedRating, comment);
        
        hideCsatModal();
        showClientToast('Спасибо за ваш отзыв!', 'success');
        
        // Refresh ticket list
        if (window.loadClientTickets) {
            window.loadClientTickets();
        }
    } catch (e) {
        showClientToast('Ошибка отправки оценки', 'error');
    }
}

function skipCsatRating() {
    hideCsatModal();
}

function showCsatModal(ticketId) {
    currentRatingTicketId = ticketId;
    selectedRating = 0;
    highlightCsatStars(0);
    document.getElementById('csatComment').value = '';
    document.getElementById('csatModal').classList.remove('hidden');
}

function hideCsatModal() {
    document.getElementById('csatModal').classList.add('hidden');
}

async function submitClientRating() {
    const rating = parseInt(document.getElementById('clientRatingStars').dataset.rating || 0);
    if (rating === 0) {
        showClientToast('Пожалуйста, выберите оценку', 'warning');
        return;
    }
    
    try {
        const comment = document.getElementById('clientRatingComment').value;
        await featuresAPI.rateTicket(currentRatingTicketId, rating, comment);
        
        document.getElementById('ratingSection').classList.add('hidden');
        showClientToast('Спасибо за ваш отзыв!', 'success');
        
        // Refresh ticket list
        if (window.loadClientTickets) {
            window.loadClientTickets();
        }
    } catch (e) {
        showClientToast('Ошибка отправки оценки', 'error');
    }
}

// Check if ticket needs rating
async function checkTicketRating(ticketId, status) {
    // Show rating for closed/resolved tickets
    const closedStatuses = ['закрыт', 'closed', 'решён', 'resolved'];
    
    if (closedStatuses.includes(status.toLowerCase())) {
        try {
            // Check if already rated
            const ratings = await featuresAPI.getMyRatings();
            const alreadyRated = ratings.some(r => r.ticket_id === ticketId);
            
            if (!alreadyRated) {
                currentRatingTicketId = ticketId;
                
                // Show inline rating section in detail view
                const ratingSection = document.getElementById('ratingSection');
                if (ratingSection) {
                    ratingSection.classList.remove('hidden');
                    // Reset stars
                    document.getElementById('clientRatingStars').dataset.rating = 0;
                    highlightClientStars(0);
                    document.getElementById('clientRatingComment').value = '';
                } else {
                    // Show modal if detail view doesn't have inline rating
                    showCsatModal(ticketId);
                }
            }
        } catch (e) {
            console.error('Error checking rating:', e);
        }
    }
}

// ============================================
// ASSETS VIEWING
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Navigation to assets view
    document.querySelector('[data-view="assets"]')?.addEventListener('click', () => {
        loadClientAssets();
    });
});

async function loadClientAssets() {
    const container = document.getElementById('clientAssetsList');
    if (!container) return;
    
    try {
        // Get current user's company
        const user = await api.getCurrentUser();
        if (!user || !user.company_id) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                    <i class="fas fa-desktop fa-3x" style="margin-bottom: 1rem; opacity: 0.5;"></i>
                    <p>Вы не привязаны к организации</p>
                </div>
            `;
            return;
        }
        
        const assets = await featuresAPI.getCompanyAssets(user.company_id);
        
        if (assets.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                    <i class="fas fa-box-open fa-3x" style="margin-bottom: 1rem; opacity: 0.5;"></i>
                    <p>У вас пока нет зарегистрированного оборудования</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = `
            <div class="assets-grid">
                ${assets.map(asset => renderAssetCard(asset)).join('')}
            </div>
        `;
    } catch (e) {
        console.error('Error loading assets:', e);
        container.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                <i class="fas fa-exclamation-circle fa-2x" style="margin-bottom: 1rem;"></i>
                <p>Ошибка загрузки оборудования</p>
            </div>
        `;
    }
}

function renderAssetCard(asset) {
    const statusColors = {
        'active': 'var(--jarvis-emerald)',
        'repair': '#fbbf24',
        'retired': 'var(--text-tertiary)'
    };
    
    const statusLabels = {
        'active': 'Активно',
        'repair': 'В ремонте',
        'retired': 'Списано'
    };
    
    const icons = {
        'computer': 'desktop',
        'server': 'server',
        'printer': 'print',
        'network': 'network-wired'
    };
    
    const warrantyStatus = getWarrantyStatus(asset.warranty_end);
    
    return `
        <div class="glass-card" style="padding: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <div style="width: 50px; height: 50px; border-radius: 12px; background: rgba(0,212,255,0.1); border: 1px solid rgba(0,212,255,0.2); display: flex; align-items: center; justify-content: center;">
                    <i class="fas fa-${icons[asset.asset_type] || 'box'}" style="font-size: 1.25rem; color: var(--jarvis-cyan);"></i>
                </div>
                <div style="flex: 1;">
                    <h3 style="margin: 0; font-size: 1.1rem;">${asset.name}</h3>
                    <p style="margin: 0; font-size: 0.85rem; color: var(--text-tertiary);">${asset.model || 'Модель не указана'}</p>
                </div>
                <span style="padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; background: ${statusColors[asset.status]}22; color: ${statusColors[asset.status]};">
                    ${statusLabels[asset.status] || asset.status}
                </span>
            </div>
            
            ${asset.specifications ? `
                <div style="margin-bottom: 1rem; padding: 0.75rem; background: rgba(255,255,255,0.03); border-radius: 8px;">
                    <div style="font-size: 0.75rem; color: var(--text-tertiary); margin-bottom: 0.5rem;">ХАРАКТЕРИСТИКИ</div>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem;">
                        ${Object.entries(asset.specifications).map(([key, value]) => `
                            <div style="font-size: 0.85rem;">
                                <span style="color: var(--text-tertiary);">${key}:</span>
                                <span style="color: var(--text-primary); margin-left: 0.5rem;">${value}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            <div style="display: flex; gap: 1rem; font-size: 0.85rem;">
                <div style="flex: 1;">
                    <span style="color: var(--text-tertiary);">S/N:</span>
                    <span style="color: var(--text-primary); margin-left: 0.5rem; font-family: monospace;">${asset.serial_number || '—'}</span>
                </div>
                <div style="flex: 1;">
                    <span style="color: var(--text-tertiary);">Гарантия:</span>
                    <span class="warranty-status ${warrantyStatus.class}">
                        ${warrantyStatus.text}
                    </span>
                </div>
            </div>
            
            ${asset.remote_access_id ? `
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05);">
                    <div style="font-size: 0.75rem; color: var(--text-tertiary); margin-bottom: 0.5rem;">УДАЛЕННЫЙ ДОСТУП</div>
                    <div style="display: flex; gap: 0.5rem;">
                        <span class="remote-access-badge" onclick="copyClientClipboard('${asset.remote_access_id}')">
                            <i class="fas fa-desktop"></i> ${asset.remote_access_id}
                        </span>
                        ${asset.remote_access_password ? `
                            <span class="remote-access-badge" onclick="copyClientClipboard('${asset.remote_access_password}')">
                                <i class="fas fa-key"></i> Пароль
                            </span>
                        ` : ''}
                    </div>
                </div>
            ` : ''}
            
            ${asset.location ? `
                <div style="margin-top: 0.75rem; font-size: 0.85rem; color: var(--text-tertiary);">
                    <i class="fas fa-map-marker-alt" style="margin-right: 0.5rem;"></i>
                    ${asset.location}
                </div>
            ` : ''}
        </div>
    `;
}

function getWarrantyStatus(warrantyEnd) {
    if (!warrantyEnd) {
        return { class: 'normal', text: 'Нет данных' };
    }
    
    const end = new Date(warrantyEnd);
    const now = new Date();
    const diffDays = Math.floor((end - now) / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
        return { class: 'expired', text: 'Истекла' };
    } else if (diffDays < 30) {
        return { class: 'expiring', text: `Истекает через ${diffDays} дн.` };
    } else {
        return { class: 'valid', text: `До ${end.toLocaleDateString()}` };
    }
}

function copyClientClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showClientToast('Скопировано: ' + text, 'success');
    });
}

// ============================================
// HELPER FUNCTIONS
// ============================================
function showClientToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        left: 50%;
        transform: translateX(-50%);
        padding: 1rem 2rem;
        background: ${type === 'success' ? 'rgba(16,185,129,0.9)' : type === 'error' ? 'rgba(244,63,94,0.9)' : 'rgba(59,130,246,0.9)'};
        color: white;
        border-radius: 8px;
        z-index: 9999;
        animation: slideUp 0.3s ease;
        font-weight: 500;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Override viewTicket to check for rating
const originalClientViewTicket = window.viewTicket;
window.viewTicket = async function(ticketId) {
    // Call original function
    if (originalClientViewTicket) {
        await originalClientViewTicket(ticketId);
    }
    
    // Get ticket status and check rating
    try {
        const tickets = await api.getMyTickets();
        const ticket = tickets.find(t => t.id === ticketId);
        if (ticket) {
            await checkTicketRating(ticketId, ticket.status);
        }
    } catch (e) {
        console.error('Error in viewTicket override:', e);
    }
};

// Global functions for buttons
window.showCSATModal = function() {
    selectedRating = 0;
    highlightCsatStars(0);
    document.getElementById('csatComment').value = '';
    document.getElementById('csatModal').classList.remove('hidden');
};

window.submitCsatRating = submitCsatRating;
window.skipCsatRating = skipCsatRating;
window.submitClientRating = submitClientRating;
window.copyClientClipboard = copyClientClipboard;

// Navigation function for client portal
window.showView = function(viewName) {
    // Hide all views
    document.querySelectorAll('.view-container').forEach(view => {
        view.classList.add('hidden');
    });
    
    // Show selected view
    const selectedView = document.getElementById(viewName + 'View');
    if (selectedView) {
        selectedView.classList.remove('hidden');
    }
    
    // Update nav items
    document.querySelectorAll('.client-nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.view === viewName) {
            item.classList.add('active');
        }
    });
    
    // Load data if needed
    if (viewName === 'assets') {
        loadClientAssets();
    }
};

// Force show features panel on page load
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        // Make sure navigation items are visible
        const assetsNav = document.querySelector('[data-view="assets"]');
        if (assetsNav) {
            assetsNav.style.cssText += '; display: flex !important; visibility: visible !important; opacity: 1 !important;';
        }
    }, 500);
});