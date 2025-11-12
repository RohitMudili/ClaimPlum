from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from api.routes import claims_supabase, members_supabase
from db.supabase_client import get_supabase

settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered OPD claim adjudication system with Supabase",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://claimplum-app.onrender.com/", "*"],  # Allow all for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(claims_supabase.router)
app.include_router(members_supabase.router)


@app.on_event("startup")
async def startup_event():
    """Verify Supabase connection on startup"""
    try:
        supabase = get_supabase()
        # Test connection
        result = supabase.table("members").select("id").limit(1).execute()
        print("✅ Supabase connection successful")
    except Exception as e:
        print(f"⚠️  Supabase connection failed: {str(e)}")
        print("Make sure SUPABASE_URL and SUPABASE_KEY are set in .env")


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Plum OPD Claim Adjudication API",
        "version": settings.APP_VERSION,
        "status": "active",
        "endpoints": {
            "claims": "/api/claims",
            "members": "/api/members",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "debug_mode": settings.DEBUG
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
