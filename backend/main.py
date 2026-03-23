import os
import sys
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from loguru import logger
import uvicorn

# Load environment variables
load_dotenv()

# We set the version constant explicitly for the health route to read
VERSION = "1.0.0"

# Adjust python path if this is run directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from backend.routes.search import router as search_router
from backend.routes.anime import router as anime_router
from backend.routes.health import router as health_router
from backend.routes.history import router as history_router
from backend.routes.history import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Railway passes port dynamically via $PORT, fallback to $API_PORT or 8000
    port = int(os.environ.get("PORT", os.getenv("API_PORT", 8000)))
    environment = "production" if os.environ.get("PORT") else "development"
    
    # Application startup
    logger.info("Initializing Hibiki API dependencies...")
    init_db()  # Initialize SQLite Tables
    logger.info(f"Starting Hibiki API in {environment} mode on port {port}")
    logger.success("API Startup complete.")
    yield
    # Application shutdown
    logger.info("Shutting down Hibiki API gracefully...")

# Hide stack traces in production
is_production = bool(os.environ.get("RAILWAY_ENVIRONMENT"))

app = FastAPI(
    title="Hibiki API",
    description="A Semantic Search Engine Backend for Anime discovery powered by ChromaDB & Sentence Transformers.",
    version=VERSION,
    lifespan=lifespan,
    debug=not is_production
)

# Parse CORS Origins strictly
cors_origins_str = os.getenv("CORS_ORIGINS", "")
origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"], # Fallback to all for local dev if not set
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 10240:
        return JSONResponse(status_code=413, content={"detail": "Payload too large. Maximum size is 10KB."})
    return await call_next(request)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Register routers 
app.include_router(search_router, prefix="/api")
app.include_router(anime_router)
app.include_router(health_router)
app.include_router(history_router)

if __name__ == "__main__":
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.environ.get("PORT", os.getenv("API_PORT", 8000)))
    
    logger.info(f"Starting server on http://{api_host}:{api_port}")
    logger.info(f"API Documentation available at: http://{api_host}:{api_port}/docs")
    
    # Run the application using Uvicorn
    uvicorn.run("backend.main:app", host=api_host, port=api_port, reload=True)
