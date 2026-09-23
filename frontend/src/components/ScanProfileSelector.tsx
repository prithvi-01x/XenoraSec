import React from 'react';
import { Zap, ShieldCheck, Network, Sliders } from 'lucide-react';
import type { ScanProfile } from '../types/api';

interface ScanProfileSelectorProps {
    selectedProfile: ScanProfile;
    onSelectProfile: (profile: ScanProfile) => void;
    disabled?: boolean;
}

interface ProfileOption {
    id: ScanProfile;
    name: string;
    description: string;
    icon: React.ReactNode;
    duration: string;
    badgeText: string;
    badgeColor: string;
}

export const ScanProfileSelector: React.FC<ScanProfileSelectorProps> = ({
    selectedProfile,
    onSelectProfile,
    disabled = false,
}) => {
    const profiles: ProfileOption[] = [
        {
            id: 'quick',
            name: 'Quick Recon',
            description: 'Fast perimeter scan on top 100 ports with core CVE & vulnerability checks.',
            icon: <Zap className="w-5 h-5 text-amber-400" />,
            duration: '~1-2 min',
            badgeText: 'FAST',
            badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
        },
        {
            id: 'full',
            name: 'Full Web Audit',
            description: 'In-depth assessment covering web endpoints, full CVE database, RCE, and misconfigurations.',
            icon: <ShieldCheck className="w-5 h-5 text-blue-400" />,
            duration: '~5-10 min',
            badgeText: 'RECOMMENDED',
            badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
        },
        {
            id: 'network',
            name: 'Network Discovery',
            description: 'Deep infrastructure audit with OS detection, service fingerprinting, and standard ports.',
            icon: <Network className="w-5 h-5 text-emerald-400" />,
            duration: '~3-5 min',
            badgeText: 'PORTS',
            badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
        },
        {
            id: 'custom',
            name: 'Custom Scan',
            description: 'Define custom port ranges, timing policy, and select specific Nuclei tags / categories.',
            icon: <Sliders className="w-5 h-5 text-purple-400" />,
            duration: 'Variable',
            badgeText: 'ADVANCED',
            badgeColor: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
        },
    ];

    return (
        <div className="space-y-2">
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
                Scan Profile &amp; Engine Mode
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {profiles.map((p) => {
                    const isSelected = selectedProfile === p.id;
                    return (
                        <button
                            key={p.id}
                            type="button"
                            disabled={disabled}
                            onClick={() => onSelectProfile(p.id)}
                            className={`flex flex-col text-left p-3.5 rounded-xl border transition-all duration-200 ${
                                isSelected
                                    ? 'bg-cyber-blue/10 border-cyber-blue shadow-lg shadow-cyber-blue/10 ring-1 ring-cyber-blue/30'
                                    : 'bg-cyber-light/20 border-cyber-border hover:border-gray-600 hover:bg-cyber-light/40'
                            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                        >
                            <div className="flex items-center justify-between w-full mb-2">
                                <div className="p-2 rounded-lg bg-cyber-dark/80 border border-cyber-border">
                                    {p.icon}
                                </div>
                                <span
                                    className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border font-semibold ${p.badgeColor}`}
                                >
                                    {p.badgeText}
                                </span>
                            </div>

                            <span className="font-semibold text-sm text-white mb-1">
                                {p.name}
                            </span>

                            <p className="text-xs text-gray-400 line-clamp-2 mb-3 flex-1 leading-relaxed">
                                {p.description}
                            </p>

                            <div className="flex items-center justify-between text-[11px] text-gray-500 font-mono border-t border-cyber-border/60 pt-2 mt-auto">
                                <span>Est. Duration:</span>
                                <span className="text-gray-300 font-medium">{p.duration}</span>
                            </div>
                        </button>
                    );
                })}
            </div>
        </div>
    );
};
