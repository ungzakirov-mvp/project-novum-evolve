/**
 * API клиент для новых функций
 */
const featuresAPI = {
    // Time Tracking
    getTimerStatus: async () => {
        const response = await fetch('/api/v1/features/time-entries/timer-status', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        return response.json();
    },
    
    startTimer: async (ticketId, description = '') => {
        const response = await fetch('/api/v1/features/time-entries/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({ ticket_id: ticketId, description })
        });
        return response.json();
    },
    
    stopTimer: async (entryId) => {
        const response = await fetch(`/api/v1/features/time-entries/${entryId}/stop`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        return response.json();
    },
    
    getTicketTimeSummary: async (ticketId) => {
        const response = await fetch(`/api/v1/features/time-entries/ticket/${ticketId}/summary`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        return response.json();
    },
    
    // Canned Responses
    getCannedResponses: async (search = '') => {
        const url = search ? `/api/v1/features/canned-responses?search=${search}` : '/api/v1/features/canned-responses';
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        return response.json();
    },
    
    createCannedResponse: async (data) => {
        const response = await fetch('/api/v1/features/canned-responses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify(data)
        });
        return response.json();
    },
    
    // Checklists
    getChecklist: async (ticketId) => {
        const response = await fetch(`/api/v1/features/tickets/${ticketId}/checklist`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        return response.json();
    },
    
    addChecklistItem: async (ticketId, title, description = '') => {
        const response = await fetch(`/api/v1/features/tickets/${ticketId}/checklist`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({ title, description })
        });
        return response.json();
    },
    
    toggleChecklistItem: async (itemId) => {
        const response = await fetch(`/api/v1/features/checklist/${itemId}/toggle`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        return response.json();
    },
    
    deleteChecklistItem: async (itemId) => {
        const response = await fetch(`/api/v1/features/checklist/${itemId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        return response.json();
    },
    
    // Ratings (CSAT)
    rateTicket: async (ticketId, rating, comment = '') => {
        const response = await fetch(`/api/v1/features/tickets/${ticketId}/rate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({ rating, comment })
        });
        return response.json();
    },
    
    // Internal Notes
    getInternalNotes: async (ticketId) => {
        const response = await fetch(`/api/v1/features/tickets/${ticketId}/internal-notes`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        return response.json();
    },
    
    createInternalNote: async (ticketId, content, isPinned = false) => {
        const response = await fetch(`/api/v1/features/tickets/${ticketId}/internal-notes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({ content, is_pinned: isPinned })
        });
        return response.json();
    },
    
    // Customer Assets
    getCompanyAssets: async (companyId, assetType = '') => {
        let url = `/api/v1/features/companies/${companyId}/assets`;
        if (assetType) url += `?asset_type=${assetType}`;
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        return response.json();
    },
    
    createAsset: async (data) => {
        const response = await fetch('/api/v1/features/assets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify(data)
        });
        return response.json();
    },
    
    // Reports
    getTimeReport: async (startDate, endDate, userId = null) => {
        let url = `/api/v1/features/reports/time-tracking?start_date=${startDate}&end_date=${endDate}`;
        if (userId) url += `&user_id=${userId}`;
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        return response.json();
    },
    
    getCSATReport: async (startDate = '', endDate = '') => {
        let url = '/api/v1/features/reports/csat';
        if (startDate) url += `?start_date=${startDate}`;
        if (endDate) url += `&end_date=${endDate}`;
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        return response.json();
    }
};

window.featuresAPI = featuresAPI;