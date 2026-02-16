/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: '#0f172a',
                surface: '#1e293b',
                'surface-light': '#334155',
                primary: '#3b82f6',
                'primary-dark': '#2563eb',
                success: '#22c55e',
                danger: '#ef4444',
                warning: '#f59e0b',
                info: '#6b7280',
                critical: '#dc2626',
                high: '#f97316',
                medium: '#eab308',
                low: '#22c55e',
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
