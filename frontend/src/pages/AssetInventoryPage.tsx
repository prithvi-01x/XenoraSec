import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
    Check,
    CheckCircle2,
    AlertCircle
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
    const navigate = useNavigate();
    const [search, setSearch] = useState('');
    const [assetType, setAssetType] = useState<string>('');
    const [criticality, setCriticality] = useState<string>('');
    const [selectedAssetId, setSelectedAssetId] = useState<number | null>(null);
    const [actionNotice, setActionNotice] = useState<{ type: 'success' | 'error'; text: string; scanId?: string } | null>(null);
    const [pendingDeleteAsset, setPendingDeleteAsset] = useState<AssetItem | null>(null);

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
            const res = await scanAsset.mutateAsync(asset.id);
            setActionNotice({
                type: 'success',
                text: `Security scan initiated for ${asset.hostname || asset.ip_address}`,
                scanId: res.scan_id,
            });
            setTimeout(() => setActionNotice(null), 6000);
        } catch {
            setActionNotice({
                type: 'error',
                text: `Failed to initiate audit scan for ${asset.hostname || asset.ip_address}`,
            });
            setTimeout(() => setActionNotice(null), 6000);
        }
    };

    const confirmDelete = async () => {
        if (!pendingDeleteAsset) return;
        try {
            await deleteAsset.mutateAsync(pendingDeleteAsset.id);
            if (selectedAssetId === pendingDeleteAsset.id) {
                setSelectedAssetId(null);
            }
            setPendingDeleteAsset(null);
            setActionNotice({
                type: 'success',
                text: `Asset ${pendingDeleteAsset.hostname || pendingDeleteAsset.ip_address} purged from catalog.`,
            });
            setTimeout(() => setActionNotice(null), 5000);
        } catch {
            setActionNotice({
                type: 'error',
                text: 'Failed to delete asset from inventory.',
            });
            setTimeout(() => setActionNotice(null), 5000);
        }
    };

    return (
        <div className="space-y-5">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-surface-border pb-4">
                <div>
                    <h1 className="text-xl font-bold tracking-tight text-white font-mono uppercase flex items-center gap-2">
                        <Server className="w-5 h-5 text-blue-400" />
                        Asset Attack Surface Inventory
                    </h1>
                    <p className="text-xs text-slate-400 mt-0.5">
                        Consolidated target registry, exposed network ports, and live vulnerability disclosures.
                    </p>
                </div>
                <button
                    onClick={() => refetch()}
                    className="btn btn-secondary text-xs self-start sm:self-auto font-mono"
                >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Refresh Inventory</span>
                </button>
            </div>

            {/* In-app Action Notification Banner */}
            {actionNotice && (
                <div className={`p-3 rounded border text-xs font-mono flex items-center justify-between gap-2 transition-all ${
                    actionNotice.type === 'success' 
                        ? 'bg-emerald-950/60 border-emerald-800 text-emerald-300' 
                        : 'bg-rose-950/60 border-rose-800 text-rose-300'
                }`}>
                    <div className="flex items-center gap-2">
                        {actionNotice.type === 'success' ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        ) : (
                            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                        )}
                        <span>{actionNotice.text}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        {actionNotice.scanId && (
                            <button
                                onClick={() => navigate(`/scan/${actionNotice.scanId}`)}
                                className="px-2 py-0.5 bg-emerald-900/80 hover:bg-emerald-800 text-white rounded text-[10px] font-bold uppercase transition-colors"
                            >
                                View Live Scan &rarr;
                            </button>
                        )}
                        <button
                            onClick={() => setActionNotice(null)}
                            className="p-1 hover:text-white"
                            aria-label="Dismiss notice"
                        >
                            <X className="w-3.5 h-3.5" />
                        </button>
                    </div>
                </div>
            )}

            {/* KPI Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="card bg-surface p-3.5 border-surface-border">
                    <div className="flex items-center justify-between text-slate-400 text-[11px] font-mono uppercase">
                        <span>Indexed Assets</span>
                        <Server className="w-4 h-4 text-blue-400" />
                    </div>
                    <div className="text-2xl font-bold font-mono text-white mt-1.5">
                        {statsData?.total_assets ?? 0}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-1 font-mono">
                        {statsData?.active_assets ?? 0} active in registry
                    </div>
                </div>

                <div className="card bg-surface p-3.5 border-surface-border">
                    <div className="flex items-center justify-between text-slate-400 text-[11px] font-mono uppercase">
                        <span>Critical Threat Assets</span>
                        <AlertTriangle className="w-4 h-4 text-red-400" />
                    </div>
                    <div className="text-2xl font-bold font-mono text-red-400 mt-1.5">
                        {statsData?.critical_risk_assets ?? 0}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-1 font-mono">Risk score &ge; 7.0</div>
                </div>

                <div className="card bg-surface p-3.5 border-surface-border">
                    <div className="flex items-center justify-between text-slate-400 text-[11px] font-mono uppercase">
                        <span>Open Endpoints</span>
                        <Shield className="w-4 h-4 text-blue-400" />
                    </div>
                    <div className="text-2xl font-bold font-mono text-white mt-1.5">
                        {statsData?.total_open_ports ?? 0}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-1 font-mono">Fingerprinted ports</div>
                </div>

                <div className="card bg-surface p-3.5 border-surface-border">
                    <div className="flex items-center justify-between text-slate-400 text-[11px] font-mono uppercase">
                        <span>Active CVEs &amp; Flaws</span>
                        <AlertTriangle className="w-4 h-4 text-amber-400" />
                    </div>
                    <div className="text-2xl font-bold font-mono text-amber-400 mt-1.5">
                        {statsData?.total_vulnerabilities ?? 0}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-1 font-mono">Pending remediation</div>
                </div>
            </div>

            {/* Filter & Search Bar */}
            <div className="card p-3 bg-surface border-surface-border flex flex-col md:flex-row gap-2.5 items-stretch md:items-center justify-between">
                <div className="relative flex-1">
                    <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search assets by IP address or hostname..."
                        className="input pl-8 text-xs py-1.5"
                    />
                </div>

                <div className="flex flex-wrap items-center gap-2 font-mono">
                    <div className="flex items-center gap-1 text-[11px] text-slate-400">
                        <Filter className="w-3.5 h-3.5 text-blue-400" />
                        <span>Filter:</span>
                    </div>

                    <select
                        value={assetType}
                        onChange={(e) => setAssetType(e.target.value)}
                        className="input text-xs py-1 px-2 sm:w-36 bg-[#070b12]"
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
                        className="input text-xs py-1 px-2 sm:w-36 bg-[#070b12]"
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
            <div className="card p-0 overflow-hidden">
                {isLoading ? (
                    <div className="p-12 text-center">
                        <LoadingSpinner size="lg" className="mx-auto mb-2 text-blue-500" />
                        <p className="text-xs font-mono text-slate-400">Retrieving asset catalog...</p>
                    </div>
                ) : !assetsData?.items || assetsData.items.length === 0 ? (
                    <div className="p-12 text-center space-y-2 text-slate-500">
                        <Server className="w-8 h-8 mx-auto opacity-30 text-blue-400" />
                        <h3 className="text-xs font-mono font-bold uppercase text-white">No Assets Found</h3>
                        <p className="text-[11px] max-w-sm mx-auto">
                            Scan a host or CIDR subnet to automatically register discoveries in the inventory.
                        </p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs font-mono">
                            <thead className="bg-[#070b12] text-slate-400 uppercase text-[10px] border-b border-surface-border">
                                <tr>
                                    <th className="py-2.5 px-4 font-semibold">Target / Host</th>
                                    <th className="py-2.5 px-3 font-semibold">Type</th>
                                    <th className="py-2.5 px-3 font-semibold">Risk Posture</th>
                                    <th className="py-2.5 px-3 font-semibold">Open Ports</th>
                                    <th className="py-2.5 px-3 font-semibold">Vulnerabilities</th>
                                    <th className="py-2.5 px-3 font-semibold">Last Assessed</th>
                                    <th className="py-2.5 px-4 text-right font-semibold">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-surface-border/60">
                                {assetsData.items.map((asset) => (
                                    <tr 
                                        key={asset.id} 
                                        className="hover:bg-surface-light/40 transition-colors cursor-pointer"
                                        onClick={() => setSelectedAssetId(asset.id)}
                                    >
                                        <td className="py-2.5 px-4">
                                            <div className="flex items-center gap-2">
                                                {asset.asset_type === 'domain' || asset.asset_type === 'url' ? (
                                                    <Globe className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                                                ) : (
                                                    <Server className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                                                )}
                                                <div>
                                                    <div className="text-white font-bold hover:text-blue-400 transition-colors">
                                                        {asset.hostname || asset.ip_address}
                                                    </div>
                                                    {asset.hostname && asset.ip_address !== asset.hostname && (
                                                        <div className="text-[10px] text-slate-400 font-normal">
                                                            {asset.ip_address}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="py-2.5 px-3">
                                            <span className="px-1.5 py-0.2 rounded text-[9px] uppercase font-semibold bg-[#070b12] border border-surface-border text-slate-300">
                                                {asset.asset_type}
                                            </span>
                                        </td>
                                        <td className="py-2.5 px-3">
                                            <span className={`font-bold ${getRiskColor(asset.risk_score)}`}>
                                                {asset.risk_score.toFixed(1)} / 10
                                            </span>
                                        </td>
                                        <td className="py-2.5 px-3">
                                            <span className="font-semibold text-slate-300">
                                                {asset.open_ports_count} ports
                                            </span>
                                        </td>
                                        <td className="py-2.5 px-3">
                                            {asset.vulnerabilities_count > 0 ? (
                                                <div className="flex items-center gap-1 flex-wrap">
                                                    {asset.critical_count > 0 && (
                                                        <span className="px-1 py-0.2 rounded text-[9px] bg-red-950 text-red-300 font-bold border border-red-800">
                                                            {asset.critical_count} crit
                                                        </span>
                                                    )}
                                                    {asset.high_count > 0 && (
                                                        <span className="px-1 py-0.2 rounded text-[9px] bg-orange-950 text-orange-300 font-semibold border border-orange-800">
                                                            {asset.high_count} high
                                                        </span>
                                                    )}
                                                    {asset.medium_count > 0 && (
                                                        <span className="px-1 py-0.2 rounded text-[9px] bg-amber-950 text-amber-300 border border-amber-800">
                                                            {asset.medium_count} med
                                                        </span>
                                                    )}
                                                </div>
                                            ) : (
                                                <span className="text-slate-500 text-[11px]">Clean</span>
                                            )}
                                        </td>
                                        <td className="py-2.5 px-3 text-slate-400 font-sans text-[11px]">
                                            {asset.last_scanned_at ? formatDate(asset.last_scanned_at) : 'Never'}
                                        </td>
                                        <td className="py-2.5 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                                            <div className="flex items-center justify-end gap-1">
                                                <button
                                                    onClick={() => handleQuickScan(asset)}
                                                    className="p-1 rounded text-slate-400 hover:text-blue-400 hover:bg-surface-light"
                                                    title="Launch Security Audit"
                                                >
                                                    <Play className="w-3.5 h-3.5" />
                                                </button>
                                                <button
                                                    onClick={() => setPendingDeleteAsset(asset)}
                                                    className="p-1 rounded text-slate-400 hover:text-rose-400 hover:bg-surface-light"
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

            {/* In-app Purge Confirmation Dialog */}
            {pendingDeleteAsset && (
                <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-surface border border-rose-900/80 rounded-lg p-5 max-w-md w-full font-mono text-xs shadow-2xl space-y-4">
                        <div className="flex items-center gap-2.5 text-rose-400 border-b border-surface-border pb-3">
                            <AlertTriangle className="w-5 h-5 shrink-0" />
                            <h3 className="font-bold text-sm text-white uppercase tracking-tight">Confirm Asset Deletion</h3>
                        </div>
                        <p className="text-slate-300 font-sans leading-relaxed">
                            Are you sure you want to purge <strong className="text-white font-mono">{pendingDeleteAsset.hostname || pendingDeleteAsset.ip_address}</strong> from the asset inventory? Associated port maps and vulnerability records for this target will be removed.
                        </p>
                        <div className="flex items-center justify-end gap-2 pt-2 border-t border-surface-border">
                            <button
                                onClick={() => setPendingDeleteAsset(null)}
                                className="btn btn-secondary text-xs"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={confirmDelete}
                                disabled={deleteAsset.isPending}
                                className="btn btn-danger text-xs font-mono"
                            >
                                {deleteAsset.isPending ? 'Purging...' : 'Purge Target'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Asset Detail Drawer / Modal */}
            {selectedAssetId && (
                <AssetDetailModal
                    assetId={selectedAssetId}
                    onClose={() => setSelectedAssetId(null)}
                    onQuickScan={(asset) => {
                        setSelectedAssetId(null);
                        handleQuickScan(asset);
                    }}
                />
            )}
        </div>
    );
}

function AssetDetailModal({ 
    assetId, 
    onClose, 
    onQuickScan 
}: { 
    assetId: number; 
    onClose: () => void; 
    onQuickScan: (asset: AssetItem) => void; 
}) {
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
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div className="bg-surface border border-surface-border rounded-lg p-6 text-center max-w-sm w-full font-mono text-xs">
                    <LoadingSpinner size="lg" className="mx-auto mb-2 text-blue-500" />
                    <p className="text-slate-300">Loading asset intelligence...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-surface border border-surface-border rounded-lg shadow-2xl max-w-3xl w-full flex flex-col max-h-[85vh] overflow-hidden">
                {/* Header */}
                <div className="px-4 py-3 border-b border-surface-border flex items-center justify-between bg-[#070b12]">
                    <div className="flex items-center gap-2.5">
                        <Server className="w-4 h-4 text-blue-400" />
                        <div>
                            <div className="flex items-center gap-2">
                                <h3 className="font-bold text-white text-xs font-mono">
                                    {asset.hostname || asset.ip_address}
                                </h3>
                                <span className="px-1.5 py-0.2 rounded text-[9px] uppercase font-semibold bg-surface border border-surface-border text-slate-300 font-mono">
                                    {asset.asset_type}
                                </span>
                            </div>
                            {asset.hostname && (
                                <p className="text-[10px] text-slate-400 font-mono">IP: {asset.ip_address}</p>
                            )}
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-slate-400 hover:text-white p-1 rounded hover:bg-surface-light"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-4 overflow-y-auto space-y-4 flex-1 text-xs">
                    {/* Security Overview Grid */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono">
                        <div className="bg-[#070b12] p-2.5 rounded border border-surface-border">
                            <span className="text-slate-500 block text-[10px] uppercase">Risk Posture</span>
                            <span className={`text-sm font-bold ${getRiskColor(asset.risk_score)}`}>
                                {asset.risk_score.toFixed(1)} / 10
                            </span>
                        </div>
                        <div className="bg-[#070b12] p-2.5 rounded border border-surface-border">
                            <span className="text-slate-500 block text-[10px] uppercase">Criticality</span>
                            <span className="text-sm font-bold text-white capitalize">
                                {asset.criticality}
                            </span>
                        </div>
                        <div className="bg-[#070b12] p-2.5 rounded border border-surface-border">
                            <span className="text-slate-500 block text-[10px] uppercase">Open Ports</span>
                            <span className="text-sm font-bold text-white">
                                {asset.open_ports_count}
                            </span>
                        </div>
                        <div className="bg-[#070b12] p-2.5 rounded border border-surface-border">
                            <span className="text-slate-500 block text-[10px] uppercase">Vulnerabilities</span>
                            <span className="text-sm font-bold text-amber-400">
                                {asset.vulnerabilities_count}
                            </span>
                        </div>
                    </div>

                    {/* Metadata & Notes */}
                    <div className="bg-[#070b12] border border-surface-border rounded p-3 space-y-2">
                        <div className="flex items-center justify-between">
                            <h4 className="font-semibold text-white uppercase tracking-wider text-[10px] font-mono">
                                Asset Metadata &amp; Parameters
                            </h4>
                            {!isEditing ? (
                                <button
                                    onClick={() => {
                                        setCriticality(asset.criticality);
                                        setStatus(asset.status);
                                        setNotes(asset.notes || '');
                                        setIsEditing(true);
                                    }}
                                    className="flex items-center gap-1 text-blue-400 hover:underline text-[10px] font-mono"
                                >
                                    <Edit3 className="w-3 h-3" /> Edit Metadata
                                </button>
                            ) : (
                                <button
                                    onClick={handleSaveMetadata}
                                    className="flex items-center gap-1 text-emerald-400 hover:underline text-[10px] font-mono font-semibold"
                                >
                                    <Check className="w-3 h-3" /> Save Changes
                                </button>
                            )}
                        </div>

                        {isEditing ? (
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 font-mono">
                                <div>
                                    <label className="block text-slate-400 text-[10px] uppercase font-semibold mb-1">
                                        Criticality Tier
                                    </label>
                                    <select
                                        value={criticality}
                                        onChange={(e) => setCriticality(e.target.value as AssetCriticality)}
                                        className="input text-xs py-1"
                                    >
                                        <option value="low">Low</option>
                                        <option value="medium">Medium</option>
                                        <option value="high">High</option>
                                        <option value="critical">Critical</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-slate-400 text-[10px] uppercase font-semibold mb-1">
                                        Operational Status
                                    </label>
                                    <select
                                        value={status}
                                        onChange={(e) => setStatus(e.target.value as AssetStatus)}
                                        className="input text-xs py-1"
                                    >
                                        <option value="active">Active</option>
                                        <option value="inactive">Inactive</option>
                                        <option value="decommissioned">Decommissioned</option>
                                    </select>
                                </div>
                                <div className="sm:col-span-2">
                                    <label className="block text-slate-400 text-[10px] uppercase font-semibold mb-1">
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
                            <p className="text-slate-300 italic text-[11px] font-sans">
                                {asset.notes || 'No operational notes recorded for this asset.'}
                            </p>
                        )}
                    </div>

                    {/* Discovered Ports */}
                    <div className="space-y-1.5 font-mono">
                        <h4 className="font-semibold text-white uppercase tracking-wider text-[10px]">
                            Discovered Open Ports ({asset.ports?.length || 0})
                        </h4>
                        {asset.ports && asset.ports.length > 0 ? (
                            <div className="border border-surface-border rounded overflow-hidden">
                                <table className="w-full text-left text-[11px]">
                                    <thead className="bg-[#070b12] text-slate-400 text-[10px] uppercase border-b border-surface-border">
                                        <tr>
                                            <th className="py-2 px-2.5">Port</th>
                                            <th className="py-2 px-2.5">Protocol</th>
                                            <th className="py-2 px-2.5">Service</th>
                                            <th className="py-2 px-2.5">Product &amp; Version</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-surface-border/60">
                                        {asset.ports.map((p) => (
                                            <tr key={`${p.port}-${p.protocol}`} className="hover:bg-surface-light/40">
                                                <td className="py-1.5 px-2.5 text-blue-400 font-bold">{p.port}</td>
                                                <td className="py-1.5 px-2.5 uppercase text-slate-400">{p.protocol}</td>
                                                <td className="py-1.5 px-2.5 text-white">{p.service || 'unknown'}</td>
                                                <td className="py-1.5 px-2.5 text-slate-300">
                                                    {[p.product, p.version].filter(Boolean).join(' ') || '-'}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <p className="text-slate-500 text-[11px]">No open ports identified on this target.</p>
                        )}
                    </div>

                    {/* Discovered Vulnerabilities */}
                    <div className="space-y-1.5 font-mono">
                        <h4 className="font-semibold text-white uppercase tracking-wider text-[10px]">
                            Discovered Vulnerabilities ({asset.vulnerabilities?.length || 0})
                        </h4>
                        {asset.vulnerabilities && asset.vulnerabilities.length > 0 ? (
                            <div className="space-y-1.5">
                                {asset.vulnerabilities.map((vuln) => (
                                    <div
                                        key={vuln.id || `${vuln.template_id}-${vuln.name}`}
                                        className="p-2.5 rounded bg-[#070b12] border border-surface-border flex flex-col sm:flex-row sm:items-center justify-between gap-1.5"
                                    >
                                        <div className="space-y-0.5">
                                            <div className="flex items-center gap-2">
                                                <SeverityBadge severity={vuln.severity.toLowerCase() as Severity} className="text-[9px] py-0.2 px-1.5" />
                                                <span className="font-semibold text-white text-xs">{vuln.name}</span>
                                            </div>
                                            <div className="flex items-center gap-2 text-slate-400 text-[10px]">
                                                {vuln.cve && <span className="text-red-400 font-bold">{vuln.cve}</span>}
                                                {vuln.cvss && <span>CVSS {vuln.cvss}</span>}
                                                {vuln.matched_at && <span className="truncate max-w-xs">{vuln.matched_at}</span>}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-slate-500 text-[11px]">No vulnerability findings recorded for this asset.</p>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div className="px-4 py-2.5 border-t border-surface-border flex items-center justify-between bg-surface">
                    <button
                        onClick={() => onQuickScan(asset)}
                        className="btn btn-primary text-xs font-mono"
                    >
                        <Play className="w-3.5 h-3.5" />
                        <span>Launch Audit Scan</span>
                    </button>
                    <button
                        onClick={onClose}
                        className="btn btn-secondary text-xs"
                    >
                        Close Details
                    </button>
                </div>
            </div>
        </div>
    );
}
