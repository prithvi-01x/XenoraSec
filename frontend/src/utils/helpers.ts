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

export function validateTarget(target: string): { valid: boolean; error?: string } {
    if (!target || target.trim().length === 0) {
        return { valid: false, error: 'Target is required' };
    }

    const trimmed = target.trim();

    // IP address pattern
    const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;

    // Domain pattern
    const domainPattern = /^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$/;

    // URL pattern
    const urlPattern = /^https?:\/\/.+/;

    if (ipPattern.test(trimmed)) {
        // Validate IP octets
        const octets = trimmed.split('.').map(Number);
        if (octets.some(octet => octet < 0 || octet > 255)) {
            return { valid: false, error: 'Invalid IP address' };
        }
        return { valid: true };
    }

    if (domainPattern.test(trimmed) || urlPattern.test(trimmed)) {
        return { valid: true };
    }

    return { valid: false, error: 'Invalid target format. Use IP, domain, or URL' };
}
