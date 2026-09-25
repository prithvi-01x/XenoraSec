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
    ports: string;
}

export const ScanProfileSelector: React.FC<ScanProfileSelectorProps> = ({
    selectedProfile,
    onSelectProfile,
    disabled = false,
}) => {
    const profiles: ProfileOption[] = [
        {
            id: 'quick',
            name: 'Quick Perimeter',
            description: 'Fast reconnaissance of top 100 ports with core CVE & vulnerability checks.',
            icon: <Zap className="w-4 h-4 text-amber-400" />,
            duration: '~1-2 min',
            badgeText: 'FAST',
            ports: 'Top 100 Ports',
        },
        {
            id: 'full',
            name: 'Full Web Audit',
            description: 'In-depth assessment covering web endpoints, full CVE database, RCE, and misconfigurations.',
            icon: <ShieldCheck className="w-4 h-4 text-blue-400" />,
            duration: '~5-10 min',
            badgeText: 'DEFAULT',
            ports: 'Standard + Web',
        },
        {
            id: 'network',
            name: 'Network Discovery',
            description: 'Deep infrastructure audit with OS detection, service fingerprinting, and standard ports.',
            icon: <Network className="w-4 h-4 text-emerald-400" />,
            duration: '~3-5 min',
            badgeText: 'PORTS',
            ports: '1-1024 + Standard',
        },
        {
            id: 'custom',
            name: 'Custom Profile',
            description: 'Fine-tune custom port ranges, timing policy, and select specific Nuclei template tags.',
            icon: <Sliders className="w-4 h-4 text-purple-400" />,
            duration: 'Manual',
            badgeText: 'CONFIG',
            ports: 'User Defined',
        },
    ];

    return (
        <div className="space-y-2">
            <label className="block text-[11px] font-mono uppercase font-semibold text-slate-400">
                Scan Profile &amp; Engine Mode
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
                {profiles.map((p) => {
                    const isSelected = selectedProfile === p.id;
                    return (
                        <button
                            key={p.id}
                            type="button"
                            disabled={disabled}
                            onClick={() => onSelectProfile(p.id)}
                            className={`flex flex-col text-left p-3 rounded border transition-all text-xs ${
                                isSelected
                                    ? 'bg-blue-600/10 border-blue-500 shadow-sm ring-1 ring-blue-500/40'
                                    : 'bg-[#070b12] border-surface-border hover:border-slate-600 hover:bg-surface-light'
                            } ${disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}`}
                        >
                            <div className="flex items-center justify-between w-full mb-1.5">
                                <div className="p-1.5 rounded bg-surface border border-surface-border">
                                    {p.icon}
                                </div>
                                <span className={`text-[9px] font-mono uppercase px-1.5 py-0.2 rounded border font-semibold ${
                                    isSelected ? 'bg-blue-950/80 text-blue-400 border-blue-800' : 'bg-surface text-slate-400 border-surface-border'
                                }`}>
                                    {p.badgeText}
                                </span>
                            </div>

                            <span className="font-semibold text-white text-xs mb-1">
                                {p.name}
                            </span>

                            <p className="text-[11px] text-slate-400 line-clamp-2 mb-2 flex-1 leading-normal">
                                {p.description}
                            </p>

                            <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono border-t border-surface-border pt-1.5 mt-auto">
                                <span>{p.ports}</span>
                                <span className="text-slate-300 font-medium">{p.duration}</span>
                            </div>
                        </button>
                    );
                })}
            </div>
        </div>
    );
};
