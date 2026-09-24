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
    Sliders 
} from 'lucide-react';
import { useStartScan, useStartBatchScan, useScanTemplates } from '../hooks/useApi';
import { validateTarget, parseBatchTargetsPreview } from '../utils/helpers';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ScanProfileSelector } from './ScanProfileSelector';
import { BatchProgressModal } from './BatchProgressModal';
import type { ScanProfile, ScanTiming, ScanOptions } from '../types/api';

const DEFAULT_POPULAR_TAGS = [
    { id: 'cve', label: 'CVE Database', category: 'cve' },
    { id: 'rce', label: 'Remote Code Exec', category: 'vulnerability' },
    { id: 'misconfig', label: 'Misconfigurations', category: 'misconfig' },
    { id: 'exposure', label: 'Information Exposure', category: 'exposure' },
    { id: 'sqli', label: 'SQL Injection', category: 'vulnerability' },
    { id: 'xss', label: 'Cross-Site Scripting', category: 'vulnerability' },
    { id: 'default-login', label: 'Default Logins', category: 'misconfig' },
    { id: 'auth-bypass', label: 'Auth Bypass', category: 'vulnerability' },
    { id: 'tech', label: 'Tech Detect', category: 'service' },
    { id: 'ssl', label: 'SSL / TLS Security', category: 'service' },
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
        ? templatesData.tags.map((t) => ({ id: t.id, label: t.name, category: t.category }))
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

        // If single target was actually a CIDR block, automatically launch it via batch API
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
                    setSubmitError('Rate limit exceeded. Please wait before starting another scan.');
                } else if (err.response?.status === 503) {
                    setSubmitError('Scan queue is full. Please try again later.');
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
                ipv4: <Server className="w-3.5 h-3.5" />,
                ipv6: <Server className="w-3.5 h-3.5" />,
                domain: <Globe className="w-3.5 h-3.5" />,
                url: <Link2 className="w-3.5 h-3.5" />,
                localhost: <Server className="w-3.5 h-3.5" />,
                cidr: <Network className="w-3.5 h-3.5" />,
            };
            const labels = {
                ipv4: 'IPv4 Address',
                ipv6: 'IPv6 Address',
                domain: 'Domain Host',
                url: 'Web URL',
                localhost: 'Localhost',
                cidr: `CIDR Subnet (~${singleValidation.hostCount || 0} hosts)`,
            };
            const type = singleValidation.targetType || 'domain';
            return (
                <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                    {icons[type]}
                    <span>{labels[type]}</span>
                </span>
            );
        }
        return (
            <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30">
                <AlertCircle className="w-3 h-3 text-amber-400" />
                <span>Format checking...</span>
            </span>
        );
    };

    const isPending = startScan.isPending || startBatchScan.isPending;

    return (
        <div className="card space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-1">Launch Security Audit</h2>
                    <p className="text-sm text-gray-400">
                        Multi-target network reconnaissance, CIDR subnet expansion, and AI risk synthesis.
                    </p>
                </div>

                {/* Single vs Multi-Target / CIDR Toggle */}
                <div className="inline-flex p-1 bg-surface-light border border-gray-700 rounded-lg shrink-0 self-start sm:self-auto">
                    <button
                        type="button"
                        onClick={() => {
                            setScanMode('single');
                            setSubmitError('');
                        }}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                            scanMode === 'single'
                                ? 'bg-primary text-white shadow'
                                : 'text-gray-400 hover:text-white'
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
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                            scanMode === 'batch'
                                ? 'bg-primary text-white shadow'
                                : 'text-gray-400 hover:text-white'
                        }`}
                    >
                        <Layers className="w-3.5 h-3.5" />
                        Multi-Target / CIDR
                    </button>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Target input */}
                <div>
                    <div className="flex items-center justify-between mb-2">
                        <label htmlFor="target" className="block text-xs font-semibold uppercase tracking-wider text-gray-400">
                            {scanMode === 'single' ? 'Target Specification' : 'Multi-Target & Subnet Specification'}
                        </label>
                        {scanMode === 'single' && getTargetBadge()}
                        {scanMode === 'batch' && batchPreview && (
                            <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-primary/20 text-primary border border-primary/30">
                                <Network className="w-3.5 h-3.5" />
                                <span>~{batchPreview.totalEstimatedHosts} hosts ({batchPreview.rawCount} targets)</span>
                            </span>
                        )}
                    </div>

                    {scanMode === 'single' ? (
                        <input
                            id="target"
                            type="text"
                            value={target}
                            onChange={(e) => {
                                setTarget(e.target.value);
                                if (submitError) setSubmitError('');
                            }}
                            placeholder="e.g., scanme.nmap.org, 192.168.1.0/28, https://target.app"
                            className={`input ${
                                singleValidation && !singleValidation.valid && target.trim().length > 3
                                    ? 'border-amber-500/50 focus:border-amber-500'
                                    : ''
                            }`}
                            disabled={isPending}
                        />
                    ) : (
                        <textarea
                            id="batch-targets"
                            rows={4}
                            value={rawBatchTargets}
                            onChange={(e) => {
                                setRawBatchTargets(e.target.value);
                                if (submitError) setSubmitError('');
                            }}
                            placeholder="Enter multiple IP addresses, hostnames, or CIDR blocks separated by newlines or commas.&#10;e.g.:&#10;192.168.1.0/28&#10;api.example.com&#10;10.0.0.5"
                            className="input font-mono text-xs leading-relaxed"
                            disabled={isPending}
                        />
                    )}

                    {/* Inline real-time validation hint */}
                    {scanMode === 'single' && singleValidation && !singleValidation.valid && target.trim().length > 3 && (
                        <p className="mt-1.5 text-xs text-amber-400 flex items-center gap-1">
                            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                            <span>{singleValidation.error}</span>
                        </p>
                    )}

                    {scanMode === 'batch' && batchPreview?.invalidTokens && batchPreview.invalidTokens.length > 0 && (
                        <p className="mt-1.5 text-xs text-amber-400 flex items-center gap-1">
                            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                            <span>Unrecognized target format: {batchPreview.invalidTokens.slice(0, 3).join(', ')}</span>
                        </p>
                    )}

                    {/* Target format guide & CIDR helper chips */}
                    <div className="mt-2.5 flex flex-wrap items-center gap-2 text-xs text-gray-400">
                        <span className="font-medium text-gray-300">CIDR Helpers:</span>
                        {CIDR_PRESETS.map((preset) => (
                            <button
                                key={preset.snippet}
                                type="button"
                                onClick={() => handleInsertCidrPreset(preset.snippet)}
                                className="px-2 py-0.5 rounded bg-surface border border-gray-700 hover:border-primary text-gray-300 hover:text-primary transition-colors font-mono text-[11px]"
                            >
                                + {preset.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Scan Profile Selector */}
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
                <div className="border border-cyber-border rounded-xl bg-cyber-light/10 overflow-hidden">
                    <button
                        type="button"
                        onClick={() => setShowAdvanced(!showAdvanced)}
                        className="w-full flex items-center justify-between px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-300 hover:text-white hover:bg-cyber-light/20 transition-colors"
                    >
                        <div className="flex items-center space-x-2">
                            <Sliders className="w-4 h-4 text-cyber-blue" />
                            <span>Advanced Engine &amp; Template Options</span>
                            {profile === 'custom' && (
                                <span className="text-[10px] bg-purple-500/20 text-purple-300 px-1.5 py-0.5 rounded border border-purple-500/30">
                                    Active for Custom Profile
                                </span>
                            )}
                        </div>
                        {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>

                    {showAdvanced && (
                        <div className="p-4 border-t border-cyber-border/80 space-y-4 bg-cyber-dark/40 text-xs">
                            {/* Port specification and timing */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-gray-300 font-medium mb-1.5">
                                        Custom Port Range / List
                                    </label>
                                    <input
                                        type="text"
                                        value={customPorts}
                                        onChange={(e) => setCustomPorts(e.target.value)}
                                        placeholder="e.g. 80,443,8080-8090, or 1-1000"
                                        className="input text-xs py-1.5"
                                    />
                                    <span className="text-[11px] text-gray-500 mt-1 block">
                                        Leave empty to use profile default ports.
                                    </span>
                                </div>

                                <div>
                                    <label className="block text-gray-300 font-medium mb-1.5">
                                        Nmap Timing Policy
                                    </label>
                                    <select
                                        value={timing}
                                        onChange={(e) => setTiming(e.target.value as ScanTiming)}
                                        className="input text-xs py-1.5 bg-cyber-dark text-gray-200"
                                    >
                                        <option value="paranoid">T0 - Paranoid (IDS Evasion)</option>
                                        <option value="sneaky">T1 - Sneaky (Slow / Stealth)</option>
                                        <option value="polite">T2 - Polite (Low Bandwidth)</option>
                                        <option value="normal">T3 - Normal (Standard)</option>
                                        <option value="aggressive">T4 - Aggressive (Fast)</option>
                                        <option value="insane">T5 - Insane (Speed-focused)</option>
                                    </select>
                                </div>
                            </div>

                            {/* Service and OS detection flags */}
                            <div className="flex flex-wrap gap-6 pt-1">
                                <label className="flex items-center space-x-2 cursor-pointer text-gray-300">
                                    <input
                                        type="checkbox"
                                        checked={serviceDetection}
                                        onChange={(e) => setServiceDetection(e.target.checked)}
                                        className="rounded border-cyber-border text-cyber-blue focus:ring-0 bg-cyber-dark"
                                    />
                                    <span>Enable Service Fingerprinting (-sV)</span>
                                </label>

                                <label className="flex items-center space-x-2 cursor-pointer text-gray-300">
                                    <input
                                        type="checkbox"
                                        checked={osDetection}
                                        onChange={(e) => setOsDetection(e.target.checked)}
                                        className="rounded border-cyber-border text-cyber-blue focus:ring-0 bg-cyber-dark"
                                    />
                                    <span>Enable OS Detection (-O)</span>
                                </label>
                            </div>

                            {/* Nuclei Template Tags Selector */}
                            <div className="pt-2 border-t border-cyber-border/40">
                                <div className="flex items-center justify-between mb-2">
                                    <label className="text-gray-300 font-medium flex items-center space-x-1.5">
                                        <Tag className="w-3.5 h-3.5 text-cyber-blue" />
                                        <span>Nuclei Vulnerability Tags ({selectedTags.length} active)</span>
                                    </label>
                                    <div className="space-x-2 text-[11px]">
                                        <button
                                            type="button"
                                            onClick={() => setSelectedTags(availableTags.map((t) => t.id))}
                                            className="text-cyber-blue hover:underline"
                                        >
                                            Select All
                                        </button>
                                        <span className="text-gray-600">|</span>
                                        <button
                                            type="button"
                                            onClick={() => setSelectedTags([])}
                                            className="text-gray-400 hover:underline"
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
                                                className={`px-2.5 py-1 rounded-full text-xs font-mono transition-all border ${
                                                    isSelected
                                                        ? 'bg-cyber-blue/20 text-cyber-blue border-cyber-blue font-semibold'
                                                        : 'bg-cyber-light/20 text-gray-400 border-cyber-border hover:border-gray-500'
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
                    <div className="flex items-center gap-2 p-3 bg-danger/10 border border-danger/30 rounded-lg text-danger">
                        <AlertCircle className="w-5 h-5 flex-shrink-0" />
                        <span className="text-sm">{submitError}</span>
                    </div>
                )}

                <button
                    type="submit"
                    disabled={
                        isPending ||
                        (scanMode === 'single'
                            ? !target.trim() || (singleValidation !== null && !singleValidation.valid)
                            : !rawBatchTargets.trim())
                    }
                    className="btn btn-primary w-full flex items-center justify-center gap-2 py-3 text-base font-semibold disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-cyber-blue/20"
                >
                    {isPending ? (
                        <>
                            <LoadingSpinner size="sm" />
                            Dispatching Target Queue...
                        </>
                    ) : (
                        <>
                            <Play className="w-5 h-5 fill-current" />
                            {scanMode === 'single'
                                ? `Start Security Assessment (${profile.toUpperCase()})`
                                : `Launch Batch Subnet Scan (${profile.toUpperCase()})`}
                        </>
                    )}
                </button>
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
