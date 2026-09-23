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
            desc: 'Modern dark/cyber standalone document with embedded CSS and print-to-PDF styles.',
            icon: <Globe className="w-5 h-5 text-cyber-blue" />,
            badge: 'RECOMMENDED',
            badgeColor: 'bg-cyber-blue/15 text-cyber-blue border-cyber-blue/30',
        },
        {
            id: 'pdf',
            name: 'Publication PDF Document',
            desc: 'Professional multi-page PDF formatted with ReportLab for board and stakeholder delivery.',
            icon: <FileText className="w-5 h-5 text-red-400" />,
            badge: 'PRINT READY',
            badgeColor: 'bg-red-500/15 text-red-400 border-red-500/30',
        },
        {
            id: 'markdown',
            name: 'Technical Markdown',
            desc: 'Clean GitHub-flavored Markdown tables and advisories ready for Git repos and PRs.',
            icon: <FileCode className="w-5 h-5 text-emerald-400" />,
            badge: 'DOCUMENTATION',
            badgeColor: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
        },
        {
            id: 'json',
            name: 'Raw Structured JSON',
            desc: 'Complete vulnerability data, CVSS metrics, and service discovery for SIEM/automation ingestion.',
            icon: <Database className="w-5 h-5 text-amber-400" />,
            badge: 'MACHINE-READABLE',
            badgeColor: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
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
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
            <div className="relative w-full max-w-xl bg-cyber-dark border border-cyber-border rounded-2xl shadow-2xl overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-cyber-border bg-cyber-light/20">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 rounded-lg bg-cyber-blue/10 border border-cyber-blue/20">
                            <ShieldAlert className="w-5 h-5 text-cyber-blue" />
                        </div>
                        <div>
                            <h3 className="font-bold text-white text-base">Generate Security Assessment Report</h3>
                            <p className="text-xs text-gray-400 font-mono">Target: {target}</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-1.5 text-gray-400 hover:text-white rounded-lg hover:bg-cyber-light/40 transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Body */}
                <div className="p-6 space-y-6">
                    {/* Audience Selector */}
                    <div>
                        <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
                            Report Audience &amp; Depth
                        </label>
                        <div className="grid grid-cols-2 gap-3">
                            <button
                                type="button"
                                onClick={() => setReportType('technical')}
                                className={`p-3 rounded-xl border text-left transition-all ${
                                    reportType === 'technical'
                                        ? 'bg-cyber-blue/15 border-cyber-blue text-white ring-1 ring-cyber-blue/30'
                                        : 'bg-cyber-light/10 border-cyber-border text-gray-400 hover:text-gray-200'
                                }`}
                            >
                                <span className="font-bold text-sm block mb-1">Technical Audit</span>
                                <span className="text-xs text-gray-400 block leading-relaxed">
                                    Full vulnerability proofs, CVE details, open port tables, and remediation notes.
                                </span>
                            </button>

                            <button
                                type="button"
                                onClick={() => setReportType('executive')}
                                className={`p-3 rounded-xl border text-left transition-all ${
                                    reportType === 'executive'
                                        ? 'bg-cyber-blue/15 border-cyber-blue text-white ring-1 ring-cyber-blue/30'
                                        : 'bg-cyber-light/10 border-cyber-border text-gray-400 hover:text-gray-200'
                                }`}
                            >
                                <span className="font-bold text-sm block mb-1">Executive Summary</span>
                                <span className="text-xs text-gray-400 block leading-relaxed">
                                    Strategic risk scores, high-level posture, and top remediation priorities.
                                </span>
                            </button>
                        </div>
                    </div>

                    {/* Format Selector */}
                    <div>
                        <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
                            Export Format
                        </label>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                            {formats.map((f) => {
                                const isSelected = selectedFormat === f.id;
                                return (
                                    <button
                                        key={f.id}
                                        type="button"
                                        onClick={() => setSelectedFormat(f.id)}
                                        className={`flex flex-col text-left p-3 rounded-xl border transition-all ${
                                            isSelected
                                                ? 'bg-cyber-blue/15 border-cyber-blue ring-1 ring-cyber-blue/30'
                                                : 'bg-cyber-light/10 border-cyber-border hover:bg-cyber-light/20 hover:border-gray-600'
                                        }`}
                                    >
                                        <div className="flex items-center justify-between mb-1.5">
                                            <div className="flex items-center space-x-2">
                                                {f.icon}
                                                <span className="font-semibold text-xs text-white">
                                                    {f.name}
                                                </span>
                                            </div>
                                            <span
                                                className={`text-[9px] font-mono uppercase px-1.5 py-0.2 rounded border font-semibold ${f.badgeColor}`}
                                            >
                                                {f.badge}
                                            </span>
                                        </div>
                                        <p className="text-[11px] text-gray-400 leading-normal">
                                            {f.desc}
                                        </p>
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                </div>

                {/* Footer Controls */}
                <div className="flex items-center justify-between px-6 py-4 bg-cyber-dark/80 border-t border-cyber-border">
                    <a
                        href={previewUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center space-x-1.5 text-xs text-cyber-blue hover:underline font-mono"
                    >
                        <span>Open Raw Stream / URL</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                    </a>

                    <div className="flex items-center space-x-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-xs font-semibold text-gray-400 hover:text-white rounded-lg hover:bg-cyber-light/30 transition-colors"
                        >
                            Cancel
                        </button>

                        <button
                            type="button"
                            onClick={handleDownload}
                            disabled={downloadMutation.isPending}
                            className="btn btn-primary flex items-center space-x-2 px-4 py-2 text-xs font-semibold rounded-lg shadow-lg shadow-cyber-blue/20 disabled:opacity-50"
                        >
                            {downloadMutation.isPending ? (
                                <>
                                    <LoadingSpinner size="sm" />
                                    <span>Compiling Report...</span>
                                </>
                            ) : downloadSuccess ? (
                                <>
                                    <Check className="w-4 h-4 text-emerald-400" />
                                    <span>Downloaded!</span>
                                </>
                            ) : (
                                <>
                                    <Download className="w-4 h-4" />
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
