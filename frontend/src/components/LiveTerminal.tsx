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
                    // Deduplicate by timestamp + message if replaying
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
                    message: `[STREAM COMPLETE] Scan execution finished with status: ${data.status || 'completed'}.`,
                };
                setLogs((prev) => [...prev, finalEvent]);
            } catch {
                // Ignore parse errors on completion event
            }
        });

        eventSource.onerror = () => {
            setIsConnected(false);
            // If scan already completed or done, close peacefully
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
            className={`flex flex-col bg-cyber-dark/95 border border-cyber-border rounded-xl overflow-hidden shadow-2xl backdrop-blur-md transition-all duration-200 ${
                isExpanded ? 'fixed inset-4 z-50 h-auto' : 'h-[440px]'
            } ${className}`}
        >
            {/* Terminal Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-cyber-light/40 border-b border-cyber-border select-none">
                <div className="flex items-center space-x-3">
                    <div className="flex space-x-1.5">
                        <div className="w-3 h-3 rounded-full bg-red-500/80" />
                        <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                        <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                    </div>
                    <div className="flex items-center space-x-2 text-xs font-mono text-gray-300">
                        <Terminal className="w-4 h-4 text-cyber-blue" />
                        <span className="font-semibold text-white">Live Execution Terminal</span>
                        <span className="text-gray-500">|</span>
                        <span>scan_id: {scanId.slice(0, 8)}...</span>
                    </div>
                </div>

                {/* Status Indicator */}
                <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                        {isConnected ? (
                            <span className="flex items-center text-xs font-mono text-emerald-400">
                                <Radio className="w-3.5 h-3.5 mr-1 text-emerald-400 animate-pulse" />
                                LIVE STREAMING
                            </span>
                        ) : isDone ? (
                            <span className="text-xs font-mono text-gray-400">
                                STREAM FINISHED
                            </span>
                        ) : (
                            <span className="text-xs font-mono text-yellow-500">
                                OFFLINE / BUFFERED
                            </span>
                        )}
                    </div>

                    <div className="flex items-center space-x-1 text-gray-400">
                        <button
                            onClick={() => setIsExpanded(!isExpanded)}
                            title={isExpanded ? 'Collapse' : 'Expand full screen'}
                            className="p-1.5 hover:text-white hover:bg-cyber-light/60 rounded-md transition-colors"
                        >
                            {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Filter and Control Toolbar */}
            <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-2 bg-cyber-dark/60 border-b border-cyber-border text-xs">
                <div className="flex items-center space-x-2">
                    {/* Search */}
                    <div className="relative">
                        <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Filter console..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="bg-cyber-light/40 border border-cyber-border rounded pl-8 pr-2.5 py-1 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-cyber-blue"
                        />
                    </div>

                    {/* Stage filter dropdown */}
                    <select
                        value={filterStage}
                        onChange={(e) => setFilterStage(e.target.value)}
                        className="bg-cyber-light/40 border border-cyber-border rounded px-2 py-1 text-xs text-gray-200 focus:outline-none focus:border-cyber-blue"
                    >
                        <option value="all">All Stages</option>
                        <option value="init">Init</option>
                        <option value="nmap">Port Scan (Nmap)</option>
                        <option value="nuclei">Vuln Scan (Nuclei)</option>
                        <option value="ai">AI Analysis</option>
                    </select>
                </div>

                {/* Toolbar Buttons */}
                <div className="flex items-center space-x-2">
                    <button
                        onClick={() => setAutoScroll(!autoScroll)}
                        className={`flex items-center space-x-1 px-2.5 py-1 rounded border transition-colors ${
                            autoScroll
                                ? 'bg-cyber-blue/15 text-cyber-blue border-cyber-blue/40'
                                : 'bg-cyber-light/40 text-gray-400 border-cyber-border hover:text-white'
                        }`}
                        title="Toggle Auto-Scroll"
                    >
                        {autoScroll ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                        <span>Auto-scroll</span>
                    </button>

                    <button
                        onClick={handleCopyAll}
                        className="flex items-center space-x-1 px-2.5 py-1 bg-cyber-light/40 hover:bg-cyber-light/80 text-gray-300 hover:text-white border border-cyber-border rounded transition-colors"
                        title="Copy all logs to clipboard"
                    >
                        {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                        <span>{copied ? 'Copied' : 'Copy'}</span>
                    </button>

                    <button
                        onClick={handleClearLogs}
                        className="p-1 text-gray-400 hover:text-red-400 rounded transition-colors"
                        title="Clear terminal view"
                    >
                        <Trash2 className="w-3.5 h-3.5" />
                    </button>

                    {!isConnected && (
                        <button
                            onClick={handleReconnect}
                            className="p-1 text-gray-400 hover:text-cyber-blue rounded transition-colors"
                            title="Reconnect stream"
                        >
                            <RotateCcw className="w-3.5 h-3.5" />
                        </button>
                    )}
                </div>
            </div>

            {/* Terminal Output Display */}
            <div className="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-1.5 bg-[#0a0f1d] select-text">
                {filteredLogs.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-gray-500 py-12">
                        <Terminal className="w-8 h-8 mb-2 opacity-40 text-cyber-blue" />
                        <p>No terminal output received yet.</p>
                        <p className="text-[11px] text-gray-600 mt-1">
                            Awaiting scanner process log stream from backend...
                        </p>
                    </div>
                ) : (
                    filteredLogs.map((log, index) => {
                        const stageBadge = getLogStageBadge(log.stage);
                        const levelClass = getLogLevelClass(log.level);

                        return (
                            <div
                                key={`${log.timestamp}-${index}`}
                                className="flex items-start space-x-2.5 leading-relaxed hover:bg-white/[0.02] px-1 py-0.5 rounded transition-colors group"
                            >
                                <span className="text-gray-500 select-none shrink-0">
                                    {formatLogTimestamp(log.timestamp)}
                                </span>

                                <span
                                    className={`inline-block px-1.5 py-0.2 rounded border text-[10px] font-semibold tracking-wider uppercase shrink-0 ${stageBadge.colorClass}`}
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
            <div className="flex items-center justify-between px-4 py-1.5 bg-[#070b14] border-t border-cyber-border/60 text-[11px] font-mono text-gray-500">
                <span>Total events: {logs.length} | Filtered: {filteredLogs.length}</span>
                <span className="flex items-center space-x-1">
                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-cyber-blue animate-pulse" />
                    <span>XenoraSec Stream v1.0</span>
                </span>
            </div>
        </div>
    );
};
