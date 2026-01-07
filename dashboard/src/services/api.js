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
    runTask: (task) => client.post('/agent/run', { task }),
};

export default client;
