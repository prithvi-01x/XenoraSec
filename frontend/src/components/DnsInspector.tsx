import { useState } from 'react';
import { 
    Network, 
    Mail, 
    ShieldCheck, 
    AlertTriangle, 
    ShieldAlert, 
    Copy, 
    Check, 
    Server, 
    ArrowRight
} from 'lucide-react';
import type { DNSIntelligence } from '../types/api';

interface DnsInspectorProps {
    dns: DNSIntelligence;
}

export function DnsInspector({ dns }: DnsInspectorProps) {
    const [copiedIndex, setCopiedIndex] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<'a_records' | 'mx' | 'txt' | 'ns' | 'asn'>('a_records');

    const copyToClipboard = (text: string, id: string) => {
        navigator.clipboard.writeText(text);
        setCopiedIndex(id);
        setTimeout(() => setCopiedIndex(null), 2000);
    };

    const mailSecurity = dns.mail_security;

    // Filter records by category
    const addressRecords = dns.records.filter(r => ['A', 'AAAA', 'CNAME'].includes(r.record_type));
    const mxRecords = dns.records.filter(r => r.record_type === 'MX').sort((a, b) => (a.priority || 0) - (b.priority || 0));
    const txtRecords = dns.records.filter(r => r.record_type === 'TXT');
    const nsRecords = dns.records.filter(r => r.record_type === 'NS');

    const getMailRatingBadge = (rating?: string) => {
        if (rating === 'secure') {
            return (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-950/80 border border-emerald-700 text-emerald-400 text-xs font-mono font-semibold">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    Mail Spoofing Protected
                </span>
            );
        }
        if (rating === 'warning') {
            return (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-950/80 border border-amber-700 text-amber-400 text-xs font-mono font-semibold">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    Permissive Email Policy
                </span>
            );
        }
        return (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-rose-950/80 border border-rose-700 text-rose-400 text-xs font-mono font-semibold">
                <ShieldAlert className="w-3.5 h-3.5" />
                Vulnerable to Email Spoofing
            </span>
        );
    };

    return (
        <div className="bg-surface rounded-lg border border-surface-border p-5 space-y-5">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded bg-blue-600/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
                        <Network className="w-4 h-4" />
                    </div>
                    <div>
                        <h3 className="text-sm font-semibold text-white font-mono flex items-center gap-2">
                            DNS Topology & Network Intelligence
                            <span className="text-xs px-2 py-0.5 rounded-full bg-blue-950 border border-blue-800 text-blue-400 font-mono">
                                {dns.records.length} Records
                            </span>
                        </h3>
                        <p className="text-xs text-slate-400">Resource records, authoritative nameservers, and mail authentication</p>
                    </div>
                </div>

                {mailSecurity && getMailRatingBadge(mailSecurity.security_rating)}
            </div>

            {/* Email Security Hygiene Card */}
            {mailSecurity && (
                <div className="bg-[#070b13] rounded border border-surface-border p-3.5 space-y-3">
                    <div className="flex items-center gap-2 text-xs font-mono font-semibold text-slate-300">
                        <Mail className="w-4 h-4 text-blue-400" />
                        <span>Domain Email Authentication Hygiene</span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
                        {/* SPF Card */}
                        <div className="p-2.5 rounded bg-surface border border-surface-border space-y-1.5">
                            <div className="flex items-center justify-between">
                                <span className="text-slate-400">SPF (Sender Policy Framework)</span>
                                <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-semibold ${
                                    mailSecurity.spf_status === 'pass'
                                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                                        : mailSecurity.spf_status === 'warning'
                                        ? 'bg-amber-950 text-amber-400 border border-amber-800'
                                        : 'bg-rose-950 text-rose-400 border border-rose-800'
                                }`}>
                                    {mailSecurity.spf_status}
                                </span>
                            </div>
                            <p className="text-[11px] text-slate-300 break-all bg-[#090d16] p-1.5 rounded border border-surface-border">
                                {mailSecurity.spf_record || 'No v=spf1 TXT record configured on root domain'}
                            </p>
                        </div>

                        {/* DMARC Card */}
                        <div className="p-2.5 rounded bg-surface border border-surface-border space-y-1.5">
                            <div className="flex items-center justify-between">
                                <span className="text-slate-400">DMARC Policy Enforcement</span>
                                <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-semibold ${
                                    mailSecurity.dmarc_policy === 'reject'
                                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                                        : mailSecurity.dmarc_policy === 'quarantine'
                                        ? 'bg-amber-950 text-amber-400 border border-amber-800'
                                        : 'bg-rose-950 text-rose-400 border border-rose-800'
                                }`}>
                                    {mailSecurity.dmarc_policy || 'missing'}
                                </span>
                            </div>
                            <p className="text-[11px] text-slate-300 break-all bg-[#090d16] p-1.5 rounded border border-surface-border">
                                {mailSecurity.dmarc_record || 'No _dmarc TXT policy configured for domain'}
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Record type tab selectors */}
            <div className="flex items-center gap-1.5 border-b border-surface-border pb-2 overflow-x-auto text-xs font-mono">
                <button
                    onClick={() => setActiveTab('a_records')}
                    className={`px-3 py-1.5 rounded transition-colors whitespace-nowrap ${
                        activeTab === 'a_records'
                            ? 'bg-blue-600/20 text-blue-400 border border-blue-500/40 font-semibold'
                            : 'text-slate-400 hover:text-white hover:bg-surface-light border border-transparent'
                    }`}
                >
                    A / AAAA / CNAME ({addressRecords.length})
                </button>
                <button
                    onClick={() => setActiveTab('mx')}
                    className={`px-3 py-1.5 rounded transition-colors whitespace-nowrap ${
                        activeTab === 'mx'
                            ? 'bg-blue-600/20 text-blue-400 border border-blue-500/40 font-semibold'
                            : 'text-slate-400 hover:text-white hover:bg-surface-light border border-transparent'
                    }`}
                >
                    MX Exchangers ({mxRecords.length})
                </button>
                <button
                    onClick={() => setActiveTab('ns')}
                    className={`px-3 py-1.5 rounded transition-colors whitespace-nowrap ${
                        activeTab === 'ns'
                            ? 'bg-blue-600/20 text-blue-400 border border-blue-500/40 font-semibold'
                            : 'text-slate-400 hover:text-white hover:bg-surface-light border border-transparent'
                    }`}
                >
                    Nameservers ({nsRecords.length})
                </button>
                <button
                    onClick={() => setActiveTab('txt')}
                    className={`px-3 py-1.5 rounded transition-colors whitespace-nowrap ${
                        activeTab === 'txt'
                            ? 'bg-blue-600/20 text-blue-400 border border-blue-500/40 font-semibold'
                            : 'text-slate-400 hover:text-white hover:bg-surface-light border border-transparent'
                    }`}
                >
                    TXT Records ({txtRecords.length})
                </button>
                <button
                    onClick={() => setActiveTab('asn')}
                    className={`px-3 py-1.5 rounded transition-colors whitespace-nowrap ${
                        activeTab === 'asn'
                            ? 'bg-blue-600/20 text-blue-400 border border-blue-500/40 font-semibold'
                            : 'text-slate-400 hover:text-white hover:bg-surface-light border border-transparent'
                    }`}
                >
                    ASN & Topology ({Object.keys(dns.asn_details || {}).length})
                </button>
            </div>

            {/* Tab content view */}
            <div className="space-y-2">
                {activeTab === 'a_records' && (
                    <div className="space-y-2">
                        {addressRecords.length === 0 ? (
                            <p className="text-xs text-slate-500 py-4 text-center font-mono">No Address records discovered</p>
                        ) : (
                            addressRecords.map((rec, i) => {
                                const revHost = dns.reverse_dns?.[rec.value];
                                const asn = dns.asn_details?.[rec.value];

                                return (
                                    <div 
                                        key={i}
                                        className="p-3 rounded bg-[#070a11] border border-surface-border flex flex-col md:flex-row md:items-center justify-between gap-2 text-xs font-mono"
                                    >
                                        <div className="flex items-center gap-3">
                                            <span className="px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800 font-semibold">
                                                {rec.record_type}
                                            </span>
                                            <span className="text-slate-200 font-semibold">{rec.host}</span>
                                            <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                                            <span className="text-emerald-400 font-bold">{rec.value}</span>
                                            {revHost && (
                                                <span className="text-slate-400 text-[11px]">
                                                    (PTR: {revHost})
                                                </span>
                                            )}
                                        </div>
                                        <div className="flex items-center gap-2">
                                            {asn && (
                                                <span className="px-1.5 py-0.5 rounded bg-surface border border-surface-border text-[10px] text-slate-400">
                                                    {asn.asn} · {asn.org}
                                                </span>
                                            )}
                                            {rec.ttl && (
                                                <span className="text-slate-500 text-[10px]">TTL {rec.ttl}s</span>
                                            )}
                                            <button
                                                onClick={() => copyToClipboard(rec.value, `addr-${i}`)}
                                                className="p-1 rounded text-slate-400 hover:text-white"
                                                title="Copy IP"
                                            >
                                                {copiedIndex === `addr-${i}` ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                                            </button>
                                        </div>
                                    </div>
                                );
                            })
                        )}
                    </div>
                )}

                {activeTab === 'mx' && (
                    <div className="space-y-2">
                        {mxRecords.length === 0 ? (
                            <p className="text-xs text-slate-500 py-4 text-center font-mono">No MX records configured</p>
                        ) : (
                            mxRecords.map((rec, i) => (
                                <div key={i} className="p-3 rounded bg-[#070a11] border border-surface-border flex items-center justify-between text-xs font-mono">
                                    <div className="flex items-center gap-3">
                                        <span className="px-2 py-0.5 rounded bg-purple-950 text-purple-400 border border-purple-800 font-semibold">
                                            MX {rec.priority !== undefined ? `[Pri ${rec.priority}]` : ''}
                                        </span>
                                        <span className="text-slate-200">{rec.value}</span>
                                    </div>
                                    <button
                                        onClick={() => copyToClipboard(rec.value, `mx-${i}`)}
                                        className="p-1 rounded text-slate-400 hover:text-white"
                                    >
                                        {copiedIndex === `mx-${i}` ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                )}

                {activeTab === 'ns' && (
                    <div className="space-y-2">
                        {nsRecords.length === 0 ? (
                            <p className="text-xs text-slate-500 py-4 text-center font-mono">No NS records returned</p>
                        ) : (
                            nsRecords.map((rec, i) => (
                                <div key={i} className="p-3 rounded bg-[#070a11] border border-surface-border flex items-center justify-between text-xs font-mono">
                                    <div className="flex items-center gap-3">
                                        <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-semibold">
                                            NS
                                        </span>
                                        <span className="text-slate-200">{rec.value}</span>
                                    </div>
                                    <button
                                        onClick={() => copyToClipboard(rec.value, `ns-${i}`)}
                                        className="p-1 rounded text-slate-400 hover:text-white"
                                    >
                                        {copiedIndex === `ns-${i}` ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                )}

                {activeTab === 'txt' && (
                    <div className="space-y-2">
                        {txtRecords.length === 0 ? (
                            <p className="text-xs text-slate-500 py-4 text-center font-mono">No TXT records discovered</p>
                        ) : (
                            txtRecords.map((rec, i) => (
                                <div key={i} className="p-3 rounded bg-[#070a11] border border-surface-border flex items-start justify-between gap-3 text-xs font-mono">
                                    <div className="flex items-start gap-3">
                                        <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800 font-semibold shrink-0">
                                            TXT
                                        </span>
                                        <span className="text-slate-300 break-all select-all">{rec.value}</span>
                                    </div>
                                    <button
                                        onClick={() => copyToClipboard(rec.value, `txt-${i}`)}
                                        className="p-1 rounded text-slate-400 hover:text-white shrink-0"
                                    >
                                        {copiedIndex === `txt-${i}` ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                )}

                {activeTab === 'asn' && (
                    <div className="space-y-2">
                        {Object.entries(dns.asn_details || {}).length === 0 ? (
                            <p className="text-xs text-slate-500 py-4 text-center font-mono">No ASN mappings available</p>
                        ) : (
                            Object.entries(dns.asn_details).map(([ip, details], i) => (
                                <div key={i} className="p-3 rounded bg-[#070a11] border border-surface-border flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-mono">
                                    <div className="flex items-center gap-3">
                                        <Server className="w-4 h-4 text-blue-400" />
                                        <span className="text-emerald-400 font-bold">{ip}</span>
                                        <span className="text-slate-400">({details.country || 'N/A'})</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className="px-2 py-0.5 rounded bg-blue-950/80 border border-blue-800 text-blue-300 font-semibold">
                                            {details.asn || 'AS-UNKNOWN'}
                                        </span>
                                        <span className="text-slate-300 font-medium">
                                            {details.org || 'Registered Org'}
                                        </span>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
