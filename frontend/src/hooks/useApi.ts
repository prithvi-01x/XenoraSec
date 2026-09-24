import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { scanApi, dashboardApi, healthApi, batchScanApi, assetApi } from '../api/client';
import type { 
    ScanCreateRequest, 
    ReportFormat, 
    ReportType, 
    BatchScanCreateRequest, 
    AssetUpdateRequest 
} from '../types/api';

// Query keys
export const queryKeys = {
    scanResults: (scanId: string) => ['scan', 'results', scanId] as const,
    scanHistory: (params?: Record<string, unknown>) => ['scan', 'history', params] as const,
    queueInfo: () => ['scan', 'queue'] as const,
    dashboardStats: () => ['dashboard', 'stats'] as const,
    health: () => ['health'] as const,
    profiles: () => ['scan', 'profiles'] as const,
    templates: () => ['scan', 'templates'] as const,
    batchStatus: (batchId: string) => ['scan', 'batch', batchId] as const,
    assets: (params?: Record<string, unknown>) => ['assets', 'list', params] as const,
    assetStats: () => ['assets', 'stats'] as const,
    assetDetail: (assetId: number) => ['assets', 'detail', assetId] as const,
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

// Available scan profiles query
export function useScanProfiles() {
    return useQuery({
        queryKey: queryKeys.profiles(),
        queryFn: () => scanApi.getProfiles(),
        staleTime: 1000 * 60 * 10, // 10 minutes cache
    });
}

// Available Nuclei template tags query
export function useScanTemplates() {
    return useQuery({
        queryKey: queryKeys.templates(),
        queryFn: () => scanApi.getTemplates(),
        staleTime: 1000 * 60 * 10, // 10 minutes cache
    });
}

// Download report mutation
export function useDownloadReport() {
    return useMutation({
        mutationFn: async ({
            scanId,
            format = 'html',
            reportType = 'technical',
        }: {
            scanId: string;
            format?: ReportFormat;
            reportType?: ReportType;
        }) => {
            const blob = await scanApi.downloadReport(scanId, format, reportType);
            const ext = format === 'pdf' ? 'pdf' : format === 'markdown' ? 'md' : format === 'json' ? 'json' : 'html';
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `xenorasec-report-${scanId.slice(0, 8)}-${reportType}.${ext}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            return { success: true };
        },
    });
}

// ==================== BATCH SCAN HOOKS ====================

// Start a batch / CIDR scan
export function useStartBatchScan() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (data: BatchScanCreateRequest) => batchScanApi.startBatchScan(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.queueInfo() });
            queryClient.invalidateQueries({ queryKey: ['scan', 'history'] });
            queryClient.invalidateQueries({ queryKey: ['assets'] });
        },
    });
}

// Polling batch scan status
export function useBatchStatus(batchId: string | null) {
    return useQuery({
        queryKey: queryKeys.batchStatus(batchId || ''),
        queryFn: () => (batchId ? batchScanApi.getBatchStatus(batchId) : null),
        enabled: !!batchId,
        refetchInterval: (query) => {
            const data = query.state.data;
            if (!data) return 2500;
            // Stop polling when no tasks are running or pending
            const isDone = data.running === 0 && data.pending === 0;
            return isDone ? false : 2500;
        },
    });
}

// ==================== ASSET INVENTORY HOOKS ====================

// List assets with pagination and filters
export function useAssets(params?: {
    limit?: number;
    offset?: number;
    search?: string;
    asset_type?: string;
    status?: string;
    criticality?: string;
    min_risk?: number;
}) {
    return useQuery({
        queryKey: queryKeys.assets(params),
        queryFn: () => assetApi.getAssets(params),
    });
}

// Aggregated asset inventory metrics
export function useAssetStats() {
    return useQuery({
        queryKey: queryKeys.assetStats(),
        queryFn: () => assetApi.getAssetStats(),
        refetchInterval: 15000,
    });
}

// Single asset detail with discovered ports and vulnerabilities
export function useAssetDetail(assetId: number | null) {
    return useQuery({
        queryKey: queryKeys.assetDetail(assetId || 0),
        queryFn: () => (assetId ? assetApi.getAssetDetail(assetId) : null),
        enabled: !!assetId,
    });
}

// Update asset metadata (tags, notes, status, criticality)
export function useUpdateAsset() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ assetId, data }: { assetId: number; data: AssetUpdateRequest }) =>
            assetApi.updateAsset(assetId, data),
        onSuccess: (_data, variables) => {
            queryClient.invalidateQueries({ queryKey: queryKeys.assetDetail(variables.assetId) });
            queryClient.invalidateQueries({ queryKey: ['assets'] });
        },
    });
}

// Delete asset from inventory
export function useDeleteAsset() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (assetId: number) => assetApi.deleteAsset(assetId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['assets'] });
        },
    });
}

// Launch on-demand scan on asset
export function useScanAsset() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (assetId: number) => assetApi.scanAsset(assetId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.queueInfo() });
            queryClient.invalidateQueries({ queryKey: ['scan', 'history'] });
        },
    });
}

