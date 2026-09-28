import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import Base, engine, SessionLocal, ensure_schema_updated
from backend.models import (
    User,
    Session,
    Transcript,
    ClinicalNote,
    CodeSuggestion,
    ScrubbingResult,
    ReviewAudit,
    CaseDocument,
    Notification,
    ActivityLog,
)
from backend.services.seed_service import seed_database
from backend.routers import (
    auth,
    sessions,
    transcripts,
    clinical_notes,
    coding,
    scrubbing,
    reviews,
    dashboard,
    zoom,
    teams,
    performance,
    notifications,
    assistant,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("medcode")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and auto-seed database
    logger.info("Initializing MedCode AI database schema...")
    Base.metadata.create_all(bind=engine)
    ensure_schema_updated()
    
    db = SessionLocal()
    try:
        seed_database(db)
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
    finally:
        db.close()
    
    yield
    # Shutdown
    logger.info("MedCode AI backend shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Medical Scrubber & Coder Operations Platform API",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Core & Scrubber Routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(sessions.router, prefix=settings.API_PREFIX)
app.include_router(transcripts.router, prefix=settings.API_PREFIX)
app.include_router(clinical_notes.router, prefix=settings.API_PREFIX)
app.include_router(coding.router, prefix=settings.API_PREFIX)
app.include_router(scrubbing.router, prefix=settings.API_PREFIX)
app.include_router(reviews.router, prefix=settings.API_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_PREFIX)
app.include_router(zoom.router, prefix=settings.API_PREFIX)
app.include_router(teams.router, prefix=settings.API_PREFIX)
app.include_router(performance.router, prefix=settings.API_PREFIX)
app.include_router(notifications.router, prefix=settings.API_PREFIX)
app.include_router(assistant.router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs_url": "/docs",
    }

@app.get("/health")
def health():
    return {"status": "healthy", "engine": settings.AI_MODE}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
