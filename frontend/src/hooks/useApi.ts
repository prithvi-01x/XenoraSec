import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { scanApi, dashboardApi, healthApi } from '../api/client';
import type { ScanCreateRequest } from '../types/api';

// Query keys
export const queryKeys = {
    scanResults: (scanId: string) => ['scan', 'results', scanId] as const,
    scanHistory: (params?: Record<string, unknown>) => ['scan', 'history', params] as const,
    queueInfo: () => ['scan', 'queue'] as const,
    dashboardStats: () => ['dashboard', 'stats'] as const,
    health: () => ['health'] as const,
};

// Scan results query
export function useScanResults(scanId: string, options?: { refetchInterval?: number }) {
    return useQuery({
        queryKey: queryKeys.scanResults(scanId),
        queryFn: () => scanApi.getScanResults(scanId),
        refetchInterval: options?.refetchInterval,
        enabled: !!scanId,
    });
}

// Scan history query
export function useScanHistory(params?: {
    limit?: number;
    offset?: number;
    status?: string;
    target?: string;
}) {
    return useQuery({
        queryKey: queryKeys.scanHistory(params),
        queryFn: () => scanApi.getScanHistory(params),
    });
}

// Queue info query
export function useQueueInfo() {
    return useQuery({
        queryKey: queryKeys.queueInfo(),
        queryFn: () => scanApi.getQueueInfo(),
        refetchInterval: 5000, // Refresh every 5 seconds
    });
}

// Dashboard stats query
export function useDashboardStats() {
    return useQuery({
        queryKey: queryKeys.dashboardStats(),
        queryFn: () => dashboardApi.getStats(),
    });
}

// Health query
export function useHealth() {
    return useQuery({
        queryKey: queryKeys.health(),
        queryFn: () => healthApi.getHealth(),
        refetchInterval: 30000, // Refresh every 30 seconds
    });
}

// Start scan mutation
export function useStartScan() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: ScanCreateRequest) => scanApi.startScan(data),
        onSuccess: () => {
            // Invalidate relevant queries
            queryClient.invalidateQueries({ queryKey: ['scan', 'history'] });
            queryClient.invalidateQueries({ queryKey: queryKeys.queueInfo() });
            queryClient.invalidateQueries({ queryKey: queryKeys.dashboardStats() });
        },
    });
}

// Retry scan mutation
export function useRetryScan() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (scanId: string) => scanApi.retryScan(scanId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['scan', 'history'] });
            queryClient.invalidateQueries({ queryKey: queryKeys.queueInfo() });
        },
    });
}

// Delete scan mutation
export function useDeleteScan() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (scanId: string) => scanApi.deleteScan(scanId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['scan', 'history'] });
            queryClient.invalidateQueries({ queryKey: queryKeys.dashboardStats() });
        },
    });
}

// Cleanup scans mutation
export function useCleanupScans() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (days?: number) => scanApi.cleanupScans(days),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['scan', 'history'] });
            queryClient.invalidateQueries({ queryKey: queryKeys.dashboardStats() });
        },
    });
}
