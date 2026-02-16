# VulnScanner Frontend

Production-ready React + TypeScript frontend for the AI-powered vulnerability scanner.

## Tech Stack

- **React 18** with TypeScript
- **Vite** - Fast build tool and dev server
- **TailwindCSS** - Utility-first styling
- **React Router** - Client-side routing
- **TanStack Query (React Query)** - Server state management
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **Lucide React** - Icon library

## Features

### 1. Dashboard
- Real-time statistics (total scans, running scans, avg risk score, critical findings)
- Severity distribution chart
- Recent scans table
- Integrated scan panel

### 2. Scan Panel
- Target validation (IP, domain, URL)
- Real-time error handling (rate limits, queue full)
- Automatic navigation to results

### 3. Scan Results Page
- Live updates for running scans (3-second polling)
- Executive summary with risk score visualization
- Tabbed interface:
  - **Summary**: Severity distribution and top ports
  - **Ports**: Detailed port scan results table
  - **Vulnerabilities**: Filterable/searchable vulnerability list with expandable details
  - **Raw JSON**: Full scan data
- Retry failed scans
- Delete scans

### 4. History Page
- Paginated scan history (10 per page)
- Filter by status
- Search by target
- Quick actions (view, delete)

### 5. Settings Page
- Scanner configuration (mock - backend API needed)
- Nmap timing templates
- Concurrency limits
- Rate limiting
- Target restrictions

## Project Structure

```
src/
├── api/
│   └── client.ts           # Axios client with interceptors
├── components/
│   ├── ErrorState.tsx      # Error display component
│   ├── LoadingSpinner.tsx  # Loading states
│   ├── RiskScore.tsx       # Risk score visualization
│   ├── ScanPanel.tsx       # Scan initiation form
│   ├── SeverityBadge.tsx   # Severity indicators
│   └── StatusBadge.tsx     # Status indicators
├── hooks/
│   └── useApi.ts           # React Query hooks
├── layouts/
│   └── Layout.tsx          # Main layout with sidebar
├── pages/
│   ├── DashboardPage.tsx   # Dashboard view
│   ├── HistoryPage.tsx     # Scan history
│   ├── ScanResultsPage.tsx # Detailed scan results
│   └── SettingsPage.tsx    # Configuration
├── types/
│   └── api.ts              # TypeScript definitions
├── utils/
│   └── helpers.ts          # Utility functions
├── App.tsx                 # Root component
├── main.tsx                # Entry point
└── index.css               # Global styles
```

## Setup Instructions

### Prerequisites
- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API endpoint:**
   
   Edit `.env` file:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```
   
   The app will be available at `http://localhost:5173`

4. **Build for production:**
   ```bash
   npm run build
   ```
   
   Output will be in `dist/` directory

### Backend Integration

The frontend expects the following API endpoints:

#### Scan Operations
- `POST /api/scan/` - Start new scan
- `GET /api/scan/results/{scan_id}` - Get scan results
- `GET /api/scan/history` - Get scan history (with pagination)
- `POST /api/scan/{scan_id}/retry` - Retry failed scan
- `DELETE /api/scan/{scan_id}` - Delete scan
- `GET /api/scan/queue` - Get queue info
- `POST /api/scan/cleanup` - Cleanup old scans

#### Dashboard
- `GET /ui/api/dashboard-stats` - Get dashboard statistics

#### Health
- `GET /health` - Health check

## Performance Optimizations

1. **React Query Caching**
   - 30-second stale time for queries
   - Automatic cache invalidation on mutations
   - Smart refetching strategies

2. **Polling Strategy**
   - Only active for running scans
   - 3-second interval for live updates
   - Automatic cleanup on unmount

3. **Code Splitting**
   - Route-based lazy loading ready
   - Component-level memoization where needed

4. **Optimized Rendering**
   - Minimal re-renders with proper dependency arrays
   - Debounced search inputs
   - Virtualization-ready table structure

## Design System

### Colors
- **Background**: `#0f172a` (slate-900)
- **Surface**: `#1e293b` (slate-800)
- **Primary**: `#3b82f6` (blue-500)
- **Success**: `#22c55e` (green-500)
- **Danger**: `#ef4444` (red-500)
- **Warning**: `#f59e0b` (amber-500)

### Severity Colors
- **Critical**: `#dc2626` (red-600)
- **High**: `#f97316` (orange-500)
- **Medium**: `#eab308` (yellow-500)
- **Low**: `#22c55e` (green-500)
- **Info**: `#6b7280` (gray-500)

### Typography
- Font: Inter (Google Fonts)
- Weights: 400, 500, 600, 700

## Development Guidelines

### Adding New Features

1. **Create types** in `src/types/api.ts`
2. **Add API methods** in `src/api/client.ts`
3. **Create React Query hooks** in `src/hooks/useApi.ts`
4. **Build components** in `src/components/`
5. **Add pages** in `src/pages/`
6. **Update routing** in `src/App.tsx`

### Code Style

- Use TypeScript strict mode
- Prefer functional components with hooks
- Use Tailwind utility classes
- Follow component composition patterns
- Keep components focused and reusable

### Testing (Future)

Recommended testing stack:
- **Vitest** - Unit testing
- **React Testing Library** - Component testing
- **Playwright** - E2E testing

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Known Limitations

1. **Settings API**: Settings page uses mock data - backend implementation needed
2. **WebSockets**: Currently using polling - WebSocket support can be added for real-time updates
3. **Authentication**: No auth implemented - add JWT/OAuth2 as needed
4. **Offline Support**: No service worker - can be added for PWA functionality

## Future Enhancements

- [ ] WebSocket integration for real-time updates
- [ ] Export scan results (PDF, CSV)
- [ ] Scan comparison view
- [ ] Advanced filtering and sorting
- [ ] Scheduled scans
- [ ] User authentication and authorization
- [ ] Dark/light theme toggle
- [ ] Keyboard shortcuts
- [ ] Accessibility improvements (ARIA labels)

## Troubleshooting

### API Connection Issues
- Verify backend is running on correct port
- Check CORS settings in backend
- Confirm `.env` has correct `VITE_API_BASE_URL`

### Build Errors
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf node_modules/.vite`

### Performance Issues
- Check React DevTools for unnecessary re-renders
- Verify React Query cache settings
- Monitor network tab for excessive API calls

## License

MIT

## Support

For issues and questions, please open a GitHub issue or contact the development team.
