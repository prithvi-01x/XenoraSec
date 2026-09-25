import type { ScanStatus } from '../types/api';
import { getStatusBadgeClass } from '../utils/helpers';
import { Loader2, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';

interface StatusBadgeProps {
    status: ScanStatus;
    className?: string;
}

export function StatusBadge({ status, className = '' }: StatusBadgeProps) {
    const icons = {
        running: <Loader2 className="w-3 h-3 animate-spin text-blue-400" />,
        completed: <CheckCircle className="w-3 h-3 text-emerald-400" />,
        failed: <XCircle className="w-3 h-3 text-rose-400" />,
        timeout: <Clock className="w-3 h-3 text-amber-400" />,
        partial: <AlertTriangle className="w-3 h-3 text-amber-400" />,
    };

    return (
        <span className={`badge ${getStatusBadgeClass(status)} ${className}`}>
            {icons[status]}
            <span>{status.toUpperCase()}</span>
        </span>
    );
}
