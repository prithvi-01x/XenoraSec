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
    scan_profile?: ScanProfile;
    scan_options?: ScanOptions;
    summary: ScanSummary;
    nmap: NmapResult;
    nuclei: NucleiResult;
    created_at: string;
    updated_at: string;
    error?: string;
}

export type ScanProfile = 'quick' | 'full' | 'network' | 'custom';

export type ScanTiming = 'paranoid' | 'sneaky' | 'polite' | 'normal' | 'aggressive' | 'insane';

export interface ScanOptions {
    ports?: string;
    timing?: ScanTiming;
    service_detection?: boolean;
    os_detection?: boolean;
    tags?: string[];
    exclude_tags?: string[];
    severity?: Severity[];
    rate_limit?: number;
}

export interface ProfileDefinition {
    id: ScanProfile;
    name: string;
    description: string;
    icon: string;
    estimated_duration: string;
    default_ports?: string;
    default_tags?: string[];
    is_custom?: boolean;
}

export interface TemplateTag {
    id: string;
    name: string;
    description: string;
    category: 'cve' | 'vulnerability' | 'exposure' | 'misconfig' | 'service';
    count_estimate?: string;
}

export type ReportFormat = 'html' | 'pdf' | 'markdown' | 'json';
export type ReportType = 'technical' | 'executive';

export interface ScanLogEvent {
    scan_id: string;
    timestamp: string;
    stage: 'init' | 'nmap' | 'nuclei' | 'ai' | 'completed' | 'failed';
    level: 'info' | 'warn' | 'error' | 'success';
    message: string;
    metadata?: Record<string, unknown>;
}

export interface ScanCreateRequest {
    target: string;
    scan_profile?: ScanProfile;
    options?: ScanOptions;
}

export interface ScanCreateResponse {
    scan_id: string;
    target: string;
    status: ScanStatus;
    scan_profile?: ScanProfile;
    message?: string;
}

export interface ScanHistoryItem {
    scan_id: string;
    target: string;
    status: ScanStatus;
    scan_profile?: string;
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
    uptime?: number;
    database?: string;
    timestamp?: string;
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

// ==================== ASSET INVENTORY ====================

export type AssetType = 'ip' | 'domain' | 'url' | 'cidr_host';
export type AssetCriticality = 'low' | 'medium' | 'high' | 'critical';
export type AssetStatus = 'active' | 'inactive' | 'scanned' | 'decommissioned';

export interface AssetPort {
    id?: number;
    port: number;
    protocol: string;
    service?: string;
    product?: string;
    version?: string;
    last_seen?: string;
}

export interface AssetVulnerability {
    id?: number;
    template_id?: string;
    name: string;
    severity: Severity;
    cve?: string;
    cvss?: number;
    matched_at?: string;
    status: string;
    first_seen?: string;
    last_seen?: string;
}

export interface AssetItem {
    id: number;
    ip_address: string;
    hostname?: string;
    asset_type: AssetType;
    status: AssetStatus;
    criticality: AssetCriticality;
    risk_score: number;
    open_ports_count: number;
    vulnerabilities_count: number;
    critical_count: number;
    high_count: number;
    medium_count: number;
    low_count: number;
    tags?: string[];
    notes?: string;
    last_scanned_at?: string;
    created_at: string;
    updated_at: string;
}

export interface AssetDetail extends AssetItem {
    ports: AssetPort[];
    vulnerabilities: AssetVulnerability[];
}

export interface AssetListResponse {
    items: AssetItem[];
    total: number;
    limit: number;
    offset: number;
}

export interface AssetStats {
    total_assets: number;
    active_assets: number;
    critical_risk_assets: number;
    total_open_ports: number;
    total_vulnerabilities: number;
    asset_type_distribution: Record<string, number>;
    criticality_distribution: Record<string, number>;
}

export interface AssetUpdateRequest {
    criticality?: AssetCriticality;
    status?: AssetStatus;
    tags?: string[];
    notes?: string;
}

// ==================== BATCH SCANS ====================

export interface BatchScanCreateRequest {
    targets?: string[];
    raw_targets?: string;
    scan_profile?: ScanProfile;
    options?: ScanOptions;
    batch_name?: string;
}

export interface BatchScanItem {
    scan_id: string;
    target: string;
    status: ScanStatus;
    risk_score: number;
    duration?: number;
    error?: string;
}

export interface BatchScanCreateResponse {
    batch_id: string;
    batch_name?: string;
    total_targets: number;
    created_scans: BatchScanItem[];
    skipped_targets: Array<{ target: string; reason: string }>;
    message: string;
}

export interface BatchScanStatusResponse {
    batch_id: string;
    batch_name?: string;
    total: number;
    completed: number;
    running: number;
    failed: number;
    pending: number;
    scans: BatchScanItem[];
    overall_risk_score: number;
    created_at?: string;
}