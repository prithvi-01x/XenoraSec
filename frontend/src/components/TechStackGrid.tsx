import { 
    ShieldCheck, 
    AlertCircle, 
    CheckCircle2, 
    XCircle, 
    Lock, 
    Server, 
    Code, 
    Cloud, 
    FileCode,
    ExternalLink
} from 'lucide-react';
import type { TechFingerprint, TechStackItem, SecurityHeaderCheck } from '../types/api';

interface TechStackGridProps {
    techStack: TechFingerprint;
}

export function TechStackGrid({ techStack }: TechStackGridProps) {
    const scoreColor = 
        techStack.security_score >= 80 ? 'text-emerald-400 border-emerald-500/40 bg-emerald-950/40' :
        techStack.security_score >= 50 ? 'text-amber-400 border-amber-500/40 bg-amber-950/40' :
        'text-rose-400 border-rose-500/40 bg-rose-950/40';

    const renderTechBadge = (item: TechStackItem, idx: number) => (
        <div 
            key={`${item.name}-${idx}`}
            className="p-2.5 rounded bg-[#070b13] border border-surface-border flex items-center justify-between gap-2 text-xs font-mono hover:border-slate-500 transition-colors"
        >
            <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded bg-blue-600/10 border border-blue-500/30 flex items-center justify-center text-blue-400 text-[10px] font-bold">
                    {item.name.slice(0, 2).toUpperCase()}
                </div>
                <div>
                    <div className="flex items-center gap-1.5">
                        <span className="font-semibold text-slate-100">{item.name}</span>
                        {item.version && (
                            <span className="px-1.5 py-0.2 rounded bg-surface border border-surface-border text-[10px] text-blue-300">
                                v{item.version}
                            </span>
                        )}
                    </div>
                    {item.match_evidence && (
                        <p className="text-[10px] text-slate-500 truncate max-w-[220px]" title={item.match_evidence}>
                            {item.match_evidence}
                        </p>
                    )}
                </div>
            </div>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-surface border border-surface-border text-slate-400">
                {item.confidence}%
            </span>
        </div>
    );

    const renderHeaderCheck = (check: SecurityHeaderCheck, idx: number) => {
        const isPass = check.status === 'pass';
        const isWarning = check.status === 'warning';

        return (
            <div 
                key={`${check.header}-${idx}`}
                className="p-3 rounded bg-[#070b13] border border-surface-border flex flex-col gap-1.5 text-xs font-mono"
            >
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        {isPass ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        ) : isWarning ? (
                            <AlertCircle className="w-4 h-4 text-amber-400" />
                        ) : (
                            <XCircle className="w-4 h-4 text-rose-400" />
                        )}
                        <span className="font-semibold text-slate-200">{check.header}</span>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-semibold ${
                        isPass ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' :
                        isWarning ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                        'bg-rose-950 text-rose-400 border border-rose-800'
                    }`}>
                        {check.status}
                    </span>
                </div>

                {check.value && (
                    <p className="text-[11px] text-slate-400 break-all bg-surface/50 p-1.5 rounded border border-surface-border">
                        {check.value}
                    </p>
                )}

                {check.recommendation && (
                    <p className="text-[11px] text-amber-400/90 italic">
                        Tip: {check.recommendation}
                    </p>
                )}
            </div>
        );
    };

    return (
        <div className="space-y-5">
            {/* Top Overview Bar */}
            <div className="bg-surface rounded-lg border border-surface-border p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                    <div className="flex items-center gap-2">
                        <span className="text-xs font-mono uppercase text-slate-500 font-semibold tracking-wider">
                            Target Endpoint
                        </span>
                        {techStack.status_code && (
                            <span className="px-1.5 py-0.2 rounded bg-emerald-950 border border-emerald-800 text-emerald-400 text-[11px] font-mono font-bold">
                                HTTP {techStack.status_code}
                            </span>
                        )}
                    </div>
                    <h3 className="text-sm font-bold text-white font-mono flex items-center gap-2">
                        <a 
                            href={techStack.target_url} 
                            target="_blank" 
                            rel="noreferrer" 
                            className="hover:text-blue-400 flex items-center gap-1.5 transition-colors"
                        >
                            <span>{techStack.target_url}</span>
                            <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
                        </a>
                    </h3>
                    {techStack.title && (
                        <p className="text-xs text-slate-400 font-mono">
                            Page Title: &quot;{techStack.title}&quot;
                        </p>
                    )}
                </div>

                {/* Security Posture Rating Meter */}
                <div className="flex items-center gap-3">
                    <div className="text-right">
                        <div className="text-[10px] font-mono text-slate-400 uppercase">Defensive Headers Score</div>
                        <div className="text-xs text-slate-500 font-mono">Out of 100 benchmark</div>
                    </div>
                    <div className={`px-4 py-2 rounded-lg border flex items-center gap-2 font-mono font-bold text-lg ${scoreColor}`}>
                        <ShieldCheck className="w-5 h-5" />
                        <span>{techStack.security_score} / 100</span>
                    </div>
                </div>
            </div>

            {/* Grid of Discovered Technologies */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Web Servers */}
                <div className="bg-surface rounded-lg border border-surface-border p-4 space-y-3">
                    <div className="flex items-center gap-2 text-xs font-mono font-semibold text-slate-300">
                        <Server className="w-4 h-4 text-blue-400" />
                        <span>Web Servers ({techStack.web_servers.length})</span>
                    </div>
                    <div className="space-y-2">
                        {techStack.web_servers.length === 0 ? (
                            <p className="text-xs text-slate-500 italic py-2">No server header detected</p>
                        ) : (
                            techStack.web_servers.map((item, idx) => renderTechBadge(item, idx))
                        )}
                    </div>
                </div>

                {/* Frameworks & Languages */}
                <div className="bg-surface rounded-lg border border-surface-border p-4 space-y-3">
                    <div className="flex items-center gap-2 text-xs font-mono font-semibold text-slate-300">
                        <Code className="w-4 h-4 text-cyan-400" />
                        <span>Frameworks & Tech ({techStack.frameworks.length})</span>
                    </div>
                    <div className="space-y-2">
                        {techStack.frameworks.length === 0 ? (
                            <p className="text-xs text-slate-500 italic py-2">No framework signatures found</p>
                        ) : (
                            techStack.frameworks.map((item, idx) => renderTechBadge(item, idx))
                        )}
                    </div>
                </div>

                {/* Content Management Systems (CMS) */}
                <div className="bg-surface rounded-lg border border-surface-border p-4 space-y-3">
                    <div className="flex items-center gap-2 text-xs font-mono font-semibold text-slate-300">
                        <FileCode className="w-4 h-4 text-amber-400" />
                        <span>CMS & Platforms ({techStack.cms.length})</span>
                    </div>
                    <div className="space-y-2">
                        {techStack.cms.length === 0 ? (
                            <p className="text-xs text-slate-500 italic py-2">No CMS signature detected</p>
                        ) : (
                            techStack.cms.map((item, idx) => renderTechBadge(item, idx))
                        )}
                    </div>
                </div>

                {/* CDN & Edge WAF */}
                <div className="bg-surface rounded-lg border border-surface-border p-4 space-y-3">
                    <div className="flex items-center gap-2 text-xs font-mono font-semibold text-slate-300">
                        <Cloud className="w-4 h-4 text-purple-400" />
                        <span>CDN & Edge Proxy ({techStack.cdn_waf.length})</span>
                    </div>
                    <div className="space-y-2">
                        {techStack.cdn_waf.length === 0 ? (
                            <p className="text-xs text-slate-500 italic py-2">Direct origin connection</p>
                        ) : (
                            techStack.cdn_waf.map((item, idx) => renderTechBadge(item, idx))
                        )}
                    </div>
                </div>
            </div>

            {/* Defensive HTTP Security Headers Card */}
            <div className="bg-surface rounded-lg border border-surface-border p-5 space-y-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded bg-blue-600/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
                            <Lock className="w-4 h-4" />
                        </div>
                        <div>
                            <h4 className="text-sm font-semibold text-white font-mono">
                                Defensive Security Headers Evaluation
                            </h4>
                            <p className="text-xs text-slate-400">
                                Browser security mechanisms, framing restrictions, and transport encryption
                            </p>
                        </div>
                    </div>
                    <div className="text-xs font-mono text-slate-400">
                        {techStack.security_headers.filter(c => c.status === 'pass').length} / {techStack.security_headers.length} Passed
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {techStack.security_headers.map((check, idx) => renderHeaderCheck(check, idx))}
                </div>
            </div>
        </div>
    );
}
