# 🎯 Quick Reference - New Features

## 🆕 New Pages

| URL | Purpose | Key Features |
|-----|---------|--------------|
| `/scans/new` | Create new scan | Scan modes, advanced options, queue status |
| `/scans/progress/{id}` | Track scan progress | Phase tracker, live logs, real-time stats |
| `/scans/history` | View scan history | Renamed from `/history` (auto-redirects) |

## 🎨 Scan Modes

### ⚡ Quick Scan
- **Ports**: 1-1000 (top ports)
- **Templates**: CVE, Misconfig, Exposure
- **Timeout**: 15 minutes
- **Use Case**: Fast initial assessment

### 🔍 Deep Scan
- **Ports**: 1-65535 (all ports)
- **Templates**: All categories
- **Timeout**: 60 minutes
- **Use Case**: Comprehensive security audit

### ⚙️ Custom Scan
- **Ports**: User-defined
- **Templates**: User-selected
- **Timeout**: User-set
- **Use Case**: Specific testing needs

## 📊 Progress Phases

1. **Validation** - Target validation and preparation
2. **Nmap Scan** - Port scanning and service detection
3. **Nuclei Scan** - Vulnerability template execution
4. **AI Analysis** - Risk scoring and prioritization
5. **Complete** - Final report generation

## 🎨 Visual Indicators

### Phase States
- 🟢 **Green** = Completed
- 🔵 **Blue (pulsing)** = Running
- ⚪ **Gray** = Pending

### Log Colors
- 🟢 **Green** = Success (ports found, scan complete)
- 🟡 **Yellow** = Warning (vulnerabilities found)
- 🔴 **Red** = Error/Critical (critical vulns, failures)
- 🔵 **Blue** = Info (general updates)

### Risk Scores
- 🟢 **0-3.9** = Low (green)
- 🟡 **4-5.9** = Medium (yellow)
- 🟠 **6-7.9** = High (orange)
- 🔴 **8-10** = Critical (red)

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+Shift+R` | Hard refresh (if styles not loading) |
| `F12` | Open browser DevTools |
| `Ctrl+Shift+M` | Toggle device toolbar (responsive testing) |

## 🔧 Advanced Options

### Port Range Examples
- `1-1000` - Top 1000 ports
- `1-65535` - All ports
- `80,443,8080` - Specific ports
- `1-100,443,8000-9000` - Mixed ranges

### Nmap Timing
- `T1` - Paranoid (very slow, stealthy)
- `T2` - Sneaky (slow)
- `T3` - Normal (default)
- `T4` - Aggressive (recommended)
- `T5` - Insane (very fast, may miss results)

### Nuclei Templates
- **CVE** - Known vulnerabilities
- **Misconfig** - Configuration issues
- **Exposure** - Sensitive data exposure
- **Tech Detection** - Technology fingerprinting

## 📱 Responsive Breakpoints

| Device | Width | Layout |
|--------|-------|--------|
| Desktop | 1200px+ | Full grid, side-by-side |
| Tablet | 768-1199px | Stacked grids |
| Mobile | <768px | Single column |

## 🚨 Common Issues

### Scan Won't Start
1. Check queue has available slots
2. Verify target is valid
3. Check backend is running
4. Review browser console

### Progress Not Updating
1. Check polling is active (connection status)
2. Verify scan is running in backend
3. Check API endpoint returns data
4. Hard refresh browser

### Styles Not Applied
1. Hard refresh: `Ctrl+Shift+R`
2. Clear browser cache
3. Check CSS file loaded (DevTools Network tab)

## 🎯 Best Practices

### Scan Configuration
- ✅ Use **Quick Scan** for initial assessment
- ✅ Use **Deep Scan** for thorough audits
- ✅ Lower concurrency for unstable targets
- ✅ Adjust timeout based on target size

### Performance
- ✅ Close progress page when done (stops polling)
- ✅ Don't run too many concurrent scans
- ✅ Monitor queue status before starting
- ✅ Use appropriate scan mode for task

### Security
- ⚠️ Only scan targets you own or have permission to test
- ⚠️ Be aware of rate limits on target systems
- ⚠️ Deep scans may trigger security alerts
- ⚠️ Review results before taking action

## 📊 API Endpoints (for developers)

### UI Routes
```
GET  /scans/new              - Scan creation page
GET  /scans/progress/{id}    - Progress tracking page
GET  /scans/history          - Scan history page
GET  /scan/{id}              - Scan detail page
GET  /dashboard              - Dashboard page
```

### API Routes (existing)
```
POST /api/scan/              - Create scan
GET  /api/scan/results/{id}  - Get scan results
GET  /api/scan/history       - Get scan history
GET  /api/scan/queue         - Get queue status
GET  /ui/api/dashboard-stats - Get dashboard stats
```

## 🎨 CSS Classes (for customization)

### Buttons
- `.btn` - Base button
- `.btn-primary` - Primary action (blue)
- `.btn-outline` - Outlined button
- `.btn-danger` - Destructive action (red)
- `.btn-lg` - Large button

### Status Badges
- `.badge-running` - Running status (blue)
- `.badge-completed` - Completed status (green)
- `.badge-failed` - Failed status (red)
- `.badge-timeout` - Timeout status (yellow)

### Cards
- `.card` - Base card
- `.stat-card` - Statistics card
- `.info-card` - Information card
- `.phase-tracker-card` - Phase tracker container

## 🔍 Debugging Tips

### Browser Console
```javascript
// Check if polling is running
console.log('Polling active:', pollingInterval !== null);

// Check current scan data
console.log('Scan data:', data);

// Check connection status
console.log('Connection:', document.querySelector('.status-text').textContent);
```

### Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Filter by "Fetch/XHR"
4. Watch for polling requests to `/api/scan/results/{id}`
5. Check response data

### Console Errors
- Red errors = JavaScript issues
- Yellow warnings = Non-critical issues
- Blue info = General logging

## 📈 Performance Metrics

### Expected Load Times
- New Scan page: <500ms
- Progress page: <500ms
- Dashboard: <1s (with charts)

### Polling Behavior
- Interval: 2 seconds
- Stops on: completed, failed, timeout
- Continues on: running, pending

### Animation Performance
- Target: 60fps
- Method: Hardware-accelerated CSS
- Fallback: Reduced motion for accessibility

## 🎓 Tips & Tricks

### Quick Workflow
1. Bookmark `/scans/new` for fast access
2. Use browser back button to return to progress
3. Open scan detail in new tab to keep progress visible
4. Use Quick Scan for most targets

### Power User
1. Use Custom mode for specific testing
2. Adjust concurrency based on target
3. Monitor queue status before bulk scans
4. Review logs for detailed insights

### Troubleshooting
1. Always check browser console first
2. Verify backend logs if frontend looks fine
3. Hard refresh if styles broken
4. Clear cache if persistent issues

## 📞 Quick Help

### File Locations
```
Templates:     app/templates/scan_new.html
               app/templates/scan_progress.html

JavaScript:    app/static/js/scan_new.js
               app/static/js/scan_progress.js

CSS:           app/static/css/styles.css

Routes:        app/routes/ui.py
```

### Documentation
```
Architecture:  SAAS_UPGRADE_PLAN.md
Details:       IMPLEMENTATION_SUMMARY.md
Testing:       TESTING_GUIDE.md
Summary:       UPGRADE_SUMMARY.md
Reference:     QUICK_REFERENCE.md (this file)
```

---

**Print this page for quick reference while testing!** 📄
