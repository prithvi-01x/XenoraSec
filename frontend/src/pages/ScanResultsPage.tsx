import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useScanResults, useRetryScan, useDeleteScan, useCancelScan } from '../hooks/useApi';
import { LoadingState } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';
import { RiskScore } from '../components/RiskScore';
import { StatusBadge } from '../components/StatusBadge';
import { SeverityBadge } from '../components/SeverityBadge';
import { LiveTerminal } from '../components/LiveTerminal';
import { ReportExportModal } from '../components/ReportExportModal';
import { formatDuration, formatDate } from '../utils/helpers';
import { 
    RefreshCw, 
    Trash2, 
    ChevronDown, 
    ExternalLink, 
    XCircle, 
    Download, 
    Radio,
    Terminal,
    Shield,
    Server,
    AlertTriangle,
    Sliders,
    Search,
    Code
} from 'lucide-react';
import type { Vulnerability } from '../types/api';

export function ScanResultsPage() {
    const { scanId } = useParams<{ scanId: string }>();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<'summary' | 'terminal' | 'ports' | 'vulnerabilities' | 'raw'>('summary');
    const [expandedVulnIndex, setExpandedVulnIndex] = useState<number | null>(null);
    const [severityFilter, setSeverityFilter] = useState<string>('all');
    const [searchTerm, setSearchTerm] = useState('');
    const [deleteConfirm, setDeleteConfirm] = useState(false);
    const [showReportModal, setShowReportModal] = useState(false);

    // Auto-polling handled inside useScanResults via refetchInterval
    const { data: scan, isLoading, error, refetch } = useScanResults(scanId!);

    const retryScan = useRetryScan();
    const deleteScan = useDeleteScan();
    const cancelScan = useCancelScan();

    const handleRetry = async () => {
        if (!scanId) return;
        try {
            const result = await retryScan.mutateAsync(scanId);
            navigate(`/scan/${result.scan_id}`);
        } catch (err) {
            console.error('Failed to retry scan:', err);
        }
    };

    const handleDelete = async () => {
        if (!scanId) return;
        try {
            await deleteScan.mutateAsync(scanId);
            navigate('/history');
        } catch (err) {
            console.error('Failed to delete scan:', err);
        }
    };

    const handleCancel = async () => {
        if (!scanId) return;
        try {
            await cancelScan.mutateAsync(scanId);
        } catch (err) {
            console.error('Failed to cancel scan:', err);
        }
    };

    if (isLoading) return <LoadingState message="Loading scan intelligence dossier..." />;
    if (error) return <ErrorState message="Failed to load scan results" onRetry={refetch} />;
    if (!scan) return null;

    const filteredVulnerabilities = scan.nuclei.vulnerabilities.filter((vuln: Vulnerability) => {
        const matchesSeverity = severityFilter === 'all' || vuln.severity.toLowerCase() === severityFilter.toLowerCase();
        const matchesSearch = !searchTerm ||
            vuln.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            vuln.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            vuln.template_id?.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesSeverity && matchesSearch;
    });

    return (
        <div className="space-y-5">
            {/* Header Area */}
            <div className="flex items-start justify-between flex-wrap gap-4 border-b border-surface-border pb-4">
                <div>
                    <div className="flex items-center gap-2.5 mb-1.5 flex-wrap">
                        <h1 className="text-xl sm:text-2xl font-bold font-mono text-white tracking-tight">
                            {scan.target}
                        </h1>
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-blue-950/80 text-blue-400 border border-blue-800 uppercase">
                            <Sliders className="w-3 h-3" />
                            PROFILE: {scan.scan_profile || 'quick'}
                        </span>
                        {scan.batch_id && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-purple-950/80 text-purple-400 border border-purple-800 uppercase">
                                BATCH JOB
                            </span>
                        )}
                    </div>
                    <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
                        <span>ID: <code className="text-slate-300">{scan.scan_id}</code></span>
                        <span>&bull;</span>
                        <span>{formatDate(scan.created_at)}</span>
                        {scan.duration && (
                            <>
                                <span>&bull;</span>
                                <span className="text-emerald-400 font-semibold">{formatDuration(scan.duration)}</span>
                            </>
                        )}
                    </div>
                </div>

                <div className="flex items-center gap-2 flex-wrap font-mono">
                    <button
                        onClick={() => setShowReportModal(true)}
                        className="btn btn-primary"
                        title="Download executive or technical assessment report"
                    >
                        <Download className="w-3.5 h-3.5" />
                        <span>Export Report</span>
                    </button>

                    {scan.status === 'running' && (
                        <button
                            onClick={handleCancel}
                            disabled={cancelScan.isPending}
                            className="btn btn-secondary text-amber-400 hover:text-amber-300"
                        >
                            <XCircle className="w-3.5 h-3.5" />
                            <span>{cancelScan.isPending ? 'Aborting...' : 'Abort Scan'}</span>
                        </button>
                    )}

                    {(scan.status === 'failed' || scan.status === 'timeout' || scan.status === 'partial') && (
                        <button
                            onClick={handleRetry}
                            disabled={retryScan.isPending}
                            className="btn btn-secondary"
                        >
                            <RefreshCw className="w-3.5 h-3.5" />
                            <span>Retry</span>
                        </button>
                    )}

                    {deleteConfirm ? (
                        <div className="flex items-center gap-1.5 p-1 bg-red-950/60 border border-red-800 rounded">
                            <span className="text-[11px] text-red-300 px-1 font-sans">Delete scan?</span>
                            <button
                                onClick={handleDelete}
                                disabled={deleteScan.isPending}
                                className="btn btn-danger btn-sm"
                            >
                                Confirm
                            </button>
                            <button
                                onClick={() => setDeleteConfirm(false)}
                                className="btn btn-secondary btn-sm"
                            >
                                Cancel
                            </button>
                        </div>
                    ) : (
                        <button
                            onClick={() => setDeleteConfirm(true)}
                            className="btn btn-outline text-slate-400 hover:text-rose-400 hover:border-rose-900"
                            title="Delete scan"
                        >
                            <Trash2 className="w-3.5 h-3.5" />
                        </button>
                    )}
                </div>
            </div>

            {/* Live Progress Banner when running */}
            {scan.status === 'running' && (
                <div className="flex items-center justify-between p-3 bg-blue-950/40 border border-blue-800/80 rounded flex-wrap gap-2 text-xs font-mono">
                    <div className="flex items-center gap-2.5">
                        <span className="w-2.5 h-2.5 rounded-full bg-blue-400 animate-pulse" />
                        <span className="text-blue-300 font-medium">
                            Scan actively executing &mdash; streaming backend engine telemetry in real-time
                        </span>
                    </div>
                    <button
                        onClick={() => setActiveTab('terminal')}
                        className="btn btn-secondary btn-sm text-blue-400"
                    >
                        <Radio className="w-3 h-3 text-emerald-400 animate-pulse" />
                        <span>Inspect Live Terminal</span>
                    </button>
                </div>
            )}

            {/* Executive KPI Matrix */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="card bg-surface p-3 flex flex-col justify-center">
                    <RiskScore score={scan.risk_score} size="lg" />
                </div>

                <div className="card bg-surface p-3 flex flex-col justify-between">
                    <div>
                        <div className="text-[10px] font-mono uppercase text-slate-400">Execution Status</div>
                        <div className="mt-1">
                            <StatusBadge status={scan.status} className="text-xs" />
                        </div>
                    </div>
                    {scan.error && (
                        <p className="mt-2 text-[11px] text-rose-400 font-mono line-clamp-2">{scan.error}</p>
                    )}
                    <div className="text-[10px] text-slate-500 font-mono mt-2 pt-2 border-t border-surface-border">
                        Duration: {formatDuration(scan.duration)}
                    </div>
                </div>

                <div className="card bg-surface p-3 flex flex-col justify-between">
                    <div>
                        <div className="text-[10px] font-mono uppercase text-slate-400">Discovered Vulnerabilities</div>
                        <div className="text-2xl font-bold font-mono text-white mt-1">
                            {scan.summary.total_vulnerabilities}
                        </div>
                    </div>
                    <div className="text-[11px] font-mono text-slate-400 mt-2 pt-2 border-t border-surface-border flex items-center gap-2">
                        <span className="text-red-400 font-bold">{scan.summary.critical_count} crit</span>
                        <span>&bull;</span>
                        <span className="text-orange-400 font-bold">{scan.summary.high_count} high</span>
                    </div>
                </div>

                <div className="card bg-surface p-3 flex flex-col justify-between">
                    <div>
                        <div className="text-[10px] font-mono uppercase text-slate-400">Open TCP / UDP Ports</div>
                        <div className="text-2xl font-bold font-mono text-white mt-1">
                            {scan.summary.open_ports}
                        </div>
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono mt-2 pt-2 border-t border-surface-border">
                        Fingerprinted via Nmap
                    </div>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="card p-0 overflow-hidden">
                <div className="border-b border-surface-border bg-[#070b12] px-3 flex gap-2 overflow-x-auto select-none">
                    {(['summary', 'terminal', 'ports', 'vulnerabilities', 'raw'] as const).map((tab) => {
                        const isActive = activeTab === tab;
                        return (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={`px-3 py-2.5 text-xs font-mono font-medium capitalize transition-all border-b-2 whitespace-nowrap flex items-center gap-1.5 ${
                                    isActive
                                        ? 'border-blue-500 text-blue-400 bg-surface/60 font-semibold'
                                        : 'border-transparent text-slate-400 hover:text-slate-200'
                                }`}
                            >
                                {tab === 'summary' && <Shield className="w-3.5 h-3.5" />}
                                {tab === 'terminal' && <Terminal className="w-3.5 h-3.5" />}
                                {tab === 'ports' && <Server className="w-3.5 h-3.5" />}
                                {tab === 'vulnerabilities' && <AlertTriangle className="w-3.5 h-3.5" />}
                                {tab === 'raw' && <Code className="w-3.5 h-3.5" />}

                                <span>{tab === 'terminal' ? 'Live Console' : tab}</span>

                                {tab === 'terminal' && scan.status === 'running' && (
                                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse ml-1" />
                                )}

                                {tab === 'vulnerabilities' && scan.summary.total_vulnerabilities > 0 && (
                                    <span className="text-[10px] font-mono bg-red-950 text-red-400 border border-red-800 px-1 py-0.2 rounded">
                                        {scan.summary.total_vulnerabilities}
                                    </span>
                                )}

                                {tab === 'ports' && scan.summary.open_ports > 0 && (
                                    <span className="text-[10px] font-mono bg-blue-950 text-blue-400 border border-blue-800 px-1 py-0.2 rounded">
                                        {scan.summary.open_ports}
                                    </span>
                                )}
                            </button>
                        );
                    })}
                </div>

                <div className="p-4 sm:p-5">
                    {/* Summary Tab */}
                    {activeTab === 'summary' && (
                        <div className="space-y-5">
                            <div>
                                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 mb-3">
                                    Vulnerability Severity Breakdown
                                </h3>
                                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5 font-mono">
                                    {Object.entries(scan.summary.severity_distribution).map(([sev, count]) => (
                                        <div key={sev} className="bg-[#070b12] p-3 rounded border border-surface-border">
                                            <div className="text-[10px] uppercase text-slate-500 font-semibold">{sev}</div>
                                            <div className="text-xl font-bold text-white mt-1">{count}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 mb-3">
                                    Discovered Services &amp; Ports
                                </h3>
                                {scan.nmap.ports.length === 0 ? (
                                    <p className="text-xs font-mono text-slate-500">No open ports identified on this target.</p>
                                ) : (
                                    <div className="flex flex-wrap gap-2">
                                        {scan.nmap.ports.map((port) => (
                                            <span 
                                                key={port.port} 
                                                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#070b12] border border-surface-border text-xs font-mono text-slate-200"
                                            >
                                                <span className="text-blue-400 font-bold">{port.port}</span>
                                                <span className="text-slate-500">/</span>
                                                <span className="uppercase text-slate-400">{port.protocol}</span>
                                                <span className="text-emerald-400 font-semibold">({port.service})</span>
                                                {port.version && <span className="text-slate-500 text-[10px]">[{port.version}]</span>}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Ports Tab */}
                    {activeTab === 'ports' && (
                        <div>
                            {scan.nmap.ports.length === 0 ? (
                                <p className="text-xs font-mono text-slate-500 py-6 text-center">No open ports discovered.</p>
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left text-xs font-mono">
                                        <thead className="bg-[#070b12] text-slate-400 text-[10px] uppercase border-b border-surface-border">
                                            <tr>
                                                <th className="py-2.5 px-3">Port</th>
                                                <th className="py-2.5 px-3">Protocol</th>
                                                <th className="py-2.5 px-3">Service</th>
                                                <th className="py-2.5 px-3">Product / Version</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-surface-border/60">
                                            {scan.nmap.ports.map((port) => (
                                                <tr key={port.port} className="hover:bg-surface-light/40 transition-colors">
                                                    <td className="py-2.5 px-3 font-bold text-blue-400">{port.port}</td>
                                                    <td className="py-2.5 px-3 uppercase text-slate-400">{port.protocol}</td>
                                                    <td className="py-2.5 px-3 font-semibold text-white">{port.service}</td>
                                                    <td className="py-2.5 px-3 text-slate-400">{port.version || '-'}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Vulnerabilities Tab */}
                    {activeTab === 'vulnerabilities' && (
                        <div className="space-y-4">
                            {/* Filters Bar */}
                            <div className="flex flex-col sm:flex-row gap-2">
                                <select
                                    value={severityFilter}
                                    onChange={(e) => setSeverityFilter(e.target.value)}
                                    className="input sm:w-44"
                                >
                                    <option value="all">All Severities</option>
                                    <option value="critical">Critical</option>
                                    <option value="high">High</option>
                                    <option value="medium">Medium</option>
                                    <option value="low">Low</option>
                                    <option value="info">Info</option>
                                </select>

                                <div className="relative flex-1">
                                    <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
                                    <input
                                        type="text"
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                        placeholder="Search findings by CVE, name, or template ID..."
                                        className="input pl-8"
                                    />
                                </div>
                            </div>

                            {/* Vulnerabilities List */}
                            <div className="space-y-2">
                                {filteredVulnerabilities.length === 0 ? (
                                    <div className="text-center py-10 text-slate-500">
                                        <Shield className="w-8 h-8 mx-auto mb-2 opacity-30 text-emerald-400" />
                                        <p className="text-xs font-mono">No vulnerabilities matching current filters.</p>
                                    </div>
                                ) : (
                                    filteredVulnerabilities.map((vuln, index) => (
                                        <div 
                                            key={index} 
                                            className="border border-surface-border rounded bg-[#070b12] overflow-hidden"
                                        >
                                            <button
                                                onClick={() => setExpandedVulnIndex(expandedVulnIndex === index ? null : index)}
                                                className="w-full px-3.5 py-2.5 flex items-center justify-between hover:bg-surface-light transition-colors text-left"
                                            >
                                                <div className="flex items-center gap-2.5 flex-wrap">
                                                    <SeverityBadge severity={vuln.severity} />
                                                    <span className="font-semibold text-xs text-white">{vuln.name}</span>
                                                    {vuln.cve && (
                                                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-red-950/80 text-red-300 border border-red-800">
                                                            {vuln.cve}
                                                        </span>
                                                    )}
                                                    <span className="text-[10px] font-mono text-slate-500">
                                                        [{vuln.template_id}]
                                                    </span>
                                                </div>
                                                <ChevronDown
                                                    className={`w-4 h-4 text-slate-400 transition-transform ${expandedVulnIndex === index ? 'rotate-180' : ''}`}
                                                />
                                            </button>

                                            {expandedVulnIndex === index && (
                                                <div className="p-3.5 bg-surface border-t border-surface-border space-y-3 text-xs">
                                                    <div>
                                                        <div className="text-[10px] font-mono uppercase font-semibold text-slate-400 mb-1">Description</div>
                                                        <p className="text-slate-300 leading-relaxed font-sans">{vuln.description || 'No description available for this template.'}</p>
                                                    </div>

                                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] font-mono">
                                                        <div>
                                                            <span className="text-slate-500 block">Template ID:</span>
                                                            <code className="text-slate-200">{vuln.template_id}</code>
                                                        </div>
                                                        {vuln.matcher_name && (
                                                            <div>
                                                                <span className="text-slate-500 block">Matcher Name:</span>
                                                                <code className="text-slate-200">{vuln.matcher_name}</code>
                                                            </div>
                                                        )}
                                                        {vuln.cvss && (
                                                            <div>
                                                                <span className="text-slate-500 block">CVSS Score:</span>
                                                                <span className="font-bold text-amber-400">{vuln.cvss}</span>
                                                            </div>
                                                        )}
                                                    </div>

                                                    {vuln.references && vuln.references.length > 0 && (
                                                        <div>
                                                            <div className="text-[10px] font-mono uppercase font-semibold text-slate-400 mb-1">External References</div>
                                                            <ul className="space-y-1">
                                                                {vuln.references.map((ref, i) => (
                                                                    <li key={i}>
                                                                        <a
                                                                            href={ref}
                                                                            target="_blank"
                                                                            rel="noopener noreferrer"
                                                                            className="text-[11px] font-mono text-blue-400 hover:underline flex items-center gap-1"
                                                                        >
                                                                            <span className="truncate max-w-lg">{ref}</span>
                                                                            <ExternalLink className="w-3 h-3 shrink-0" />
                                                                        </a>
                                                                    </li>
                                                                ))}
                                                            </ul>
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    )}

                    {/* Live Console Tab */}
                    {activeTab === 'terminal' && (
                        <LiveTerminal 
                            scanId={scan.scan_id} 
                            isScanActive={scan.status === 'running'} 
                        />
                    )}

                    {/* Raw JSON Tab */}
                    {activeTab === 'raw' && (
                        <div className="relative">
                            <pre className="bg-[#05080e] p-3 rounded border border-surface-border overflow-x-auto text-[11px] font-mono text-slate-300 max-h-[500px]">
                                {JSON.stringify(scan, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>
            </div>

            {/* Report Export Modal */}
            <ReportExportModal
                scanId={scan.scan_id}
                target={scan.target}
                isOpen={showReportModal}
                onClose={() => setShowReportModal(false)}
            />
        </div>
    );
}
