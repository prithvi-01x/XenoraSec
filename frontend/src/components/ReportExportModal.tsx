import React, { useState } from 'react';
import { 
    X, 
    Download, 
    FileText, 
    Globe, 
    FileCode, 
    Database, 
    Check, 
    ExternalLink,
    ShieldAlert
} from 'lucide-react';
import type { ReportFormat, ReportType } from '../types/api';
import { useDownloadReport } from '../hooks/useApi';
import { scanApi } from '../api/client';
import { LoadingSpinner } from './LoadingSpinner';

interface ReportExportModalProps {
    scanId: string;
    target: string;
    isOpen: boolean;
    onClose: () => void;
}

interface FormatOption {
    id: ReportFormat;
    name: string;
    desc: string;
    icon: React.ReactNode;
    badge: string;
    badgeColor: string;
}

export const ReportExportModal: React.FC<ReportExportModalProps> = ({
    scanId,
    target,
    isOpen,
    onClose,
}) => {
    const [selectedFormat, setSelectedFormat] = useState<ReportFormat>('html');
    const [reportType, setReportType] = useState<ReportType>('technical');
    const [downloadSuccess, setDownloadSuccess] = useState<boolean>(false);

    const downloadMutation = useDownloadReport();

    if (!isOpen) return null;

    const formats: FormatOption[] = [
        {
            id: 'html',
            name: 'Interactive HTML Report',
            desc: 'Self-contained responsive dashboard with embedded telemetry and styling.',
            icon: <Globe className="w-4 h-4 text-blue-400" />,
            badge: 'RECOMMENDED',
            badgeColor: 'bg-blue-950/80 text-blue-400 border-blue-800',
        },
        {
            id: 'pdf',
            name: 'Publication PDF Document',
            desc: 'Multi-page executive/technical PDF compiled with ReportLab.',
            icon: <FileText className="w-4 h-4 text-red-400" />,
            badge: 'PRINT READY',
            badgeColor: 'bg-red-950/80 text-red-400 border-red-800',
        },
        {
            id: 'markdown',
            name: 'Technical Markdown',
            desc: 'GitHub-flavored tables and advisories for PRs and issues.',
            icon: <FileCode className="w-4 h-4 text-emerald-400" />,
            badge: 'DOCS',
            badgeColor: 'bg-emerald-950/80 text-emerald-400 border-emerald-800',
        },
        {
            id: 'json',
            name: 'Raw Structured JSON',
            desc: 'Full vulnerability schema, CVSS metrics, and service discovery.',
            icon: <Database className="w-4 h-4 text-amber-400" />,
            badge: 'SIEM READY',
            badgeColor: 'bg-amber-950/80 text-amber-400 border-amber-800',
        },
    ];

    const handleDownload = async () => {
        setDownloadSuccess(false);
        try {
            await downloadMutation.mutateAsync({
                scanId,
                format: selectedFormat,
                reportType,
            });
            setDownloadSuccess(true);
            setTimeout(() => setDownloadSuccess(false), 3000);
        } catch (err) {
            console.error('Download failed:', err);
        }
    };

    const previewUrl = scanApi.getReportUrl(scanId, selectedFormat, reportType);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <div className="relative w-full max-w-lg bg-surface border border-surface-border rounded-lg shadow-2xl overflow-hidden font-sans">
                {/* Header */}
                <div className="flex items-center justify-between px-4 py-3 border-b border-surface-border bg-[#070b12]">
                    <div className="flex items-center space-x-2.5">
                        <div className="p-1.5 rounded bg-blue-950/80 border border-blue-800 text-blue-400">
                            <ShieldAlert className="w-4 h-4" />
                        </div>
                        <div>
                            <h3 className="font-bold text-white text-xs font-mono uppercase tracking-wider">
                                Export Assessment Dossier
                            </h3>
                            <p className="text-[10px] text-slate-400 font-mono">Target: {target}</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-1 text-slate-400 hover:text-white rounded hover:bg-surface-light transition-colors"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>

                {/* Body */}
                <div className="p-4 space-y-4">
                    {/* Audience Depth */}
                    <div>
                        <label className="block text-[10px] font-mono uppercase font-semibold text-slate-400 mb-1.5">
                            Report Depth &amp; Focus
                        </label>
                        <div className="grid grid-cols-2 gap-2">
                            <button
                                type="button"
                                onClick={() => setReportType('technical')}
                                className={`p-2.5 rounded border text-left transition-all ${
                                    reportType === 'technical'
                                        ? 'bg-blue-600/10 border-blue-500 ring-1 ring-blue-500/30'
                                        : 'bg-[#070b12] border-surface-border text-slate-400 hover:text-slate-200'
                                }`}
                            >
                                <span className="font-bold text-xs block text-white mb-0.5">Technical Audit</span>
                                <span className="text-[10px] text-slate-400 block leading-normal">
                                    Vulnerability proofs, CVE details, open ports, and remediation advisory.
                                </span>
                            </button>

                            <button
                                type="button"
                                onClick={() => setReportType('executive')}
                                className={`p-2.5 rounded border text-left transition-all ${
                                    reportType === 'executive'
                                        ? 'bg-blue-600/10 border-blue-500 ring-1 ring-blue-500/30'
                                        : 'bg-[#070b12] border-surface-border text-slate-400 hover:text-slate-200'
                                }`}
                            >
                                <span className="font-bold text-xs block text-white mb-0.5">Executive Summary</span>
                                <span className="text-[10px] text-slate-400 block leading-normal">
                                    Strategic risk postures, CVSS distribution, and priority highlights.
                                </span>
                            </button>
                        </div>
                    </div>

                    {/* Format Selector */}
                    <div>
                        <label className="block text-[10px] font-mono uppercase font-semibold text-slate-400 mb-1.5">
                            Format Output
                        </label>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {formats.map((f) => {
                                const isSelected = selectedFormat === f.id;
                                return (
                                    <button
                                        key={f.id}
                                        type="button"
                                        onClick={() => setSelectedFormat(f.id)}
                                        className={`flex flex-col text-left p-2.5 rounded border transition-all ${
                                            isSelected
                                                ? 'bg-blue-600/10 border-blue-500 ring-1 ring-blue-500/30'
                                                : 'bg-[#070b12] border-surface-border hover:bg-surface-light hover:border-slate-600'
                                        }`}
                                    >
                                        <div className="flex items-center justify-between mb-1">
                                            <div className="flex items-center space-x-1.5">
                                                {f.icon}
                                                <span className="font-semibold text-xs text-white">
                                                    {f.name}
                                                </span>
                                            </div>
                                            <span
                                                className={`text-[8px] font-mono uppercase px-1 py-0.2 rounded border font-semibold ${f.badgeColor}`}
                                            >
                                                {f.badge}
                                            </span>
                                        </div>
                                        <p className="text-[10px] text-slate-400 leading-normal">
                                            {f.desc}
                                        </p>
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                </div>

                {/* Footer Controls */}
                <div className="flex items-center justify-between px-4 py-3 bg-[#070b12] border-t border-surface-border">
                    <a
                        href={previewUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center space-x-1 text-[11px] text-blue-400 hover:underline font-mono"
                    >
                        <span>Open Direct Link</span>
                        <ExternalLink className="w-3 h-3" />
                    </a>

                    <div className="flex items-center space-x-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="btn btn-secondary text-xs"
                        >
                            Cancel
                        </button>

                        <button
                            type="button"
                            onClick={handleDownload}
                            disabled={downloadMutation.isPending}
                            className="btn btn-primary text-xs"
                        >
                            {downloadMutation.isPending ? (
                                <>
                                    <LoadingSpinner size="sm" />
                                    <span>Compiling...</span>
                                </>
                            ) : downloadSuccess ? (
                                <>
                                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                                    <span>Downloaded</span>
                                </>
                            ) : (
                                <>
                                    <Download className="w-3.5 h-3.5" />
                                    <span>Download {selectedFormat.toUpperCase()}</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
