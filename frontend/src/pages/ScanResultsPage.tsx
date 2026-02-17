import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useScanResults, useRetryScan, useDeleteScan, useCancelScan } from '../hooks/useApi';
import { LoadingState } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';
import { RiskScore } from '../components/RiskScore';
import { StatusBadge } from '../components/StatusBadge';
import { SeverityBadge } from '../components/SeverityBadge';
import { formatDuration, formatDate } from '../utils/helpers';
import { RefreshCw, Trash2, ChevronDown, ExternalLink, XCircle } from 'lucide-react';
import type { Vulnerability } from '../types/api';

export function ScanResultsPage() {
    const { scanId } = useParams<{ scanId: string }>();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<'summary' | 'ports' | 'vulnerabilities' | 'raw'>('summary');
    const [expandedVulnIndex, setExpandedVulnIndex] = useState<number | null>(null);
    const [severityFilter, setSeverityFilter] = useState<string>('all');
    const [searchTerm, setSearchTerm] = useState('');
    const [deleteConfirm, setDeleteConfirm] = useState(false);

    // Polling is now handled inside useScanResults via refetchInterval
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

    if (isLoading) return <LoadingState message="Loading scan results..." />;
    if (error) return <ErrorState message="Failed to load scan results" onRetry={refetch} />;
    if (!scan) return null;

    const filteredVulnerabilities = scan.nuclei.vulnerabilities.filter((vuln: Vulnerability) => {
        const matchesSeverity = severityFilter === 'all' || vuln.severity === severityFilter;
        const matchesSearch = !searchTerm ||
            vuln.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            vuln.description?.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesSeverity && matchesSearch;
    });

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div>
                    <h1 className="text-3xl font-bold mb-2">{scan.target}</h1>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                        <span>ID: {scan.scan_id.substring(0, 8)}...</span>
                        <span>Created: {formatDate(scan.created_at)}</span>
                        {scan.duration && <span>Duration: {formatDuration(scan.duration)}</span>}
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {/* Cancel button — only visible while running */}
                    {scan.status === 'running' && (
                        <button
                            onClick={handleCancel}
                            disabled={cancelScan.isPending}
                            className="btn btn-secondary flex items-center gap-2"
                        >
                            <XCircle className="w-4 h-4" />
                            {cancelScan.isPending ? 'Cancelling...' : 'Cancel'}
                        </button>
                    )}
                    {(scan.status === 'failed' || scan.status === 'timeout') && (
                        <button
                            onClick={handleRetry}
                            disabled={retryScan.isPending}
                            className="btn btn-secondary flex items-center gap-2"
                        >
                            <RefreshCw className="w-4 h-4" />
                            Retry
                        </button>
                    )}
                    {/* Inline delete confirmation — no more browser confirm() */}
                    {deleteConfirm ? (
                        <div className="flex items-center gap-2">
                            <span className="text-sm text-danger">Sure?</span>
                            <button
                                onClick={handleDelete}
                                disabled={deleteScan.isPending}
                                className="btn btn-danger btn-sm"
                            >
                                Yes, Delete
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
                            className="btn btn-danger flex items-center gap-2"
                        >
                            <Trash2 className="w-4 h-4" />
                            Delete
                        </button>
                    )}
                </div>
            </div>

            {/* Running indicator */}
            {scan.status === 'running' && (
                <div className="flex items-center gap-3 p-4 bg-primary/10 border border-primary/30 rounded-lg">
                    <div className="w-3 h-3 rounded-full bg-primary animate-pulse" />
                    <span className="text-sm text-primary font-medium">
                        Scan in progress — results will appear automatically when complete
                    </span>
                </div>
            )}

            {/* Executive Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="card flex flex-col items-center justify-center">
                    <RiskScore score={scan.risk_score} size="lg" />
                </div>

                <div className="card">
                    <div className="text-sm text-gray-400 mb-2">Status</div>
                    <StatusBadge status={scan.status} className="text-base" />
                    {scan.error && (
                        <p className="mt-2 text-sm text-danger">{scan.error}</p>
                    )}
                </div>

                <div className="card">
                    <div className="text-sm text-gray-400 mb-2">Vulnerabilities</div>
                    <div className="text-3xl font-bold">{scan.summary.total_vulnerabilities}</div>
                    <div className="mt-2 text-sm text-gray-400">
                        {scan.summary.critical_count} critical, {scan.summary.high_count} high
                    </div>
                </div>

                <div className="card">
                    <div className="text-sm text-gray-400 mb-2">Open Ports</div>
                    <div className="text-3xl font-bold">{scan.summary.open_ports}</div>
                </div>
            </div>

            {/* Tabs */}
            <div className="card">
                <div className="border-b border-gray-700 mb-6">
                    <div className="flex gap-4">
                        {(['summary', 'ports', 'vulnerabilities', 'raw'] as const).map((tab) => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={`px-4 py-3 font-medium capitalize transition-colors border-b-2 ${activeTab === tab
                                    ? 'border-primary text-primary'
                                    : 'border-transparent text-gray-400 hover:text-gray-300'
                                    }`}
                            >
                                {tab}
                                {tab === 'vulnerabilities' && scan.summary.total_vulnerabilities > 0 && (
                                    <span className="ml-2 text-xs bg-danger/20 text-danger px-1.5 py-0.5 rounded-full">
                                        {scan.summary.total_vulnerabilities}
                                    </span>
                                )}
                                {tab === 'ports' && scan.summary.open_ports > 0 && (
                                    <span className="ml-2 text-xs bg-primary/20 text-primary px-1.5 py-0.5 rounded-full">
                                        {scan.summary.open_ports}
                                    </span>
                                )}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Summary Tab */}
                {activeTab === 'summary' && (
                    <div className="space-y-6">
                        <div>
                            <h3 className="text-lg font-semibold mb-4">Severity Distribution</h3>
                            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                                {Object.entries(scan.summary.severity_distribution).map(([severity, count]) => (
                                    <div key={severity} className="card bg-background">
                                        <div className="text-sm text-gray-400 mb-1 capitalize">{severity}</div>
                                        <div className="text-2xl font-bold">{count}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div>
                            <h3 className="text-lg font-semibold mb-4">Top Ports</h3>
                            <div className="flex flex-wrap gap-2">
                                {scan.nmap.ports.slice(0, 10).map((port) => (
                                    <span key={port.port} className="badge badge-info">
                                        {port.port}/{port.protocol} ({port.service})
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* Ports Tab */}
                {activeTab === 'ports' && (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-700">
                                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Port</th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Protocol</th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Service</th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Version</th>
                                </tr>
                            </thead>
                            <tbody>
                                {scan.nmap.ports.map((port) => (
                                    <tr key={port.port} className="border-b border-gray-700/50">
                                        <td className="py-3 px-4 font-mono font-bold">{port.port}</td>
                                        <td className="py-3 px-4">{port.protocol}</td>
                                        <td className="py-3 px-4">{port.service}</td>
                                        <td className="py-3 px-4 text-gray-400">{port.version || 'N/A'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {/* Vulnerabilities Tab */}
                {activeTab === 'vulnerabilities' && (
                    <div className="space-y-4">
                        {/* Filters */}
                        <div className="flex gap-4">
                            <select
                                value={severityFilter}
                                onChange={(e) => setSeverityFilter(e.target.value)}
                                className="input w-48"
                            >
                                <option value="all">All Severities</option>
                                <option value="critical">Critical</option>
                                <option value="high">High</option>
                                <option value="medium">Medium</option>
                                <option value="low">Low</option>
                                <option value="info">Info</option>
                            </select>

                            <input
                                type="text"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                placeholder="Search vulnerabilities..."
                                className="input flex-1"
                            />
                        </div>

                        {/* Vulnerabilities List */}
                        <div className="space-y-3">
                            {filteredVulnerabilities.length === 0 ? (
                                <p className="text-center text-gray-400 py-8">No vulnerabilities found</p>
                            ) : (
                                filteredVulnerabilities.map((vuln, index) => (
                                    <div key={index} className="border border-gray-700 rounded-lg overflow-hidden">
                                        <button
                                            onClick={() => setExpandedVulnIndex(expandedVulnIndex === index ? null : index)}
                                            className="w-full px-4 py-3 flex items-center justify-between hover:bg-surface-light transition-colors"
                                        >
                                            <div className="flex items-center gap-3">
                                                <SeverityBadge severity={vuln.severity} />
                                                <span className="font-medium">{vuln.name}</span>
                                                {vuln.cve && (
                                                    <span className="text-xs text-gray-400 font-mono">{vuln.cve}</span>
                                                )}
                                            </div>
                                            <ChevronDown
                                                className={`w-5 h-5 transition-transform ${expandedVulnIndex === index ? 'rotate-180' : ''}`}
                                            />
                                        </button>

                                        {expandedVulnIndex === index && (
                                            <div className="px-4 py-3 bg-background border-t border-gray-700 space-y-3">
                                                <div>
                                                    <div className="text-sm font-medium text-gray-400 mb-1">Description</div>
                                                    <p className="text-sm">{vuln.description || 'No description available'}</p>
                                                </div>

                                                <div>
                                                    <div className="text-sm font-medium text-gray-400 mb-1">Template ID</div>
                                                    <code className="text-sm font-mono">{vuln.template_id}</code>
                                                </div>

                                                {vuln.matcher_name && (
                                                    <div>
                                                        <div className="text-sm font-medium text-gray-400 mb-1">Matcher</div>
                                                        <code className="text-sm font-mono">{vuln.matcher_name}</code>
                                                    </div>
                                                )}

                                                {vuln.cvss && (
                                                    <div>
                                                        <div className="text-sm font-medium text-gray-400 mb-1">CVSS Score</div>
                                                        <span className="text-sm font-bold">{vuln.cvss}</span>
                                                    </div>
                                                )}

                                                {vuln.references && vuln.references.length > 0 && (
                                                    <div>
                                                        <div className="text-sm font-medium text-gray-400 mb-1">References</div>
                                                        <ul className="space-y-1">
                                                            {vuln.references.map((ref, i) => (
                                                                <li key={i}>
                                                                    <a
                                                                        href={ref}
                                                                        target="_blank"
                                                                        rel="noopener noreferrer"
                                                                        className="text-sm text-primary hover:text-primary-dark flex items-center gap-1"
                                                                    >
                                                                        {ref}
                                                                        <ExternalLink className="w-3 h-3" />
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

                {/* Raw JSON Tab */}
                {activeTab === 'raw' && (
                    <pre className="bg-background p-4 rounded-lg overflow-x-auto text-sm">
                        {JSON.stringify(scan, null, 2)}
                    </pre>
                )}
            </div>
        </div>
    );
}

