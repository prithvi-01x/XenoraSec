import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, History, Settings, Shield, Menu, X, Server } from 'lucide-react';
import { useQueueInfo } from '../hooks/useApi';

interface LayoutProps {
    children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
    const location = useLocation();
    const { data: queueInfo } = useQueueInfo();
    const [mobileOpen, setMobileOpen] = useState(false);

    const navItems = [
        { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/assets', icon: Server, label: 'Asset Inventory' },
        { path: '/history', icon: History, label: 'History' },
        { path: '/settings', icon: Settings, label: 'Settings' },
    ];

    const renderSidebarContent = (isMobile = false) => (
        <>
            <div className="p-6 border-b border-gray-700 flex items-center justify-between">
                <Link 
                    to="/" 
                    className="flex items-center gap-3"
                    onClick={() => isMobile && setMobileOpen(false)}
                >
                    <Shield className="w-8 h-8 text-primary flex-shrink-0" />
                    <div>
                        <h1 className="text-xl font-bold tracking-tight text-white">XenoraSec</h1>
                        <p className="text-xs text-gray-400">Security Analysis</p>
                    </div>
                </Link>
                {isMobile && (
                    <button
                        onClick={() => setMobileOpen(false)}
                        className="p-1 rounded-md text-gray-400 hover:text-white hover:bg-surface-light"
                        aria-label="Close menu"
                    >
                        <X className="w-5 h-5" />
                    </button>
                )}
            </div>

            <nav className="flex-1 p-4">
                <ul className="space-y-2">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;

                        return (
                            <li key={item.path}>
                                <Link
                                    to={item.path}
                                    onClick={() => isMobile && setMobileOpen(false)}
                                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                                        isActive
                                            ? 'bg-primary text-white'
                                            : 'text-gray-300 hover:bg-surface-light'
                                    }`}
                                >
                                    <Icon className="w-5 h-5" />
                                    <span className="font-medium">{item.label}</span>
                                </Link>
                            </li>
                        );
                    })}
                </ul>
            </nav>

            {/* Queue Info */}
            {queueInfo && (
                <div className="p-4 border-t border-gray-700">
                    <div className="bg-background rounded-lg p-3">
                        <div className="text-xs text-gray-400 mb-1">Scan Queue</div>
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">
                                {queueInfo.scans_running} / {queueInfo.max_concurrent_scans}
                            </span>
                            <span className="text-xs text-gray-400">active</span>
                        </div>
                        {queueInfo.available_slots === 0 && (
                            <div className="mt-2 text-xs text-warning">Queue Full</div>
                        )}
                    </div>
                </div>
            )}
        </>
    );

    return (
        <div className="min-h-screen flex flex-col md:flex-row bg-background">
            {/* Mobile Header */}
            <header className="md:hidden flex items-center justify-between p-4 bg-surface border-b border-gray-700 sticky top-0 z-30">
                <Link to="/" className="flex items-center gap-2">
                    <Shield className="w-7 h-7 text-primary" />
                    <span className="text-lg font-bold tracking-tight text-white">XenoraSec</span>
                </Link>
                <button
                    onClick={() => setMobileOpen(true)}
                    className="p-2 rounded-lg text-gray-300 hover:text-white hover:bg-surface-light transition-colors"
                    aria-label="Open menu"
                >
                    <Menu className="w-6 h-6" />
                </button>
            </header>

            {/* Mobile Drawer Backdrop */}
            {mobileOpen && (
                <div
                    className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden"
                    onClick={() => setMobileOpen(false)}
                />
            )}

            {/* Mobile Drawer */}
            <aside
                className={`fixed inset-y-0 left-0 w-64 bg-surface border-r border-gray-700 z-50 flex flex-col md:hidden transform transition-transform duration-300 ease-in-out ${
                    mobileOpen ? 'translate-x-0' : '-translate-x-full'
                }`}
            >
                {renderSidebarContent(true)}
            </aside>

            {/* Desktop Sidebar */}
            <aside className="hidden md:flex flex-col w-64 bg-surface border-r border-gray-700 shrink-0 min-h-screen">
                {renderSidebarContent(false)}
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                <div className="max-w-7xl mx-auto p-4 sm:p-6 md:p-8">
                    {children}
                </div>
            </main>
        </div>
    );
}
