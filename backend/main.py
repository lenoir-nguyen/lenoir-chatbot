"""
Lenoir Chatbot API - Main Application Entry Point

This is the FastAPI application factory and configuration. It handles:
- CORS middleware for cross-origin requests from frontend
- Router registration for all API endpoints
- Health check endpoint with Redis status monitoring

Configuration:
- Version: 1.0.0 (Basic chat with language support)
- Base URL: /chat (all chat endpoints prefixed with /chat)
- Health check: /health (returns API and cache status)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from routers import chat
from cache import is_redis_available

settings = get_settings()
app = FastAPI(title="Lenoir Chatbot API", version="1.0.0")

# ============================================================================
# CORS Middleware - Allow Frontend to Call This API
# ============================================================================
# CORS (Cross-Origin Resource Sharing) is required because the frontend
# (Vercel) and backend (Railway) are on different domains.
#
# Configuration:
# - allow_origins: Frontend URLs that can call this API
# - allow_credentials: Allow cookies/auth headers
# - allow_methods: All HTTP methods allowed (GET, POST, DELETE, etc.)
# - allow_headers: All headers allowed (Content-Type, Authorization, etc.)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API Routes Registration
# ============================================================================
# Include all routers. Routes are prefixed with their router prefix.
# Example: chat router has prefix="/chat", so endpoints are /chat/message

app.include_router(chat.router)

# ============================================================================
# Health Check Endpoint - Includes Redis Status
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring API status.

    Returns both API and Redis (cache) status. Useful for:
    - Load balancer health checks (Railway, Vercel, etc.)
    - Monitoring Redis connectivity
    - Debugging deployment issues

    Redis Usage:
    - Checks if Redis is accessible via is_redis_available()
    - Returns "connected" or "disconnected" status
    - Does NOT affect response if Redis is down (graceful degradation)

    Returns:
        dict: Contains "status" (API status) and "redis" (cache status)

    Example response:
        {
            "status": "ok",
            "redis": "connected"
        }
    """
    # REDIS CHECK: Ping Redis to verify cache layer is accessible
    # If Redis is down, this still returns "ok" but "redis": "disconnected"
    redis_status = "connected" if is_redis_available() else "disconnected"

    return {
        "status": "ok",
        "redis": redis_status
    }


# ============================================================================
# Application Startup
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
