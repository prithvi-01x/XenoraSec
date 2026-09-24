import { useState } from 'react';
import { 
    Server, 
    Search, 
    AlertTriangle, 
    Shield, 
    RefreshCw, 
    Trash2, 
    Play, 
    X, 
    Globe, 
    Filter,
    Edit3,
    Check
} from 'lucide-react';
import { 
    useAssets, 
    useAssetStats, 
    useAssetDetail, 
    useUpdateAsset, 
    useDeleteAsset, 
    useScanAsset 
} from '../hooks/useApi';
import { SeverityBadge } from '../components/SeverityBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { getRiskColor, formatDate } from '../utils/helpers';
import type { AssetItem, AssetCriticality, AssetStatus, Severity } from '../types/api';

export function AssetInventoryPage() {
    const [search, setSearch] = useState('');
    const [assetType, setAssetType] = useState<string>('');
    const [criticality, setCriticality] = useState<string>('');
    const [selectedAssetId, setSelectedAssetId] = useState<number | null>(null);

    const { data: statsData } = useAssetStats();
    const { data: assetsData, isLoading, refetch } = useAssets({
        search: search.trim() || undefined,
        asset_type: assetType || undefined,
        criticality: criticality || undefined,
        limit: 50,
    });

    const deleteAsset = useDeleteAsset();
    const scanAsset = useScanAsset();

    const handleQuickScan = async (asset: AssetItem) => {
        try {
            await scanAsset.mutateAsync(asset.id);
            alert(`Scan initiated for ${asset.hostname || asset.ip_address}`);
        } catch {
            alert('Failed to launch scan for asset');
        }
    };

    const handleDelete = async (asset: AssetItem) => {
        if (confirm(`Remove asset ${asset.hostname || asset.ip_address} from inventory?`)) {
            await deleteAsset.mutateAsync(asset.id);
            if (selectedAssetId === asset.id) {
                setSelectedAssetId(null);
            }
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white flex items-center gap-2">
                        <Server className="w-7 h-7 text-primary" />
                        Asset Inventory
                    </h1>
                    <p className="text-sm text-gray-400 mt-1">
                        Consolidated attack surface registry, tracked IP endpoints, open ports, and live vulnerability exposures.
                    </p>
                </div>
                <button
                    onClick={() => refetch()}
                    className="btn btn-secondary flex items-center gap-2 text-xs self-start sm:self-auto"
                >
                    <RefreshCw className="w-3.5 h-3.5" />
                    Refresh Inventory
                </button>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card p-4 bg-surface border-gray-700/80">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold uppercase text-gray-400">Total Assets</span>
                        <Server className="w-4 h-4 text-primary" />
                    </div>
                    <div className="text-2xl font-bold text-white mt-2">
                        {statsData?.total_assets ?? 0}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                        {statsData?.active_assets ?? 0} active in registry
                    </div>
                </div>

                <div className="card p-4 bg-surface border-gray-700/80">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold uppercase text-gray-400">Critical / High Risk</span>
                        <AlertTriangle className="w-4 h-4 text-danger" />
                    </div>
                    <div className="text-2xl font-bold text-danger mt-2">
                        {statsData?.critical_risk_assets ?? 0}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">Risk score &ge; 7.0</div>
                </div>

                <div className="card p-4 bg-surface border-gray-700/80">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold uppercase text-gray-400">Discovered Ports</span>
                        <Shield className="w-4 h-4 text-cyber-blue" />
                    </div>
                    <div className="text-2xl font-bold text-white mt-2">
                        {statsData?.total_open_ports ?? 0}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">Across all indexed hosts</div>
                </div>

                <div className="card p-4 bg-surface border-gray-700/80">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold uppercase text-gray-400">Active Vulnerabilities</span>
                        <AlertTriangle className="w-4 h-4 text-amber-400" />
                    </div>
                    <div className="text-2xl font-bold text-amber-400 mt-2">
                        {statsData?.total_vulnerabilities ?? 0}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">Open findings requiring fix</div>
                </div>
            </div>

            {/* Filter & Search Bar */}
            <div className="card p-4 bg-surface border-gray-700 flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
                <div className="relative flex-1">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search assets by IP address or hostname..."
                        className="input pl-9 text-xs py-2 w-full"
                    />
                </div>

                <div className="flex flex-wrap items-center gap-2">
                    <div className="flex items-center gap-1.5 text-xs text-gray-400">
                        <Filter className="w-3.5 h-3.5 text-primary" />
                        <span>Filter:</span>
                    </div>

                    <select
                        value={assetType}
                        onChange={(e) => setAssetType(e.target.value)}
                        className="input text-xs py-1.5 px-2 bg-surface-light border-gray-700 text-gray-200"
                    >
                        <option value="">All Types</option>
                        <option value="ip">IPv4 / IPv6</option>
                        <option value="domain">Domain Host</option>
                        <option value="url">Web Service (URL)</option>
                        <option value="cidr_host">Subnet Host</option>
                    </select>

                    <select
                        value={criticality}
                        onChange={(e) => setCriticality(e.target.value)}
                        className="input text-xs py-1.5 px-2 bg-surface-light border-gray-700 text-gray-200"
                    >
                        <option value="">All Criticalities</option>
                        <option value="critical">Critical</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                    </select>
                </div>
            </div>

            {/* Assets Table */}
            <div className="card overflow-hidden p-0 border-gray-700">
                {isLoading ? (
                    <div className="p-12 text-center">
                        <LoadingSpinner size="lg" className="mx-auto mb-2" />
                        <p className="text-xs text-gray-400">Retrieving asset catalog...</p>
                    </div>
                ) : !assetsData?.items || assetsData.items.length === 0 ? (
                    <div className="p-12 text-center space-y-2">
                        <Server className="w-10 h-10 text-gray-600 mx-auto" />
                        <h3 className="text-base font-semibold text-white">No Assets Found</h3>
                        <p className="text-xs text-gray-400 max-w-sm mx-auto">
                            Scan a target or CIDR subnet from the dashboard to automatically register assets in your inventory.
                        </p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs">
                            <thead className="bg-surface-light/60 text-gray-400 uppercase tracking-wider text-[11px] border-b border-gray-700">
                                <tr>
                                    <th className="p-3.5 pl-4">Target / Host</th>
                                    <th className="p-3.5">Type</th>
                                    <th className="p-3.5">Risk Score</th>
                                    <th className="p-3.5">Open Ports</th>
                                    <th className="p-3.5">Vulnerabilities</th>
                                    <th className="p-3.5">Last Scanned</th>
                                    <th className="p-3.5 pr-4 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700/60 font-mono">
                                {assetsData.items.map((asset) => (
                                    <tr 
                                        key={asset.id} 
                                        className="hover:bg-surface-light/30 transition-colors cursor-pointer"
                                        onClick={() => setSelectedAssetId(asset.id)}
                                    >
                                        <td className="p-3.5 pl-4">
                                            <div className="flex items-center gap-2">
                                                {asset.asset_type === 'domain' || asset.asset_type === 'url' ? (
                                                    <Globe className="w-4 h-4 text-cyber-blue shrink-0" />
                                                ) : (
                                                    <Server className="w-4 h-4 text-gray-400 shrink-0" />
                                                )}
                                                <div>
                                                    <div className="text-white font-bold hover:text-primary transition-colors">
                                                        {asset.hostname || asset.ip_address}
                                                    </div>
                                                    {asset.hostname && asset.ip_address !== asset.hostname && (
                                                        <div className="text-[11px] text-gray-400 font-normal">
                                                            {asset.ip_address}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="p-3.5">
                                            <span className="px-2 py-0.5 rounded text-[10px] uppercase font-semibold bg-gray-700/60 text-gray-300">
                                                {asset.asset_type}
                                            </span>
                                        </td>
                                        <td className="p-3.5">
                                            <span className={`font-bold ${getRiskColor(asset.risk_score)}`}>
                                                {asset.risk_score.toFixed(1)} / 10
                                            </span>
                                        </td>
                                        <td className="p-3.5">
                                            <span className="font-semibold text-gray-300">
                                                {asset.open_ports_count} ports
                                            </span>
                                        </td>
                                        <td className="p-3.5">
                                            {asset.vulnerabilities_count > 0 ? (
                                                <div className="flex items-center gap-1.5 flex-wrap">
                                                    {asset.critical_count > 0 && (
                                                        <span className="px-1.5 py-0.5 rounded text-[10px] bg-red-500/20 text-red-400 font-bold border border-red-500/30">
                                                            {asset.critical_count} crit
                                                        </span>
                                                    )}
                                                    {asset.high_count > 0 && (
                                                        <span className="px-1.5 py-0.5 rounded text-[10px] bg-orange-500/20 text-orange-400 font-semibold border border-orange-500/30">
                                                            {asset.high_count} high
                                                        </span>
                                                    )}
                                                    {asset.medium_count > 0 && (
                                                        <span className="px-1.5 py-0.5 rounded text-[10px] bg-yellow-500/20 text-yellow-300 border border-yellow-500/30">
                                                            {asset.medium_count} med
                                                        </span>
                                                    )}
                                                </div>
                                            ) : (
                                                <span className="text-gray-500">None detected</span>
                                            )}
                                        </td>
                                        <td className="p-3.5 text-gray-400 font-sans text-[11px]">
                                            {asset.last_scanned_at ? formatDate(asset.last_scanned_at) : 'Never'}
                                        </td>
                                        <td className="p-3.5 pr-4 text-right" onClick={(e) => e.stopPropagation()}>
                                            <div className="flex items-center justify-end gap-1.5">
                                                <button
                                                    onClick={() => handleQuickScan(asset)}
                                                    className="p-1.5 rounded text-gray-400 hover:text-primary hover:bg-surface-light"
                                                    title="Launch Security Audit"
                                                >
                                                    <Play className="w-3.5 h-3.5" />
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(asset)}
                                                    className="p-1.5 rounded text-gray-400 hover:text-danger hover:bg-surface-light"
                                                    title="Delete Asset"
                                                >
                                                    <Trash2 className="w-3.5 h-3.5" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Asset Detail Drawer / Modal */}
            {selectedAssetId && (
                <AssetDetailModal
                    assetId={selectedAssetId}
                    onClose={() => setSelectedAssetId(null)}
                />
            )}
        </div>
    );
}

function AssetDetailModal({ assetId, onClose }: { assetId: number; onClose: () => void }) {
    const { data: asset, isLoading } = useAssetDetail(assetId);
    const updateAsset = useUpdateAsset();

    const [isEditing, setIsEditing] = useState(false);
    const [criticality, setCriticality] = useState<AssetCriticality>('medium');
    const [status, setStatus] = useState<AssetStatus>('active');
    const [notes, setNotes] = useState('');

    const handleSaveMetadata = async () => {
        await updateAsset.mutateAsync({
            assetId,
            data: {
                criticality,
                status,
                notes: notes.trim(),
            },
        });
        setIsEditing(false);
    };

    if (isLoading || !asset) {
        return (
            <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div className="bg-surface border border-gray-700 rounded-xl p-8 text-center max-w-sm w-full">
                    <LoadingSpinner size="lg" className="mx-auto mb-2" />
                    <p className="text-xs text-gray-300">Loading asset intelligence...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-surface border border-gray-700 rounded-xl shadow-2xl max-w-4xl w-full flex flex-col max-h-[90vh] overflow-hidden">
                {/* Header */}
                <div className="p-4 sm:p-6 border-b border-gray-700 flex items-center justify-between">
                    <div>
                        <div className="flex items-center gap-2">
                            <Server className="w-5 h-5 text-primary" />
                            <h3 className="font-bold text-white text-lg font-mono">
                                {asset.hostname || asset.ip_address}
                            </h3>
                            <span className="px-2 py-0.5 rounded text-[10px] uppercase font-semibold bg-gray-700 text-gray-300">
                                {asset.asset_type}
                            </span>
                        </div>
                        {asset.hostname && (
                            <p className="text-xs text-gray-400 font-mono mt-0.5">IP: {asset.ip_address}</p>
                        )}
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white p-1 rounded-lg hover:bg-surface-light"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-4 sm:p-6 overflow-y-auto space-y-6 flex-1 text-xs">
                    {/* Security Overview Grid */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        <div className="bg-surface-light p-3 rounded-lg border border-gray-700">
                            <span className="text-gray-400 block text-[11px]">Calculated Risk</span>
                            <span className={`text-base font-bold font-mono ${getRiskColor(asset.risk_score)}`}>
                                {asset.risk_score.toFixed(1)} / 10
                            </span>
                        </div>
                        <div className="bg-surface-light p-3 rounded-lg border border-gray-700">
                            <span className="text-gray-400 block text-[11px]">Criticality</span>
                            <span className="text-base font-bold text-white capitalize">
                                {asset.criticality}
                            </span>
                        </div>
                        <div className="bg-surface-light p-3 rounded-lg border border-gray-700">
                            <span className="text-gray-400 block text-[11px]">Discovered Ports</span>
                            <span className="text-base font-bold text-white font-mono">
                                {asset.open_ports_count}
                            </span>
                        </div>
                        <div className="bg-surface-light p-3 rounded-lg border border-gray-700">
                            <span className="text-gray-400 block text-[11px]">Vulnerabilities</span>
                            <span className="text-base font-bold text-amber-400 font-mono">
                                {asset.vulnerabilities_count}
                            </span>
                        </div>
                    </div>

                    {/* Metadata & Notes */}
                    <div className="bg-surface-light/40 border border-gray-700 rounded-lg p-4 space-y-3">
                        <div className="flex items-center justify-between">
                            <h4 className="font-semibold text-white uppercase tracking-wider text-[11px]">
                                Asset Metadata &amp; Notes
                            </h4>
                            {!isEditing ? (
                                <button
                                    onClick={() => {
                                        setCriticality(asset.criticality);
                                        setStatus(asset.status);
                                        setNotes(asset.notes || '');
                                        setIsEditing(true);
                                    }}
                                    className="flex items-center gap-1 text-primary hover:underline text-[11px]"
                                >
                                    <Edit3 className="w-3 h-3" /> Edit
                                </button>
                            ) : (
                                <button
                                    onClick={handleSaveMetadata}
                                    className="flex items-center gap-1 text-emerald-400 hover:underline text-[11px] font-semibold"
                                >
                                    <Check className="w-3 h-3" /> Save Changes
                                </button>
                            )}
                        </div>

                        {isEditing ? (
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                                <div>
                                    <label className="block text-gray-400 text-[10px] uppercase font-semibold mb-1">
                                        Criticality Tier
                                    </label>
                                    <select
                                        value={criticality}
                                        onChange={(e) => setCriticality(e.target.value as AssetCriticality)}
                                        className="input text-xs py-1.5"
                                    >
                                        <option value="low">Low</option>
                                        <option value="medium">Medium</option>
                                        <option value="high">High</option>
                                        <option value="critical">Critical</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-gray-400 text-[10px] uppercase font-semibold mb-1">
                                        Operational Status
                                    </label>
                                    <select
                                        value={status}
                                        onChange={(e) => setStatus(e.target.value as AssetStatus)}
                                        className="input text-xs py-1.5"
                                    >
                                        <option value="active">Active</option>
                                        <option value="inactive">Inactive</option>
                                        <option value="decommissioned">Decommissioned</option>
                                    </select>
                                </div>
                                <div className="sm:col-span-2">
                                    <label className="block text-gray-400 text-[10px] uppercase font-semibold mb-1">
                                        Asset Notes
                                    </label>
                                    <textarea
                                        rows={2}
                                        value={notes}
                                        onChange={(e) => setNotes(e.target.value)}
                                        placeholder="Add operational notes or business criticality details..."
                                        className="input text-xs"
                                    />
                                </div>
                            </div>
                        ) : (
                            <p className="text-gray-300 italic text-[11px]">
                                {asset.notes || 'No operational notes recorded.'}
                            </p>
                        )}
                    </div>

                    {/* Discovered Ports */}
                    <div className="space-y-2">
                        <h4 className="font-semibold text-white uppercase tracking-wider text-[11px]">
                            Discovered Open Ports ({asset.ports?.length || 0})
                        </h4>
                        {asset.ports && asset.ports.length > 0 ? (
                            <div className="border border-gray-700 rounded-lg overflow-hidden font-mono">
                                <table className="w-full text-left">
                                    <thead className="bg-surface-light text-gray-400 text-[10px] uppercase border-b border-gray-700">
                                        <tr>
                                            <th className="p-2.5">Port</th>
                                            <th className="p-2.5">Protocol</th>
                                            <th className="p-2.5">Service</th>
                                            <th className="p-2.5">Product &amp; Version</th>
                                            <th className="p-2.5">Last Seen</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-700/60">
                                        {asset.ports.map((p) => (
                                            <tr key={`${p.port}-${p.protocol}`} className="hover:bg-surface-light/40">
                                                <td className="p-2.5 text-primary font-bold">{p.port}</td>
                                                <td className="p-2.5 uppercase text-gray-400">{p.protocol}</td>
                                                <td className="p-2.5 text-white">{p.service || 'unknown'}</td>
                                                <td className="p-2.5 text-gray-300">
                                                    {[p.product, p.version].filter(Boolean).join(' ') || '-'}
                                                </td>
                                                <td className="p-2.5 text-gray-500 font-sans text-[10px]">
                                                    {p.last_seen ? formatDate(p.last_seen) : '-'}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <p className="text-gray-500">No open ports identified on this target.</p>
                        )}
                    </div>

                    {/* Discovered Vulnerabilities */}
                    <div className="space-y-2">
                        <h4 className="font-semibold text-white uppercase tracking-wider text-[11px]">
                            Discovered Vulnerabilities ({asset.vulnerabilities?.length || 0})
                        </h4>
                        {asset.vulnerabilities && asset.vulnerabilities.length > 0 ? (
                            <div className="space-y-2">
                                {asset.vulnerabilities.map((vuln) => (
                                    <div
                                        key={vuln.id || `${vuln.template_id}-${vuln.name}`}
                                        className="p-3 rounded-lg bg-surface-light border border-gray-700 flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                                    >
                                        <div className="space-y-1">
                                            <div className="flex items-center gap-2">
                                                <SeverityBadge severity={vuln.severity.toLowerCase() as Severity} className="text-[10px] py-0.5 px-2" />
                                                <span className="font-semibold text-white">{vuln.name}</span>
                                            </div>
                                            <div className="flex items-center gap-3 text-gray-400 text-[11px] font-mono">
                                                {vuln.cve && <span className="text-primary font-bold">{vuln.cve}</span>}
                                                {vuln.cvss && <span>CVSS {vuln.cvss}</span>}
                                                {vuln.matched_at && (
                                                    <span className="truncate max-w-xs">{vuln.matched_at}</span>
                                                )}
                                            </div>
                                        </div>
                                        <div className="text-[10px] text-gray-500 self-end sm:self-auto shrink-0 font-sans">
                                            {vuln.last_seen ? formatDate(vuln.last_seen) : ''}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500">No vulnerability findings recorded for this asset.</p>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-700 flex justify-end gap-2 bg-surface">
                    <button
                        onClick={onClose}
                        className="btn btn-secondary text-xs px-4 py-2"
                    >
                        Close Details
                    </button>
                </div>
            </div>
        </div>
    );
}
