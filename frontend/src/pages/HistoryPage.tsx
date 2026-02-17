import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useScanHistory, useDeleteScan } from '../hooks/useApi';
import { LoadingState } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';
import { StatusBadge } from '../components/StatusBadge';
import { formatDate, formatDuration } from '../utils/helpers';
import { Trash2, Eye, ChevronLeft, ChevronRight } from 'lucide-react';

const ITEMS_PER_PAGE = 10;

// Simple debounce hook — waits for user to stop typing before firing
function useDebounce<T>(value: T, delayMs: number): T {
    const [debounced, setDebounced] = useState(value);
    useEffect(() => {
        const timer = setTimeout(() => setDebounced(value), delayMs);
        return () => clearTimeout(timer);
    }, [value, delayMs]);
    return debounced;
}

export function HistoryPage() {
    const [page, setPage] = useState(0);
    const [statusFilter, setStatusFilter] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

    // Debounce search — only fires query 400ms after user stops typing
    const debouncedSearch = useDebounce(searchTerm, 400);

    const { data, isLoading, error, refetch } = useScanHistory({
        limit: ITEMS_PER_PAGE,
        offset: page * ITEMS_PER_PAGE,
        status: statusFilter || undefined,
        target: debouncedSearch || undefined,
    });

    const deleteScan = useDeleteScan();

    const handleDelete = async (scanId: string) => {
        try {
            await deleteScan.mutateAsync(scanId);
            setDeleteConfirmId(null);
            refetch();
        } catch (err) {
            console.error('Failed to delete scan:', err);
        }
    };

    if (isLoading) return <LoadingState message="Loading scan history..." />;
    if (error) return <ErrorState message="Failed to load scan history" onRetry={refetch} />;
    if (!data) return null;

    const totalPages = Math.ceil(data.total / ITEMS_PER_PAGE);

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold mb-2">Scan History</h1>
                <p className="text-gray-400">View and manage all scan records</p>
            </div>

            {/* Filters */}
            <div className="card">
                <div className="flex gap-4">
                    <select
                        value={statusFilter}
                        onChange={(e) => {
                            setStatusFilter(e.target.value);
                            setPage(0);
                        }}
                        className="input w-48"
                    >
                        <option value="">All Statuses</option>
                        <option value="running">Running</option>
                        <option value="completed">Completed</option>
                        <option value="failed">Failed</option>
                        <option value="timeout">Timeout</option>
                        <option value="partial">Partial</option>
                    </select>

                    <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => {
                            setSearchTerm(e.target.value);
                            setPage(0);
                        }}
                        placeholder="Search by target..."
                        className="input flex-1"
                    />
                </div>
            </div>

            {/* Table */}
            <div className="card">
                {data.items.length === 0 ? (
                    <p className="text-center text-gray-400 py-12">No scans found</p>
                ) : (
                    <>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-gray-700">
                                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Target</th>
                                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Status</th>
                                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Risk Score</th>
                                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Duration</th>
                                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Created</th>
                                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.items.map((scan) => (
                                        <tr key={scan.scan_id} className="border-b border-gray-700/50 hover:bg-surface-light">
                                            <td className="py-3 px-4">
                                                <div>
                                                    <div className="font-medium">{scan.target}</div>
                                                    <div className="text-xs text-gray-400 font-mono">
                                                        {scan.scan_id.substring(0, 8)}...
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="py-3 px-4">
                                                <StatusBadge status={scan.status} />
                                            </td>
                                            <td className="py-3 px-4">
                                                <span className="font-bold text-lg">{scan.risk_score.toFixed(1)}</span>
                                            </td>
                                            <td className="py-3 px-4 text-gray-400">
                                                {formatDuration(scan.duration)}
                                            </td>
                                            <td className="py-3 px-4 text-sm text-gray-400">
                                                {formatDate(scan.created_at)}
                                            </td>
                                            <td className="py-3 px-4">
                                                <div className="flex items-center gap-2">
                                                    <Link
                                                        to={`/scan/${scan.scan_id}`}
                                                        className="btn btn-secondary btn-sm flex items-center gap-1"
                                                        title="View Details"
                                                    >
                                                        <Eye className="w-4 h-4" />
                                                    </Link>
                                                    {deleteConfirmId === scan.scan_id ? (
                                                        <>
                                                            <button
                                                                onClick={() => handleDelete(scan.scan_id)}
                                                                disabled={deleteScan.isPending}
                                                                className="btn btn-danger btn-sm"
                                                            >
                                                                Confirm
                                                            </button>
                                                            <button
                                                                onClick={() => setDeleteConfirmId(null)}
                                                                className="btn btn-secondary btn-sm"
                                                            >
                                                                Cancel
                                                            </button>
                                                        </>
                                                    ) : (
                                                        <button
                                                            onClick={() => setDeleteConfirmId(scan.scan_id)}
                                                            className="btn btn-danger btn-sm flex items-center gap-1"
                                                            title="Delete"
                                                        >
                                                            <Trash2 className="w-4 h-4" />
                                                        </button>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        {/* Pagination */}
                        {totalPages > 1 && (
                            <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-700">
                                <div className="text-sm text-gray-400">
                                    Showing {page * ITEMS_PER_PAGE + 1} to{' '}
                                    {Math.min((page + 1) * ITEMS_PER_PAGE, data.total)} of {data.total} scans
                                </div>

                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => setPage(page - 1)}
                                        disabled={page === 0}
                                        className="btn btn-outline btn-sm flex items-center gap-1"
                                    >
                                        <ChevronLeft className="w-4 h-4" />
                                        Previous
                                    </button>

                                    <span className="text-sm text-gray-400">
                                        Page {page + 1} of {totalPages}
                                    </span>

                                    <button
                                        onClick={() => setPage(page + 1)}
                                        disabled={page >= totalPages - 1}
                                        className="btn btn-outline btn-sm flex items-center gap-1"
                                    >
                                        Next
                                        <ChevronRight className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
