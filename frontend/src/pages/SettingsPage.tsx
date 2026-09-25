import { Info, RefreshCw, Cpu, Server, Shield, Lock } from 'lucide-react';
import { useQueueInfo, useHealth } from '../hooks/useApi';

export function SettingsPage() {
    const { data: queueInfo, isLoading: queueLoading, refetch: refetchQueue } = useQueueInfo();
    const { data: health, isLoading: healthLoading } = useHealth();

    return (
        <div className="space-y-5">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-surface-border pb-4">
                <div>
                    <h1 className="text-xl font-bold tracking-tight text-white font-mono uppercase flex items-center gap-2">
                        <Cpu className="w-5 h-5 text-blue-400" />
                        Engine Telemetry &amp; Parameters
                    </h1>
                    <p className="text-xs text-slate-400 mt-0.5">
                        Live scanner engine configuration, worker concurrency, and security environment parameters.
                    </p>
                </div>
                <div className="text-xs font-mono text-slate-400">
                    Mode: <span className="text-emerald-400 font-bold">Production Ready</span>
                </div>
            </div>

            {/* Read-only Notice */}
            <div className="p-3.5 bg-blue-950/30 border border-blue-800/60 rounded flex items-start gap-3">
                <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                <div className="text-xs font-sans text-slate-300">
                    <span className="font-semibold text-white block mb-0.5">Read-Only Environment Synchronization</span>
                    Configuration parameters are loaded directly from the backend process environment variables and container definitions.
                    To modify concurrency limits, timeouts, or network boundaries, adjust your <code className="text-blue-400 font-mono text-[11px]">.env</code> specification and restart the service.
                </div>
            </div>

            {/* Grid for Queue and Health */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Scan Queue Status */}
                <div className="card p-4 space-y-3">
                    <div className="flex items-center justify-between border-b border-surface-border pb-2.5">
                        <div className="flex items-center gap-2">
                            <Server className="w-4 h-4 text-blue-400" />
                            <h2 className="text-xs font-mono font-bold uppercase text-white tracking-wider">
                                Worker Queue Concurrency
                            </h2>
                        </div>
                        <button
                            onClick={() => refetchQueue()}
                            className="btn btn-secondary btn-sm"
                        >
                            <RefreshCw className="w-3 h-3" />
                            <span>Refresh</span>
                        </button>
                    </div>

                    {queueLoading ? (
                        <p className="text-xs font-mono text-slate-400 py-4">Polling queue telemetry...</p>
                    ) : queueInfo ? (
                        <div className="grid grid-cols-3 gap-2 text-center font-mono">
                            <div className="bg-[#070b12] p-2.5 rounded border border-surface-border">
                                <div className="text-[10px] text-slate-400 uppercase">Running</div>
                                <div className="text-xl font-bold text-white mt-1">{queueInfo.scans_running}</div>
                            </div>
                            <div className="bg-[#070b12] p-2.5 rounded border border-surface-border">
                                <div className="text-[10px] text-slate-400 uppercase">Max Tasks</div>
                                <div className="text-xl font-bold text-blue-400 mt-1">{queueInfo.max_concurrent_scans}</div>
                            </div>
                            <div className="bg-[#070b12] p-2.5 rounded border border-surface-border">
                                <div className="text-[10px] text-slate-400 uppercase">Slots Open</div>
                                <div className={`text-xl font-bold mt-1 ${queueInfo.available_slots === 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                                    {queueInfo.available_slots}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <p className="text-xs font-mono text-rose-400 py-4">Could not poll queue status.</p>
                    )}
                </div>

                {/* Health & Engine Status */}
                <div className="card p-4 space-y-3">
                    <div className="flex items-center justify-between border-b border-surface-border pb-2.5">
                        <div className="flex items-center gap-2">
                            <Shield className="w-4 h-4 text-emerald-400" />
                            <h2 className="text-xs font-mono font-bold uppercase text-white tracking-wider">
                                Backend Engine Status
                            </h2>
                        </div>
                        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/80 border border-emerald-800 px-1.5 py-0.5 rounded uppercase font-semibold">
                            {health?.status || 'HEALTHY'}
                        </span>
                    </div>

                    {healthLoading ? (
                        <p className="text-xs font-mono text-slate-400 py-4">Checking engine heartbeat...</p>
                    ) : health ? (
                        <div className="grid grid-cols-3 gap-2 text-center font-mono">
                            <div className="bg-[#070b12] p-2.5 rounded border border-surface-border">
                                <div className="text-[10px] text-slate-400 uppercase">Version</div>
                                <div className="text-sm font-bold text-white mt-1.5">{health.version}</div>
                            </div>
                            <div className="bg-[#070b12] p-2.5 rounded border border-surface-border">
                                <div className="text-[10px] text-slate-400 uppercase">Database</div>
                                <div className="text-sm font-bold text-blue-400 mt-1.5">SQLite / Async</div>
                            </div>
                            <div className="bg-[#070b12] p-2.5 rounded border border-surface-border">
                                <div className="text-[10px] text-slate-400 uppercase">Uptime</div>
                                <div className="text-sm font-bold text-emerald-400 mt-1.5">
                                    {health.uptime ? `${Math.floor(health.uptime / 60)}m ${Math.floor(health.uptime % 60)}s` : 'Active'}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <p className="text-xs font-mono text-rose-400 py-4">Could not verify backend status.</p>
                    )}
                </div>
            </div>

            {/* Environmental Parameters Table */}
            <div className="card p-0 overflow-hidden">
                <div className="px-4 py-3 border-b border-surface-border bg-[#070b12] flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Lock className="w-4 h-4 text-blue-400" />
                        <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-white">
                            Environment Security Policies &amp; Parameters
                        </h2>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-xs font-mono">
                        <thead className="bg-[#070b12] text-slate-400 text-[10px] uppercase border-b border-surface-border text-left">
                            <tr>
                                <th className="py-2.5 px-4 font-semibold">Environment Key</th>
                                <th className="py-2.5 px-4 font-semibold">Functional Description</th>
                                <th className="py-2.5 px-4 font-semibold">Default / Policy</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-surface-border/60">
                            {[
                                ['NMAP_TIMEOUT', 'Phase timeout threshold for port scan execution (seconds)', '180s'],
                                ['NUCLEI_TIMEOUT', 'Phase timeout threshold for vulnerability template scan (seconds)', '300s'],
                                ['GLOBAL_SCAN_TIMEOUT', 'Hard global ceiling for end-to-end target audit (seconds)', '600s'],
                                ['MAX_CONCURRENT_SCANS', 'Maximum parallel scans allocated to worker queue', '3 workers'],
                                ['RATE_LIMIT_PER_MINUTE', 'Per-IP request rate throttle across public endpoints', '10 req/min'],
                                ['ALLOW_PRIVATE_IP_SCANNING', 'Security gate permitting scans targeting RFC1918 addresses', 'false (Enforced)'],
                                ['ALLOW_LOCALHOST_SCANNING', 'Permit loopback / 127.0.0.1 reconnaissance', 'true (Configured)'],
                                ['DATABASE_URL', 'Persistent backend store connection URI', 'sqlite+aiosqlite:///./scans.db'],
                            ].map(([key, desc, def]) => (
                                <tr key={key} className="hover:bg-surface-light/40 transition-colors">
                                    <td className="py-2 px-4 text-blue-400 font-semibold">{key}</td>
                                    <td className="py-2 px-4 text-slate-300 font-sans text-xs">{desc}</td>
                                    <td className="py-2 px-4 text-slate-400">{def}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
