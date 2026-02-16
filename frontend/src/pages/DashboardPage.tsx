import { useDashboardStats } from '../hooks/useApi';
import { LoadingState } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';
import { ScanPanel } from '../components/ScanPanel';
import { Activity, TrendingUp, AlertTriangle, Shield } from 'lucide-react';
import { Link } from 'react-router-dom';
import { StatusBadge } from '../components/StatusBadge';
import { formatDate } from '../utils/helpers';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

export function DashboardPage() {
    const { data: stats, isLoading, error, refetch } = useDashboardStats();

    if (isLoading) return <LoadingState message="Loading dashboard..." />;
    if (error) return <ErrorState message="Failed to load dashboard" onRetry={refetch} />;
    if (!stats) return null;

    const severityData = [
        { name: 'Critical', value: stats.severity_distribution.critical || 0, color: '#dc2626' },
        { name: 'High', value: stats.severity_distribution.high || 0, color: '#f97316' },
        { name: 'Medium', value: stats.severity_distribution.medium || 0, color: '#eab308' },
        { name: 'Low', value: stats.severity_distribution.low || 0, color: '#22c55e' },
        { name: 'Info', value: stats.severity_distribution.info || 0, color: '#6b7280' },
    ];

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
                <p className="text-gray-400">Security scanning overview and controls</p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="card">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-400 text-sm">Total Scans</span>
                        <Activity className="w-5 h-5 text-primary" />
                    </div>
                    <div className="text-3xl font-bold">{stats.total_scans}</div>
                </div>

                <div className="card">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-400 text-sm">Running Scans</span>
                        <TrendingUp className="w-5 h-5 text-success" />
                    </div>
                    <div className="text-3xl font-bold text-success">{stats.running_scans}</div>
                </div>

                <div className="card">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-400 text-sm">Avg Risk Score</span>
                        <Shield className="w-5 h-5 text-warning" />
                    </div>
                    <div className="text-3xl font-bold text-warning">{stats.avg_risk.toFixed(1)}</div>
                </div>

                <div className="card">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-400 text-sm">Critical Findings</span>
                        <AlertTriangle className="w-5 h-5 text-danger" />
                    </div>
                    <div className="text-3xl font-bold text-danger">{stats.critical_findings}</div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Scan Panel */}
                <div className="lg:col-span-2">
                    <ScanPanel />
                </div>

                {/* Severity Distribution */}
                <div className="card">
                    <h3 className="text-lg font-semibold mb-4">Severity Distribution</h3>
                    <ResponsiveContainer width="100%" height={200}>
                        <PieChart>
                            <Pie
                                data={severityData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={2}
                                dataKey="value"
                            >
                                {severityData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1e293b',
                                    border: '1px solid #374151',
                                    borderRadius: '8px',
                                }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                    <div className="mt-4 space-y-2">
                        {severityData.map((item) => (
                            <div key={item.name} className="flex items-center justify-between text-sm">
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                                    <span className="text-gray-300">{item.name}</span>
                                </div>
                                <span className="font-medium">{item.value}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Recent Scans */}
            <div className="card">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold">Recent Scans</h3>
                    <Link to="/history" className="text-primary hover:text-primary-dark text-sm font-medium">
                        View All →
                    </Link>
                </div>

                {stats.recent_scans.length === 0 ? (
                    <p className="text-center text-gray-400 py-8">No scans yet</p>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-700">
                                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Target</th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Status</th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Risk Score</th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Created</th>
                                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {stats.recent_scans.map((scan) => (
                                    <tr key={scan.scan_id} className="border-b border-gray-700/50 hover:bg-surface-light">
                                        <td className="py-3 px-4 font-medium">{scan.target}</td>
                                        <td className="py-3 px-4">
                                            <StatusBadge status={scan.status} />
                                        </td>
                                        <td className="py-3 px-4">
                                            <span className="font-bold">{scan.risk_score.toFixed(1)}</span>
                                        </td>
                                        <td className="py-3 px-4 text-sm text-gray-400">{formatDate(scan.created_at)}</td>
                                        <td className="py-3 px-4">
                                            <Link
                                                to={`/scan/${scan.scan_id}`}
                                                className="text-primary hover:text-primary-dark text-sm font-medium"
                                            >
                                                View
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
