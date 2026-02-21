from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base

from routers import videos, sync, categories

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Korean Food Encyclopedia API",
    description="API to serve K-Food YouTube content for the Web App",
    version="1.0.0"
)

# Setup CORS for Frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In prod, allow only frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(videos.router)
app.include_router(sync.router)
app.include_router(categories.router)

@app.get("/api/health")
def read_health():
    return {"status": "ok"}
