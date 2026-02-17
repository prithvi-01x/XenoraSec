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

// Scan results query — auto-polls every 3s while scan is running, stops when done
export function useScanResults(scanId: string) {
    return useQuery({
        queryKey: queryKeys.scanResults(scanId),
        queryFn: () => scanApi.getScanResults(scanId),
        enabled: !!scanId,
        refetchInterval: (query) => {
            const status = query.state.data?.status;
            // Keep polling only while running; stop on any terminal state
            return status === 'running' ? 3000 : false;
        },
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
        refetchInterval: 5000,
    });
}

// Dashboard stats — auto-refresh every 15s so running scan count stays live
export function useDashboardStats() {
    return useQuery({
        queryKey: queryKeys.dashboardStats(),
        queryFn: () => dashboardApi.getStats(),
        refetchInterval: 15000,
    });
}

// Health query
export function useHealth() {
    return useQuery({
        queryKey: queryKeys.health(),
        queryFn: () => healthApi.getHealth(),
        refetchInterval: 30000,
    });
}

// Start scan mutation
export function useStartScan() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: ScanCreateRequest) => scanApi.startScan(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['scan', 'history'] });
            queryClient.invalidateQueries({ queryKey: queryKeys.queueInfo() });
            queryClient.invalidateQueries({ queryKey: queryKeys.dashboardStats() });
        },
    });
}

// Cancel scan mutation
export function useCancelScan() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (scanId: string) => scanApi.cancelScan(scanId),
        onSuccess: (_data, scanId) => {
            // Immediately invalidate so the UI reflects cancelled state
            queryClient.invalidateQueries({ queryKey: queryKeys.scanResults(scanId) });
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
        mutationFn: ({ days, secret }: { days?: number; secret?: string }) =>
            scanApi.cleanupScans(days, secret),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['scan', 'history'] });
            queryClient.invalidateQueries({ queryKey: queryKeys.dashboardStats() });
        },
    });
}
