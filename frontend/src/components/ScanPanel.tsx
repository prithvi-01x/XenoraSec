import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, AlertCircle, CheckCircle2, Globe, Server, Link2 } from 'lucide-react';
import { useStartScan } from '../hooks/useApi';
import { validateTarget } from '../utils/helpers';
import { LoadingSpinner } from '../components/LoadingSpinner';

export function ScanPanel() {
    const [target, setTarget] = useState('');
    const [submitError, setSubmitError] = useState('');
    const navigate = useNavigate();
    const startScan = useStartScan();

    const validation = useMemo(() => {
        if (!target.trim()) return null;
        return validateTarget(target);
    }, [target]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitError('');

        // Validate target
        const res = validateTarget(target);
        if (!res.valid) {
            setSubmitError(res.error || 'Invalid target');
            return;
        }

        try {
            const result = await startScan.mutateAsync({ target: target.trim() });
            // Navigate to scan results page
            navigate(`/scan/${result.scan_id}`);
        } catch (err: any) {
            if (err.response?.status === 429) {
                setSubmitError('Rate limit exceeded. Please wait before starting another scan.');
            } else if (err.response?.status === 503) {
                setSubmitError('Scan queue is full. Please try again later.');
            } else {
                setSubmitError(err.response?.data?.detail || 'Failed to start scan');
            }
        }
    };

    const getTargetBadge = () => {
        if (!validation) return null;
        if (validation.valid) {
            const icons = {
                ipv4: <Server className="w-3.5 h-3.5" />,
                ipv6: <Server className="w-3.5 h-3.5" />,
                domain: <Globe className="w-3.5 h-3.5" />,
                url: <Link2 className="w-3.5 h-3.5" />,
                localhost: <Server className="w-3.5 h-3.5" />
            };
            const labels = {
                ipv4: 'IPv4 Address',
                ipv6: 'IPv6 Address',
                domain: 'Domain Host',
                url: 'Web URL',
                localhost: 'Localhost'
            };
            const type = validation.targetType || 'domain';
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

    return (
        <div className="card">
            <h2 className="text-2xl font-bold mb-6">Start New Scan</h2>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <div className="flex items-center justify-between mb-2">
                        <label htmlFor="target" className="block text-sm font-medium text-gray-300">
                            Target Specification
                        </label>
                        {getTargetBadge()}
                    </div>
                    <input
                        id="target"
                        type="text"
                        value={target}
                        onChange={(e) => {
                            setTarget(e.target.value);
                            if (submitError) setSubmitError('');
                        }}
                        placeholder="e.g., example.com, 192.168.1.1, https://target.app"
                        className={`input ${
                            validation && !validation.valid && target.trim().length > 3
                                ? 'border-amber-500/50 focus:border-amber-500'
                                : ''
                        }`}
                        disabled={startScan.isPending}
                    />

                    {/* Inline real-time validation hint */}
                    {validation && !validation.valid && target.trim().length > 3 && (
                        <p className="mt-1.5 text-xs text-amber-400 flex items-center gap-1">
                            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                            <span>{validation.error}</span>
                        </p>
                    )}

                    {/* Target format guide & quick presets */}
                    <div className="mt-2.5 flex flex-wrap items-center gap-2 text-xs text-gray-400">
                        <span>Quick presets:</span>
                        {[
                            'scanme.nmap.org',
                            'https://example.com'
                        ].map((preset) => (
                            <button
                                key={preset}
                                type="button"
                                onClick={() => {
                                    setTarget(preset);
                                    setSubmitError('');
                                }}
                                className="px-2 py-0.5 rounded bg-surface border border-gray-700 hover:border-primary text-gray-300 hover:text-primary transition-colors"
                            >
                                {preset}
                            </button>
                        ))}
                    </div>
                </div>

                {submitError && (
                    <div className="flex items-center gap-2 p-3 bg-danger/10 border border-danger/30 rounded-lg text-danger">
                        <AlertCircle className="w-5 h-5 flex-shrink-0" />
                        <span className="text-sm">{submitError}</span>
                    </div>
                )}

                <button
                    type="submit"
                    disabled={startScan.isPending || !target.trim() || (validation !== null && !validation.valid)}
                    className="btn btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {startScan.isPending ? (
                        <>
                            <LoadingSpinner size="sm" />
                            Starting Scan...
                        </>
                    ) : (
                        <>
                            <Play className="w-5 h-5" />
                            Start Security Scan
                        </>
                    )}
                </button>
            </form>
        </div>
    );
}
