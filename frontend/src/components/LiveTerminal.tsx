import React, { useState, useEffect, useRef } from 'react';
import { 
    Terminal, 
    Play, 
    Pause, 
    Copy, 
    Trash2, 
    Check, 
    Search, 
    Radio, 
    RotateCcw,
    Maximize2,
    Minimize2
} from 'lucide-react';
import type { ScanLogEvent } from '../types/api';
import { scanApi } from '../api/client';
import { 
    getLogStageBadge, 
    getLogLevelClass, 
    formatLogTimestamp, 
    copyToClipboard 
} from '../utils/helpers';

interface LiveTerminalProps {
    scanId: string;
    isScanActive?: boolean;
    initialLogs?: ScanLogEvent[];
    className?: string;
}

export const LiveTerminal: React.FC<LiveTerminalProps> = ({
    scanId,
    isScanActive = true,
    initialLogs = [],
    className = '',
}) => {
    const [logs, setLogs] = useState<ScanLogEvent[]>(initialLogs);
    const [isConnected, setIsConnected] = useState<boolean>(false);
    const [isDone, setIsDone] = useState<boolean>(false);
    const [autoScroll, setAutoScroll] = useState<boolean>(true);
    const [filterStage, setFilterStage] = useState<string>('all');
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [copied, setCopied] = useState<boolean>(false);
    const [isExpanded, setIsExpanded] = useState<boolean>(false);

    const terminalEndRef = useRef<HTMLDivElement>(null);
    const eventSourceRef = useRef<EventSource | null>(null);

    // Setup SSE connection
    useEffect(() => {
        if (!scanId) return;

        const streamUrl = scanApi.getStreamUrl(scanId);
        const eventSource = new EventSource(streamUrl);
        eventSourceRef.current = eventSource;

        eventSource.onopen = () => {
            setIsConnected(true);
        };

        const handleLogEvent = (e: MessageEvent) => {
            try {
                const eventData: ScanLogEvent = JSON.parse(e.data);
                setLogs((prev) => {
                    const exists = prev.some(
                        (l) => l.timestamp === eventData.timestamp && l.message === eventData.message
                    );
                    if (exists) return prev;
                    return [...prev, eventData];
                });
            } catch (err) {
                console.error('Failed to parse log event:', err);
            }
        };

        eventSource.addEventListener('init', handleLogEvent);
        eventSource.addEventListener('nmap', handleLogEvent);
        eventSource.addEventListener('nuclei', handleLogEvent);
        eventSource.addEventListener('ai', handleLogEvent);
        eventSource.addEventListener('log', handleLogEvent);

        eventSource.addEventListener('done', (e: MessageEvent) => {
            setIsDone(true);
            setIsConnected(false);
            eventSource.close();
            try {
                const data = JSON.parse(e.data);
                const finalEvent: ScanLogEvent = {
                    scan_id: scanId,
                    timestamp: new Date().toISOString(),
                    stage: 'completed',
                    level: 'success',
                    message: `[STREAM COMPLETE] Scan execution finalized with status: ${data.status || 'completed'}.`,
                };
                setLogs((prev) => [...prev, finalEvent]);
            } catch {
                // Ignore parse errors on completion event
            }
        });

        eventSource.onerror = () => {
            setIsConnected(false);
            if (isDone || !isScanActive) {
                eventSource.close();
            }
        };

        return () => {
            eventSource.close();
        };
    }, [scanId, isScanActive, isDone]);

    // Auto-scroll effect
    useEffect(() => {
        if (autoScroll && terminalEndRef.current) {
            terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [logs, autoScroll]);

    // Filter logs
    const filteredLogs = logs.filter((log) => {
        const matchesStage = filterStage === 'all' || log.stage === filterStage;
        const matchesSearch =
            !searchQuery ||
            log.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
            log.stage.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesStage && matchesSearch;
    });

    const handleCopyAll = async () => {
        const text = logs
            .map(
                (l) =>
                    `[${formatLogTimestamp(l.timestamp)}] [${l.stage.toUpperCase()}] [${l.level.toUpperCase()}] ${l.message}`
            )
            .join('\n');
        const success = await copyToClipboard(text);
        if (success) {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const handleClearLogs = () => {
        setLogs([]);
    };

    const handleReconnect = () => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
        }
        setIsDone(false);
        const streamUrl = scanApi.getStreamUrl(scanId);
        const es = new EventSource(streamUrl);
        eventSourceRef.current = es;
        setIsConnected(true);
    };

    return (
        <div
            className={`flex flex-col bg-[#05080e] border border-surface-border rounded-lg overflow-hidden shadow-2xl transition-all duration-200 ${
                isExpanded ? 'fixed inset-4 z-50 h-auto' : 'h-[440px]'
            } ${className}`}
        >
            {/* Terminal Header */}
            <div className="flex items-center justify-between px-3.5 py-2.5 bg-[#090d16] border-b border-surface-border select-none">
                <div className="flex items-center space-x-2.5">
                    <div className="flex space-x-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
                        <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80" />
                        <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
                    </div>
                    <div className="flex items-center space-x-2 text-xs font-mono text-slate-300">
                        <Terminal className="w-3.5 h-3.5 text-blue-400" />
                        <span className="font-semibold text-white">Execution Console</span>
                        <span className="text-slate-600">|</span>
                        <span className="text-slate-400">scan_id: {scanId.slice(0, 8)}...</span>
                    </div>
                </div>

                {/* Status Indicator */}
                <div className="flex items-center space-x-3">
                    <div className="flex items-center space-x-2">
                        {isConnected ? (
                            <span className="flex items-center text-[11px] font-mono text-emerald-400">
                                <Radio className="w-3 h-3 mr-1 text-emerald-400 animate-pulse" />
                                STREAMING LIVE
                            </span>
                        ) : isDone ? (
                            <span className="text-[11px] font-mono text-slate-400">
                                STREAM CLOSED
                            </span>
                        ) : (
                            <span className="text-[11px] font-mono text-amber-400">
                                BUFFERED
                            </span>
                        )}
                    </div>

                    <div className="flex items-center space-x-1 text-slate-400">
                        <button
                            onClick={() => setIsExpanded(!isExpanded)}
                            title={isExpanded ? 'Collapse' : 'Expand full screen'}
                            className="p-1 hover:text-white hover:bg-surface-light rounded transition-colors"
                        >
                            {isExpanded ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Filter and Control Toolbar */}
            <div className="flex flex-wrap items-center justify-between gap-2 px-3 py-1.5 bg-[#070b12] border-b border-surface-border text-xs">
                <div className="flex items-center space-x-2">
                    {/* Search */}
                    <div className="relative">
                        <Search className="w-3 h-3 absolute left-2 top-1/2 -translate-y-1/2 text-slate-500" />
                        <input
                            type="text"
                            placeholder="Filter console..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="bg-[#05080e] border border-surface-border rounded pl-7 pr-2 py-0.5 text-xs text-slate-100 placeholder-slate-600 font-mono focus:outline-none focus:border-blue-500"
                        />
                    </div>

                    {/* Stage filter dropdown */}
                    <select
                        value={filterStage}
                        onChange={(e) => setFilterStage(e.target.value)}
                        className="bg-[#05080e] border border-surface-border rounded px-2 py-0.5 text-xs text-slate-300 font-mono focus:outline-none focus:border-blue-500"
                    >
                        <option value="all">All Stages</option>
                        <option value="init">Init</option>
                        <option value="nmap">Nmap Discovery</option>
                        <option value="nuclei">Nuclei Scanner</option>
                        <option value="ai">AI Analysis</option>
                    </select>
                </div>

                {/* Toolbar Buttons */}
                <div className="flex items-center space-x-1.5 font-mono">
                    <button
                        onClick={() => setAutoScroll(!autoScroll)}
                        className={`flex items-center space-x-1 px-2 py-0.5 rounded border text-[11px] transition-colors ${
                            autoScroll
                                ? 'bg-blue-950/80 text-blue-400 border-blue-800'
                                : 'bg-surface text-slate-400 border-surface-border hover:text-white'
                        }`}
                        title="Toggle Auto-Scroll"
                    >
                        {autoScroll ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                        <span>Auto-scroll</span>
                    </button>

                    <button
                        onClick={handleCopyAll}
                        className="flex items-center space-x-1 px-2 py-0.5 bg-surface hover:bg-surface-light text-slate-300 hover:text-white border border-surface-border rounded text-[11px] transition-colors"
                        title="Copy logs to clipboard"
                    >
                        {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                        <span>{copied ? 'Copied' : 'Copy'}</span>
                    </button>

                    <button
                        onClick={handleClearLogs}
                        className="p-1 text-slate-400 hover:text-rose-400 rounded transition-colors"
                        title="Clear terminal view"
                    >
                        <Trash2 className="w-3.5 h-3.5" />
                    </button>

                    {!isConnected && (
                        <button
                            onClick={handleReconnect}
                            className="p-1 text-slate-400 hover:text-blue-400 rounded transition-colors"
                            title="Reconnect stream"
                        >
                            <RotateCcw className="w-3.5 h-3.5" />
                        </button>
                    )}
                </div>
            </div>

            {/* Terminal Output Display */}
            <div className="flex-1 overflow-y-auto p-3 font-mono text-[11px] space-y-1 bg-[#05080e] select-text">
                {filteredLogs.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-slate-500 py-12">
                        <Terminal className="w-6 h-6 mb-2 opacity-30 text-blue-400" />
                        <p>No terminal output received yet.</p>
                        <p className="text-[10px] text-slate-600 mt-0.5">
                            Awaiting scanner process log stream from backend engine...
                        </p>
                    </div>
                ) : (
                    filteredLogs.map((log, index) => {
                        const stageBadge = getLogStageBadge(log.stage);
                        const levelClass = getLogLevelClass(log.level);

                        return (
                            <div
                                key={`${log.timestamp}-${index}`}
                                className="flex items-start space-x-2 leading-relaxed hover:bg-white/[0.02] px-1 py-0.5 rounded transition-colors"
                            >
                                <span className="text-slate-500 select-none shrink-0 text-[10px]">
                                    {formatLogTimestamp(log.timestamp)}
                                </span>

                                <span
                                    className={`inline-block px-1.5 py-0.2 rounded border text-[9px] font-semibold tracking-wider uppercase shrink-0 font-mono ${stageBadge.colorClass}`}
                                >
                                    {stageBadge.label}
                                </span>

                                <span className={`flex-1 break-all ${levelClass}`}>
                                    {log.message}
                                </span>
                            </div>
                        );
                    })
                )}
                <div ref={terminalEndRef} />
            </div>

            {/* Terminal Footer status info */}
            <div className="flex items-center justify-between px-3 py-1 bg-[#070b12] border-t border-surface-border text-[10px] font-mono text-slate-500">
                <span>Total log events: {logs.length} | Displayed: {filteredLogs.length}</span>
                <span className="flex items-center space-x-1.5">
                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-blue-500" />
                    <span>XenoraSec Stream Service</span>
                </span>
            </div>
        </div>
    );
};
