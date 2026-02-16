import type { Severity } from '../types/api';
import { getSeverityBadgeClass } from '../utils/helpers';

interface SeverityBadgeProps {
    severity: Severity;
    className?: string;
}

export function SeverityBadge({ severity, className = '' }: SeverityBadgeProps) {
    return (
        <span className={`badge ${getSeverityBadgeClass(severity)} ${className}`}>
            {severity.toUpperCase()}
        </span>
    );
}
