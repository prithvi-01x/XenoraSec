import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    Search, 
    Globe, 
    Shield, 
    Server, 
    Network, 
    Layers, 
    Loader2, 
    History, 
    Clock, 
    AlertCircle,
    CheckCircle2,
    Radar,
    Terminal
} from 'lucide-react';
import { useStartRecon, useReconHistory, useImportSubdomains } from '../hooks/useApi';
import { SubdomainTable } from '../components/SubdomainTable';
import { DnsInspector } from '../components/DnsInspector';
import { TechStackGrid } from '../components/TechStackGrid';
import type { ReconResult, ReconRequest } from '../types/api';

export function ReconPage() {
    const navigate = useNavigate();
    const [targetInput, setTargetInput] = useState('');
    const [includeSubdomains, setIncludeSubdomains] = useState(true);
    const [resolveSubdomains, setResolveSubdomains] = useState(true);
    const [includeDns, setIncludeDns] = useState(true);
    const [includeTechStack, setIncludeTechStack] = useState(true);

    const [activeTab, setActiveTab] = useState<'subdomains' | 'dns' | 'tech'>('subdomains');
    const [reconResult, setReconResult] = useState<ReconResult | null>(null);
    const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

    const startReconMutation = useStartRecon();
    const importSubdomainsMutation = useImportSubdomains();
    const { data: historyData, refetch: refetchHistory } = useReconHistory({ limit: 5 });

    const handleRunRecon = async (e?: React.FormEvent) => {
        if (e) e.preventDefault();
        const trimmed = targetInput.trim();
        if (!trimmed) return;

        setNotification(null);
        try {
            const payload: ReconRequest = {
                domain: trimmed,
                include_subdomains: includeSubdomains,
                resolve_subdomains: resolveSubdomains,
                include_dns: includeDns,
                include_tech_stack: includeTechStack,
            };

            const result = await startReconMutation.mutateAsync(payload);
            setReconResult(result);
            refetchHistory();
            setNotification({
                type: 'success',
                message: `Passive reconnaissance completed for ${result.domain}. Discovered ${result.subdomains_count} subdomains.`,
            });
        } catch (err: unknown) {
            const errorMsg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Recon assessment failed. Check domain format and try again.';
            setNotification({
                type: 'error',
                message: errorMsg,
            });
        }
    };

    const handleImportSubdomains = async (selectedList?: string[]) => {
        if (!reconResult) return;
        setNotification(null);

        try {
            const res = await importSubdomainsMutation.mutateAsync({
                domain: reconResult.domain,
                data: {
                    subdomains: selectedList && selectedList.length > 0 ? selectedList : null,
                    target_status: 'active',
                    default_criticality: 'medium',
                    tags: ['recon-discovered', `domain:${reconResult.domain}`],
                },
            });

            setNotification({
                type: 'success',
                message: res.message || `Successfully imported ${res.imported_count} subdomains into Asset Inventory!`,
            });
        } catch {
            setNotification({
                type: 'error',
                message: 'Failed to import subdomains into Asset Inventory.',
            });
        }
    };

    const handleAuditTarget = (subdomain: string) => {
        // Navigate to Dashboard with target prefilled in URL or state
        navigate('/', { state: { prefillTarget: subdomain } });
    };

    const quickTargets = ['scanme.nmap.org', 'cloudflare.com', 'github.com', 'owasp.org'];

    return (
        <div className="space-y-6 pb-12 font-sans">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded bg-blue-950/80 border border-blue-800 text-blue-400 text-xs font-mono font-semibold">
                            OSINT & RECON EXPANSION
                        </span>
                        <span className="text-xs text-slate-500 font-mono">Module Option 3</span>
                    </div>
                    <h1 className="text-2xl font-bold tracking-tight text-white font-mono flex items-center gap-2.5 mt-1">
                        <Radar className="w-6 h-6 text-blue-500" />
                        Passive Reconnaissance Center
                    </h1>
                    <p className="text-xs text-slate-400 font-mono">
                        Non-intrusive Certificate Transparency log scraping, DNS topology map, and technology stack fingerprinting
                    </p>
                </div>
            </div>

            {/* Notification alert */}
            {notification && (
                <div className={`p-4 rounded-lg border flex items-center justify-between text-xs font-mono ${
                    notification.type === 'success' 
                        ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300' 
                        : 'bg-rose-950/40 border-rose-500/40 text-rose-300'
                }`}>
                    <div className="flex items-center gap-2">
                        {notification.type === 'success' ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        ) : (
                            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                        )}
                        <span>{notification.message}</span>
                    </div>
                    <button 
                        onClick={() => setNotification(null)}
                        className="text-slate-400 hover:text-white ml-2"
                    >
                        ×
                    </button>
                </div>
            )}

            {/* Target Search & Options Console */}
            <div className="bg-surface rounded-lg border border-surface-border p-5 space-y-4">
                <form onSubmit={handleRunRecon} className="space-y-4">
                    <div className="flex flex-col sm:flex-row items-center gap-3">
                        <div className="relative flex-1 w-full">
                            <Search className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                            <input
                                type="text"
                                placeholder="Enter apex or target domain (e.g., example.com, uber.com, tesla.com)..."
                                value={targetInput}
                                onChange={(e) => setTargetInput(e.target.value)}
                                className="w-full pl-10 pr-4 py-2.5 bg-[#090d16] border border-surface-border rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={startReconMutation.isPending || !targetInput.trim()}
                            className="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-mono font-semibold flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
                        >
                            {startReconMutation.isPending ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    <span>Gathering OSINT...</span>
                                </>
                            ) : (
                                <>
                                    <Radar className="w-4 h-4" />
                                    <span>Launch Passive Recon</span>
                                </>
                            )}
                        </button>
                    </div>

                    {/* Feature Toggles & Preset Badges */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pt-1 border-t border-surface-border text-xs font-mono">
                        <div className="flex items-center gap-4 flex-wrap text-slate-300">
                            <label className="flex items-center gap-2 cursor-pointer select-none">
                                <input
                                    type="checkbox"
                                    checked={includeSubdomains}
                                    onChange={(e) => setIncludeSubdomains(e.target.checked)}
                                    className="rounded border-slate-700 bg-slate-900 text-blue-600 focus:ring-blue-500"
                                />
                                <span>Certificate Logs (crt.sh)</span>
                            </label>
                            <label className="flex items-center gap-2 cursor-pointer select-none">
                                <input
                                    type="checkbox"
                                    checked={resolveSubdomains}
                                    onChange={(e) => setResolveSubdomains(e.target.checked)}
                                    className="rounded border-slate-700 bg-slate-900 text-blue-600 focus:ring-blue-500"
                                />
                                <span>Active IP Resolution</span>
                            </label>
                            <label className="flex items-center gap-2 cursor-pointer select-none">
                                <input
                                    type="checkbox"
                                    checked={includeDns}
                                    onChange={(e) => setIncludeDns(e.target.checked)}
                                    className="rounded border-slate-700 bg-slate-900 text-blue-600 focus:ring-blue-500"
                                />
                                <span>DNS & Mail Security</span>
                            </label>
                            <label className="flex items-center gap-2 cursor-pointer select-none">
                                <input
                                    type="checkbox"
                                    checked={includeTechStack}
                                    onChange={(e) => setIncludeTechStack(e.target.checked)}
                                    className="rounded border-slate-700 bg-slate-900 text-blue-600 focus:ring-blue-500"
                                />
                                <span>Passive Tech Fingerprint</span>
                            </label>
                        </div>

                        {/* Quick Presets */}
                        <div className="flex items-center gap-1.5 flex-wrap">
                            <span className="text-slate-500">Presets:</span>
                            {quickTargets.map((qt) => (
                                <button
                                    key={qt}
                                    type="button"
                                    onClick={() => setTargetInput(qt)}
                                    className="px-2 py-0.5 rounded bg-surface-light border border-surface-border text-slate-400 hover:text-white hover:border-slate-500 transition-colors"
                                >
                                    {qt}
                                </button>
                            ))}
                        </div>
                    </div>
                </form>
            </div>

            {/* Results Section */}
            {reconResult && (
                <div className="space-y-5 animate-in fade-in duration-300">
                    {/* Metrics Banner */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                        <div className="bg-surface rounded-lg border border-surface-border p-3.5 space-y-1">
                            <span className="text-[10px] font-mono uppercase text-slate-400">Total Subdomains</span>
                            <div className="text-xl font-bold font-mono text-white flex items-center gap-2">
                                <Globe className="w-5 h-5 text-blue-400" />
                                {reconResult.subdomains_count}
                            </div>
                        </div>

                        <div className="bg-surface rounded-lg border border-surface-border p-3.5 space-y-1">
                            <span className="text-[10px] font-mono uppercase text-slate-400">Active Resolving</span>
                            <div className="text-xl font-bold font-mono text-emerald-400 flex items-center gap-2">
                                <Server className="w-5 h-5 text-emerald-400" />
                                {reconResult.active_subdomains_count}
                            </div>
                        </div>

                        <div className="bg-surface rounded-lg border border-surface-border p-3.5 space-y-1">
                            <span className="text-[10px] font-mono uppercase text-slate-400">DNS Records</span>
                            <div className="text-xl font-bold font-mono text-white flex items-center gap-2">
                                <Network className="w-5 h-5 text-cyan-400" />
                                {reconResult.dns?.records?.length || 0}
                            </div>
                        </div>

                        <div className="bg-surface rounded-lg border border-surface-border p-3.5 space-y-1">
                            <span className="text-[10px] font-mono uppercase text-slate-400">Technologies</span>
                            <div className="text-xl font-bold font-mono text-purple-400 flex items-center gap-2">
                                <Layers className="w-5 h-5 text-purple-400" />
                                {reconResult.tech_stack?.all_technologies?.length || 0}
                            </div>
                        </div>

                        <div className="bg-surface rounded-lg border border-surface-border p-3.5 space-y-1 col-span-2 sm:col-span-1">
                            <span className="text-[10px] font-mono uppercase text-slate-400">Security Score</span>
                            <div className="text-xl font-bold font-mono text-blue-400 flex items-center gap-2">
                                <Shield className="w-5 h-5 text-blue-400" />
                                {reconResult.tech_stack?.security_score ?? 'N/A'}/100
                            </div>
                        </div>
                    </div>

                    {/* Navigation Tabs */}
                    <div className="flex items-center gap-2 border-b border-surface-border pb-1 font-mono text-xs">
                        <button
                            onClick={() => setActiveTab('subdomains')}
                            className={`px-4 py-2 rounded-t-lg transition-colors flex items-center gap-2 ${
                                activeTab === 'subdomains'
                                    ? 'bg-blue-600/20 text-blue-400 border-b-2 border-blue-500 font-semibold'
                                    : 'text-slate-400 hover:text-white'
                            }`}
                        >
                            <Globe className="w-3.5 h-3.5" />
                            <span>Subdomain Discovery ({reconResult.subdomains.length})</span>
                        </button>

                        <button
                            onClick={() => setActiveTab('dns')}
                            className={`px-4 py-2 rounded-t-lg transition-colors flex items-center gap-2 ${
                                activeTab === 'dns'
                                    ? 'bg-blue-600/20 text-blue-400 border-b-2 border-blue-500 font-semibold'
                                    : 'text-slate-400 hover:text-white'
                            }`}
                        >
                            <Network className="w-3.5 h-3.5" />
                            <span>DNS Map & Email Security</span>
                        </button>

                        <button
                            onClick={() => setActiveTab('tech')}
                            className={`px-4 py-2 rounded-t-lg transition-colors flex items-center gap-2 ${
                                activeTab === 'tech'
                                    ? 'bg-blue-600/20 text-blue-400 border-b-2 border-blue-500 font-semibold'
                                    : 'text-slate-400 hover:text-white'
                            }`}
                        >
                            <Layers className="w-3.5 h-3.5" />
                            <span>Tech Stack & Security Headers</span>
                        </button>
                    </div>

                    {/* Tab Panes */}
                    <div>
                        {activeTab === 'subdomains' && (
                            <SubdomainTable
                                subdomains={reconResult.subdomains}
                                domain={reconResult.domain}
                                onAuditTarget={handleAuditTarget}
                                onImportSelected={(selected) => handleImportSubdomains(selected)}
                                isImporting={importSubdomainsMutation.isPending}
                            />
                        )}

                        {activeTab === 'dns' && reconResult.dns && (
                            <DnsInspector dns={reconResult.dns} />
                        )}

                        {activeTab === 'tech' && reconResult.tech_stack && (
                            <TechStackGrid techStack={reconResult.tech_stack} />
                        )}
                    </div>
                </div>
            )}

            {/* Historical Recon Assessments */}
            {historyData && historyData.items.length > 0 && (
                <div className="bg-surface rounded-lg border border-surface-border p-5 space-y-3">
                    <div className="flex items-center justify-between text-xs font-mono">
                        <div className="flex items-center gap-2 text-slate-300 font-semibold">
                            <History className="w-4 h-4 text-blue-400" />
                            <span>Recent Recon Assessments</span>
                        </div>
                        <span className="text-slate-500">{historyData.total} total assessments</span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                        {historyData.items.map((item) => (
                            <button
                                key={item.id}
                                onClick={() => {
                                    setTargetInput(item.domain);
                                }}
                                className="p-3 rounded bg-[#070a11] border border-surface-border text-left hover:border-slate-500 transition-all font-mono space-y-1.5 group"
                            >
                                <div className="flex items-center justify-between">
                                    <span className="font-semibold text-slate-200 group-hover:text-blue-400 transition-colors text-xs truncate max-w-[180px]">
                                        {item.domain}
                                    </span>
                                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-blue-950 border border-blue-800 text-blue-400">
                                        Score {item.security_score}/100
                                    </span>
                                </div>
                                <div className="flex items-center justify-between text-[11px] text-slate-400">
                                    <span>{item.subdomains_count} subdomains</span>
                                    <span className="flex items-center gap-1 text-slate-500">
                                        <Clock className="w-3 h-3" />
                                        {item.duration}s
                                    </span>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
export default ReconPage;
