# Backend CORS Configuration

To allow the React frontend to communicate with the FastAPI backend, you need to enable CORS.

## Add CORS Middleware to Backend

Edit `app/main.py` and add the following after creating the FastAPI app:

```python
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade AI-powered vulnerability scanner",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",  # Alternative localhost
        # Add your production domain here
        # "https://yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## For Production

Update the `allow_origins` list to include your production frontend URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Testing CORS

1. Start the backend:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Open browser to http://localhost:5173

4. Check browser console for CORS errors. If configured correctly, you should see successful API requests.

## Troubleshooting

If you still see CORS errors:

1. **Check the error message** in browser console
2. **Verify backend is running** on port 8000
3. **Ensure CORS middleware is added** before route includes
4. **Check allow_origins** includes the frontend URL
5. **Try clearing browser cache** and hard reload (Ctrl+Shift+R)

## Security Note

For production:
- Never use `allow_origins=["*"]` (allows any origin)
- Specify exact domains
- Use HTTPS in production
- Consider implementing authentication/authorization
