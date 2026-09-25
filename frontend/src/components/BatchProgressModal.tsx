import { Link } from 'react-router-dom';
import { 
    X, 
    Layers, 
    CheckCircle2, 
    Clock, 
    AlertTriangle, 
    ExternalLink,
    RefreshCw 
} from 'lucide-react';
import { useBatchStatus } from '../hooks/useApi';
import { StatusBadge } from './StatusBadge';
import { LoadingSpinner } from './LoadingSpinner';

interface BatchProgressModalProps {
    batchId: string;
    onClose: () => void;
}

export function BatchProgressModal({ batchId, onClose }: BatchProgressModalProps) {
    const { data: batch, isLoading } = useBatchStatus(batchId);

    if (isLoading && !batch) {
        return (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div className="bg-surface border border-surface-border rounded-lg p-6 text-center max-w-sm w-full">
                    <LoadingSpinner size="lg" className="mx-auto mb-3 text-blue-500" />
                    <p className="text-xs font-mono text-slate-300">Retrieving batch telemetry...</p>
                </div>
            </div>
        );
    }

    const total = batch?.total || 1;
    const completed = batch?.completed || 0;
    const running = batch?.running || 0;
    const failed = batch?.failed || 0;
    const percent = Math.min(100, Math.round(((completed + failed) / total) * 100));
    const isFinished = running === 0 && (batch?.pending || 0) === 0;

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-surface border border-surface-border rounded-lg shadow-2xl max-w-2xl w-full flex flex-col max-h-[85vh] overflow-hidden">
                {/* Header */}
                <div className="px-4 py-3 border-b border-surface-border flex items-center justify-between bg-[#070b12]">
                    <div className="flex items-center gap-2.5">
                        <div className="p-1.5 rounded bg-blue-950/80 text-blue-400 border border-blue-800">
                            <Layers className="w-4 h-4" />
                        </div>
                        <div>
                            <h3 className="font-bold text-white text-xs font-mono uppercase tracking-wider">
                                {batch?.batch_name || 'Subnet Batch Execution'}
                            </h3>
                            <p className="text-[10px] text-slate-400 font-mono">ID: {batchId}</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-slate-400 hover:text-white p-1 rounded hover:bg-surface-light"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>

                {/* Progress Stats Bar */}
                <div className="p-4 border-b border-surface-border bg-surface space-y-3">
                    <div className="flex items-center justify-between text-xs font-mono">
                        <span className="text-slate-300 flex items-center gap-2">
                            {!isFinished && <RefreshCw className="w-3 h-3 animate-spin text-blue-400" />}
                            {isFinished ? 'Execution Complete' : 'Executing Concurrent Scans...'}
                        </span>
                        <span className="text-blue-400 font-bold">{percent}%</span>
                    </div>

                    <div className="w-full bg-[#070b12] rounded-full h-1.5 overflow-hidden border border-surface-border">
                        <div
                            className="bg-blue-500 h-full transition-all duration-300 rounded-full"
                            style={{ width: `${percent}%` }}
                        />
                    </div>

                    {/* Stat Badges */}
                    <div className="grid grid-cols-4 gap-2 pt-1 text-center font-mono">
                        <div className="bg-[#070b12] p-2 rounded border border-surface-border">
                            <div className="text-[10px] text-slate-400">Total</div>
                            <div className="text-sm font-bold text-white">{total}</div>
                        </div>
                        <div className="bg-[#070b12] p-2 rounded border border-surface-border">
                            <div className="text-[10px] text-emerald-400 flex items-center justify-center gap-1">
                                <CheckCircle2 className="w-3 h-3" /> Done
                            </div>
                            <div className="text-sm font-bold text-white">{completed}</div>
                        </div>
                        <div className="bg-[#070b12] p-2 rounded border border-surface-border">
                            <div className="text-[10px] text-blue-400 flex items-center justify-center gap-1">
                                <Clock className="w-3 h-3" /> Running
                            </div>
                            <div className="text-sm font-bold text-white">{running}</div>
                        </div>
                        <div className="bg-[#070b12] p-2 rounded border border-surface-border">
                            <div className="text-[10px] text-rose-400 flex items-center justify-center gap-1">
                                <AlertTriangle className="w-3 h-3" /> Failed
                            </div>
                            <div className="text-sm font-bold text-white">{failed}</div>
                        </div>
                    </div>
                </div>

                {/* Target Scan List */}
                <div className="p-3 overflow-y-auto flex-1 space-y-1.5 bg-[#05080e]">
                    <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400 px-1 py-1">
                        Targets ({batch?.scans?.length || 0})
                    </div>
                    {batch?.scans?.map((scan) => (
                        <div
                            key={scan.scan_id}
                            className="flex items-center justify-between p-2.5 rounded bg-surface border border-surface-border hover:border-slate-600 transition-colors text-xs font-mono"
                        >
                            <div className="flex items-center gap-2">
                                <span className="text-slate-100 font-semibold">{scan.target}</span>
                                {scan.risk_score > 0 && (
                                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-950 text-amber-300 border border-amber-800">
                                        Risk {scan.risk_score.toFixed(1)}
                                    </span>
                                )}
                            </div>

                            <div className="flex items-center gap-3">
                                <StatusBadge status={scan.status} className="text-[9px] py-0.5 px-1.5" />
                                <Link
                                    to={`/scan/${scan.scan_id}`}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="p-1 rounded text-slate-400 hover:text-blue-400 transition-colors"
                                    title="Open Scan Report"
                                >
                                    <ExternalLink className="w-3.5 h-3.5" />
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Footer */}
                <div className="px-4 py-2.5 border-t border-surface-border flex justify-end bg-surface">
                    <button
                        onClick={onClose}
                        className="btn btn-secondary text-xs"
                    >
                        Close Telemetry
                    </button>
                </div>
            </div>
        </div>
    );
}
