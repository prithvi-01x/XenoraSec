# Quick Start Guide

## Prerequisites

1. **Backend API must be running** on `http://localhost:8000`
2. Node.js 18+ installed
3. npm installed

## Running the Frontend

### 1. Install Dependencies (First Time Only)

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The application will be available at: **http://localhost:5173**

### 3. Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

### 4. Preview Production Build

```bash
npm run preview
```

## Configuration

Edit `.env` to change the API base URL:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Testing the Application

1. **Start the backend** (in a separate terminal):
   ```bash
   cd ..
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Start the frontend**:
   ```bash
   npm run dev
   ```

3. **Open browser** to http://localhost:5173

4. **Try scanning**:
   - Enter a target (e.g., `scanme.nmap.org`)
   - Click "Start Scan"
   - View results in real-time

## Troubleshooting

### CORS Errors
If you see CORS errors in the browser console, ensure your backend has CORS configured:

```python
# In backend app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Connection Failed
- Verify backend is running on port 8000
- Check `.env` file has correct `VITE_API_BASE_URL`
- Open browser DevTools → Network tab to see failed requests

### Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Features to Test

1. **Dashboard**
   - View statistics
   - Start new scan
   - See recent scans

2. **Scan Results**
   - Live updates for running scans
   - View vulnerabilities
   - Filter by severity
   - Export raw JSON

3. **History**
   - Paginated list
   - Filter by status
   - Search by target
   - Delete scans

4. **Settings**
   - Configure scanner (mock data)

## Next Steps

- Add authentication
- Implement WebSocket for real-time updates
- Add export functionality (PDF/CSV)
- Implement settings API endpoints in backend
