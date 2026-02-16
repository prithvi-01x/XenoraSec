import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, History, Settings, Activity } from 'lucide-react';
import { useQueueInfo } from '../hooks/useApi';

interface LayoutProps {
    children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
    const location = useLocation();
    const { data: queueInfo } = useQueueInfo();

    const navItems = [
        { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/history', icon: History, label: 'History' },
        { path: '/settings', icon: Settings, label: 'Settings' },
    ];

    return (
        <div className="min-h-screen flex">
            {/* Sidebar */}
            <aside className="w-64 bg-surface border-r border-gray-700 flex flex-col">
                <div className="p-6 border-b border-gray-700">
                    <div className="flex items-center gap-2">
                        <Activity className="w-8 h-8 text-primary" />
                        <div>
                            <h1 className="text-xl font-bold">VulnScanner</h1>
                            <p className="text-xs text-gray-400">Security Analysis</p>
                        </div>
                    </div>
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
                                        className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive
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
                                    {queueInfo.active_scans} / {queueInfo.max_concurrent_scans}
                                </span>
                                <span className="text-xs text-gray-400">active</span>
                            </div>
                            {queueInfo.available_slots === 0 && (
                                <div className="mt-2 text-xs text-warning">Queue Full</div>
                            )}
                        </div>
                    </div>
                )}
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                <div className="max-w-7xl mx-auto p-8">
                    {children}
                </div>
            </main>
        </div>
    );
}
