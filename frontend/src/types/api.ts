export type ScanStatus = 'running' | 'completed' | 'failed' | 'timeout' | 'partial';

export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info';

export interface Port {
    port: number;
    protocol: string;
    service: string;
    version?: string;
}

export interface Vulnerability {
    name: string;
    severity: Severity;
    description: string;
    template_id: string;
    matcher_name?: string;
    references?: string[];
    cvss?: number;
    cve?: string;
}

export interface ScanSummary {
    total_vulnerabilities: number;
    open_ports: number;
    severity_distribution: Record<Severity, number>;
    critical_count: number;
    high_count: number;
}

export interface NmapResult {
    status: string;
    target: string;
    ports: Port[];
    total_ports: number;
}

export interface NucleiResult {
    status: string;
    target: string;
    vulnerabilities: Vulnerability[];
    total_vulnerabilities: number;
    severity_distribution: Record<Severity, number>;
}

export interface ScanResult {
    scan_id: string;
    target: string;
    status: ScanStatus;
    risk_score: number;
    duration?: number;
    summary: ScanSummary;
    nmap: NmapResult;
    nuclei: NucleiResult;
    created_at: string;
    updated_at: string;
    error?: string;
}

export interface ScanCreateRequest {
    target: string;
}

export interface ScanCreateResponse {
    scan_id: string;
    target: string;
    status: ScanStatus;
    message?: string;
}

export interface ScanHistoryItem {
    scan_id: string;
    target: string;
    status: ScanStatus;
    risk_score: number;
    created_at: string;
    updated_at: string;
    duration?: number;
}

export interface ScanHistoryResponse {
    items: ScanHistoryItem[];
    total: number;
    limit: number;
    offset: number;
}

export interface QueueInfo {
    scans_running: number;        // was incorrectly named active_scans
    max_concurrent_scans: number;
    available_slots: number;
}

export interface HealthStatus {
    status: string;
    version: string;
    uptime: number;
}

export interface DashboardStats {
    total_scans: number;
    running_scans: number;
    avg_risk: number;
    critical_findings: number;
    severity_distribution: Record<Severity, number>;
    risk_history: Array<{ date: string; risk_score: number }>;
    recent_scans: ScanHistoryItem[];
}