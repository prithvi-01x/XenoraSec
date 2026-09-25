import { useDashboardStats, useQueueInfo } from '../hooks/useApi';
import { LoadingState } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';
import { ScanPanel } from '../components/ScanPanel';
import { 
    Activity, 
    AlertTriangle, 
    Shield, 
    Layers, 
    Clock, 
    ExternalLink, 
    ChevronRight,
    Flame
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { StatusBadge } from '../components/StatusBadge';
import { formatDate } from '../utils/helpers';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

export function DashboardPage() {
    const { data: stats, isLoading, error, refetch } = useDashboardStats();
    const { data: queueInfo } = useQueueInfo();

    if (isLoading) return <LoadingState message="Connecting to engine & compiling telemetry..." />;
    if (error) return <ErrorState message="Failed to load dashboard metrics" onRetry={refetch} />;
    if (!stats) return null;

    const severityData = [
        { name: 'Critical', value: stats.severity_distribution?.critical || 0, color: '#dc2626' },
        { name: 'High', value: stats.severity_distribution?.high || 0, color: '#f97316' },
        { name: 'Medium', value: stats.severity_distribution?.medium || 0, color: '#eab308' },
        { name: 'Low', value: stats.severity_distribution?.low || 0, color: '#10b981' },
        { name: 'Info', value: stats.severity_distribution?.info || 0, color: '#64748b' },
    ];

    const totalFindings = severityData.reduce((acc, curr) => acc + curr.value, 0);

    return (
        <div className="space-y-6">
            {/* Top Tactical Status Bar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-surface-border pb-4">
                <div>
                    <h1 className="text-xl font-bold tracking-tight text-white font-mono uppercase">
                        Security Operations &amp; Posture
                    </h1>
                    <p className="text-xs text-slate-400 mt-0.5">
                        Continuous network host discovery, port telemetry, and threat surface assessment.
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#070b12] border border-surface-border text-xs font-mono">
                        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                        <span className="text-slate-300">Queue Capacity:</span>
                        <span className="text-white font-bold">{queueInfo?.available_slots ?? 3} open</span>
                    </span>
                </div>
            </div>

            {/* Metrics KPI Row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <div className="card bg-surface p-3.5 border-surface-border">
                    <div className="flex items-center justify-between text-slate-400 text-[11px] font-mono uppercase">
                        <span>Cumulative Scans</span>
                        <Activity className="w-4 h-4 text-blue-400" />
                    </div>
                    <div className="text-2xl font-bold font-mono text-white mt-1.5">{stats.total_scans}</div>
                    <div className="text-[10px] text-slate-400 mt-1 flex items-center gap-1 font-mono">
                        <span className="text-blue-400">{stats.running_scans} in execution</span>
                    </div>
                </div>

                <div className="card bg-surface p-3.5 border-surface-border">
                    <div className="flex items-center justify-between text-slate-400 text-[11px] font-mono uppercase">
                        <span>Active Concurrency</span>
                        <Clock className="w-4 h-4 text-emerald-400" />
                    </div>
                    <div className="text-2xl font-bold font-mono text-emerald-400 mt-1.5">{stats.running_scans}</div>
                    <div className="text-[10px] text-slate-400 mt-1 font-mono">
                        <span>{queueInfo?.scans_running ?? 0} worker processes active</span>
                    </div>
                </div>

                <div className="card bg-surface p-3.5 border-surface-border">
                    <div className="flex items-center justify-between text-slate-400 text-[11px] font-mono uppercase">
                        <span>Mean Risk Posture</span>
                        <Shield className="w-4 h-4 text-amber-400" />
                    </div>
                    <div className="text-2xl font-bold font-mono text-amber-400 mt-1.5">
                        {stats.avg_risk.toFixed(1)} <span className="text-xs text-slate-500 font-normal">/ 10</span>
                    </div>
                    <div className="text-[10px] text-slate-400 mt-1 font-mono">
                        <span>Aggregated CVSS baseline</span>
                    </div>
                </div>

                <div className="card bg-surface p-3.5 border-surface-border">
                    <div className="flex items-center justify-between text-slate-400 text-[11px] font-mono uppercase">
                        <span>Critical Targets</span>
                        <Flame className="w-4 h-4 text-red-400" />
                    </div>
                    <div className="text-2xl font-bold font-mono text-red-400 mt-1.5">{stats.critical_findings}</div>
                    <div className="text-[10px] text-slate-400 mt-1 font-mono">
                        <span>Severe exposure risk &ge; 9.0</span>
                    </div>
                </div>
            </div>

            {/* Launch & Analytics Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
                {/* Scan Dispatch Panel */}
                <div className="lg:col-span-2">
                    <ScanPanel />
                </div>

                {/* Threat Distribution Chart */}
                <div className="card flex flex-col justify-between">
                    <div>
                        <div className="flex items-center justify-between border-b border-surface-border pb-3 mb-3">
                            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-white flex items-center gap-1.5">
                                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                                Exposure Distribution
                            </h3>
                            <span className="text-[10px] font-mono text-slate-400">
                                {totalFindings} findings
                            </span>
                        </div>

                        {totalFindings === 0 ? (
                            <div className="h-44 flex flex-col items-center justify-center text-center text-slate-500">
                                <Shield className="w-8 h-8 mb-2 opacity-30 text-blue-400" />
                                <p className="text-xs font-mono">No vulnerability records</p>
                                <p className="text-[10px] text-slate-600 mt-0.5">Run a scan to build telemetry</p>
                            </div>
                        ) : (
                            <div>
                                <ResponsiveContainer width="100%" height={160}>
                                    <PieChart>
                                        <Pie
                                            data={severityData}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={45}
                                            outerRadius={65}
                                            paddingAngle={3}
                                            dataKey="value"
                                        >
                                            {severityData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.color} stroke="#0e1526" strokeWidth={2} />
                                            ))}
                                        </Pie>
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: '#090d16',
                                                border: '1px solid #1e2c47',
                                                borderRadius: '4px',
                                                fontSize: '11px',
                                                fontFamily: 'monospace',
                                            }}
                                        />
                                    </PieChart>
                                </ResponsiveContainer>

                                <div className="space-y-1.5 mt-2 pt-2 border-t border-surface-border font-mono text-xs">
                                    {severityData.map((item) => (
                                        <div key={item.name} className="flex items-center justify-between py-0.5 text-slate-300">
                                            <div className="flex items-center gap-2">
                                                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                                                <span className="text-[11px] text-slate-400">{item.name}</span>
                                            </div>
                                            <span className="font-bold text-[11px]">{item.value}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="pt-3 border-t border-surface-border text-[10px] text-slate-400 font-mono mt-3 flex items-center justify-between">
                        <span>Database: scans.db</span>
                        <span className="text-blue-400">Nuclei v3 Engine</span>
                    </div>
                </div>
            </div>

            {/* Recent Scans Table */}
            <div className="card p-0 overflow-hidden">
                <div className="px-4 py-3 border-b border-surface-border flex items-center justify-between bg-[#070b12]">
                    <div className="flex items-center gap-2">
                        <Layers className="w-4 h-4 text-blue-400" />
                        <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-white">
                            Recent Scan Records
                        </h3>
                    </div>
                    <Link 
                        to="/history" 
                        className="text-xs font-mono text-blue-400 hover:text-blue-300 flex items-center gap-1 transition-colors"
                    >
                        <span>Full Audit Ledger</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                    </Link>
                </div>

                {stats.recent_scans.length === 0 ? (
                    <div className="text-center py-10 text-slate-500">
                        <Activity className="w-8 h-8 mx-auto mb-2 opacity-30 text-blue-400" />
                        <p className="text-xs font-mono">No scans recorded in database.</p>
                        <p className="text-[10px] text-slate-600 mt-0.5">Use the dispatch panel above to trigger your first target scan.</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs font-mono">
                            <thead className="bg-[#070b12] text-slate-400 text-[10px] uppercase border-b border-surface-border">
                                <tr>
                                    <th className="py-2.5 px-4 font-semibold">Target / Host</th>
                                    <th className="py-2.5 px-4 font-semibold">Status</th>
                                    <th className="py-2.5 px-4 font-semibold">Risk Posture</th>
                                    <th className="py-2.5 px-4 font-semibold">Recorded Time</th>
                                    <th className="py-2.5 px-4 font-semibold text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-surface-border/60">
                                {stats.recent_scans.map((scan) => (
                                    <tr key={scan.scan_id} className="hover:bg-surface-light/40 transition-colors">
                                        <td className="py-2.5 px-4">
                                            <div className="font-bold text-white hover:text-blue-400 transition-colors">
                                                <Link to={`/scan/${scan.scan_id}`}>{scan.target}</Link>
                                            </div>
                                            <div className="text-[10px] text-slate-500">ID: {scan.scan_id.substring(0, 8)}...</div>
                                        </td>
                                        <td className="py-2.5 px-4">
                                            <StatusBadge status={scan.status} className="text-[9px] py-0.5 px-1.5" />
                                        </td>
                                        <td className="py-2.5 px-4">
                                            <span className={`font-bold ${scan.risk_score >= 7 ? 'text-red-400' : scan.risk_score >= 4 ? 'text-amber-400' : 'text-slate-300'}`}>
                                                {scan.risk_score.toFixed(1)} / 10
                                            </span>
                                        </td>
                                        <td className="py-2.5 px-4 text-slate-400 text-[11px] font-sans">
                                            {formatDate(scan.created_at)}
                                        </td>
                                        <td className="py-2.5 px-4 text-right">
                                            <Link
                                                to={`/scan/${scan.scan_id}`}
                                                className="btn btn-secondary btn-sm"
                                            >
                                                <span>Inspect</span>
                                                <ExternalLink className="w-3 h-3" />
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}
