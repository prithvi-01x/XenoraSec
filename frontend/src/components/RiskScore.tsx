import { getRiskLevel } from '../utils/helpers';

interface RiskScoreProps {
    score: number;
    size?: 'sm' | 'md' | 'lg';
}

export function RiskScore({ score, size = 'md' }: RiskScoreProps) {
    const level = getRiskLevel(score);

    // Color definitions based on CVSS standard
    const getColor = (s: number) => {
        if (s >= 9.0) return { text: 'text-red-400', border: 'border-red-500/80', bg: 'bg-red-950/30', bar: 'bg-red-500' };
        if (s >= 7.0) return { text: 'text-orange-400', border: 'border-orange-500/80', bg: 'bg-orange-950/30', bar: 'bg-orange-500' };
        if (s >= 4.0) return { text: 'text-amber-400', border: 'border-amber-500/80', bg: 'bg-amber-950/30', bar: 'bg-amber-500' };
        if (s > 0) return { text: 'text-emerald-400', border: 'border-emerald-500/80', bg: 'bg-emerald-950/30', bar: 'bg-emerald-500' };
        return { text: 'text-slate-400', border: 'border-slate-700', bg: 'bg-slate-900/30', bar: 'bg-slate-600' };
    };

    const color = getColor(score);

    if (size === 'sm') {
        return (
            <div className="inline-flex items-center gap-1.5 font-mono">
                <span className={`text-xs font-bold px-1.5 py-0.5 rounded border ${color.bg} ${color.border} ${color.text}`}>
                    {score.toFixed(1)}
                </span>
                <span className="text-[10px] text-slate-400 uppercase font-sans">{level}</span>
            </div>
        );
    }

    if (size === 'lg') {
        const percentage = Math.min(100, (score / 10) * 100);
        return (
            <div className="w-full flex flex-col items-center p-3 text-center">
                <div className="flex items-baseline gap-1 font-mono">
                    <span className={`text-4xl font-black tracking-tight ${color.text}`}>
                        {score.toFixed(1)}
                    </span>
                    <span className="text-xs text-slate-500 font-semibold">/10.0</span>
                </div>
                <div className={`mt-1 inline-flex items-center gap-1 text-[11px] font-mono uppercase font-semibold px-2 py-0.5 rounded ${color.bg} ${color.text} border ${color.border}`}>
                    {level} Risk Posture
                </div>
                <div className="w-full bg-[#070b12] rounded-full h-1.5 mt-3 border border-slate-800 overflow-hidden">
                    <div 
                        className={`h-full transition-all duration-500 ${color.bar}`} 
                        style={{ width: `${percentage}%` }} 
                    />
                </div>
            </div>
        );
    }

    // Default 'md'
    return (
        <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded border ${color.border} ${color.bg} flex items-center justify-center font-mono font-bold text-lg ${color.text}`}>
                {score.toFixed(1)}
            </div>
            <div>
                <div className={`text-xs font-bold uppercase font-mono ${color.text}`}>{level} Risk</div>
                <div className="text-[10px] text-slate-400">Score Range: 0.0 - 10.0</div>
            </div>
        </div>
    );
}
