import type { Severity } from '../types/api';
import { getSeverityBadgeClass } from '../utils/helpers';

interface SeverityBadgeProps {
    severity: Severity;
    className?: string;
    showDot?: boolean;
}

export function SeverityBadge({ severity, className = '', showDot = true }: SeverityBadgeProps) {
    const dotColors: Record<Severity, string> = {
        critical: 'bg-red-500',
        high: 'bg-orange-500',
        medium: 'bg-amber-400',
        low: 'bg-emerald-400',
        info: 'bg-slate-400',
    };

    return (
        <span className={`badge ${getSeverityBadgeClass(severity)} ${className}`}>
            {showDot && (
                <span className={`w-1.5 h-1.5 rounded-full ${dotColors[severity] || 'bg-slate-400'}`} />
            )}
            {severity.toUpperCase()}
        </span>
    );
}
