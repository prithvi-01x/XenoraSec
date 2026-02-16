import type { ScanStatus } from '../types/api';
import { getStatusBadgeClass } from '../utils/helpers';
import { Loader2, CheckCircle, XCircle, Clock } from 'lucide-react';

interface StatusBadgeProps {
    status: ScanStatus;
    className?: string;
}

export function StatusBadge({ status, className = '' }: StatusBadgeProps) {
    const icons = {
        running: <Loader2 className="w-3 h-3 animate-spin" />,
        completed: <CheckCircle className="w-3 h-3" />,
        failed: <XCircle className="w-3 h-3" />,
        timeout: <Clock className="w-3 h-3" />,
        partial: <CheckCircle className="w-3 h-3" />,
    };

    return (
        <span className={`badge ${getStatusBadgeClass(status)} inline-flex items-center gap-1 ${className}`}>
            {icons[status]}
            {status.toUpperCase()}
        </span>
    );
}
