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
            <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div className="bg-surface border border-gray-700 rounded-xl p-6 text-center max-w-sm w-full">
                    <LoadingSpinner size="lg" className="mx-auto mb-3" />
                    <p className="text-sm text-gray-300">Loading batch scan telemetry...</p>
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
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-surface border border-gray-700 rounded-xl shadow-2xl max-w-2xl w-full flex flex-col max-h-[90vh] overflow-hidden">
                {/* Header */}
                <div className="p-4 sm:p-5 border-b border-gray-700 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-primary/20 text-primary">
                            <Layers className="w-5 h-5" />
                        </div>
                        <div>
                            <h3 className="font-bold text-white text-base sm:text-lg">
                                {batch?.batch_name || 'Subnet Batch Execution'}
                            </h3>
                            <p className="text-xs text-gray-400 font-mono">ID: {batchId.slice(0, 18)}...</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white p-1 rounded-lg hover:bg-surface-light"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Progress Stats Bar */}
                <div className="p-4 sm:p-5 border-b border-gray-700 bg-background/50 space-y-3">
                    <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-300 font-medium flex items-center gap-2">
                            {!isFinished && <RefreshCw className="w-3.5 h-3.5 animate-spin text-primary" />}
                            {isFinished ? 'Batch Scan Completed' : 'Scanning Targets in Concurrency Queue...'}
                        </span>
                        <span className="font-mono text-primary font-bold">{percent}%</span>
                    </div>

                    <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                        <div
                            className="bg-primary h-full transition-all duration-500 rounded-full"
                            style={{ width: `${percent}%` }}
                        />
                    </div>

                    {/* Stat Badges */}
                    <div className="grid grid-cols-4 gap-2 pt-1 text-center">
                        <div className="bg-surface p-2 rounded-lg border border-gray-700/60">
                            <div className="text-xs text-gray-400">Total</div>
                            <div className="text-sm font-bold text-white">{total}</div>
                        </div>
                        <div className="bg-surface p-2 rounded-lg border border-gray-700/60">
                            <div className="text-xs text-emerald-400 flex items-center justify-center gap-1">
                                <CheckCircle2 className="w-3 h-3" /> Done
                            </div>
                            <div className="text-sm font-bold text-white">{completed}</div>
                        </div>
                        <div className="bg-surface p-2 rounded-lg border border-gray-700/60">
                            <div className="text-xs text-primary flex items-center justify-center gap-1">
                                <Clock className="w-3 h-3" /> Running
                            </div>
                            <div className="text-sm font-bold text-white">{running}</div>
                        </div>
                        <div className="bg-surface p-2 rounded-lg border border-gray-700/60">
                            <div className="text-xs text-danger flex items-center justify-center gap-1">
                                <AlertTriangle className="w-3 h-3" /> Failed
                            </div>
                            <div className="text-sm font-bold text-white">{failed}</div>
                        </div>
                    </div>
                </div>

                {/* Target Scan List */}
                <div className="p-4 sm:p-5 overflow-y-auto flex-1 space-y-2">
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
                        Target Queue ({batch?.scans?.length || 0})
                    </h4>
                    {batch?.scans?.map((scan) => (
                        <div
                            key={scan.scan_id}
                            className="flex items-center justify-between p-3 rounded-lg bg-surface-light border border-gray-700/80 hover:border-gray-600 transition-colors text-xs"
                        >
                            <div className="flex items-center gap-2">
                                <span className="font-mono text-white font-medium">{scan.target}</span>
                                {scan.risk_score > 0 && (
                                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono">
                                        Risk {scan.risk_score.toFixed(1)}
                                    </span>
                                )}
                            </div>

                            <div className="flex items-center gap-3">
                                <StatusBadge status={scan.status} className="text-[10px] py-0.5 px-2" />
                                <Link
                                    to={`/scan/${scan.scan_id}`}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="p-1 rounded text-gray-400 hover:text-primary transition-colors"
                                    title="Open Scan Report"
                                >
                                    <ExternalLink className="w-4 h-4" />
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-700 flex justify-end gap-2 bg-surface">
                    <button
                        onClick={onClose}
                        className="btn btn-secondary text-xs px-4 py-2"
                    >
                        Dismiss Window
                    </button>
                </div>
            </div>
        </div>
    );
}
