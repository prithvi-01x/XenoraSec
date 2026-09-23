import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { Severity, ScanStatus } from '../types/api';

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

export function getSeverityColor(severity: Severity): string {
    const colors: Record<Severity, string> = {
        critical: 'text-critical',
        high: 'text-high',
        medium: 'text-medium',
        low: 'text-low',
        info: 'text-info',
    };
    return colors[severity] || 'text-gray-400';
}

export function getSeverityBadgeClass(severity: Severity): string {
    const classes: Record<Severity, string> = {
        critical: 'badge-critical',
        high: 'badge-high',
        medium: 'badge-medium',
        low: 'badge-low',
        info: 'badge-info',
    };
    return classes[severity] || 'badge-info';
}

export function getStatusBadgeClass(status: ScanStatus): string {
    const classes: Record<ScanStatus, string> = {
        running: 'badge-running',
        completed: 'badge-success',
        failed: 'badge-failed',
        timeout: 'badge-failed',
        partial: 'badge-medium',
    };
    return classes[status] || 'badge-info';
}

export function getRiskColor(riskScore: number): string {
    if (riskScore >= 9) return 'text-critical';
    if (riskScore >= 7) return 'text-high';
    if (riskScore >= 5) return 'text-medium';
    if (riskScore >= 3) return 'text-low';
    return 'text-info';
}

export function getRiskLevel(riskScore: number): string {
    if (riskScore >= 9) return 'Critical';
    if (riskScore >= 7) return 'High';
    if (riskScore >= 5) return 'Medium';
    if (riskScore >= 3) return 'Low';
    return 'Info';
}

export function formatDuration(seconds?: number): string {
    if (!seconds) return 'N/A';
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}m ${secs}s`;
}

export function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleString();
}

export interface TargetValidationResult {
    valid: boolean;
    error?: string;
    targetType?: 'ipv4' | 'ipv6' | 'domain' | 'url' | 'localhost';
}

export function validateTarget(target: string): TargetValidationResult {
    if (!target || target.trim().length === 0) {
        return { valid: false, error: 'Target is required' };
    }

    const trimmed = target.trim();
    const lower = trimmed.toLowerCase();

    // Check localhost
    if (lower === 'localhost' || lower.endsWith('.localhost')) {
        return { valid: true, targetType: 'localhost' };
    }

    // URL format check
    if (lower.startsWith('http://') || lower.startsWith('https://')) {
        try {
            const parsed = new URL(trimmed);
            if (!parsed.hostname) {
                return { valid: false, error: 'URL is missing a valid hostname' };
            }
            if (parsed.hostname === 'localhost') {
                return { valid: true, targetType: 'localhost' };
            }
            return { valid: true, targetType: 'url' };
        } catch {
            return { valid: false, error: 'Malformed URL format' };
        }
    }

    // IPv4 pattern
    if (/^[\d.]+$/.test(trimmed)) {
        const parts = trimmed.split('.');
        if (parts.length !== 4) {
            return { valid: false, error: 'IPv4 address must contain exactly 4 octets' };
        }
        for (const part of parts) {
            if (part === '' || isNaN(Number(part))) {
                return { valid: false, error: 'Invalid numeric octet in IP address' };
            }
            const num = Number(part);
            if (num < 0 || num > 255) {
                return { valid: false, error: `IP octet ${num} is out of range (0-255)` };
            }
        }
        if (trimmed.startsWith('127.')) {
            return { valid: true, targetType: 'localhost' };
        }
        return { valid: true, targetType: 'ipv4' };
    }

    // Simple IPv6 check (e.g., ::1 or standard hex groups)
    if (trimmed.includes(':')) {
        if (trimmed === '::1') {
            return { valid: true, targetType: 'localhost' };
        }
        const ipv6Pattern = /^([0-9a-fA-F]{1,4}:){1,7}:?([0-9a-fA-F]{1,4})?$/;
        if (ipv6Pattern.test(trimmed)) {
            return { valid: true, targetType: 'ipv6' };
        }
        return { valid: false, error: 'Invalid IPv6 address format' };
    }

    // Domain validation
    if (trimmed.length > 253) {
        return { valid: false, error: 'Domain name cannot exceed 253 characters' };
    }

    const domainPattern = /^([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$/;
    if (domainPattern.test(trimmed)) {
        return { valid: true, targetType: 'domain' };
    }

    return { 
        valid: false, 
        error: 'Invalid target format. Enter a valid IPv4/IPv6, domain (e.g. example.com), or URL (https://...)' 
    };
}

export function getLogStageBadge(stage: string): { label: string; colorClass: string } {
    switch (stage) {
        case 'nmap':
            return { label: 'PORT-SCAN', colorClass: 'bg-blue-500/10 text-blue-400 border-blue-500/30' };
        case 'nuclei':
            return { label: 'NUCLEI', colorClass: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30' };
        case 'ai':
            return { label: 'AI-ANALYSIS', colorClass: 'bg-purple-500/10 text-purple-400 border-purple-500/30' };
        case 'completed':
            return { label: 'DONE', colorClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' };
        case 'failed':
            return { label: 'FAILED', colorClass: 'bg-red-500/10 text-red-400 border-red-500/30' };
        default:
            return { label: 'INIT', colorClass: 'bg-gray-500/10 text-gray-400 border-gray-500/30' };
    }
}

export function getLogLevelClass(level: string): string {
    switch (level) {
        case 'error':
            return 'text-red-400 font-semibold';
        case 'warn':
            return 'text-yellow-400';
        case 'success':
            return 'text-emerald-400 font-medium';
        default:
            return 'text-gray-300';
    }
}

export function formatLogTimestamp(timestamp: string): string {
    try {
        const d = new Date(timestamp);
        return d.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
        return timestamp;
    }
}

export function triggerFileDownload(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

export async function copyToClipboard(text: string): Promise<boolean> {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch {
        return false;
    }
}

