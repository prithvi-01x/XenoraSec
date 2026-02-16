import axios from 'axios';
import type {
    ScanCreateRequest,
    ScanCreateResponse,
    ScanResult,
    ScanHistoryResponse,
    QueueInfo,
    HealthStatus,
    DashboardStats,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
    (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            console.error(`[API Error] ${error.response.status}:`, error.response.data);
        } else if (error.request) {
            console.error('[API Error] No response received:', error.request);
        } else {
            console.error('[API Error]:', error.message);
        }
        return Promise.reject(error);
    }
);

export const scanApi = {
    // Start a new scan
    startScan: async (data: ScanCreateRequest): Promise<ScanCreateResponse> => {
        const response = await apiClient.post<ScanCreateResponse>('/api/scan/', data);
        return response.data;
    },

    // Get scan results
    getScanResults: async (scanId: string): Promise<ScanResult> => {
        const response = await apiClient.get<ScanResult>(`/api/scan/results/${scanId}`);
        return response.data;
    },

    // Get scan history
    getScanHistory: async (params?: {
        limit?: number;
        offset?: number;
        status?: string;
        target?: string;
    }): Promise<ScanHistoryResponse> => {
        const response = await apiClient.get<ScanHistoryResponse>('/api/scan/history', { params });
        return response.data;
    },

    // Retry a scan
    retryScan: async (scanId: string): Promise<ScanCreateResponse> => {
        const response = await apiClient.post<ScanCreateResponse>(`/api/scan/${scanId}/retry`);
        return response.data;
    },

    // Delete a scan
    deleteScan: async (scanId: string): Promise<void> => {
        await apiClient.delete(`/api/scan/${scanId}`);
    },

    // Get queue info
    getQueueInfo: async (): Promise<QueueInfo> => {
        const response = await apiClient.get<QueueInfo>('/api/scan/queue');
        return response.data;
    },

    // Cleanup old scans
    cleanupScans: async (days?: number): Promise<{ scans_deleted: number }> => {
        const response = await apiClient.post('/api/scan/cleanup', null, {
            params: days ? { days } : undefined,
        });
        return response.data;
    },
};

export const healthApi = {
    // Get health status
    getHealth: async (): Promise<HealthStatus> => {
        const response = await apiClient.get<HealthStatus>('/health');
        return response.data;
    },
};

export const dashboardApi = {
    // Get dashboard stats
    getStats: async (): Promise<DashboardStats> => {
        const response = await apiClient.get<DashboardStats>('/ui/api/dashboard-stats');
        return response.data;
    },
};

export default apiClient;
