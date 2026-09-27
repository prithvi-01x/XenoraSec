import { useState, useMemo } from 'react';
import { 
    Search, 
    Filter, 
    Download, 
    ShieldAlert, 
    Globe, 
    ExternalLink, 
    CheckSquare, 
    Square, 
    Server
} from 'lucide-react';
import type { SubdomainRecord } from '../types/api';

interface SubdomainTableProps {
    subdomains: SubdomainRecord[];
    domain: string;
    onAuditTarget?: (subdomain: string) => void;
    onImportSelected?: (subdomains: string[]) => void;
    isImporting?: boolean;
}

export function SubdomainTable({
    subdomains,
    domain,
    onAuditTarget,
    onImportSelected,
    isImporting = false,
}: SubdomainTableProps) {
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive' | 'wildcard'>('all');
    const [selectedSubdomains, setSelectedSubdomains] = useState<Set<string>>(new Set());

    // Filter logic
    const filteredSubdomains = useMemo(() => {
        return subdomains.filter((sub) => {
            const matchesSearch = 
                sub.subdomain.toLowerCase().includes(searchTerm.toLowerCase()) ||
                sub.ip_addresses.some(ip => ip.includes(searchTerm));

            if (!matchesSearch) return false;

            if (statusFilter === 'active') return sub.is_active === true;
            if (statusFilter === 'inactive') return sub.is_active === false;
            if (statusFilter === 'wildcard') return sub.is_wildcard;

            return true;
        });
    }, [subdomains, searchTerm, statusFilter]);

    // Selection handlers
    const toggleSelectAll = () => {
        if (selectedSubdomains.size === filteredSubdomains.length) {
            setSelectedSubdomains(new Set());
        } else {
            setSelectedSubdomains(new Set(filteredSubdomains.map(s => s.subdomain)));
        }
    };

    const toggleSelectOne = (subdomain: string) => {
        const next = new Set(selectedSubdomains);
        if (next.has(subdomain)) {
            next.delete(subdomain);
        } else {
            next.add(subdomain);
        }
        setSelectedSubdomains(next);
    };

    // Export handler
    const handleExportJson = () => {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(subdomains, null, 2));
        const downloadAnchor = document.createElement('a');
        downloadAnchor.setAttribute("href", dataStr);
        downloadAnchor.setAttribute("download", `${domain}-subdomains-recon.json`);
        document.body.appendChild(downloadAnchor);
        downloadAnchor.click();
        downloadAnchor.remove();
    };

    const activeCount = subdomains.filter(s => s.is_active === true).length;

    return (
        <div className="bg-surface rounded-lg border border-surface-border p-5 space-y-4">
            {/* Header with stats and actions */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded bg-blue-600/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
                        <Globe className="w-4 h-4" />
                    </div>
                    <div>
                        <h3 className="text-sm font-semibold text-white font-mono flex items-center gap-2">
                            Discovered Subdomains
                            <span className="text-xs px-2 py-0.5 rounded-full bg-blue-950 border border-blue-800 text-blue-400 font-mono">
                                {subdomains.length} Total ({activeCount} Active)
                            </span>
                        </h3>
                        <p className="text-xs text-slate-400">Certificate Transparency logs and passive DNS records</p>
                    </div>
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                    {onImportSelected && (
                        <button
                            onClick={() => onImportSelected(Array.from(selectedSubdomains))}
                            disabled={isImporting || selectedSubdomains.size === 0}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-blue-600/20 border border-blue-500/40 text-blue-300 hover:bg-blue-600/30 text-xs font-mono font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            <Server className="w-3.5 h-3.5" />
                            <span>
                                {isImporting ? 'Importing...' : `Import to Assets (${selectedSubdomains.size})`}
                            </span>
                        </button>
                    )}

                    <button
                        onClick={handleExportJson}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-surface-light border border-surface-border text-slate-300 hover:text-white hover:border-slate-500 text-xs font-mono transition-all"
                    >
                        <Download className="w-3.5 h-3.5" />
                        <span>Export JSON</span>
                    </button>
                </div>
            </div>

            {/* Filter toolbar */}
            <div className="flex flex-col md:flex-row items-center gap-3">
                <div className="relative flex-1 w-full">
                    <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                        type="text"
                        placeholder="Search by subdomain name or IP address..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-9 pr-3 py-1.5 bg-[#090d16] border border-surface-border rounded text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
                    />
                </div>

                <div className="flex items-center gap-1.5 w-full md:w-auto">
                    <Filter className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    {(['all', 'active', 'inactive', 'wildcard'] as const).map((filter) => (
                        <button
                            key={filter}
                            onClick={() => setStatusFilter(filter)}
                            className={`px-2.5 py-1 rounded text-xs font-mono uppercase transition-colors ${
                                statusFilter === filter
                                    ? 'bg-blue-600/20 text-blue-400 border border-blue-500/40 font-semibold'
                                    : 'text-slate-400 hover:text-white hover:bg-surface-light border border-transparent'
                            }`}
                        >
                            {filter}
                        </button>
                    ))}
                </div>
            </div>

            {/* Subdomain records table */}
            <div className="overflow-x-auto border border-surface-border rounded bg-[#070a11]">
                <table className="w-full text-left text-xs font-mono border-collapse">
                    <thead>
                        <tr className="border-b border-surface-border bg-surface/80 text-slate-400 text-[11px] uppercase tracking-wider">
                            <th className="p-3 w-10 text-center">
                                <button
                                    onClick={toggleSelectAll}
                                    className="text-slate-400 hover:text-white"
                                    aria-label="Select all"
                                >
                                    {selectedSubdomains.size > 0 && selectedSubdomains.size === filteredSubdomains.length ? (
                                        <CheckSquare className="w-4 h-4 text-blue-400" />
                                    ) : (
                                        <Square className="w-4 h-4" />
                                    )}
                                </button>
                            </th>
                            <th className="p-3 font-semibold">Subdomain</th>
                            <th className="p-3 font-semibold">Resolved IP(s)</th>
                            <th className="p-3 font-semibold">Source</th>
                            <th className="p-3 font-semibold">Status</th>
                            <th className="p-3 font-semibold text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-surface-border/60">
                        {filteredSubdomains.length === 0 ? (
                            <tr>
                                <td colSpan={6} className="p-8 text-center text-slate-500">
                                    No subdomains matching filter criteria
                                </td>
                            </tr>
                        ) : (
                            filteredSubdomains.map((sub) => {
                                const isSelected = selectedSubdomains.has(sub.subdomain);

                                return (
                                    <tr 
                                        key={sub.subdomain}
                                        className={`hover:bg-blue-950/20 transition-colors ${
                                            isSelected ? 'bg-blue-950/30' : ''
                                        }`}
                                    >
                                        <td className="p-3 text-center">
                                            <button
                                                onClick={() => toggleSelectOne(sub.subdomain)}
                                                className="text-slate-400 hover:text-white"
                                            >
                                                {isSelected ? (
                                                    <CheckSquare className="w-4 h-4 text-blue-400" />
                                                ) : (
                                                    <Square className="w-4 h-4" />
                                                )}
                                            </button>
                                        </td>
                                        <td className="p-3">
                                            <div className="flex items-center gap-2">
                                                <span className="font-semibold text-slate-200">
                                                    {sub.subdomain}
                                                </span>
                                                {sub.is_wildcard && (
                                                    <span className="px-1.5 py-0.2 rounded bg-purple-950/80 border border-purple-800 text-purple-300 text-[10px]">
                                                        *.wildcard
                                                    </span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="p-3 text-slate-300">
                                            {sub.ip_addresses && sub.ip_addresses.length > 0 ? (
                                                <div className="flex flex-wrap gap-1">
                                                    {sub.ip_addresses.map((ip) => (
                                                        <span key={ip} className="px-1.5 py-0.5 rounded bg-surface border border-surface-border text-[11px] text-slate-300">
                                                            {ip}
                                                        </span>
                                                    ))}
                                                </div>
                                            ) : (
                                                <span className="text-slate-500 italic">Unresolved</span>
                                            )}
                                        </td>
                                        <td className="p-3">
                                            <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-400 text-[10px] uppercase">
                                                {sub.source}
                                            </span>
                                        </td>
                                        <td className="p-3">
                                            {sub.is_active === true ? (
                                                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-800/80 text-emerald-400 text-[11px]">
                                                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                                                    Active
                                                </span>
                                            ) : (
                                                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-400 text-[11px]">
                                                    <span className="w-1.5 h-1.5 rounded-full bg-slate-500" />
                                                    Inactive
                                                </span>
                                            )}
                                        </td>
                                        <td className="p-3 text-right">
                                            <div className="flex items-center justify-end gap-2">
                                                <a
                                                    href={`https://${sub.subdomain}`}
                                                    target="_blank"
                                                    rel="noreferrer"
                                                    className="p-1 rounded text-slate-400 hover:text-white hover:bg-surface-light transition-colors"
                                                    title="Open in new tab"
                                                >
                                                    <ExternalLink className="w-3.5 h-3.5" />
                                                </a>
                                                {onAuditTarget && (
                                                    <button
                                                        onClick={() => onAuditTarget(sub.subdomain)}
                                                        className="inline-flex items-center gap-1 px-2 py-1 rounded bg-blue-600/20 border border-blue-500/40 text-blue-400 hover:bg-blue-600/30 text-[11px] font-medium transition-colors"
                                                        title="Launch vulnerability audit"
                                                    >
                                                        <ShieldAlert className="w-3 h-3" />
                                                        <span>Audit</span>
                                                    </button>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })
                        )}
                    </tbody>
                </table>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-500 font-mono">
                <span>Showing {filteredSubdomains.length} of {subdomains.length} records</span>
                <span>{selectedSubdomains.size} selected</span>
            </div>
        </div>
    );
}
