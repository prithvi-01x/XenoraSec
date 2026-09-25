import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
    Play, 
    AlertCircle, 
    CheckCircle2, 
    Globe, 
    Server, 
    Link2, 
    Network,
    Layers,
    ChevronDown, 
    ChevronUp, 
    Tag, 
    Sliders,
    Info,
    Terminal
} from 'lucide-react';
import { useStartScan, useStartBatchScan, useScanTemplates } from '../hooks/useApi';
import { validateTarget, parseBatchTargetsPreview } from '../utils/helpers';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ScanProfileSelector } from './ScanProfileSelector';
import { BatchProgressModal } from './BatchProgressModal';
import type { ScanProfile, ScanTiming, ScanOptions } from '../types/api';

const DEFAULT_POPULAR_TAGS = [
    { id: 'cve', label: 'CVE Database' },
    { id: 'rce', label: 'Remote Code Exec' },
    { id: 'misconfig', label: 'Misconfigurations' },
    { id: 'exposure', label: 'Information Exposure' },
    { id: 'sqli', label: 'SQL Injection' },
    { id: 'xss', label: 'Cross-Site Scripting' },
    { id: 'default-login', label: 'Default Credentials' },
    { id: 'auth-bypass', label: 'Auth Bypass' },
    { id: 'tech', label: 'Tech Stack Fingerprinting' },
    { id: 'ssl', label: 'SSL / TLS Security' },
];

const CIDR_PRESETS = [
    { label: '/30 (2 hosts)', snippet: '192.168.1.0/30' },
    { label: '/29 (6 hosts)', snippet: '192.168.1.0/29' },
    { label: '/28 (14 hosts)', snippet: '192.168.1.0/28' },
    { label: '/24 (254 hosts)', snippet: '192.168.1.0/24' },
];

export function ScanPanel() {
    const [scanMode, setScanMode] = useState<'single' | 'batch'>('single');
    const [target, setTarget] = useState('');
    const [rawBatchTargets, setRawBatchTargets] = useState('');
    const [profile, setProfile] = useState<ScanProfile>('quick');
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [submitError, setSubmitError] = useState('');
    const [activeBatchId, setActiveBatchId] = useState<string | null>(null);

    // Custom options state
    const [customPorts, setCustomPorts] = useState('');
    const [timing, setTiming] = useState<ScanTiming>('normal');
    const [serviceDetection, setServiceDetection] = useState(true);
    const [osDetection, setOsDetection] = useState(false);
    const [selectedTags, setSelectedTags] = useState<string[]>(['cve', 'misconfig']);

    const navigate = useNavigate();
    const startScan = useStartScan();
    const startBatchScan = useStartBatchScan();
    const { data: templatesData } = useScanTemplates();

    const availableTags = templatesData?.tags?.length
        ? templatesData.tags.map((t) => ({ id: t.id, label: t.name }))
        : DEFAULT_POPULAR_TAGS;

    const singleValidation = useMemo(() => {
        if (!target.trim()) return null;
        return validateTarget(target);
    }, [target]);

    const batchPreview = useMemo(() => {
        if (scanMode !== 'batch') return null;
        return parseBatchTargetsPreview(rawBatchTargets);
    }, [scanMode, rawBatchTargets]);

    const toggleTag = (tagId: string) => {
        setSelectedTags((prev) =>
            prev.includes(tagId) ? prev.filter((t) => t !== tagId) : [...prev, tagId]
        );
    };

    const handleInsertCidrPreset = (snippet: string) => {
        if (scanMode === 'single') {
            setTarget(snippet);
        } else {
            setRawBatchTargets((prev) => (prev.trim() ? `${prev.trim()}\n${snippet}` : snippet));
        }
        setSubmitError('');
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitError('');

        const options: ScanOptions = {};
        if (customPorts.trim()) {
            options.ports = customPorts.trim();
        }
        if (timing) {
            options.timing = timing;
        }
        options.service_detection = serviceDetection;
        options.os_detection = osDetection;
        if (selectedTags.length > 0) {
            options.tags = selectedTags;
        }

        const scanOptions = profile === 'custom' || showAdvanced ? options : undefined;

        if (scanMode === 'batch') {
            if (!rawBatchTargets.trim()) {
                setSubmitError('Please enter at least one target or CIDR subnet');
                return;
            }
            if (batchPreview?.invalidTokens && batchPreview.invalidTokens.length > 0) {
                setSubmitError(`Invalid target(s): ${batchPreview.invalidTokens.slice(0, 3).join(', ')}`);
                return;
            }

            try {
                const res = await startBatchScan.mutateAsync({
                    raw_targets: rawBatchTargets.trim(),
                    scan_profile: profile,
                    options: scanOptions,
                    batch_name: `Batch Scan (${batchPreview?.totalEstimatedHosts || 0} hosts)`,
                });
                setActiveBatchId(res.batch_id);
            } catch (err: unknown) {
                if (axios.isAxiosError(err)) {
                    const detail = (err.response?.data as { detail?: string } | undefined)?.detail;
                    setSubmitError(detail || 'Failed to start batch scan');
                } else {
                    setSubmitError('Failed to start batch scan');
                }
            }
            return;
        }

        // Single target validation
        const res = validateTarget(target);
        if (!res.valid) {
            setSubmitError(res.error || 'Invalid target');
            return;
        }

        // Auto-route CIDR target to batch scan
        if (res.targetType === 'cidr') {
            try {
                const batchRes = await startBatchScan.mutateAsync({
                    raw_targets: target.trim(),
                    scan_profile: profile,
                    options: scanOptions,
                    batch_name: `CIDR Subnet (${target.trim()})`,
                });
                setActiveBatchId(batchRes.batch_id);
            } catch (err: unknown) {
                if (axios.isAxiosError(err)) {
                    const detail = (err.response?.data as { detail?: string } | undefined)?.detail;
                    setSubmitError(detail || 'Failed to start CIDR scan');
                } else {
                    setSubmitError('Failed to start CIDR scan');
                }
            }
            return;
        }

        try {
            const result = await startScan.mutateAsync({
                target: target.trim(),
                scan_profile: profile,
                options: scanOptions,
            });
            navigate(`/scan/${result.scan_id}`);
        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                if (err.response?.status === 429) {
                    setSubmitError('Rate limit exceeded. Please wait before launching another scan.');
                } else if (err.response?.status === 503) {
                    setSubmitError('Scan worker queue is currently full. Please try again shortly.');
                } else {
                    const detail = (err.response?.data as { detail?: string } | undefined)?.detail;
                    setSubmitError(detail || 'Failed to start scan');
                }
            } else {
                setSubmitError('Failed to start scan');
            }
        }
    };

    const getTargetBadge = () => {
        if (!singleValidation) return null;
        if (singleValidation.valid) {
            const icons = {
                ipv4: <Server className="w-3 h-3" />,
                ipv6: <Server className="w-3 h-3" />,
                domain: <Globe className="w-3 h-3" />,
                url: <Link2 className="w-3 h-3" />,
                localhost: <Server className="w-3 h-3" />,
                cidr: <Network className="w-3 h-3" />,
            };
            const labels = {
                ipv4: 'IPv4 Host',
                ipv6: 'IPv6 Host',
                domain: 'Domain Host',
                url: 'Web Service (URL)',
                localhost: 'Localhost',
                cidr: `CIDR Subnet (~${singleValidation.hostCount || 0} hosts)`,
            };
            const type = singleValidation.targetType || 'domain';
            return (
                <span className="inline-flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/80">
                    <CheckCircle2 className="w-3 h-3" />
                    {icons[type]}
                    <span>{labels[type]}</span>
                </span>
            );
        }
        return (
            <span className="inline-flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950/60 text-amber-400 border border-amber-800/80">
                <AlertCircle className="w-3 h-3" />
                <span>Format checking...</span>
            </span>
        );
    };

    const isPending = startScan.isPending || startBatchScan.isPending;

    return (
        <div className="card space-y-5">
            {/* Header with Scan Mode Toggle */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-surface-border pb-4">
                <div>
                    <div className="flex items-center gap-2">
                        <Terminal className="w-4 h-4 text-blue-400" />
                        <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                            Dispatch Security Assessment
                        </h2>
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">
                        Target enumeration, port scanning (Nmap), and template-based vulnerability matching (Nuclei).
                    </p>
                </div>

                <div className="inline-flex p-0.5 bg-[#070b12] border border-surface-border rounded shrink-0 self-start sm:self-auto">
                    <button
                        type="button"
                        onClick={() => {
                            setScanMode('single');
                            setSubmitError('');
                        }}
                        className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-semibold transition-all ${
                            scanMode === 'single'
                                ? 'bg-surface-light text-white shadow-sm border border-surface-border'
                                : 'text-slate-400 hover:text-white'
                        }`}
                    >
                        <Server className="w-3.5 h-3.5" />
                        Single Host
                    </button>
                    <button
                        type="button"
                        onClick={() => {
                            setScanMode('batch');
                            setSubmitError('');
                        }}
                        className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-semibold transition-all ${
                            scanMode === 'batch'
                                ? 'bg-surface-light text-white shadow-sm border border-surface-border'
                                : 'text-slate-400 hover:text-white'
                        }`}
                    >
                        <Layers className="w-3.5 h-3.5" />
                        Batch / CIDR
                    </button>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
                {/* Target input */}
                <div>
                    <div className="flex items-center justify-between mb-1.5">
                        <label htmlFor="target" className="block text-[11px] font-mono uppercase font-semibold text-slate-400">
                            {scanMode === 'single' ? 'Target Host or Endpoint' : 'Batch Hostnames, IPs & Subnets'}
                        </label>
                        {scanMode === 'single' && getTargetBadge()}
                        {scanMode === 'batch' && batchPreview && (
                            <span className="inline-flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950/60 text-blue-400 border border-blue-800">
                                <Network className="w-3 h-3" />
                                <span>~{batchPreview.totalEstimatedHosts} hosts ({batchPreview.rawCount} lines)</span>
                            </span>
                        )}
                    </div>

                    {scanMode === 'single' ? (
                        <div className="relative">
                            <input
                                id="target"
                                type="text"
                                value={target}
                                onChange={(e) => {
                                    setTarget(e.target.value);
                                    if (submitError) setSubmitError('');
                                }}
                                placeholder="e.g. scanme.nmap.org, 192.168.1.1, https://target.app"
                                className={`input text-xs py-2 ${
                                    singleValidation && !singleValidation.valid && target.trim().length > 3
                                        ? 'border-amber-500/60 focus:border-amber-400'
                                        : ''
                                }`}
                                disabled={isPending}
                            />
                        </div>
                    ) : (
                        <textarea
                            id="batch-targets"
                            rows={3}
                            value={rawBatchTargets}
                            onChange={(e) => {
                                setRawBatchTargets(e.target.value);
                                if (submitError) setSubmitError('');
                            }}
                            placeholder="Enter IP addresses, hostnames, or subnets (one per line or comma-separated):&#10;192.168.1.0/28&#10;scanme.nmap.org&#10;10.0.0.1"
                            className="input text-xs leading-relaxed"
                            disabled={isPending}
                        />
                    )}

                    {/* Validation error hint */}
                    {scanMode === 'single' && singleValidation && !singleValidation.valid && target.trim().length > 3 && (
                        <p className="mt-1.5 text-[11px] font-mono text-amber-400 flex items-center gap-1">
                            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                            <span>{singleValidation.error}</span>
                        </p>
                    )}

                    {scanMode === 'batch' && batchPreview?.invalidTokens && batchPreview.invalidTokens.length > 0 && (
                        <p className="mt-1.5 text-[11px] font-mono text-amber-400 flex items-center gap-1">
                            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                            <span>Unrecognized target notation: {batchPreview.invalidTokens.slice(0, 3).join(', ')}</span>
                        </p>
                    )}

                    {/* CIDR Helper Chips */}
                    <div className="mt-2 flex flex-wrap items-center gap-1.5 text-[11px]">
                        <span className="text-slate-400 font-mono text-[10px]">Quick Presets:</span>
                        {CIDR_PRESETS.map((preset) => (
                            <button
                                key={preset.snippet}
                                type="button"
                                onClick={() => handleInsertCidrPreset(preset.snippet)}
                                className="px-2 py-0.5 rounded bg-[#070b12] border border-surface-border hover:border-blue-500 text-slate-300 hover:text-blue-400 transition-colors font-mono text-[10px]"
                            >
                                + {preset.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Profile Selector */}
                <ScanProfileSelector
                    selectedProfile={profile}
                    onSelectProfile={(p) => {
                        setProfile(p);
                        if (p === 'custom') {
                            setShowAdvanced(true);
                        }
                    }}
                    disabled={isPending}
                />

                {/* Advanced Options Accordion */}
                <div className="border border-surface-border rounded bg-[#070b12] overflow-hidden">
                    <button
                        type="button"
                        onClick={() => setShowAdvanced(!showAdvanced)}
                        className="w-full flex items-center justify-between px-3.5 py-2.5 text-xs font-mono uppercase font-semibold text-slate-300 hover:text-white hover:bg-surface-light transition-colors"
                    >
                        <div className="flex items-center gap-2">
                            <Sliders className="w-3.5 h-3.5 text-blue-400" />
                            <span>Advanced Engine &amp; Nuclei Policy</span>
                            {profile === 'custom' && (
                                <span className="text-[9px] font-mono bg-purple-950 text-purple-300 px-1.5 py-0.2 rounded border border-purple-800">
                                    Custom Active
                                </span>
                            )}
                        </div>
                        {showAdvanced ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                    </button>

                    {showAdvanced && (
                        <div className="p-3.5 border-t border-surface-border space-y-3.5 text-xs bg-surface/50">
                            {/* Ports & Timing */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-slate-300 font-mono text-[11px] mb-1">
                                        Custom Ports (Nmap -p)
                                    </label>
                                    <input
                                        type="text"
                                        value={customPorts}
                                        onChange={(e) => setCustomPorts(e.target.value)}
                                        placeholder="e.g. 80,443,8000-8080 or 1-65535"
                                        className="input"
                                    />
                                    <span className="text-[10px] text-slate-500 mt-1 block">
                                        Leave empty to use profile standard port list.
                                    </span>
                                </div>

                                <div>
                                    <label className="block text-slate-300 font-mono text-[11px] mb-1">
                                        Nmap Scan Timing
                                    </label>
                                    <select
                                        value={timing}
                                        onChange={(e) => setTiming(e.target.value as ScanTiming)}
                                        className="input bg-[#070b12]"
                                    >
                                        <option value="paranoid">T0 - Paranoid (IDS Evasion)</option>
                                        <option value="sneaky">T1 - Sneaky (Stealth / Slow)</option>
                                        <option value="polite">T2 - Polite (Low Bandwidth)</option>
                                        <option value="normal">T3 - Normal (Standard)</option>
                                        <option value="aggressive">T4 - Aggressive (Recommended)</option>
                                        <option value="insane">T5 - Insane (Fast Network)</option>
                                    </select>
                                </div>
                            </div>

                            {/* Service / OS Detection Flags */}
                            <div className="flex flex-wrap gap-4 pt-1">
                                <label className="flex items-center gap-2 cursor-pointer text-slate-300 text-xs">
                                    <input
                                        type="checkbox"
                                        checked={serviceDetection}
                                        onChange={(e) => setServiceDetection(e.target.checked)}
                                        className="rounded border-slate-700 text-blue-600 focus:ring-0 bg-[#070b12]"
                                    />
                                    <span>Enable Service Version Detection (-sV)</span>
                                </label>

                                <label className="flex items-center gap-2 cursor-pointer text-slate-300 text-xs">
                                    <input
                                        type="checkbox"
                                        checked={osDetection}
                                        onChange={(e) => setOsDetection(e.target.checked)}
                                        className="rounded border-slate-700 text-blue-600 focus:ring-0 bg-[#070b12]"
                                    />
                                    <span>Enable Operating System Fingerprinting (-O)</span>
                                </label>
                            </div>

                            {/* Nuclei Template Tags */}
                            <div className="pt-2 border-t border-surface-border">
                                <div className="flex items-center justify-between mb-2">
                                    <label className="text-slate-300 font-mono text-[11px] flex items-center gap-1.5">
                                        <Tag className="w-3.5 h-3.5 text-blue-400" />
                                        <span>Nuclei Vulnerability Tags ({selectedTags.length} enabled)</span>
                                    </label>
                                    <div className="space-x-2 text-[10px] font-mono">
                                        <button
                                            type="button"
                                            onClick={() => setSelectedTags(availableTags.map((t) => t.id))}
                                            className="text-blue-400 hover:underline"
                                        >
                                            Select All
                                        </button>
                                        <span className="text-slate-600">|</span>
                                        <button
                                            type="button"
                                            onClick={() => setSelectedTags([])}
                                            className="text-slate-400 hover:underline"
                                        >
                                            Clear
                                        </button>
                                    </div>
                                </div>

                                <div className="flex flex-wrap gap-1.5">
                                    {availableTags.map((t) => {
                                        const isSelected = selectedTags.includes(t.id);
                                        return (
                                            <button
                                                key={t.id}
                                                type="button"
                                                onClick={() => toggleTag(t.id)}
                                                className={`px-2 py-0.5 rounded text-[10px] font-mono transition-all border ${
                                                    isSelected
                                                        ? 'bg-blue-950/80 text-blue-300 border-blue-700 font-semibold'
                                                        : 'bg-[#070b12] text-slate-400 border-surface-border hover:border-slate-600'
                                                }`}
                                            >
                                                #{t.id}
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {submitError && (
                    <div className="flex items-center gap-2 p-3 bg-red-950/40 border border-red-800 text-red-300 rounded text-xs font-mono">
                        <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
                        <span>{submitError}</span>
                    </div>
                )}

                <div className="flex items-center justify-between pt-1">
                    <div className="hidden sm:flex items-center gap-1.5 text-[11px] font-mono text-slate-400">
                        <Info className="w-3.5 h-3.5 text-slate-500" />
                        <span>Results stream in real-time via SSE backend channel.</span>
                    </div>

                    <button
                        type="submit"
                        disabled={
                            isPending ||
                            (scanMode === 'single'
                                ? !target.trim() || (singleValidation !== null && !singleValidation.valid)
                                : !rawBatchTargets.trim())
                        }
                        className="btn btn-primary px-5 py-2 text-xs font-semibold uppercase tracking-wider ml-auto"
                    >
                        {isPending ? (
                            <>
                                <LoadingSpinner size="sm" />
                                <span>Queuing Scan Task...</span>
                            </>
                        ) : (
                            <>
                                <Play className="w-3.5 h-3.5 fill-current" />
                                <span>{scanMode === 'single' ? 'Launch Security Audit' : 'Execute Batch Assessment'}</span>
                            </>
                        )}
                    </button>
                </div>
            </form>

            {/* Batch Progress Modal */}
            {activeBatchId && (
                <BatchProgressModal
                    batchId={activeBatchId}
                    onClose={() => setActiveBatchId(null)}
                />
            )}
        </div>
    );
}
