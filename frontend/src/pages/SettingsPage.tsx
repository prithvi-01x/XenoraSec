import { useState } from 'react';
import { Save, Info } from 'lucide-react';

export function SettingsPage() {
    // Mock settings - in production, these would be fetched from backend
    const [settings, setSettings] = useState({
        nmapTiming: '3',
        concurrencyLimit: 3,
        rateLimit: 10,
        allowPrivateIp: false,
        allowLocalhost: false,
    });

    const [saved, setSaved] = useState(false);

    const handleSave = () => {
        // In production, this would call the backend API
        console.log('Saving settings:', settings);
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold mb-2">Settings</h1>
                <p className="text-gray-400">Configure scanner behavior and limits</p>
            </div>

            <div className="card bg-primary/10 border-primary/30">
                <div className="flex items-start gap-3">
                    <Info className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                    <div className="text-sm">
                        <p className="font-medium text-primary mb-1">Settings API Not Implemented</p>
                        <p className="text-gray-300">
                            These settings are currently mock values. Backend API endpoints for settings
                            management need to be implemented for full functionality.
                        </p>
                    </div>
                </div>
            </div>

            <div className="card space-y-6">
                <div>
                    <h2 className="text-xl font-semibold mb-4">Scan Configuration</h2>

                    <div className="space-y-4">
                        <div>
                            <label htmlFor="nmapTiming" className="block text-sm font-medium text-gray-300 mb-2">
                                Nmap Timing Template
                            </label>
                            <select
                                id="nmapTiming"
                                value={settings.nmapTiming}
                                onChange={(e) => setSettings({ ...settings, nmapTiming: e.target.value })}
                                className="input w-full md:w-64"
                            >
                                <option value="0">Paranoid (0) - Slowest</option>
                                <option value="1">Sneaky (1)</option>
                                <option value="2">Polite (2)</option>
                                <option value="3">Normal (3) - Default</option>
                                <option value="4">Aggressive (4)</option>
                                <option value="5">Insane (5) - Fastest</option>
                            </select>
                            <p className="mt-2 text-xs text-gray-400">
                                Higher values are faster but more detectable. Use lower values for stealth.
                            </p>
                        </div>

                        <div>
                            <label htmlFor="concurrency" className="block text-sm font-medium text-gray-300 mb-2">
                                Max Concurrent Scans
                            </label>
                            <input
                                id="concurrency"
                                type="number"
                                min="1"
                                max="10"
                                value={settings.concurrencyLimit}
                                onChange={(e) => setSettings({ ...settings, concurrencyLimit: parseInt(e.target.value) })}
                                className="input w-full md:w-64"
                            />
                            <p className="mt-2 text-xs text-gray-400">
                                Maximum number of scans that can run simultaneously (1-10)
                            </p>
                        </div>

                        <div>
                            <label htmlFor="rateLimit" className="block text-sm font-medium text-gray-300 mb-2">
                                Rate Limit (scans per hour)
                            </label>
                            <input
                                id="rateLimit"
                                type="number"
                                min="1"
                                max="100"
                                value={settings.rateLimit}
                                onChange={(e) => setSettings({ ...settings, rateLimit: parseInt(e.target.value) })}
                                className="input w-full md:w-64"
                            />
                            <p className="mt-2 text-xs text-gray-400">
                                Maximum number of scans a user can start per hour
                            </p>
                        </div>
                    </div>
                </div>

                <div className="border-t border-gray-700 pt-6">
                    <h2 className="text-xl font-semibold mb-4">Target Restrictions</h2>

                    <div className="space-y-4">
                        <label className="flex items-center gap-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.allowPrivateIp}
                                onChange={(e) => setSettings({ ...settings, allowPrivateIp: e.target.checked })}
                                className="w-5 h-5 rounded border-gray-600 bg-background text-primary focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background"
                            />
                            <div>
                                <div className="font-medium">Allow Private IP Scanning</div>
                                <div className="text-sm text-gray-400">
                                    Enable scanning of private IP ranges (10.x.x.x, 172.16.x.x, 192.168.x.x)
                                </div>
                            </div>
                        </label>

                        <label className="flex items-center gap-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.allowLocalhost}
                                onChange={(e) => setSettings({ ...settings, allowLocalhost: e.target.checked })}
                                className="w-5 h-5 rounded border-gray-600 bg-background text-primary focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background"
                            />
                            <div>
                                <div className="font-medium">Allow Localhost Scanning</div>
                                <div className="text-sm text-gray-400">
                                    Enable scanning of localhost and 127.0.0.1
                                </div>
                            </div>
                        </label>
                    </div>
                </div>

                <div className="border-t border-gray-700 pt-6 flex items-center justify-between">
                    <div className="text-sm text-gray-400">
                        Changes will be applied to new scans only
                    </div>

                    <button
                        onClick={handleSave}
                        className="btn btn-primary flex items-center gap-2"
                    >
                        <Save className="w-4 h-4" />
                        {saved ? 'Saved!' : 'Save Settings'}
                    </button>
                </div>
            </div>
        </div>
    );
}
