import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
    LayoutDashboard, 
    History, 
    Settings, 
    Shield, 
    Menu, 
    X, 
    Server, 
    Activity,
    Layers,
    TerminalSquare
} from 'lucide-react';
import { useQueueInfo, useHealth } from '../hooks/useApi';

interface LayoutProps {
    children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
    const location = useLocation();
    const { data: queueInfo } = useQueueInfo();
    const { data: health } = useHealth();
    const [mobileOpen, setMobileOpen] = useState(false);

    const navItems = [
        { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/assets', icon: Server, label: 'Asset Inventory' },
        { path: '/history', icon: History, label: 'Scan Audit Log' },
        { path: '/settings', icon: Settings, label: 'Engine & System' },
    ];

    const renderNavContent = (isMobile = false) => (
        <>
            {/* Logo / Header */}
            <div className="h-14 px-4 border-b border-surface-border flex items-center justify-between bg-surface">
                <Link 
                    to="/" 
                    className="flex items-center gap-2.5 group"
                    onClick={() => isMobile && setMobileOpen(false)}
                >
                    <div className="w-8 h-8 rounded bg-blue-600/10 border border-blue-500/30 flex items-center justify-center text-blue-400 group-hover:border-blue-400 transition-colors">
                        <Shield className="w-4 h-4 text-blue-400" />
                    </div>
                    <div>
                        <div className="flex items-center gap-1.5">
                            <span className="text-sm font-bold tracking-tight text-white font-mono">XENORA<span className="text-blue-500">SEC</span></span>
                            <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-blue-950/80 text-blue-400 border border-blue-800/60 font-semibold">v2.1</span>
                        </div>
                        <p className="text-[10px] text-slate-400 font-mono tracking-tight">Security Assessment Core</p>
                    </div>
                </Link>
                {isMobile && (
                    <button
                        onClick={() => setMobileOpen(false)}
                        className="p-1 rounded text-slate-400 hover:text-white hover:bg-surface-light"
                        aria-label="Close menu"
                    >
                        <X className="w-5 h-5" />
                    </button>
                )}
            </div>

            {/* Navigation links */}
            <nav className="flex-1 p-3 space-y-1">
                <div className="px-2 py-1 text-[10px] font-mono uppercase font-semibold text-slate-500 tracking-wider">
                    Navigation
                </div>
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));

                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            onClick={() => isMobile && setMobileOpen(false)}
                            className={`flex items-center gap-2.5 px-3 py-2 rounded text-xs font-medium transition-all ${
                                isActive
                                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 font-semibold'
                                    : 'text-slate-300 hover:text-white hover:bg-surface-light border border-transparent'
                            }`}
                        >
                            <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                            <span>{item.label}</span>
                        </Link>
                    );
                })}
            </nav>

            {/* Bottom Engine Telemetry Panel */}
            <div className="p-3 border-t border-surface-border bg-[#070b12] space-y-2">
                <div className="flex items-center justify-between text-[11px] font-mono">
                    <span className="text-slate-400 flex items-center gap-1.5">
                        <TerminalSquare className="w-3.5 h-3.5 text-blue-400" />
                        Backend
                    </span>
                    <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-400">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                        {health?.status === 'healthy' ? 'ONLINE' : 'ACTIVE'}
                    </span>
                </div>

                {queueInfo && (
                    <div className="bg-surface rounded p-2 border border-surface-border space-y-1.5">
                        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                            <span>WORKER QUEUE</span>
                            <span className="text-white font-bold">
                                {queueInfo.scans_running} / {queueInfo.max_concurrent_scans} active
                            </span>
                        </div>
                        <div className="w-full bg-[#05080e] rounded-full h-1 overflow-hidden">
                            <div 
                                className={`h-full transition-all duration-300 ${
                                    queueInfo.scans_running >= queueInfo.max_concurrent_scans 
                                        ? 'bg-amber-400' 
                                        : 'bg-blue-500'
                                }`}
                                style={{ 
                                    width: `${Math.min(100, (queueInfo.scans_running / Math.max(1, queueInfo.max_concurrent_scans)) * 100)}%` 
                                }}
                            />
                        </div>
                        <div className="flex items-center justify-between text-[10px] font-mono">
                            <span className="text-slate-500">Slots Open:</span>
                            <span className={queueInfo.available_slots === 0 ? 'text-amber-400 font-bold' : 'text-slate-300 font-medium'}>
                                {queueInfo.available_slots} slots
                            </span>
                        </div>
                    </div>
                )}
            </div>
        </>
    );

    return (
        <div className="min-h-screen flex flex-col md:flex-row bg-background text-slate-100">
            {/* Mobile Header Bar */}
            <header className="md:hidden flex items-center justify-between h-14 px-4 bg-surface border-b border-surface-border sticky top-0 z-30">
                <Link to="/" className="flex items-center gap-2">
                    <Shield className="w-5 h-5 text-blue-400" />
                    <span className="text-sm font-bold tracking-tight text-white font-mono">XENORA<span className="text-blue-500">SEC</span></span>
                </Link>
                <button
                    onClick={() => setMobileOpen(true)}
                    className="p-1.5 rounded text-slate-300 hover:text-white hover:bg-surface-light transition-colors"
                    aria-label="Open menu"
                >
                    <Menu className="w-5 h-5" />
                </button>
            </header>

            {/* Mobile Drawer Backdrop */}
            {mobileOpen && (
                <div
                    className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 md:hidden"
                    onClick={() => setMobileOpen(false)}
                />
            )}

            {/* Mobile Drawer */}
            <aside
                className={`fixed inset-y-0 left-0 w-64 bg-surface border-r border-surface-border z-50 flex flex-col md:hidden transform transition-transform duration-200 ease-in-out ${
                    mobileOpen ? 'translate-x-0' : '-translate-x-full'
                }`}
            >
                {renderNavContent(true)}
            </aside>

            {/* Desktop Sidebar */}
            <aside className="hidden md:flex flex-col w-60 bg-surface border-r border-surface-border shrink-0 min-h-screen sticky top-0 h-screen select-none">
                {renderNavContent(false)}
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 min-w-0 overflow-y-auto">
                {/* Global Top Bar */}
                <div className="h-12 border-b border-surface-border px-4 sm:px-6 flex items-center justify-between bg-surface/50 backdrop-blur-sm sticky top-0 z-20">
                    <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
                        <Activity className="w-3.5 h-3.5 text-blue-400" />
                        <span className="uppercase text-[11px] font-semibold text-slate-300">Target Attack Surface Security Platform</span>
                    </div>
                    <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
                        <span className="hidden sm:inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-surface border border-surface-border text-[11px]">
                            <Layers className="w-3 h-3 text-blue-400" />
                            <span>FastAPI Core + Nmap + Nuclei</span>
                        </span>
                    </div>
                </div>

                {/* Page view container */}
                <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
                    {children}
                </div>
            </main>
        </div>
    );
}
