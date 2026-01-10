import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const client = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Attendance Services
export const attendanceService = {
    getSessions: (params) => client.get('/attendance/', { params }),
    filterSessions: (params) => client.get('/attendance/filter', { params }),
    getStats: () => client.get('/attendance/stats'),
};

// Alert Services
export const alertService = {
    getDeviceAlerts: (params) => client.get('/alerts/device', { params }),
    getIdentityAlerts: (params) => client.get('/alerts/identity', { params }),
    getTimestampAlerts: (params) => client.get('/alerts/timestamp', { params }),
};

// Group Services
export const groupService = {
    getGroups: (params) => client.get('/groups/', { params }),
};

// Agent Services
export const agentService = {
    runTask: (task, conversationId = null) => client.post('/agent/run', { task, conversation_id: conversationId }),
};

// Chat Services
export const chatService = {
    createConversation: (title = null) => client.post('/chat/', title ? { title } : {}),
    listConversations: (page = 1, limit = 20) => client.get('/chat/', { params: { page, limit } }),
    getConversation: (id) => client.get(`/chat/${id}`),
    addMessage: (id, role, content, status = null) => client.post(`/chat/${id}/message`, { role, content, status }),
    updateConversationTitle: (id, title) => client.patch(`/chat/${id}/title`, { title }),
    deleteConversation: (id) => client.delete(`/chat/${id}`),
    getStats: () => client.get('/chat/stats'),
};

// Analytics Services
export const analyticsService = {
    getGroupAnalytics: (params) => client.get('/analytics/groups', { params }),
    getAttendanceTrend: (params) => client.get('/analytics/attendance-trend', { params }),
};

export default client;

