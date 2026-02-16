import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, AlertCircle } from 'lucide-react';
import { useStartScan } from '../hooks/useApi';
import { validateTarget } from '../utils/helpers';
import { LoadingSpinner } from '../components/LoadingSpinner';

export function ScanPanel() {
    const [target, setTarget] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const startScan = useStartScan();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // Validate target
        const validation = validateTarget(target);
        if (!validation.valid) {
            setError(validation.error || 'Invalid target');
            return;
        }

        try {
            const result = await startScan.mutateAsync({ target: target.trim() });
            // Navigate to scan results page
            navigate(`/scan/${result.scan_id}`);
        } catch (err: any) {
            if (err.response?.status === 429) {
                setError('Rate limit exceeded. Please wait before starting another scan.');
            } else if (err.response?.status === 503) {
                setError('Scan queue is full. Please try again later.');
            } else {
                setError(err.response?.data?.detail || 'Failed to start scan');
            }
        }
    };

    return (
        <div className="card">
            <h2 className="text-2xl font-bold mb-6">Start New Scan</h2>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="target" className="block text-sm font-medium text-gray-300 mb-2">
                        Target (IP, Domain, or URL)
                    </label>
                    <input
                        id="target"
                        type="text"
                        value={target}
                        onChange={(e) => setTarget(e.target.value)}
                        placeholder="e.g., 192.168.1.1, example.com, https://example.com"
                        className="input"
                        disabled={startScan.isPending}
                    />
                    <p className="mt-2 text-xs text-gray-400">
                        Enter an IP address, domain name, or full URL to scan
                    </p>
                </div>

                {error && (
                    <div className="flex items-center gap-2 p-3 bg-danger/10 border border-danger/30 rounded-lg text-danger">
                        <AlertCircle className="w-5 h-5 flex-shrink-0" />
                        <span className="text-sm">{error}</span>
                    </div>
                )}

                <button
                    type="submit"
                    disabled={startScan.isPending || !target.trim()}
                    className="btn btn-primary w-full flex items-center justify-center gap-2"
                >
                    {startScan.isPending ? (
                        <>
                            <LoadingSpinner size="sm" />
                            Starting Scan...
                        </>
                    ) : (
                        <>
                            <Play className="w-5 h-5" />
                            Start Scan
                        </>
                    )}
                </button>
            </form>
        </div>
    );
}
