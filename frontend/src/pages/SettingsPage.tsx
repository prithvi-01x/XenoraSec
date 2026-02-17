import { Info, RefreshCw } from 'lucide-react';
import { useQueueInfo, useHealth } from '../hooks/useApi';

export function SettingsPage() {
    const { data: queueInfo, isLoading: queueLoading, refetch: refetchQueue } = useQueueInfo();
    const { data: health, isLoading: healthLoading } = useHealth();

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold mb-2">Settings</h1>
                <p className="text-gray-400">Live backend configuration — read only</p>
            </div>

            {/* Info banner */}
            <div className="card bg-primary/10 border-primary/30">
                <div className="flex items-start gap-3">
                    <Info className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                    <div className="text-sm">
                        <p className="font-medium text-primary mb-1">Configuration is managed via environment variables</p>
                        <p className="text-gray-300">
                            To change these values, update your <code className="text-primary">.env</code> file (or Render environment variables)
                            and redeploy. Settings shown here reflect the live backend state.
                        </p>
                    </div>
                </div>
            </div>

            {/* Scan Queue */}
            <div className="card space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-xl font-semibold">Scan Queue</h2>
                    <button
                        onClick={() => refetchQueue()}
                        className="btn btn-secondary btn-sm flex items-center gap-2"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Refresh
                    </button>
                </div>

                {queueLoading ? (
                    <p className="text-gray-400 text-sm">Loading...</p>
                ) : queueInfo ? (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-background rounded-lg p-4">
                            <div className="text-sm text-gray-400 mb-1">Scans Running</div>
                            <div className="text-2xl font-bold">{queueInfo.scans_running}</div>
                        </div>
                        <div className="bg-background rounded-lg p-4">
                            <div className="text-sm text-gray-400 mb-1">Max Concurrent</div>
                            <div className="text-2xl font-bold">{queueInfo.max_concurrent_scans}</div>
                            <div className="text-xs text-gray-500 mt-1">Set via MAX_CONCURRENT_SCANS</div>
                        </div>
                        <div className="bg-background rounded-lg p-4">
                            <div className="text-sm text-gray-400 mb-1">Available Slots</div>
                            <div className={`text-2xl font-bold ${queueInfo.available_slots === 0 ? 'text-danger' : 'text-success'}`}>
                                {queueInfo.available_slots}
                            </div>
                        </div>
                    </div>
                ) : (
                    <p className="text-gray-400 text-sm">Could not load queue info</p>
                )}
            </div>

            {/* Backend Info */}
            <div className="card space-y-4">
                <h2 className="text-xl font-semibold">Backend</h2>

                {healthLoading ? (
                    <p className="text-gray-400 text-sm">Loading...</p>
                ) : health ? (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-background rounded-lg p-4">
                            <div className="text-sm text-gray-400 mb-1">Status</div>
                            <div className={`text-lg font-bold capitalize ${health.status === 'healthy' ? 'text-success' : 'text-danger'}`}>
                                {health.status}
                            </div>
                        </div>
                        <div className="bg-background rounded-lg p-4">
                            <div className="text-sm text-gray-400 mb-1">Version</div>
                            <div className="text-lg font-bold">{health.version}</div>
                        </div>
                        <div className="bg-background rounded-lg p-4">
                            <div className="text-sm text-gray-400 mb-1">Uptime</div>
                            <div className="text-lg font-bold">
                                {health.uptime ? `${Math.floor(health.uptime / 60)}m ${Math.floor(health.uptime % 60)}s` : 'N/A'}
                            </div>
                        </div>
                    </div>
                ) : (
                    <p className="text-gray-400 text-sm">Could not load backend health</p>
                )}
            </div>

            {/* Key env vars reference */}
            <div className="card space-y-4">
                <h2 className="text-xl font-semibold">Key Environment Variables</h2>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-gray-700">
                                <th className="text-left py-2 px-3 text-gray-400">Variable</th>
                                <th className="text-left py-2 px-3 text-gray-400">Description</th>
                                <th className="text-left py-2 px-3 text-gray-400">Default</th>
                            </tr>
                        </thead>
                        <tbody className="text-gray-300">
                            {[
                                ['NMAP_TIMEOUT', 'Nmap phase timeout (seconds)', '300'],
                                ['NUCLEI_TIMEOUT', 'Nuclei phase timeout (seconds)', '480'],
                                ['GLOBAL_SCAN_TIMEOUT', 'Hard limit for entire scan (seconds)', '600'],
                                ['MAX_CONCURRENT_SCANS', 'Max simultaneous scans', '3'],
                                ['RATE_LIMIT_PER_MINUTE', 'API requests per minute per IP', '10'],
                                ['ALLOW_PRIVATE_IP_SCANNING', 'Allow scanning private IPs', 'false'],
                                ['ALLOW_LOCALHOST_SCANNING', 'Allow scanning localhost', 'false'],
                                ['CLEANUP_SECRET', 'Secret to enable /cleanup endpoint', 'unset (disabled)'],
                            ].map(([key, desc, def]) => (
                                <tr key={key} className="border-b border-gray-700/50">
                                    <td className="py-2 px-3 font-mono text-primary">{key}</td>
                                    <td className="py-2 px-3">{desc}</td>
                                    <td className="py-2 px-3 text-gray-400">{def}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
