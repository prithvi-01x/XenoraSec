import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useScanHistory, useDeleteScan } from '../hooks/useApi';
import { LoadingState } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';
import { StatusBadge } from '../components/StatusBadge';
import { formatDate, formatDuration } from '../utils/helpers';
import { 
    Trash2, 
    ChevronLeft, 
    ChevronRight, 
    Search, 
    ExternalLink,
    History
} from 'lucide-react';

const ITEMS_PER_PAGE = 10;

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

    const debouncedSearch = useDebounce(searchTerm, 350);

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

    if (isLoading) return <LoadingState message="Querying scan execution ledger..." />;
    if (error) return <ErrorState message="Failed to load scan history records" onRetry={refetch} />;
    if (!data) return null;

    const totalPages = Math.ceil(data.total / ITEMS_PER_PAGE);

    return (
        <div className="space-y-5">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-surface-border pb-4">
                <div>
                    <h1 className="text-xl font-bold tracking-tight text-white font-mono uppercase flex items-center gap-2">
                        <History className="w-5 h-5 text-blue-400" />
                        Audit Ledger &amp; Scan Archive
                    </h1>
                    <p className="text-xs text-slate-400 mt-0.5">
                        Comprehensive ledger of network assessments, status logs, and historical risk scores.
                    </p>
                </div>
                <div className="text-xs font-mono text-slate-400">
                    Total Records: <span className="text-white font-bold">{data.total}</span>
                </div>
            </div>

            {/* Filters Bar */}
            <div className="card p-3 bg-surface border-surface-border">
                <div className="flex flex-col sm:flex-row gap-2.5">
                    <select
                        value={statusFilter}
                        onChange={(e) => {
                            setStatusFilter(e.target.value);
                            setPage(0);
                        }}
                        className="input sm:w-44 text-xs"
                    >
                        <option value="">All Statuses</option>
                        <option value="running">Running</option>
                        <option value="completed">Completed</option>
                        <option value="failed">Failed</option>
                        <option value="timeout">Timeout</option>
                        <option value="partial">Partial</option>
                    </select>

                    <div className="relative flex-1">
                        <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => {
                                setSearchTerm(e.target.value);
                                setPage(0);
                            }}
                            placeholder="Filter by target host or IP address..."
                            className="input pl-8 text-xs"
                        />
                    </div>
                </div>
            </div>

            {/* Table */}
            <div className="card p-0 overflow-hidden">
                {data.items.length === 0 ? (
                    <div className="p-12 text-center text-slate-500">
                        <History className="w-8 h-8 mx-auto mb-2 opacity-30 text-blue-400" />
                        <p className="text-xs font-mono">No scan records matching current search parameters.</p>
                    </div>
                ) : (
                    <>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-xs font-mono">
                                <thead className="bg-[#070b12] text-slate-400 text-[10px] uppercase border-b border-surface-border">
                                    <tr>
                                        <th className="py-2.5 px-4 font-semibold">Target / Host</th>
                                        <th className="py-2.5 px-4 font-semibold">Status</th>
                                        <th className="py-2.5 px-4 font-semibold">Risk Posture</th>
                                        <th className="py-2.5 px-4 font-semibold">Duration</th>
                                        <th className="py-2.5 px-4 font-semibold">Recorded Date</th>
                                        <th className="py-2.5 px-4 font-semibold text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-surface-border/60">
                                    {data.items.map((scan) => (
                                        <tr key={scan.scan_id} className="hover:bg-surface-light/40 transition-colors">
                                            <td className="py-2.5 px-4">
                                                <div className="flex items-center gap-2 flex-wrap">
                                                    <Link 
                                                        to={`/scan/${scan.scan_id}`}
                                                        className="font-bold text-white hover:text-blue-400 transition-colors"
                                                    >
                                                        {scan.target}
                                                    </Link>
                                                    <span className="text-[9px] font-mono uppercase px-1.5 py-0.2 rounded bg-blue-950/80 text-blue-400 border border-blue-800 font-semibold">
                                                        {scan.scan_profile || 'quick'}
                                                    </span>
                                                    {scan.batch_id && (
                                                        <span
                                                            className="text-[9px] font-mono uppercase px-1.5 py-0.2 rounded bg-purple-950 text-purple-400 border border-purple-800 font-semibold"
                                                            title={`Batch ID: ${scan.batch_id}`}
                                                        >
                                                            BATCH
                                                        </span>
                                                    )}
                                                </div>
                                                <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                                                    {scan.scan_id.substring(0, 8)}...
                                                </div>
                                            </td>
                                            <td className="py-2.5 px-4">
                                                <StatusBadge status={scan.status} className="text-[9px] py-0.5 px-1.5" />
                                            </td>
                                            <td className="py-2.5 px-4">
                                                <span className={`font-bold ${
                                                    scan.risk_score >= 7.0 
                                                        ? 'text-red-400' 
                                                        : scan.risk_score >= 4.0 
                                                        ? 'text-amber-400' 
                                                        : 'text-slate-300'
                                                }`}>
                                                    {scan.risk_score.toFixed(1)} / 10
                                                </span>
                                            </td>
                                            <td className="py-2.5 px-4 text-slate-400">
                                                {formatDuration(scan.duration)}
                                            </td>
                                            <td className="py-2.5 px-4 text-slate-400 text-[11px] font-sans">
                                                {formatDate(scan.created_at)}
                                            </td>
                                            <td className="py-2.5 px-4 text-right">
                                                <div className="flex items-center justify-end gap-1.5">
                                                    <Link
                                                        to={`/scan/${scan.scan_id}`}
                                                        className="btn btn-secondary btn-sm"
                                                        title="Inspect Scan Dossier"
                                                    >
                                                        <span>Inspect</span>
                                                        <ExternalLink className="w-3 h-3" />
                                                    </Link>

                                                    {deleteConfirmId === scan.scan_id ? (
                                                        <div className="flex items-center gap-1">
                                                            <button
                                                                onClick={() => handleDelete(scan.scan_id)}
                                                                disabled={deleteScan.isPending}
                                                                className="btn btn-danger btn-sm"
                                                            >
                                                                Yes
                                                            </button>
                                                            <button
                                                                onClick={() => setDeleteConfirmId(null)}
                                                                className="btn btn-secondary btn-sm"
                                                            >
                                                                No
                                                            </button>
                                                        </div>
                                                    ) : (
                                                        <button
                                                            onClick={() => setDeleteConfirmId(scan.scan_id)}
                                                            className="p-1.5 text-slate-500 hover:text-rose-400 rounded hover:bg-surface-light transition-colors"
                                                            title="Delete Record"
                                                        >
                                                            <Trash2 className="w-3.5 h-3.5" />
                                                        </button>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        {/* Pagination Bar */}
                        {totalPages > 1 && (
                            <div className="flex items-center justify-between p-3 border-t border-surface-border bg-[#070b12] text-xs font-mono">
                                <div className="text-slate-400">
                                    Displaying {page * ITEMS_PER_PAGE + 1} &ndash;{' '}
                                    {Math.min((page + 1) * ITEMS_PER_PAGE, data.total)} of {data.total} records
                                </div>

                                <div className="flex items-center gap-1.5">
                                    <button
                                        onClick={() => setPage(page - 1)}
                                        disabled={page === 0}
                                        className="btn btn-outline btn-sm"
                                    >
                                        <ChevronLeft className="w-3 h-3" />
                                        Prev
                                    </button>

                                    <span className="text-slate-400 px-2">
                                        Page {page + 1} of {totalPages}
                                    </span>

                                    <button
                                        onClick={() => setPage(page + 1)}
                                        disabled={page >= totalPages - 1}
                                        className="btn btn-outline btn-sm"
                                    >
                                        Next
                                        <ChevronRight className="w-3 h-3" />
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
